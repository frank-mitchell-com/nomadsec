#!/usr/bin/env lua

local MIN_SYLABLES <const> = 2

local MAX_SYLABLES <const> = 5

local INITIAL <const> = {
    '',
    'b',
    'br',
    'd',
    'dh',
    'dr',
    'f',
    'fr',
    'h',
    'k',
    'kr',
    'l',
    'm',
    'n',
    'p',
    'pr',
    'r',
    's',
    't',
    'th',
    'tr',
    'v',
    'w',
}

local FINAL <const> = {
    '',
    '',
    '',
    'l',
    'n',
    'r',
    's',
}

local VOWELS <const> = {
    'a',
    'a',
    'a',
    'a',
    'e',
    'e',
    'e',
    'e',
    'e',
    'e',
    'e',
    'e',
    'e',
    'e',
    'i',
    'i',
    'i',
    'i',
    'i',
    'o',
    'o',
    'o',
    'o',
    'u',
    'u',
    'u',
    'y',
}

local function randsyl()
    local c, v, f = math.random(#INITIAL), math.random(#VOWELS), math.random(#FINAL)
    return INITIAL[c] .. VOWELS[v] .. FINAL[f]
end

local function randname()
    local n = math.random(MIN_SYLABLES, MAX_SYLABLES)
    local a = {}
    for i = 1, n do
        table.insert(a, randsyl())
    end
    return table.concat(a)
end

local function titlecase(s)
    return (string.gsub(s, "^%l", string.upper))
end

local function randzeta(n)
    local set = {}
    local count = 0
    while count < n do
        local name = titlecase(randname())
        if not set[name] then
            set[name] = true
            count = count + 1
        end
    end

    local result = {}
    for k, v in pairs(set) do
        table.insert(result, k)
    end
    return result
end

for i, v in ipairs(randzeta(60)) do
    print(i, v, #v)
end
