#ifdef _WIN32

#ifndef _WIN32_WINNT
#define _WIN32_WINNT 0x0602
#endif

#include "appcontainer_launcher.h"

#include <windows.h>
#include <userenv.h>
#include <aclapi.h>
#include <objbase.h>
#include <sddl.h>

#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <iostream>
#include <string>
#include <thread>
#include <vector>

namespace
{
constexpr size_t kMaxSourceBytes = 64 * 1024 * 1024;
constexpr SIZE_T kWorkerMemoryLimit = 768ULL * 1024 * 1024;

struct ScopedHandle
{
    HANDLE value = nullptr;

    ScopedHandle() = default;
    explicit ScopedHandle(HANDLE handle)
        : value(handle)
    {
    }
    ~ScopedHandle()
    {
        if (value && value != INVALID_HANDLE_VALUE)
            CloseHandle(value);
    }
    ScopedHandle(const ScopedHandle&) = delete;
    ScopedHandle& operator=(const ScopedHandle&) = delete;
    HANDLE release()
    {
        HANDLE result = value;
        value = nullptr;
        return result;
    }
};

std::wstring widen(const std::string& value)
{
    if (value.empty())
        return {};
    const int count = MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS, value.data(),
                                           static_cast<int>(value.size()), nullptr, 0);
    if (count <= 0)
        return {};
    std::wstring result(static_cast<size_t>(count), L'\0');
    if (!MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS, value.data(),
                             static_cast<int>(value.size()), result.data(), count))
        return {};
    return result;
}

std::wstring quoteArgument(const std::wstring& argument)
{
    std::wstring quoted = L"\"";
    size_t slashes = 0;
    for (wchar_t character : argument)
    {
        if (character == L'\\')
        {
            ++slashes;
            continue;
        }
        if (character == L'\"')
        {
            quoted.append(slashes * 2 + 1, L'\\');
            quoted.push_back(character);
            slashes = 0;
            continue;
        }
        quoted.append(slashes, L'\\');
        slashes = 0;
        quoted.push_back(character);
    }
    quoted.append(slashes * 2, L'\\');
    quoted.push_back(L'\"');
    return quoted;
}

bool readSource(std::string& source)
{
    source.clear();
    char buffer[64 * 1024];
    while (std::cin)
    {
        std::cin.read(buffer, sizeof(buffer));
        const std::streamsize count = std::cin.gcount();
        if (count > 0)
        {
            if (source.size() + static_cast<size_t>(count) > kMaxSourceBytes)
            {
                std::fprintf(stderr, "Protez AppContainer launcher: source exceeds 64 MiB\n");
                return false;
            }
            source.append(buffer, static_cast<size_t>(count));
        }
    }
    return !std::cin.bad();
}

bool appendEnvironmentEntry(std::vector<wchar_t>& block, const std::wstring& name,
                            const std::wstring& value)
{
    const std::wstring entry = name + L"=" + value;
    block.insert(block.end(), entry.begin(), entry.end());
    block.push_back(L'\0');
    return true;
}

bool createWorkerJob(ScopedHandle& job)
{
    job.value = CreateJobObjectW(nullptr, nullptr);
    if (!job.value)
        return false;

    JOBOBJECT_EXTENDED_LIMIT_INFORMATION limits{};
    limits.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE |
                                               JOB_OBJECT_LIMIT_ACTIVE_PROCESS |
                                               JOB_OBJECT_LIMIT_PROCESS_MEMORY |
                                               JOB_OBJECT_LIMIT_JOB_MEMORY;
    limits.BasicLimitInformation.ActiveProcessLimit = 1;
    limits.ProcessMemoryLimit = kWorkerMemoryLimit;
    limits.JobMemoryLimit = kWorkerMemoryLimit;
    return SetInformationJobObject(job.value, JobObjectExtendedLimitInformation, &limits,
                                   sizeof(limits)) != FALSE;
}

bool makeWorkerDirectory(const std::wstring& profileName, PSID& appContainerSid,
                         std::wstring& workerDirectory, std::wstring& profilePath)
{
    HRESULT result = CreateAppContainerProfile(profileName.c_str(), L"Protez analysis worker",
                                                L"Runs untrusted Luau without network access",
                                                nullptr, 0, &appContainerSid);
    if (FAILED(result))
    {
        if (result != HRESULT_FROM_WIN32(ERROR_ALREADY_EXISTS))
            return false;
        result = DeriveAppContainerSidFromAppContainerName(profileName.c_str(), &appContainerSid);
        if (FAILED(result))
            return false;
    }

    PWSTR sidText = nullptr;
    if (!ConvertSidToStringSidW(appContainerSid, &sidText))
        return false;

    PWSTR rawPath = nullptr;
    result = GetAppContainerFolderPath(sidText, &rawPath);
    LocalFree(sidText);
    if (FAILED(result) || !rawPath)
        return false;
    profilePath = rawPath;
    CoTaskMemFree(rawPath);

    wchar_t suffix[80] = {};
    swprintf_s(suffix, L"\\run-%lu-%llu", GetCurrentProcessId(),
               static_cast<unsigned long long>(GetTickCount64()));
    workerDirectory = profilePath + suffix;
    return CreateDirectoryW(workerDirectory.c_str(), nullptr) != FALSE;
}

bool launchWorker(const std::wstring& workerExecutable, const std::wstring& workerDirectory,
                  const std::wstring& profilePath, const std::vector<std::wstring>& arguments,
                  PSID appContainerSid, const std::string& source, DWORD& exitCode)
{
    SECURITY_ATTRIBUTES pipeSecurity{};
    pipeSecurity.nLength = sizeof(pipeSecurity);
    pipeSecurity.bInheritHandle = TRUE;

    ScopedHandle childInput;
    ScopedHandle parentInput;
    ScopedHandle parentOutput;
    ScopedHandle childOutput;
    if (!CreatePipe(&childInput.value, &parentInput.value, &pipeSecurity, 0) ||
        !CreatePipe(&parentOutput.value, &childOutput.value, &pipeSecurity, 0))
        return false;
    if (!SetHandleInformation(parentInput.value, HANDLE_FLAG_INHERIT, 0) ||
        !SetHandleInformation(parentOutput.value, HANDLE_FLAG_INHERIT, 0))
        return false;

    STARTUPINFOEXW startup{};
    startup.StartupInfo.cb = sizeof(startup);
    startup.StartupInfo.dwFlags = STARTF_USESTDHANDLES;
    startup.StartupInfo.hStdInput = childInput.value;
    startup.StartupInfo.hStdOutput = childOutput.value;
    startup.StartupInfo.hStdError = childOutput.value;

    SIZE_T attributeBytes = 0;
    InitializeProcThreadAttributeList(nullptr, 2, 0, &attributeBytes);
    if (!attributeBytes)
        return false;
    std::vector<unsigned char> attributeStorage(attributeBytes);
    startup.lpAttributeList = reinterpret_cast<LPPROC_THREAD_ATTRIBUTE_LIST>(attributeStorage.data());
    if (!InitializeProcThreadAttributeList(startup.lpAttributeList, 2, 0, &attributeBytes))
        return false;

    SECURITY_CAPABILITIES capabilities{};
    capabilities.AppContainerSid = appContainerSid;
    HANDLE inheritedHandles[] = {childInput.value, childOutput.value};
    const bool attributesReady =
        UpdateProcThreadAttribute(startup.lpAttributeList, 0,
                                 PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES,
                                 &capabilities, sizeof(capabilities), nullptr, nullptr) &&
        UpdateProcThreadAttribute(startup.lpAttributeList, 0,
                                 PROC_THREAD_ATTRIBUTE_HANDLE_LIST,
                                 inheritedHandles, sizeof(inheritedHandles), nullptr, nullptr);
    if (!attributesReady)
    {
        DeleteProcThreadAttributeList(startup.lpAttributeList);
        return false;
    }

    std::vector<wchar_t> environment;
    wchar_t windowsDirectory[MAX_PATH] = {};
    const UINT windowsLength = GetWindowsDirectoryW(windowsDirectory, MAX_PATH);
    if (!windowsLength || windowsLength >= MAX_PATH)
    {
        DeleteProcThreadAttributeList(startup.lpAttributeList);
        return false;
    }
    const std::wstring systemRoot(windowsDirectory, windowsLength);
    const std::wstring system32 = systemRoot + L"\\System32";
    const std::wstring tempDirectory = workerDirectory + L"\\Temp";
    if (!CreateDirectoryW(tempDirectory.c_str(), nullptr) && GetLastError() != ERROR_ALREADY_EXISTS)
    {
        DeleteProcThreadAttributeList(startup.lpAttributeList);
        return false;
    }
    appendEnvironmentEntry(environment, L"LOCALAPPDATA", profilePath);
    appendEnvironmentEntry(environment, L"PATH", system32);
    appendEnvironmentEntry(environment, L"SystemRoot", systemRoot);
    appendEnvironmentEntry(environment, L"TEMP", tempDirectory);
    appendEnvironmentEntry(environment, L"TMP", tempDirectory);
    appendEnvironmentEntry(environment, L"USERPROFILE", workerDirectory);
    environment.push_back(L'\0');

    std::wstring commandLine = quoteArgument(workerExecutable);
    for (const auto& argument : arguments)
    {
        commandLine.push_back(L' ');
        commandLine += quoteArgument(argument);
    }
    std::vector<wchar_t> mutableCommand(commandLine.begin(), commandLine.end());
    mutableCommand.push_back(L'\0');

    PROCESS_INFORMATION processInfo{};
    const BOOL created = CreateProcessW(
        workerExecutable.c_str(), mutableCommand.data(), nullptr, nullptr, TRUE,
        CREATE_SUSPENDED | CREATE_NO_WINDOW | EXTENDED_STARTUPINFO_PRESENT |
            CREATE_UNICODE_ENVIRONMENT,
        environment.data(), workerDirectory.c_str(),
        reinterpret_cast<LPSTARTUPINFOW>(&startup), &processInfo);
    DeleteProcThreadAttributeList(startup.lpAttributeList);
    if (!created)
        return false;

    ScopedHandle process(processInfo.hProcess);
    ScopedHandle thread(processInfo.hThread);
    ScopedHandle job;
    if (!createWorkerJob(job) || !AssignProcessToJobObject(job.value, process.value))
    {
        TerminateProcess(process.value, 70);
        WaitForSingleObject(process.value, INFINITE);
        return false;
    }

    CloseHandle(childInput.value);
    childInput.value = nullptr;
    CloseHandle(childOutput.value);
    childOutput.value = nullptr;
    if (ResumeThread(thread.value) == static_cast<DWORD>(-1))
    {
        TerminateProcess(process.value, 70);
        WaitForSingleObject(process.value, INFINITE);
        return false;
    }

    HANDLE inputHandle = parentInput.release();
    std::thread writer([inputHandle, &source]() {
        size_t offset = 0;
        while (offset < source.size())
        {
            const DWORD request = static_cast<DWORD>(std::min<size_t>(
                source.size() - offset, static_cast<size_t>(1U << 20)));
            DWORD written = 0;
            if (!WriteFile(inputHandle, source.data() + offset, request, &written, nullptr) || !written)
                break;
            offset += written;
        }
        CloseHandle(inputHandle);
    });

    char buffer[64 * 1024];
    DWORD bytesRead = 0;
    while (ReadFile(parentOutput.value, buffer, sizeof(buffer), &bytesRead, nullptr) && bytesRead)
    {
        std::cout.write(buffer, static_cast<std::streamsize>(bytesRead));
        std::cout.flush();
    }
    writer.join();

    WaitForSingleObject(process.value, INFINITE);
    if (!GetExitCodeProcess(process.value, &exitCode))
        return false;
    return true;
}
} // namespace

int runInAppContainer(int argc, char** argv)
{
    std::string source;
    if (!readSource(source))
        return 65;

    wchar_t executablePath[MAX_PATH] = {};
    const DWORD executableLength = GetModuleFileNameW(nullptr, executablePath, MAX_PATH);
    if (!executableLength || executableLength >= MAX_PATH)
    {
        std::fprintf(stderr, "Protez AppContainer launcher: cannot locate native host\n");
        return 70;
    }

    wchar_t profileSuffix[80] = {};
    swprintf_s(profileSuffix, L"Protez.AnalysisWorker.%lu.%llu", GetCurrentProcessId(),
               static_cast<unsigned long long>(GetTickCount64()));
    const std::wstring profileName(profileSuffix);
    PSID appContainerSid = nullptr;
    std::wstring workerDirectory;
    std::wstring profilePath;
    if (!makeWorkerDirectory(profileName, appContainerSid, workerDirectory, profilePath))
    {
        RemoveDirectoryW(workerDirectory.c_str());
        DeleteAppContainerProfile(profileName.c_str());
        if (appContainerSid)
            FreeSid(appContainerSid);
        std::fprintf(stderr, "Protez AppContainer launcher: cannot create an isolated worker profile (0x%08lx)\n",
                     static_cast<unsigned long>(GetLastError()));
        return 70;
    }

    wchar_t workerName[96] = {};
    swprintf_s(workerName, L"\\protez-native-host-%lu.exe", GetCurrentProcessId());
    const std::wstring workerExecutable = workerDirectory + workerName;
    if (!CopyFileW(executablePath, workerExecutable.c_str(), FALSE))
    {
        RemoveDirectoryW(workerDirectory.c_str());
        DeleteAppContainerProfile(profileName.c_str());
        FreeSid(appContainerSid);
        std::fprintf(stderr, "Protez AppContainer launcher: cannot stage the isolated worker (win32 %lu)\n",
                     static_cast<unsigned long>(GetLastError()));
        return 70;
    }

    std::vector<std::wstring> childArguments;
    for (int index = 2; index < argc; ++index)
    {
        if (std::string(argv[index]) == "--source-stdin" ||
            std::string(argv[index]) == "--appcontainer-child")
            continue;
        const std::wstring argument = widen(argv[index]);
        if (argument.empty() && argv[index][0] != '\0')
        {
            DeleteFileW(workerExecutable.c_str());
            RemoveDirectoryW(workerDirectory.c_str());
            DeleteAppContainerProfile(profileName.c_str());
            FreeSid(appContainerSid);
            std::fprintf(stderr, "Protez AppContainer launcher: invalid UTF-8 worker argument\n");
            return 64;
        }
        childArguments.push_back(argument);
    }
    childArguments.push_back(L"--source-stdin");

    DWORD childExit = 70;
    const bool completed = launchWorker(workerExecutable, workerDirectory, profilePath,
                                        childArguments, appContainerSid, source, childExit);
    DeleteFileW(workerExecutable.c_str());
    RemoveDirectoryW((workerDirectory + L"\\Temp").c_str());
    RemoveDirectoryW(workerDirectory.c_str());
    DeleteAppContainerProfile(profileName.c_str());
    FreeSid(appContainerSid);
    if (!completed)
    {
        std::fprintf(stderr, "Protez AppContainer launcher: could not start isolated Luau worker (win32 %lu)\n",
                     static_cast<unsigned long>(GetLastError()));
        return 70;
    }
    return static_cast<int>(childExit);
}

#endif
