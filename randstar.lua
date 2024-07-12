#!/usr/bin/env lua

local SUBSECTOR_MAX_X <const> = 8
local SUBSECTOR_MAX_Y <const> = 10

local DENSITY_MAX <const> = 6
local DENSITY_CLS <const> = 5   -- cluster density
local DENSITY_AVG <const> = 3   -- average density
local DENSITY_RFT <const> = 1   -- rift density
local DENSITY_MIN <const> = 1

local function gen_sector(max_x, max_y, density)
    local result = {}
    for x = 1, max_x do
        for y = 1, max_y do
            local r = math.random(DENSITY_MIN, DENSITY_MAX)
            if r <= density then
                local p = {x=x, y=y}
                table.insert(result, p)
            end
        end
    end
    return result
end

local density = DENSITY_AVG

if arg[1] then
    local num = tonumber(arg[1])
    if num and num >= DENSITY_MIN and num < DENSITY_MAX then
        density = num
    end
end

print("# density:", density)
print("# randomseed:", math.randomseed())

local result = gen_sector(SUBSECTOR_MAX_X, SUBSECTOR_MAX_Y, density)

for i, p in ipairs(result) do
    print(string.format("%02d%02d", p.x, p.y))
end

