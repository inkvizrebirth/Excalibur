--[[
    Example script used as the "clean" half of the acceptance fixture pair
    (tests/wrd_v1_0_0.lua <-> tests/wrd_v1_0_0_clean.lua).

    It deliberately touches the Roblox API surface the sandbox stubs provide
    (services, Instances, Vector3, tasks) so that the deobfuscated result is
    reproducible under core/lua/roblox_stubs.lua.
]]
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local part = Instance.new("Part")
part.Name = "ExcaliburFixture"
part.Size = Vector3.new(4, 1, 2)
part.Anchored = true
part.Parent = workspace

local function describe(target)
    return ("%s at %s"):format(target.Name, tostring(target.Size))
end

local labels = {}
for index = 1, 6 do
    labels[index] = ("slot-%d"):format(index * index)
end

local total = 0
for _, label in ipairs(labels) do
    total = total + #label
end

print(describe(part))
print(("labels: %d, characters: %d"):format(#labels, total))
print(("players: %d"):format(#Players:GetPlayers()))
print(("heartbeat: %s"):format(typeof(RunService.Heartbeat)))

local counter = 0
local function tick()
    counter = counter + 1
    return counter
end

while counter < 3 do
    tick()
end
print(("ticks: %d"):format(counter))
