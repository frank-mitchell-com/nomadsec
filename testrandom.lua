#!/usr/bin/env lua

local NSIDES <const> = 6
local NTIMES <const> = 1000000
local EXPECT <const> = NTIMES / NSIDES

local HISTOGRAM = {}

for j = 1, NSIDES do
    HISTOGRAM[j] = 0
end

for i = 1, NTIMES do
    local r = math.random(1, NSIDES)
    HISTOGRAM[r] = HISTOGRAM[r] + 1
end

for i, n in ipairs(HISTOGRAM) do
    print(i, n, ((n - EXPECT) / EXPECT)^2)
end
