--[[
    tests/wrd_flat_mini.lua

    A *flattened* payload: exactly the shape a WRD constant layer hides behind its
    state machine, but small enough to reason about by hand.  It is not an input
    fixture (the acceptance fixture is tests/wrd_v1_0_0.lua) - it is the reference
    for tests/test_lift.py, which pins what the partial lift must recover:

      * the dispatcher        while d do ... end   (3 pivots over the state 120000)
      * a constant successor  d=480000, d=900000, ...
      * the two-statement id  d=d and 900000 / d=d and 900000 or 1500000
      * a register target     d=a["FZwOKLq0r7v3"] (read from a table -> trace)
      * a loop exit           d=nil  (literal successor)
      * a helper closure      e(f) = f+1

    Lua 5.1 syntax on purpose: no goto, no bitwise operators, no integer division.
--]]
return (function(...)
    local a = {}
    local b = 0
    local c = setmetatable
    local d = 120000
    local function e(f)
        return f + 1
    end
    while d do
        if d < 900000 then
            if d < 480000 then
                b = e(b)
                d = 480000
            else
                d = d and 900000 or 1500000
            end
        else
            if d < 2100000 then
                a["FZwOKLq0r7v3"] = 2100000
                d = a["FZwOKLq0r7v3"]
            else
                d = nil
            end
        end
    end
    return b
end)(...)
