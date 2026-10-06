cmake_minimum_required(VERSION 3.24)
project(ProtezNativeHost LANGUAGES CXX)

include(FetchContent)

set(LUAU_BUILD_CLI ON CACHE BOOL "" FORCE)
set(LUAU_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(LUAU_BUILD_WEB OFF CACHE BOOL "" FORCE)
set(LUAU_BUILD_SHARED OFF CACHE BOOL "" FORCE)
set(LUAU_STATIC_CRT ON CACHE BOOL "" FORCE)
set(LUAU_EXTERN_C OFF CACHE BOOL "" FORCE)

FetchContent_Declare(
    luau
    GIT_REPOSITORY https://github.com/luau-lang/luau.git
    GIT_TAG 0.740
    GIT_SHALLOW TRUE
)
FetchContent_MakeAvailable(luau)

add_executable(protez-native-host host.cpp appcontainer_launcher.cpp)
target_compile_features(protez-native-host PRIVATE cxx_std_17)
target_link_libraries(protez-native-host PRIVATE Luau.Compiler Luau.VM Luau.VM.Internals)

if(MSVC)
    target_link_libraries(protez-native-host PRIVATE userenv advapi32 ole32)
    target_compile_definitions(protez-native-host PRIVATE _WIN32_WINNT=0x0602)
    set_property(
        TARGET protez-native-host
        PROPERTY MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>"
    )
    target_compile_options(protez-native-host PRIVATE /W4 /permissive-)
else()
    target_compile_options(protez-native-host PRIVATE -Wall -Wextra -Wpedantic)
endif()

set(_host_output_dir "${CMAKE_BINARY_DIR}/host-bin")
set_target_properties(protez-native-host PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${_host_output_dir}")
foreach(_configuration DEBUG RELEASE RELWITHDEBINFO MINSIZEREL)
    set_target_properties(protez-native-host PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY_${_configuration} "${_host_output_dir}"
    )
endforeach()

# The family-specific Luraph v15 lifter needs Luau's JSON AST reader. Build it
# from the same pinned upstream Luau source as the sandbox worker; never ship an
# unrelated precompiled parser from a third-party deobfuscator repository.
if(TARGET Luau.Ast.CLI)
    add_dependencies(protez-native-host Luau.Ast.CLI)
    set_target_properties(Luau.Ast.CLI PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${_host_output_dir}")
    foreach(_configuration DEBUG RELEASE RELWITHDEBINFO MINSIZEREL)
        set_target_properties(Luau.Ast.CLI PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY_${_configuration} "${_host_output_dir}"
        )
    endforeach()
endif()
