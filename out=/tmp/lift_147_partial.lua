-- NOTE: this program is a partial lift. Protez's analysis deadline stopped the
-- constant-request loop after round 1; 10 constant request(s) are still
-- unresolved, and the functions that would use them are lifted as placeholders.
-- Everything else in this file was lifted from the VM.

-- Luraph v14 container, devirtualized by Protez.
--
-- The wrapper's VM state is rendered as the captured container tables
-- (`t1`, `t2`, ...): a prototype's registers, constant pools and
-- child-prototype tables are slots of those tables, exactly as the
-- capture recorded them.  One prototype is one function of the script, and `proto_1` is the entry proto (the program's main chunk).
--
-- Prototypes named `t<id>` are the ones the capture only reached
-- through a container-table reference: the number is that table's
-- id, not a prototype number.
-- lifted 59 of 60 captured prototypes.
--   skipped #2 (vm sequence 2, 0 opcodes): anti-tamper guard (scaffold score 60); PROTEZ_V14_ALL_PROTOS=1 keeps it in the output

-- The free names t1, t2, t3 are the container tables; their recorded
-- contents are the VM state the lift was made against.


-- proto 1 (the entry proto): vm sequence 1, 0 opcodes
local function proto_1()
	(t1[1])[14] = {}
	;(t1[1])[15] = (t3[1]).UDim2
	;(t1[1])[15] = (t1[1])[15].new
	;(t1[1])[14][84] = (t1[1])[15]
	;(t1[1])[14][109] = "Destroying"
	;(t1[1])[15] = (t3[1]).assert
	;(t1[1])[14][24] = (t1[1])[15]
	;(t1[1])[14][16] = "byte"
	;(t1[1])[14][129] = "NextInteger"
	;(t1[1])[14][18] = "unpack"
	;(t1[1])[14][75] = "rawset"
	;(t1[1])[15] = (t3[1]).Path2DControlPoint
	;(t1[1])[15] = (t1[1])[15].new
	;(t1[1])[14][36] = (t1[1])[15]
	;(t1[1])[15] = (t3[1]).Enum
	;(t1[1])[14][143] = (t1[1])[15]
	;(t1[1])[14][42] = "info"
	;(t1[1])[14][153] = "Enum"
	;(t1[1])[14][126] = "WaitForChild"
	;(t1[1])[14][15] = "gsub"
	;(t1[1])[14][119] = "Path2D"
	;(t1[1])[14][144] = "Right"
	;(t1[1])[14][88] = "getfenv"
	;(t1[1])[14][164] = "jjcwZK"
	;(t1[1])[14][65] = "currentline"
	;(t1[1])[14][45] = "traceback"
	;(t1[1])[14][33] = "status"
	;(t1[1])[14][60] = "source"
	;(t1[1])[14][151] = "Value"
	;(t1[1])[14][122] = "Y"
	;(t1[1])[14][34] = "defer"
	;(t1[1])[15] = (t3[1]).next
	;(t1[1])[14][8] = (t1[1])[15]
	;(t1[1])[14][128] = "NextUnitVector"
	;(t1[1])[15] = (t3[1]).rawget
	;(t1[1])[14][74] = (t1[1])[15]
	;(t1[1])[14][68] = "linedefined"
	;(t1[1])[14][152] = "number"
	;(t1[1])[14][82] = "assert"
	;(t1[1])[15] = (t3[1]).math
	;(t1[1])[14][145] = "EnumType"
	;(t1[1])[14][27] = "create"
	;(t1[1])[14][135] = "IsStudio"
	;(t1[1])[15] = (t3[1]).table
	;(t1[1])[14][76] = "rawget"
	;(t1[1])[14][104] = "userdata"
	;(t1[1])[14][134] = "IsServer"
	;(t1[1])[14][41] = "delay"
	;(t1[1])[14][26] = "running"
	;(t1[1])[14][154] = "FromName"
	;(t1[1])[14][111] = "DescendantRemoving"
	;(t1[1])[14][139] = "HttpService"
	;(t1[1])[14][120] = "Scale"
	;(t1[1])[14][31] = "cancel"
	;(t1[1])[14][137] = "StarterPlayer"
	;(t1[1])[14][57] = "[C]"
	;(t1[1])[14][116] = "Position"
	;(t1[1])[14][130] = "NextNumber"
	;(t1[1])[14][32] = "yield"
	;(t1[1])[14][163] = " --[[%s]] return setfenv(function(...) return %s(...) end, setmetatable({ [\"%s\"] = ... }, { __index = getfenv((...)) })) "
	;(t1[1])[15] = (t3[1]).bit32
	;(t1[1])[15] = (t1[1])[15].rrotate
	;(t1[1])[14][161] = (t1[1])[15]
	;(t1[1])[14][25] = "isyieldable"
	;(t1[1])[14][46] = true
	;(t1[1])[14][62] = "what"
	;(t1[1])[14][110] = "Connect"
	;(t1[1])[14][155] = "FromValue"
	;(t1[1])[15] = (t3[1]).getfenv
	;(t1[1])[14][55] = (t1[1])[15]
	;(t1[1])[15] = (t3[1]).workspace
	;(t1[1])[14][102] = (t1[1])[15]
	;(t1[1])[14][73] = "tonumber"
	;(t1[1])[14][12] = "char"
	;(t1[1])[14][165] = "Luraph"
	;(t1[1])[15] = (t3[1]).rawset
	;(t1[1])[14][71] = (t1[1])[15]
	;(t1[1])[15] = (t3[1]).identifyexecutor
	;(t1[1])[14][96] = (t1[1])[15]
	;(t1[1])[14][56] = "short_src"
	;(t1[1])[14][44] = "pack"
	;(t1[1])[15] = (t3[1]).game
	;(t1[1])[14][94] = (t1[1])[15]
	;(t1[1])[14][87] = "typeof"
	;(t1[1])[14][124] = "Workspace"
	;(t1[1])[14][114] = "The metatable is locked"
	;(t1[1])[15] = (t3[1]).Instance
	;(t1[1])[14][51] = (t1[1])[15]
	;(t1[1])[15] = (t3[1]).islclosure
	;(t1[1])[14][93] = (t1[1])[15]
	;(t1[1])[14][132] = ":(%d+)[:\r\n]"
	;(t1[1])[14][115] = "Frame"
	;(t1[1])[15] = (t3[1]).Vector3
	;(t1[1])[14][43] = (t1[1])[15]
	;(t1[1])[15] = (t3[1]).bit32
	;(t1[1])[15] = (t1[1])[15].bxor
	;(t1[1])[14][160] = (t1[1])[15]
	;(t1[1])[14][59] = "lastlinedefined"
	;(t1[1])[14][167] = "Your Lua environment does not support load or loadstring, therefore you are unable to use Luraph's 'LPH_NO_UPVALUES' macro."
	;(t1[1])[15] = (t3[1]).unpack
	;(t1[1])[14][92] = (t1[1])[15]
	;(t1[1])[14][38] = "The debug library is required on Luau platforms. Please open a support ticket."
	;(t1[1])[14][118] = "ScreenGui"
	;(t1[1])[15] = (t3[1]).loadstring
	;(t1[1])[14][40] = (t1[1])[15]
	;(t1[1])[14][141] = "PostAsync"
	;(t1[1])[15] = (t3[1]).Random
	;(t1[1])[14][21] = (t1[1])[15]
	;(t1[1])[14][101] = "뷖릙쾣쥲톳혵"
	;(t1[1])[14][81] = "pcall"
	;(t1[1])[14][52] = "wrap"
	;(t1[1])[14][6] = "match"
	;(t1[1])[15] = (t3[1]).Vector2
	;(t1[1])[14][35] = (t1[1])[15]
	;(t1[1])[14][123] = "DataModel"
	;(t1[1])[14][142] = "RequestAsync"
	;(t1[1])[14][100] = "삞섴떼콀꺼늧빏최"
	;(t1[1])[14][150] = "EnumItem"
	;(t1[1])[14][50] = "insert"
	;(t1[1])[15] = (t3[1]).task
	;(t1[1])[14][22] = (t1[1])[15]
	;(t1[1])[14][53] = "table"

	local v = table.pack((nil --[[ constant not decoded ]])[57](table.pack(table.pack(table.pack(7, 0), table.pack(8, 0), table.pack(9, 0), table.pack(10, 0), table.pack(11, 0), table.pack(3, 0), table.pack(4, 1), table.pack(5, 1), table.pack(6, 1), table.pack(12, 1)), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (2), (nil), (nil), (nil), (nil), (nil), (nil), (0), (81), (0), (4337), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (23), (nil), (37), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (table.pack(table.pack(table.pack(101, 0), table.pack(1, 1), table.pack(100, 0)), table.pack(nil, nil, 105), 5, table.pack(2, 380, 1, 2, 1, 6, 1), table.pack(127, 96, 155, 164, 139, 127, 59), {}, table.pack(0, 500, 1, 0, 0, 0, 0), {}, table.pack(0, 406, 84, 2, 2, 0, 0), 0, {})), (nil), (nil), (nil), (nil), (nil), (nil), (24975), (nil), (nil), (2661), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (74), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1147863254), (2044539472), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (52), (nil), (nil), (nil), (12), (nil), (nil), (23209), (nil), (nil), (697), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (59), (nil), (39), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (26), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (10), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (18340), (nil), (nil), (3223), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (76), (nil), (nil), (nil), (nil), (nil), (233), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (84), (94), (1674), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (table.pack(table.pack(table.pack(35, 0), table.pack(83, 0), table.pack(84, 0)), {}, 3, table.pack(2, 88, 0, 1, 1, 0, 2, 1, 1), table.pack(127, 62, 164, 164, 186, 164, 164, 186, 59), {}, table.pack(0, 491, 0, 0, 0, 0, 0, 0, 0), {}, table.pack(0, 117, 1, 2, 0, 1, 2, 0, 0), 0, {})), (nil), (nil), (nil), (nil), (nil), (166), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (table.pack(table.pack(table.pack(1, 1), table.pack(57, 0), table.pack(48, 0)), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (52), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (8), (0), (94), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (86), (7), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (64), (21005), (nil), (nil), (7), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (100), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (86), (9), (3), (185), (13) }; t.n = 115; return t end)(), 33, (function() local t = { (85), (792), (61), (0), (102), (81), (7), (0), (3), (4), (88), (211), (93), (565), (106), (0), (31), (710), (108), (25), (250), (52), (14), (0), (102), (31), (0), (0), (102), (102), (29), (25), (94), (1), (78), (265), (98), (4), (181), (153), (78), (0), (31), (0), (487), (16), (28), (25), (7), (100), (1054), (12), (0), (0), (646), (23), (535), (23), (377), (15), (6), (10), (55), (221), (11), (12), (0), (5), (78), (996), (22), (0), (31), (47), (5), (25), (128), (100), (0), (49), (49), (53), (909), (74), (3), (7), (53), (118), (5), (265), (1022), (953), (78), (94), (80), (5), (52), (13), (3), (78), (0), (1), (0), (80), (128), (37), (33), (0), (0), (31), (967), (967), (551), (551), (162), (25), (36), (13), (2), (131), (13), (120), (175), (239), (204), (3) }; t.n = 126; return t end)(), (function() local t = { (127), (86), (127), (18), (127), (127), (127), (58), (155), (155), (127), (69), (127), (86), (127), (131), (93), (101), (101), (60), (19), (127), (185), (55), (127), (93), (90), (131), (101), (101), (101), (92), (127), (164), (127), (86), (127), (160), (67), (91), (127), (90), (93), (131), (101), (101), (101), (92), (127), (127), (86), (127), (131), (90), (151), (5), (141), (17), (101), (92), (127), (160), (67), (91), (185), (185), (81), (185), (127), (86), (127), (131), (93), (101), (101), (60), (19), (127), (18), (127), (127), (8), (8), (8), (40), (127), (86), (127), (155), (8), (8), (8), (40), (127), (32), (127), (127), (127), (185), (127), (168), (59), (168), (127), (86), (127), (127), (90), (131), (93), (101), (101), (101), (101), (101), (60), (19), (127), (176), (71), (50), (64), (98), (109), (140), (127) }; t.n = 126; return t end)(), {}, (function() local t = { (0), (9), (0), (86), (0), (0), (0), (2), (0), (0), (0), (136), (0), (9), (0), (32), (0), (31), (32), (139), (146), (0), (5), (14), (0), (0), (26), (32), (26), (31), (32), (0), (0), (0), (0), (9), (0), (140), (2), (51), (0), (26), (0), (32), (31), (26), (32), (0), (0), (0), (9), (0), (22), (16), (23), (23), (23), (110), (22), (0), (0), (4), (5), (84), (3), (4), (10), (10), (0), (13), (0), (32), (0), (31), (32), (39), (195), (0), (97), (0), (0), (0), (0), (0), (10), (0), (13), (0), (0), (0), (0), (0), (6), (0), (5), (0), (0), (0), (1), (0), (0), (0), (0), (0), (9), (0), (0), (26), (32), (0), (26), (31), (32), (26), (32), (212), (251), (0), (2), (159), (7), (144), (162), (143), (90), (0) }; t.n = 126; return t end)(), (function() local t = { (nil), (194), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (152), (nil), (nil), (nil), (60), (97), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (84), (84), (94), (nil), (nil), (nil), (nil), (68), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (92), (14), (7), (nil), (nil), (nil), (236), (nil), (nil), (nil), (483), (nil), (-21397), (nil), (86), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (103), (nil), (nil), (nil), (101), (50), (nil), (nil), (nil), (nil), (nil), (nil), (21), (204), (82), (nil), (nil), (21), (nil), (nil), (68), (270), (42), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (110), (nil), (nil), (nil), (nil), (nil), (105), (105), (99), (99), (98) }; t.n = 115; return t end)(), (function() local t = { (0), (104), (0), (10), (0), (0), (0), (0), (42), (42), (0), (0), (0), (35), (0), (0), (0), (32), (33), (32), (96), (0), (0), (0), (0), (0), (0), (0), (55), (32), (29), (32), (0), (5), (0), (1), (0), (2), (193), (206), (0), (0), (0), (0), (32), (377), (28), (32), (0), (0), (78), (0), (0), (0), (684), (249), (23), (16), (28), (24), (0), (125), (53), (121), (0), (0), (0), (0), (0), (3), (0), (0), (0), (32), (20), (32), (27), (0), (6), (0), (0), (10), (11), (12), (0), (0), (69), (0), (42), (6), (7), (8), (0), (0), (0), (0), (0), (0), (0), (0), (0), (0), (0), (0), (50), (0), (0), (0), (0), (0), (377), (43), (62), (8), (612), (32), (238), (0), (150), (5), (159), (136), (35), (165), (224), (0) }; t.n = 126; return t end)(), 0, table.pack(nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 89))), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (90), (nil), (118), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (24074), (nil), (nil), (935), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (table.pack(table.pack(table.pack(56, 0), table.pack(1, 1), table.pack(48, 0)), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (5), (17), (11), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (20), (78), (nil), (nil), (nil), (nil), (127), (25), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (39), (1), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (nil), (nil), (nil), (7638), (nil), (nil), (25), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (6), (40) }; t.n = 86; return t end)(), 27, (function() local t = { (62), (0), (755), (67), (39), (883), (71), (2), (6), (0), (47), (17), (80), (244), (48), (0), (0), (25), (11), (11), (464), (19), (112), (11), (7), (81), (0), (0), (62), (120), (19), (78), (0), (0), (280), (117), (19), (7), (25), (52), (6), (7), (8), (0), (3), (47), (24), (54), (684), (4), (69), (70), (63), (67), (1), (0), (0), (105), (30), (19), (111), (1), (0), (0), (4), (790), (69), (11), (298), (78), (25), (17), (752), (17), (705), (9), (77), (25), (45), (51), (5), (40), (0), (25), (115), (330), (19), (253), (40), (1) }; t.n = 90; return t end)(), (function() local t = { (127), (131), (20), (32), (127), (8), (127), (164), (185), (55), (127), (39), (127), (86), (127), (131), (90), (93), (101), (101), (101), (60), (19), (127), (127), (127), (131), (90), (101), (101), (92), (127), (131), (90), (101), (101), (60), (19), (127), (127), (185), (185), (185), (81), (185), (32), (127), (127), (8), (185), (127), (127), (8), (127), (59), (90), (131), (101), (101), (60), (19), (127), (58), (164), (155), (8), (127), (127), (1), (127), (127), (5), (141), (17), (101), (92), (127), (127), (86), (127), (127), (127), (131), (93), (101), (101), (60), (19), (127), (127) }; t.n = 90; return t end)(), {}, (function() local t = { (0), (16), (494), (17), (0), (0), (0), (0), (3), (6), (0), (71), (0), (5), (0), (26), (20), (0), (20), (25), (26), (48), (191), (0), (0), (0), (26), (20), (20), (26), (0), (0), (26), (20), (20), (26), (58), (123), (0), (0), (3), (1), (4), (6), (6), (3), (0), (0), (0), (2), (0), (0), (0), (0), (0), (20), (26), (20), (26), (224), (35), (0), (2), (0), (1), (0), (0), (0), (256), (0), (0), (17), (17), (43), (16), (0), (0), (0), (5), (0), (0), (0), (26), (0), (25), (26), (217), (111), (0), (0) }; t.n = 90; return t end)(), (function() local t = { (nil), (nil), (283), (nil), (nil), (164), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (37), (nil), (nil), (nil), (nil), (72), (72), (68), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (3), (70), (nil), (nil), (nil), (nil), (48), (78), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (64), (nil), (nil), (nil), (4), (nil), (nil), (nil), (nil), (12), (90), (nil), (nil), (nil), (nil), (nil), (nil), (37), (nil), (nil), (nil), (nil), (nil), (nil), (-7636), (nil), (71), (nil), (nil), (nil), (64), (nil), (nil), (nil), (nil), (nil), (10), (82) }; t.n = 86; return t end)(), (function() local t = { (0), (0), (17), (0), (0), (17), (0), (3), (0), (0), (0), (0), (0), (69), (0), (0), (0), (0), (4), (99), (50), (26), (140), (0), (0), (0), (0), (0), (899), (117), (26), (0), (0), (0), (73), (187), (26), (78), (0), (0), (0), (0), (0), (0), (0), (0), (0), (0), (5), (0), (0), (0), (17), (0), (0), (0), (0), (3), (89), (26), (38), (0), (0), (3), (42), (5), (0), (0), (368), (0), (0), (735), (17), (16), (187), (18), (0), (0), (13), (0), (0), (0), (0), (0), (51), (739), (26), (162), (0), (0) }; t.n = 90; return t end)(), 0, (function() local t = { (nil), (nil), (306), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (9) }; t.n = 74; return t end)())), (nil), (nil), (table.pack(table.pack(table.pack(60, 0), table.pack(1, 1), table.pack(53, 0), table.pack(21, 0), table.pack(54, 0), table.pack(2, 0), table.pack(26, 0)), table.pack(nil, nil, 119, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 53, nil, nil, nil, nil, nil, 1), 7, table.pack(4, 35, 35, 19, 0, 21, 35, 5, 6, 5, 16, 24, 423, 5, 0, 7, 0, 3, 1, 1, 4, 4, 3, 1, 0, 4, 2, 6, 5, 0, 0, 4, 3, 6, 13, 747, 11), table.pack(127, 127, 62, 127, 58, 8, 127, 164, 164, 185, 127, 127, 83, 7, 120, 127, 173, 112, 59, 8, 164, 185, 186, 127, 164, 155, 164, 185, 7, 120, 164, 155, 164, 185, 127, 189, 127), {}, table.pack(0, 0, 2, 0, 1, 0, 0, 0, 0, 1, 0, 0, 444, 0, 3, 0, 6, 4, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 3, 0, 1, 0, 1, 0, 2, 0), table.pack(nil, nil, nil, nil, nil, 120, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 119, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 120), table.pack(0, 0, 492, 0, 0, 2, 0, 3, 4, 0, 0, 0, 329, 0, 0, 0, 0, 0, 0, 2, 3, 0, 0, 0, 3, 570, 5, 0, 0, 0, 3, 42, 5, 0, 0, 2, 0), 0, {})), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (94), (nil), (nil), (nil), (104), (2171), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (72), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (93), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (84), (0), (104), (1867), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (50), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (101), (924), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (29647), (nil), (nil), (1520), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (111), (nil), (83), (nil), (22105), (nil), (nil), (2965), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (66), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (5189), (nil), (nil), (2689), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (18), (4420), (nil), (nil), (nil), (nil), (nil), (nil), (80), (nil), (38), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (table.pack(table.pack(table.pack(52, 0), table.pack(48, 0)), (function() local t = { (nil), (nil), (nil), (366), (20044), (nil), (nil), (18), (nil), (nil), (nil), (nil), (nil), (164), (0), (28), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (54), (nil), (nil), (35), (nil), (nil), (nil), (nil), (nil), (8), (16), (38), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (127), (65) }; t.n = 84; return t end)(), 26, (function() local t = { (25), (0), (0), (988), (16), (731), (16), (3), (8), (18), (0), (24), (0), (94), (94), (739), (18), (28), (34), (7), (58), (4), (0), (77), (36), (38), (1060), (62), (119), (167), (254), (567), (12), (77), (65), (393), (0), (64), (18), (10), (4), (3), (2), (64), (86), (0), (0), (244), (117), (18), (54), (77), (19), (24), (0), (53), (0), (43), (4), (116), (18), (38), (1), (77), (1), (0), (0), (62), (73), (245), (146), (184), (57), (3), (24), (215), (40), (45), (0), (0), (0), (629), (629), (72), (18), (65), (39) }; t.n = 87; return t end)(), (function() local t = { (127), (131), (90), (151), (5), (141), (17), (101), (92), (127), (131), (93), (90), (101), (101), (101), (92), (127), (127), (160), (67), (91), (55), (127), (127), (127), (189), (127), (8), (77), (75), (161), (8), (40), (127), (159), (168), (127), (127), (127), (185), (7), (185), (32), (127), (131), (34), (101), (101), (92), (127), (62), (127), (127), (18), (127), (131), (101), (101), (101), (92), (127), (69), (127), (59), (58), (176), (71), (50), (64), (98), (109), (140), (160), (67), (91), (127), (127), (90), (131), (34), (101), (101), (101), (92), (127), (127) }; t.n = 87; return t end)(), {}, (function() local t = { (0), (15), (9), (16), (16), (16), (323), (15), (0), (0), (25), (0), (19), (19), (24), (25), (0), (0), (0), (180), (2), (104), (7), (0), (0), (0), (6), (0), (0), (37), (94), (101), (0), (3), (0), (81), (0), (0), (0), (0), (1), (0), (3), (2), (0), (25), (0), (23), (25), (0), (0), (6), (0), (0), (26), (0), (25), (25), (25), (25), (0), (0), (173), (0), (0), (1), (1), (217), (200), (105), (76), (139), (64), (23), (2), (28), (0), (0), (19), (25), (0), (23), (19), (25), (0), (0), (0) }; t.n = 87; return t end)(), (function() local t = { (nil), (nil), (nil), (422), (nil), (-20647), (nil), (39), (nil), (nil), (nil), (nil), (nil), (63), (63), (40), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (160), (nil), (35), (nil), (nil), (160), (125), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (37), (78), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (9), (5), (26), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (87), (87), (35) }; t.n = 84; return t end)(), (function() local t = { (0), (0), (0), (1044), (1000), (16), (9), (396), (17), (0), (0), (0), (0), (339), (32), (7), (25), (0), (0), (248), (230), (152), (0), (0), (0), (0), (51), (0), (3), (251), (4), (59), (5), (0), (0), (293), (162), (0), (0), (0), (0), (0), (0), (0), (0), (0), (23), (32), (593), (25), (0), (72), (0), (0), (3), (0), (0), (55), (80), (447), (25), (0), (2), (0), (0), (0), (79), (2), (108), (163), (52), (236), (101), (56), (136), (46), (0), (0), (0), (0), (23), (32), (73), (48), (25), (0), (0) }; t.n = 87; return t end)(), 0, table.pack(nil, nil, nil, nil, nil, nil, 43))), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (76), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (388), (16700), (nil), (nil), (3440), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (7), (nil), (50), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (26835), (nil), (nil), (1331), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (26), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (table.pack(table.pack(table.pack(44, 1)), table.pack(nil, nil, nil, 0, 8, nil, nil, nil, nil, nil, nil, nil, 14, 14, 35, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 21998, nil, nil, 8), 24, table.pack(34, 280, 0, 925, 244, 16, 242, 8, 17, 0, 0, 22, 7, 745, 72, 16, 35, 0, 62, 3, 4, 336, 0, 87, 0, 12, 346, 14, 212, 14, 834, 6, 89, 36, 9, 24, 2), table.pack(127, 65, 131, 101, 101, 60, 19, 127, 127, 34, 131, 93, 101, 101, 101, 92, 127, 58, 141, 195, 185, 8, 81, 65, 131, 93, 76, 5, 141, 17, 101, 60, 19, 127, 127, 127, 127), {}, table.pack(0, 502, 23, 23, 23, 238, 59, 0, 0, 0, 23, 0, 22, 21, 23, 0, 0, 1, 1, 0, 2, 0, 131, 0, 13, 0, 69, 72, 14, 54, 13, 200, 125, 0, 0, 0, 0), table.pack(nil, nil, nil, 24, 37, nil, nil, nil, nil, nil, nil, nil, 28, 27, 35, nil, nil, nil, 3, nil, nil, "f", nil, nil, nil, nil, 178, nil, -22161, nil, 36), table.pack(0, 298, 0, 32, 55, 23, 226, 0, 0, 21, 0, 0, 16, 16, 72, 23, 0, 0, 2, 0, 0, 5, 0, 3, 0, 0, 151, 446, 14, 12, 55, 15, 195, 0, 0, 0, 0), 0, table.pack(nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 12, nil, nil, 23))), (table.pack({}, {}, 4, table.pack(2, 229, 3, 0, 1), table.pack(127, 70, 127, 138, 59), {}, table.pack(0, 241, 0, 0, 0), {}, table.pack(0, 446, 0, 1, 0), 0, {})), (nil), (nil), (30), (nil), (nil), (nil), (20), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (104), (nil), (nil), (nil), (nil), (54), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (251), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (484327314), (nil), (0), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (125), (nil), (nil), (39), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (26255), (nil), (nil), (1422), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (3907), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (20), (1597), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (113), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (9), (4), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (28), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (117), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (213), (606), (nil), (nil), (1033), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (33), (nil), (nil), (4), (nil), (-271225537), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (100), (1732), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (176), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (508), (4260), (nil), (nil), (2619), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (42), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (table.pack(table.pack(table.pack(83, 0), table.pack(28, 1)), {}, 3, table.pack(5, 1, 0, 1, 1, 1, 270), table.pack(127, 195, 181, 142, 59, 127, 22), {}, table.pack(0, 1, 1, 0, 0, 0, 311), {}, table.pack(0, 0, 0, 0, 0, 0, 476), 0, {})), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (46189), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (78), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (470), (26172), (nil), (nil), (1144), (nil), (nil), (nil), (nil), (nil), (84), (0), (4608), (nil), (nil), (nil), (nil), (nil), (86), (4172), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (110), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (127), (0), (3440), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (105), (2483), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (56), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (127), (3364), (nil), (nil), (nil), (51), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1788), (nil), (nil), (3251), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (39), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (table.pack(table.pack(table.pack(7, 0), table.pack(1, 1), table.pack(65, 0), table.pack(48, 0)), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (7), (173), (0), (65), (nil), (nil), (nil), (nil), (nil), (86), (181), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (2), (47), (nil), (nil), (nil), (nil), (nil), (24885), (nil), (nil), (82), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (79), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (1), (1), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (28), (5), (28), (49), (nil), (nil), (nil), (nil), (28), (176), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (1), (1), (nil), (nil), (nil), (nil), (0), (158), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (14), (82), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (127), (75), (nil), (nil), (nil), (nil), (508), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (8), (27) }; t.n = 197; return t end)(), 38, (function() local t = { (136), (0), (132), (18), (19), (18), (13), (38), (0), (0), (0), (36), (19), (19), (19), (19), (904), (30), (25), (65), (0), (0), (938), (322), (30), (11), (181), (28), (165), (0), (151), (0), (9), (10), (62), (49), (744), (126), (0), (72), (0), (36), (280), (48), (30), (47), (176), (11), (38), (28), (306), (28), (1041), (20), (200), (74), (64), (4), (140), (130), (684), (122), (11), (168), (47), (78), (91), (1), (124), (5), (6), (31), (0), (168), (82), (0), (151), (36), (22), (5), (0), (29), (11), (12), (13), (123), (750), (76), (38), (103), (3), (112), (0), (122), (114), (127), (0), (36), (0), (5), (5), (5), (834), (30), (49), (0), (0), (244), (58), (30), (95), (176), (110), (124), (12), (59), (58), (55), (12), (195), (44), (72), (45), (183), (0), (57), (27), (12), (2), (38), (947), (35), (0), (67), (181), (455), (0), (0), (4), (5), (6), (7), (573), (151), (0), (0), (949), (765), (30), (39), (158), (65), (574), (5), (56), (228), (6), (92), (82), (0), (36), (110), (628), (30), (82), (130), (343), (114), (0), (192), (0), (0), (196), (860), (30), (75), (0), (0), (838), (126), (77), (123), (56), (9), (10), (11), (1), (158), (3), (12), (0), (1), (75), (0), (0), (318), (73), (30), (27) }; t.n = 199; return t end)(), (function() local t = { (127), (159), (127), (185), (185), (7), (185), (127), (131), (90), (34), (93), (101), (101), (101), (101), (101), (60), (19), (127), (90), (131), (101), (101), (60), (19), (127), (39), (127), (173), (127), (173), (185), (185), (127), (127), (8), (127), (18), (127), (131), (93), (101), (101), (92), (127), (127), (185), (127), (5), (141), (17), (101), (60), (19), (127), (127), (185), (77), (75), (161), (127), (185), (78), (127), (62), (127), (59), (8), (185), (185), (127), (168), (127), (127), (168), (127), (127), (8), (155), (173), (127), (155), (155), (155), (8), (8), (8), (40), (86), (127), (127), (173), (127), (86), (127), (131), (93), (90), (101), (101), (101), (101), (92), (127), (34), (131), (101), (101), (60), (19), (127), (86), (127), (155), (157), (177), (178), (144), (2), (69), (127), (189), (127), (164), (127), (127), (185), (164), (127), (8), (127), (168), (127), (127), (2), (58), (164), (185), (155), (155), (155), (8), (127), (34), (131), (101), (101), (60), (19), (127), (127), (8), (160), (67), (91), (185), (127), (127), (131), (93), (101), (101), (92), (127), (127), (86), (127), (159), (127), (90), (131), (101), (101), (92), (127), (34), (131), (162), (32), (127), (86), (127), (185), (185), (185), (78), (127), (164), (185), (55), (127), (127), (131), (90), (101), (101), (92), (127) }; t.n = 199; return t end)(), {}, (function() local t = { (0), (9), (0), (13), (12), (0), (18), (0), (37), (31), (0), (0), (37), (36), (31), (35), (37), (8), (134), (0), (31), (37), (31), (37), (53), (223), (0), (35), (0), (7), (0), (7), (5), (6), (0), (0), (0), (0), (89), (0), (37), (0), (36), (37), (0), (0), (0), (2), (0), (28), (28), (1042), (27), (91), (233), (0), (0), (2), (54), (116), (42), (0), (7), (9), (0), (8), (0), (0), (0), (3), (4), (0), (0), (0), (0), (0), (0), (0), (0), (1), (6), (0), (1), (1), (1), (0), (0), (0), (14), (17), (0), (0), (7), (0), (17), (0), (37), (0), (31), (37), (31), (36), (37), (0), (0), (0), (37), (35), (37), (97), (170), (0), (8), (0), (1), (209), (163), (13), (44), (145), (247), (0), (8), (0), (0), (0), (0), (10), (0), (0), (0), (0), (0), (0), (0), (427), (2), (0), (1), (1), (1), (1), (0), (0), (0), (37), (35), (37), (209), (61), (0), (0), (0), (95), (3), (79), (4), (0), (0), (37), (0), (36), (37), (0), (0), (0), (17), (0), (9), (0), (31), (37), (31), (37), (0), (0), (0), (27), (28), (28), (0), (17), (0), (5), (6), (7), (9), (0), (0), (11), (12), (0), (0), (37), (31), (31), (37), (0), (0) }; t.n = 199; return t end)(), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (30), (30), (30), (30), (152), (nil), (nil), (nil), (nil), (nil), (95), (135), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (158), (nil), (nil), (nil), (nil), (nil), (48), (65), (nil), (nil), (nil), (nil), (nil), (nil), (-25372), (nil), (159), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (64), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (89), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (98), (nil), (nil), (nil), (nil), (nil), (nil), (80), (214), (7), (nil), (94), (nil), (nil), (nil), (nil), (87), (nil), (nil), (nil), (nil), (50), (50), (50), (36), (nil), (nil), (nil), (nil), (37), (47), (nil), (nil), (nil), (89), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (64), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (503), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (79), (nil), (nil), (nil), (180), (188), (nil), (nil), (nil), (nil), (31), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (89), (75), (nil), (nil), (nil), (101), (nil), (nil), (nil), (nil), (nil), (77), (193), (nil), (nil), (nil), (nil), (273), (nil), (nil), (80), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (131), (127) }; t.n = 197; return t end)(), (function() local t = { (0), (188), (0), (0), (0), (0), (0), (0), (0), (0), (35), (0), (32), (28), (596), (32), (48), (37), (249), (0), (0), (0), (377), (498), (37), (154), (0), (0), (0), (0), (0), (0), (0), (0), (0), (0), (28), (0), (14), (0), (0), (0), (6), (58), (37), (0), (0), (0), (0), (955), (28), (25), (330), (29), (91), (0), (0), (0), (161), (8), (236), (0), (0), (0), (0), (433), (0), (0), (8), (0), (0), (0), (0), (0), (0), (0), (0), (0), (8), (42), (0), (0), (42), (42), (42), (14), (15), (16), (0), (134), (0), (0), (0), (0), (38), (0), (0), (0), (0), (7), (4), (7), (140), (37), (0), (35), (0), (7), (461), (37), (8), (0), (68), (0), (42), (11), (163), (54), (58), (106), (6), (0), (152), (0), (3), (0), (0), (0), (13), (0), (28), (0), (0), (0), (0), (73), (0), (3), (0), (42), (42), (42), (8), (0), (35), (0), (32), (597), (37), (29), (0), (0), (8), (40), (59), (141), (0), (0), (0), (0), (0), (16), (330), (37), (0), (0), (94), (0), (187), (0), (0), (0), (73), (628), (37), (0), (25), (0), (262), (0), (0), (166), (0), (0), (0), (0), (0), (0), (11), (0), (0), (0), (0), (0), (0), (55), (745), (37), (0) }; t.n = 199; return t end)(), 0, table.pack(nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 88))), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (8), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (146), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (-1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (191), (12018), (nil), (nil), (nil), (23996), (nil), (nil), (2011), (nil), (nil), (nil), (nil), (nil), (nil), (table.pack(table.pack(table.pack(1, 1), table.pack(15, 0)), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (1), (1), (nil), (nil), (nil), (nil), (nil), (nil), (29), (76), (30), (92), (107), (nil), (nil), (nil), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (11), (18), (89), (89), (12), (134), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (9711), (nil), (nil), (134), (nil), (nil), (nil), (nil), (nil), (10), (8), (108), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (18), (16), (51), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (1), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (1) }; t.n = 146; return t end)(), 39, (function() local t = { (143), (71), (110), (617), (96), (20), (89), (12), (553), (127), (15), (11), (12), (13), (31), (433), (86), (0), (0), (0), (710), (710), (48), (48), (65), (31), (150), (107), (9), (63), (133), (107), (0), (37), (0), (0), (33), (593), (57), (466), (79), (79), (527), (31), (225), (134), (113), (553), (15), (2), (75), (104), (11), (11), (14), (19), (47), (0), (0), (121), (29), (295), (29), (144), (21), (95), (0), (0), (0), (98), (98), (138), (31), (31), (108), (0), (130), (37), (0), (0), (280), (280), (30), (31), (14), (51), (418), (22), (15), (51), (204), (0), (124), (12), (15), (134), (0), (1), (7), (89), (663), (0), (0), (3), (150), (162), (90), (134), (377), (142), (92), (9), (102), (250), (240), (27), (222), (133), (609), (160), (3), (204), (49), (24), (2), (133), (110), (7), (777), (139), (0), (5), (0), (108), (14), (15), (16), (573), (15), (1023), (2), (75), (128), (0), (2), (3), (69), (3), (91), (121), (89), (3), (89), (75) }; t.n = 154; return t end)(), (function() local t = { (127), (86), (127), (86), (127), (86), (127), (1), (4), (8), (127), (155), (155), (155), (127), (86), (127), (34), (131), (90), (101), (101), (101), (101), (101), (60), (19), (127), (155), (8), (127), (127), (34), (93), (90), (131), (101), (101), (101), (101), (101), (101), (101), (60), (19), (127), (177), (96), (47), (182), (127), (8), (89), (89), (89), (47), (127), (131), (90), (76), (5), (141), (17), (101), (92), (127), (131), (90), (34), (101), (101), (101), (60), (19), (127), (18), (127), (93), (34), (131), (101), (101), (101), (60), (19), (127), (8), (8), (127), (127), (77), (75), (161), (182), (127), (127), (88), (164), (185), (8), (8), (22), (171), (185), (127), (86), (127), (127), (86), (127), (8), (82), (68), (45), (16), (184), (69), (127), (8), (8), (127), (77), (75), (161), (52), (127), (86), (127), (189), (127), (168), (130), (65), (127), (155), (155), (155), (8), (127), (96), (182), (127), (127), (58), (155), (155), (8), (127), (86), (127), (8), (42), (8), (40) }; t.n = 154; return t end)(), {}, (function() local t = { (0), (10), (0), (4), (0), (17), (0), (18), (13), (0), (0), (0), (0), (0), (0), (17), (0), (0), (38), (32), (36), (32), (36), (32), (38), (243), (76), (0), (0), (0), (0), (0), (0), (0), (32), (38), (37), (38), (36), (32), (32), (37), (38), (36), (67), (0), (92), (18), (18), (141), (0), (0), (12), (13), (12), (16), (0), (28), (22), (669), (29), (29), (51), (28), (0), (0), (38), (32), (0), (36), (32), (38), (187), (249), (0), (28), (0), (0), (0), (38), (37), (36), (38), (40), (16), (0), (0), (0), (0), (0), (59), (122), (251), (553), (0), (0), (5), (0), (1), (0), (0), (4), (5), (5), (0), (17), (0), (0), (10), (0), (0), (197), (227), (76), (8), (90), (102), (0), (0), (0), (0), (210), (131), (247), (2), (0), (17), (0), (2), (0), (0), (683), (0), (0), (0), (0), (0), (0), (0), (11), (141), (0), (0), (1), (0), (0), (0), (0), (10), (0), (0), (0), (0), (5) }; t.n = 154; return t end)(), (function() local t = { (nil), (4), (nil), (123), (nil), (100), (nil), (nil), (65536), (100), (nil), (nil), (nil), (nil), (nil), (79), (nil), (nil), (nil), (nil), (60), (60), (65), (65), (32), (nil), (nil), (nil), (nil), (4), (nil), (nil), (nil), (nil), (nil), (nil), (52), (54), (56), (55), (53), (53), (96), (nil), (nil), (nil), (nil), (65536), (nil), (nil), (nil), (256), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (81), (nil), (-9221), (nil), (108), (nil), (nil), (nil), (nil), (nil), (111), (111), (134), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (48), (48), (90), (nil), (nil), (nil), (403), (98), (nil), (nil), (nil), (nil), (89), (nil), (nil), (nil), (nil), (nil), (nil), (1), (-1), (nil), (nil), (nil), (nil), (98), (nil), (nil), (86), (nil), (19), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (123), (2166136261), (nil), (nil), (nil), (86), (nil), (nil), (89), (nil), (134217728), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (79), (nil), (16777619), (nil), (nil), (nil), (nil), (nil), (nil), (12), (nil), (19), (nil), (1), (nil), (1) }; t.n = 153; return t end)(), (function() local t = { (0), (133), (0), (118), (0), (105), (0), (2), (18), (17), (0), (42), (42), (42), (0), (126), (0), (36), (0), (0), (1057), (90), (19), (487), (1034), (38), (57), (0), (42), (10), (0), (0), (36), (0), (0), (0), (32), (50), (396), (110), (110), (105), (138), (38), (42), (0), (433), (16), (18), (18), (0), (14), (15), (18), (19), (18), (0), (0), (0), (29), (826), (29), (22), (138), (30), (0), (0), (0), (36), (115), (55), (144), (38), (196), (0), (5), (0), (0), (36), (0), (396), (80), (399), (38), (163), (0), (11), (17), (0), (0), (173), (17), (96), (2), (0), (0), (0), (6), (0), (8), (9), (6), (0), (0), (0), (15), (0), (0), (148), (0), (10), (190), (3), (240), (181), (79), (27), (0), (4), (2), (0), (42), (10), (201), (9), (0), (5), (0), (11), (0), (0), (2), (5), (0), (42), (42), (42), (17), (0), (2), (11), (0), (0), (0), (42), (42), (4), (0), (1), (0), (5), (6), (7), (0) }; t.n = 154; return t end)(), 0, (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (4294967296), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (485), (nil), (nil), (6), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (65536), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (649800647), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (4294967296) }; t.n = 141; return t end)())), (nil), (nil), (nil), (nil), (nil), (nil), (1120889156), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (8), (nil), (nil), (7), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (19), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (185), (500), (nil), (nil), (nil), (table.pack(table.pack(table.pack(1, 1), table.pack(56, 0)), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (29), (nil), (nil), (nil), (nil), (nil), (nil), (6), (0), (3), (70), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (1), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (10), (73), (nil), (nil), (nil), (nil), (nil), (nil), (2), (185), (0), (0), (26), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (243), (9373), (nil), (nil), (26) }; t.n = 83; return t end)(), 28, (function() local t = { (45), (1), (7), (8), (9), (62), (205), (75), (0), (0), (442), (90), (20), (59), (29), (197), (0), (0), (11), (705), (705), (628), (20), (144), (70), (74), (422), (25), (26), (0), (5), (41), (0), (3), (4), (5), (53), (40), (1038), (46), (26), (0), (7), (0), (1), (73), (4), (164), (101), (122), (40), (85), (44), (0), (102), (1021), (20), (73), (0), (0), (26), (0), (58), (58), (58), (71), (1057), (20), (78), (26), (3), (188), (40), (32), (70), (29), (16), (0), (696), (18), (505), (18), (852), (10), (28) }; t.n = 85; return t end)(), (function() local t = { (127), (164), (185), (185), (160), (67), (91), (127), (34), (131), (101), (101), (60), (19), (127), (99), (131), (34), (101), (101), (101), (101), (60), (19), (127), (127), (86), (127), (127), (81), (185), (127), (58), (155), (155), (155), (8), (127), (86), (127), (127), (137), (185), (65), (127), (127), (185), (77), (75), (161), (127), (86), (127), (131), (101), (101), (92), (127), (90), (34), (93), (131), (101), (101), (101), (101), (101), (60), (19), (127), (185), (8), (127), (127), (127), (127), (93), (131), (151), (5), (141), (17), (101), (92), (127) }; t.n = 85; return t end)(), {}, (function() local t = { (0), (0), (5), (3), (130), (4), (84), (0), (0), (27), (25), (27), (103), (227), (0), (454), (27), (0), (25), (25), (27), (27), (179), (111), (0), (0), (6), (0), (0), (7), (7), (0), (2), (0), (0), (0), (0), (0), (6), (0), (0), (5), (5), (0), (0), (0), (2), (45), (42), (125), (0), (6), (0), (27), (27), (27), (0), (0), (21), (0), (0), (27), (26), (21), (25), (25), (27), (154), (182), (0), (1), (0), (0), (0), (0), (0), (0), (17), (18), (18), (18), (745), (17), (0), (0) }; t.n = 85; return t end)(), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (31), (76), (nil), (nil), (nil), (nil), (nil), (nil), (72), (71), (71), (75), (nil), (nil), (nil), (nil), (21), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (21), (nil), (112), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (15), (nil), (15), (nil), (nil), (84), (46), (nil), (nil), (nil), (nil), (nil), (nil), (47), (47), (47), (4), (29), (nil), (nil), (nil), (nil), (112), (nil), (nil), (nil), (nil), (nil), (nil), (318), (nil), (-9928), (nil), (41) }; t.n = 83; return t end)(), (function() local t = { (0), (5), (0), (0), (51), (168), (242), (0), (25), (0), (32), (1057), (27), (120), (0), (336), (0), (25), (51), (32), (62), (120), (27), (140), (0), (0), (51), (0), (0), (0), (0), (0), (0), (42), (42), (42), (6), (0), (40), (0), (0), (5), (0), (7), (0), (0), (0), (146), (6), (174), (0), (38), (0), (0), (115), (850), (27), (0), (0), (25), (0), (0), (6), (8), (32), (32), (116), (27), (186), (0), (0), (6), (0), (0), (0), (0), (0), (0), (252), (737), (18), (16), (116), (19), (0) }; t.n = 85; return t end)(), 0, (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (27) }; t.n = 82; return t end)())), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (117), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (27314), (nil), (nil), (4187), (nil), (nil), (nil), (nil), (nil), (nil), (table.pack(table.pack(table.pack(1, 1), table.pack(86, 0), table.pack(99, 0), table.pack(48, 0)), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (5), (3), (5), (0), (54), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (nil), (nil), (0), (17), (59), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (105), (22542), (nil), (nil), (34), (nil), (nil), (nil), (nil), (2), (0), (51), (nil), (nil), (nil), (nil), (nil), (1) }; t.n = 79; return t end)(), 27, (function() local t = { (77), (41), (51), (3), (0), (42), (44), (50), (0), (25), (0), (71), (71), (4), (4), (399), (19), (33), (54), (5), (6), (3), (119), (2), (0), (25), (331), (101), (36), (19), (103), (59), (7), (0), (2), (8), (7), (126), (76), (19), (6), (53), (1), (475), (70), (170), (32), (184), (3), (40), (54), (72), (1), (34), (3), (39), (447), (32), (59), (0), (0), (515), (17), (485), (17), (593), (9), (34), (0), (25), (66), (674), (62), (19), (22), (51), (2), (0), (3), (96), (6) }; t.n = 81; return t end)(), (function() local t = { (127), (127), (127), (164), (55), (127), (107), (127), (131), (93), (34), (101), (101), (101), (101), (101), (60), (19), (127), (163), (155), (139), (8), (127), (131), (93), (101), (101), (101), (60), (19), (127), (26), (65), (164), (185), (186), (8), (127), (127), (127), (127), (59), (28), (8), (188), (147), (91), (26), (127), (127), (86), (127), (127), (32), (127), (86), (127), (127), (90), (131), (151), (5), (141), (17), (101), (92), (127), (131), (93), (101), (101), (101), (60), (19), (127), (127), (58), (155), (8), (127) }; t.n = 81; return t end)(), {}, (function() local t = { (0), (0), (0), (0), (5), (0), (187), (0), (26), (0), (0), (24), (26), (25), (24), (26), (208), (55), (0), (3), (0), (1), (0), (0), (26), (0), (25), (25), (26), (114), (12), (0), (2), (0), (0), (5), (0), (0), (0), (0), (0), (0), (0), (406), (0), (201), (1), (170), (2), (0), (0), (6), (0), (0), (3), (0), (6), (0), (0), (10), (16), (17), (17), (17), (3), (16), (0), (0), (26), (0), (25), (26), (26), (110), (41), (0), (0), (2), (0), (0), (0) }; t.n = 81; return t end)(), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (4), (4), (5), (5), (51), (nil), (nil), (nil), (nil), (nil), (nil), (35), (nil), (nil), (nil), (67), (62), (59), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (38), (nil), (nil), (nil), (nil), (nil), (nil), (36), (nil), (0), (nil), (nil), (nil), (nil), (35), (nil), (nil), (nil), (nil), (38), (nil), (nil), (nil), (nil), (207), (nil), (-22727), (nil), (54), (nil), (nil), (nil), (nil), (33), (34), (3), (nil), (nil), (nil), (nil), (nil), (nil), (25) }; t.n = 80; return t end)(), (function() local t = { (0), (0), (0), (5), (0), (0), (4), (0), (0), (0), (24), (4), (62), (4), (32), (593), (26), (167), (0), (1), (42), (6), (6), (0), (0), (0), (32), (99), (36), (26), (171), (0), (1), (7), (7), (0), (0), (6), (0), (0), (0), (0), (0), (453), (4), (5), (70), (213), (5), (0), (0), (56), (0), (0), (0), (0), (2), (0), (0), (0), (0), (84), (932), (17), (10), (674), (18), (0), (0), (0), (6), (32), (399), (26), (37), (0), (0), (0), (42), (4), (0) }; t.n = 81; return t end)(), 0, (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (25), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (39) }; t.n = 65; return t end)())), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (74), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (130), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (table.pack(table.pack(table.pack(35, 0)), {}, 2, table.pack(5, 96, 0, 0, 1, 2), table.pack(127, 147, 164, 55, 59, 127), {}, table.pack(0, 138, 0, 1, 0, 0), {}, table.pack(0, 308, 1, 0, 0, 0), 0, {})), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (59), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (204), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (table.pack({}, {}, 4, table.pack(2, 321, 3, 0, 1), table.pack(127, 112, 127, 58, 59), {}, table.pack(0, 51, 0, 2, 0), {}, table.pack(0, 396, 0, 0, 0), 0, {})), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (1251), (nil), (nil), (nil), (nil), (nil), (13484), (nil), (nil), (1531), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (4329), (nil), (nil), (nil), (25041), (nil), (nil), (3059), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (559706113), (1813149362), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (38), (nil), (nil), (nil), (nil), (nil), (nil), (table.pack(table.pack(table.pack(1, 1), table.pack(50, 0)), (function() local t = { (nil), (nil), (nil), (0), (3), (69), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (5), (7), (58), (nil), (nil), (nil), (nil), (nil), (nil), (109), (nil), (nil), (nil), (nil), (0), (127), (39), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (67), (nil), (nil), (nil), (nil), (nil), (nil), (32), (89), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (nil), (nil), (28310), (nil), (nil), (66), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (70), (nil), (nil), (nil), (nil), (nil), (nil), (8), (20), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (117) }; t.n = 92; return t end)(), 25, (function() local t = { (38), (0), (23), (850), (850), (13), (17), (151), (69), (82), (55), (0), (0), (36), (94), (11), (17), (98), (58), (80), (873), (71), (36), (33), (23), (0), (0), (289), (289), (48), (17), (19), (39), (607), (2), (75), (120), (94), (51), (75), (87), (272), (65), (77), (0), (0), (445), (900), (17), (153), (89), (0), (2), (0), (56), (66), (395), (75), (15), (1051), (15), (57), (7), (66), (39), (69), (0), (111), (75), (3), (72), (58), (0), (5), (0), (22), (41), (743), (97), (89), (0), (0), (422), (899), (17), (3), (20), (9), (73), (0), (0), (147), (97), (43), (1), (266), (75), (15), (19) }; t.n = 99; return t end)(), (function() local t = { (127), (131), (93), (101), (101), (101), (60), (19), (127), (189), (127), (131), (90), (101), (101), (101), (60), (19), (127), (127), (203), (127), (62), (127), (93), (90), (131), (101), (101), (101), (60), (19), (127), (8), (185), (127), (189), (127), (127), (62), (127), (189), (127), (127), (90), (131), (101), (101), (60), (19), (127), (58), (155), (173), (127), (127), (8), (127), (5), (141), (17), (101), (92), (127), (127), (127), (137), (8), (127), (26), (127), (127), (137), (185), (65), (62), (127), (8), (127), (127), (90), (131), (101), (101), (60), (19), (127), (127), (97), (34), (131), (85), (32), (127), (164), (8), (127), (39), (127) }; t.n = 99; return t end)(), {}, (function() local t = { (0), (24), (0), (24), (23), (24), (46), (161), (0), (4), (0), (24), (18), (18), (24), (24), (98), (106), (0), (0), (0), (0), (4), (0), (0), (18), (24), (23), (18), (24), (224), (145), (0), (0), (1), (0), (4), (0), (0), (4), (0), (4), (0), (0), (18), (24), (18), (24), (143), (150), (0), (1), (0), (3), (0), (0), (0), (0), (15), (15), (464), (14), (0), (0), (0), (0), (2), (0), (0), (2), (0), (0), (3), (3), (0), (4), (0), (0), (0), (0), (18), (24), (18), (24), (152), (190), (0), (0), (237), (0), (14), (15), (15), (0), (0), (0), (0), (71), (0) }; t.n = 99; return t end)(), (function() local t = { (nil), (nil), (nil), (73), (73), (66), (nil), (nil), (nil), (109), (nil), (nil), (nil), (59), (63), (72), (nil), (nil), (nil), (nil), (99), (nil), (nil), (nil), (nil), (nil), (nil), (69), (69), (65), (nil), (nil), (nil), (67), (nil), (nil), (70), (nil), (nil), (nil), (nil), (116), (nil), (nil), (nil), (nil), (93), (80), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (116), (nil), (nil), (-28495), (nil), (56), (nil), (nil), (nil), (nil), (nil), (109), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (189), (nil), (nil), (nil), (nil), (21), (20), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (294), (nil), (nil), (nil), (70) }; t.n = 96; return t end)(), (function() local t = { (0), (0), (0), (32), (62), (289), (24), (50), (0), (75), (0), (0), (0), (4), (28), (23), (24), (45), (0), (0), (15), (0), (82), (0), (0), (0), (0), (32), (73), (3), (24), (230), (0), (4), (0), (0), (64), (0), (0), (331), (0), (22), (0), (0), (0), (0), (65), (110), (24), (139), (0), (0), (42), (0), (0), (0), (4), (0), (945), (15), (12), (13), (16), (0), (0), (0), (2), (4), (0), (3), (0), (0), (3), (0), (5), (120), (0), (15), (0), (0), (0), (0), (55), (899), (24), (201), (0), (0), (450), (12), (0), (983), (0), (0), (3), (4), (0), (0), (0) }; t.n = 99; return t end)(), 0, table.pack(nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 68))), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (9), (8), (nil), (5), (nil), (nil), (nil), (nil), (-3022274255), (nil), (nil), (55), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (table.pack(table.pack(table.pack(51, 0), table.pack(48, 0)), table.pack(nil, nil, nil, nil, nil, nil, nil, nil, nil, 0, 60, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 20086, nil, nil, 15, nil, nil, nil, nil, 0, 63, nil, nil, nil, nil, nil, nil, nil, nil, 0, 1, 58, 0, 14), 23, (function() local t = { (68), (1), (67), (72), (69), (445), (71), (0), (21), (6), (850), (15), (245), (60), (48), (4), (3), (2), (70), (4), (0), (0), (814), (13), (186), (13), (94), (5), (15), (0), (0), (13), (11), (15), (196), (63), (65), (0), (21), (0), (0), (140), (140), (140), (140), (289), (15), (14), (0), (0), (39), (8), (212), (107), (172), (8), (3), (172), (189), (62), (1), (36), (15), (31), (72), (4), (0), (70), (14), (6), (1), (29), (7) }; t.n = 73; return t end)(), (function() local t = { (127), (164), (8), (127), (127), (120), (127), (131), (93), (101), (101), (60), (19), (127), (127), (185), (7), (185), (32), (127), (131), (90), (76), (5), (141), (17), (101), (92), (127), (34), (131), (101), (101), (60), (19), (127), (127), (34), (93), (131), (90), (101), (101), (101), (101), (101), (92), (127), (58), (176), (71), (50), (64), (98), (109), (140), (160), (67), (91), (127), (107), (127), (127), (8), (127), (185), (55), (127), (127), (127), (59), (127), (127) }; t.n = 73; return t end)(), {}, (function() local t = { (0), (83), (0), (0), (0), (169), (0), (22), (0), (21), (22), (252), (184), (0), (0), (1), (0), (3), (2), (0), (12), (6), (156), (13), (13), (120), (12), (0), (0), (0), (22), (20), (22), (139), (61), (0), (0), (0), (0), (22), (16), (20), (21), (16), (22), (22), (0), (0), (1), (187), (87), (62), (76), (45), (18), (216), (74), (2), (100), (0), (54), (0), (0), (0), (0), (2), (4), (0), (0), (0), (0), (0), (0) }; t.n = 73; return t end)(), table.pack(nil, nil, 10, nil, nil, nil, nil, nil, nil, 2, 73, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 263, nil, -20107, nil, 63, nil, nil, nil, nil, 66, 72, nil, nil, nil, nil, nil, nil, nil, nil, 49, 49, 49, 49, 69, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 23), (function() local t = { (0), (2), (3), (0), (0), (63), (0), (0), (0), (32), (710), (22), (73), (0), (0), (0), (0), (0), (0), (0), (0), (0), (13), (426), (13), (6), (85), (14), (0), (20), (0), (32), (94), (22), (151), (0), (0), (20), (0), (0), (0), (32), (89), (23), (32), (16), (22), (0), (0), (48), (2), (161), (210), (65), (92), (177), (138), (210), (251), (0), (3), (0), (0), (3), (0), (230), (0), (0), (0), (0), (0), (0), (0) }; t.n = 73; return t end)(), 0, table.pack(nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 115, nil, nil, 70, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 23))), (table.pack(table.pack(table.pack(1, 1), table.pack(52, 0), table.pack(8, 0)), (function() local t = { (nil), (nil), (nil), (0), (65), (nil), (nil), (nil), (203), (nil), (nil), (nil), (nil), (nil), (168), (137), (nil), (nil), (nil), (nil), (nil), (33), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (4), (119), (nil), (nil), (nil), (nil), (nil), (10811), (nil), (nil), (21), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (46), (nil), (nil), (nil), (nil), (nil), (0), (179), (nil), (nil), (nil), (nil), (0), (134), (nil), (nil), (nil), (nil), (nil), (nil), (185), (2), (246), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (46), (nil), (nil), (nil), (nil), (47), (nil), (nil), (nil), (1), (nil), (3), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (16), (nil), (nil), (nil), (nil), (nil), (46), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (62), (7), (209), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (88), (nil), (nil), (nil), (185), (12), (256), (nil), (nil), (nil), (1), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (155), (11), (23), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (9), (250), (nil), (nil), (nil), (nil), (nil), (nil), (47), (nil), (nil), (nil), (nil), (nil), (8), (0), (243), (nil), (nil), (nil), (303), (nil), (nil), (nil), (103), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1) }; t.n = 248; return t end)(), 35, (function() local t = { (11), (33), (0), (192), (57), (27), (21), (65), (235), (165), (62), (255), (0), (0), (746), (1060), (27), (137), (1), (4), (117), (144), (100), (110), (95), (160), (40), (220), (570), (2), (103), (0), (3), (110), (216), (108), (0), (4), (3), (156), (33), (0), (796), (1009), (27), (119), (0), (0), (494), (25), (800), (25), (631), (17), (21), (65), (1063), (114), (607), (106), (8), (0), (3), (12), (0), (58), (164), (0), (949), (104), (27), (179), (0), (0), (483), (195), (27), (134), (256), (33), (0), (0), (1043), (1043), (108), (27), (246), (27), (116), (37), (4), (26), (4), (10), (103), (204), (246), (92), (146), (117), (245), (418), (8), (132), (55), (78), (4), (186), (6), (221), (221), (118), (5), (103), (221), (158), (23), (0), (159), (75), (12), (13), (12), (3), (172), (31), (26), (250), (11), (31), (78), (127), (111), (28), (5), (2), (36), (0), (5), (6), (14), (167), (127), (221), (105), (96), (3), (60), (33), (0), (0), (60), (60), (380), (27), (209), (209), (267), (243), (137), (245), (26), (395), (128), (258), (4), (128), (71), (221), (36), (11), (188), (0), (0), (685), (685), (433), (27), (256), (0), (3), (4), (88), (764), (811), (99), (0), (31), (212), (117), (114), (1), (26), (33), (0), (0), (381), (381), (381), (375), (27), (34), (23), (134), (11), (607), (734), (751), (186), (6), (215), (123), (41), (103), (0), (879), (296), (27), (177), (250), (21), (0), (169), (3), (12), (0), (0), (0), (33), (250), (250), (1041), (27), (194), (243), (239), (203), (2), (221), (56), (34), (88), (18), (237), (25), (119), (4), (12), (3), (105), (9), (10), (9), (3), (159), (179), (223), (10), (240), (5), (103) }; t.n = 261; return t end)(), (function() local t = { (127), (93), (131), (101), (101), (60), (19), (127), (62), (127), (127), (127), (90), (131), (101), (101), (92), (127), (164), (185), (127), (62), (127), (32), (127), (127), (169), (127), (8), (164), (127), (168), (165), (127), (189), (127), (168), (185), (26), (127), (93), (131), (101), (101), (92), (127), (131), (90), (76), (5), (141), (17), (101), (92), (127), (127), (189), (127), (86), (127), (185), (65), (155), (185), (65), (169), (127), (131), (101), (101), (92), (127), (131), (34), (101), (101), (92), (127), (127), (93), (131), (90), (101), (101), (101), (92), (127), (189), (127), (8), (185), (127), (185), (8), (127), (127), (127), (107), (127), (40), (127), (189), (127), (62), (127), (127), (185), (127), (155), (127), (127), (8), (155), (127), (62), (127), (127), (18), (127), (8), (185), (185), (7), (160), (67), (91), (127), (127), (155), (127), (86), (127), (62), (127), (158), (164), (127), (168), (155), (155), (8), (8), (8), (40), (32), (127), (185), (127), (93), (131), (90), (101), (101), (101), (92), (127), (127), (146), (127), (127), (8), (127), (86), (127), (127), (160), (67), (91), (127), (127), (122), (127), (131), (90), (101), (101), (101), (92), (127), (58), (155), (155), (8), (8), (8), (127), (18), (127), (77), (75), (161), (164), (127), (93), (131), (90), (101), (101), (101), (101), (60), (19), (127), (127), (155), (8), (8), (8), (40), (185), (77), (75), (161), (127), (131), (101), (101), (60), (19), (127), (127), (18), (127), (155), (185), (65), (131), (90), (93), (101), (101), (101), (60), (19), (127), (62), (127), (164), (127), (62), (127), (86), (127), (32), (127), (127), (185), (155), (165), (127), (185), (185), (7), (185), (127), (127), (32), (127), (8), (158), (127) }; t.n = 261; return t end)(), {}, (function() local t = { (0), (0), (34), (33), (34), (125), (149), (0), (10), (0), (0), (0), (28), (34), (28), (34), (0), (0), (0), (1), (0), (11), (0), (3), (0), (0), (11), (0), (0), (0), (0), (0), (4), (0), (10), (0), (0), (2), (4), (0), (0), (34), (33), (34), (0), (0), (24), (18), (15), (25), (25), (805), (24), (0), (0), (0), (10), (0), (15), (0), (3), (0), (0), (3), (0), (7), (0), (34), (34), (34), (0), (0), (34), (0), (32), (34), (0), (0), (0), (0), (34), (28), (28), (33), (34), (0), (0), (10), (0), (0), (2), (0), (1), (0), (0), (0), (0), (79), (0), (5), (0), (10), (0), (7), (0), (0), (1), (0), (0), (0), (0), (0), (0), (0), (10), (0), (0), (130), (0), (0), (3), (4), (0), (56), (12), (29), (0), (0), (0), (0), (8), (0), (7), (0), (4), (0), (0), (0), (0), (0), (0), (0), (0), (7), (3), (0), (6), (0), (0), (34), (28), (28), (33), (34), (0), (0), (0), (133), (0), (0), (0), (0), (15), (0), (0), (216), (1), (129), (0), (0), (89), (0), (34), (28), (28), (34), (34), (0), (0), (2), (0), (0), (0), (0), (0), (0), (58), (0), (216), (168), (220), (0), (0), (0), (34), (28), (33), (28), (34), (34), (215), (103), (0), (0), (0), (0), (0), (0), (12), (3), (11), (73), (231), (0), (34), (34), (34), (211), (199), (0), (0), (87), (0), (0), (3), (0), (34), (28), (0), (28), (33), (34), (89), (117), (0), (10), (0), (0), (0), (10), (0), (8), (0), (3), (0), (0), (2), (0), (4), (0), (3), (4), (0), (9), (0), (0), (3), (0), (0), (4), (0) }; t.n = 261; return t end)(), (function() local t = { (nil), (nil), (nil), (259), (56), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (138), (160), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (74), (nil), (53), (nil), (nil), (nil), (nil), (nil), (303), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (122), (246), (nil), (nil), (nil), (nil), (306), (nil), (-10903), (nil), (221), (nil), (nil), (nil), (203), (nil), (67), (nil), (nil), (nil), (nil), (nil), (nil), (47), (nil), (nil), (180), (256), (nil), (nil), (nil), (nil), (137), (204), (nil), (nil), (nil), (nil), (nil), (nil), (247), (247), (97), (nil), (nil), (103), (nil), (74), (nil), (nil), (nil), (16), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (403), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (47), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (33), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (126), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (3), (461), (100), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (133), (133), (157), (nil), (nil), (nil), (nil), (nil), (nil), (88), (nil), (116), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (225), (225), (79), (nil), (nil), (nil), (nil), (nil), (34), (251), (92), (nil), (nil), (nil), (nil), (nil), (87), (nil), (nil), (nil), (nil), (nil), (205), (205), (205), (117), (nil), (nil), (nil), (nil), (nil), (67), (195), (49), (nil), (nil), (nil), (nil), (46), (nil), (nil), (251), (128), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (161), (161), (159), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (34), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (66) }; t.n = 259; return t end)(), (function() local t = { (0), (0), (0), (32), (48), (34), (178), (0), (1063), (0), (0), (0), (0), (0), (940), (483), (34), (0), (3), (0), (0), (66), (0), (0), (0), (0), (170), (0), (7), (3), (0), (0), (11), (0), (56), (0), (0), (0), (3), (0), (0), (0), (71), (492), (34), (0), (0), (0), (25), (972), (25), (18), (422), (26), (0), (0), (221), (0), (162), (0), (0), (8), (41), (0), (12), (97), (0), (0), (32), (540), (34), (0), (0), (32), (32), (138), (34), (0), (0), (0), (0), (0), (8), (6), (1009), (34), (0), (101), (0), (11), (0), (0), (0), (7), (0), (0), (0), (7), (0), (0), (0), (235), (0), (1021), (0), (0), (0), (0), (118), (0), (0), (7), (42), (0), (62), (0), (0), (5), (0), (11), (0), (0), (0), (231), (85), (193), (0), (0), (42), (0), (241), (0), (80), (0), (3), (3), (0), (0), (41), (42), (7), (8), (9), (0), (0), (0), (0), (0), (0), (0), (0), (101), (28), (1040), (34), (0), (0), (302), (0), (0), (11), (0), (186), (0), (0), (172), (159), (126), (0), (0), (1042), (0), (0), (0), (8), (105), (104), (34), (0), (0), (42), (42), (5), (6), (7), (0), (12), (0), (4), (11), (81), (3), (0), (0), (0), (0), (32), (603), (50), (54), (34), (230), (0), (0), (42), (12), (13), (14), (0), (0), (26), (7), (21), (0), (0), (43), (207), (34), (47), (0), (0), (7), (0), (118), (0), (12), (0), (0), (0), (55), (32), (686), (34), (33), (0), (216), (0), (3), (0), (27), (0), (117), (0), (0), (0), (0), (0), (42), (12), (0), (0), (0), (0), (0), (0), (0), (0), (0), (7), (3), (0) }; t.n = 261; return t end)(), 0, (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (59), (nil), (nil), (224), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (53) }; t.n = 98; return t end)())), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (8), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (4311), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (138), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1685119350), (1148305764), (1430007465), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (32), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (26), (2515), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (7), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (table.pack(table.pack(table.pack(1, 1), table.pack(2, 2), table.pack(98, 0), table.pack(54, 0)), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (80), (nil), (nil), (nil), (48), (nil), (nil), (nil), (nil), (46), (nil), (nil), (nil), (0), (14), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (38), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (183), (nil), (nil), (nil), (nil), (nil), (nil), (1), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (62), (62), (272), (nil), (nil), (nil), (nil), (76), (227), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (34), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (34), (nil), (nil), (nil), (9), (nil), (nil), (nil), (36), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (185), (152), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (78), (nil), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (9), (169), (249), (nil), (nil), (nil), (nil), (nil), (32), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (110), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (8), (74), (nil), (nil), (nil), (nil), (nil), (27592), (nil), (nil), (25), (nil), (nil), (nil), (46), (nil), (5), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (35), (nil), (nil), (nil), (89), (108), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (8), (155), (0), (155), (111), (nil), (nil), (nil), (79), (nil), (nil), (nil), (nil), (nil), (0), (121), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (62), (115), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (82), (nil), (nil), (nil), (185), (30), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (158), (56), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (6), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (8), (113), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (nil), (nil), (nil), (1) }; t.n = 366; return t end)(), 33, (function() local t = { (213), (6), (126), (53), (799), (157), (0), (124), (146), (311), (240), (282), (274), (259), (201), (49), (35), (8), (53), (0), (0), (102), (540), (25), (14), (330), (123), (4), (282), (227), (597), (210), (648), (241), (8), (2), (6), (220), (65), (239), (121), (183), (154), (0), (292), (13), (14), (13), (219), (82), (399), (40), (27), (72), (117), (6), (166), (165), (898), (176), (89), (770), (145), (2), (43), (0), (31), (974), (431), (25), (183), (108), (6), (43), (2), (4), (5), (213), (122), (128), (797), (10), (1), (320), (0), (0), (453), (891), (144), (25), (272), (0), (0), (291), (19), (25), (0), (227), (119), (2), (53), (489), (7), (297), (50), (0), (364), (272), (875), (6), (145), (0), (42), (196), (104), (461), (52), (198), (351), (1), (249), (142), (148), (32), (125), (0), (6), (444), (769), (18), (350), (102), (16), (0), (0), (6), (986), (25), (152), (3), (70), (145), (3), (38), (145), (113), (63), (45), (160), (22), (6), (12), (447), (119), (41), (58), (312), (8), (41), (56), (741), (20), (145), (8), (292), (131), (43), (334), (8), (1065), (53), (8), (55), (8), (2), (53), (2), (105), (14), (946), (181), (61), (322), (0), (8), (26), (246), (0), (0), (0), (580), (807), (479), (25), (189), (249), (925), (284), (302), (349), (74), (89), (320), (1), (2), (8), (978), (12), (282), (337), (163), (105), (323), (0), (0), (3), (179), (314), (171), (43), (111), (0), (0), (50), (863), (25), (74), (0), (0), (524), (23), (948), (23), (922), (15), (25), (573), (8), (12), (53), (168), (69), (652), (123), (120), (1), (194), (76), (105), (55), (159), (339), (0), (0), (283), (11), (25), (108), (173), (162), (149), (31), (0), (0), (979), (979), (979), (597), (631), (25), (146), (111), (12), (258), (433), (236), (0), (31), (867), (852), (25), (121), (0), (356), (6), (203), (0), (0), (1040), (410), (25), (115), (0), (49), (164), (15), (220), (96), (5), (20), (119), (145), (250), (98), (0), (0), (339), (274), (25), (132), (30), (30), (6), (364), (0), (0), (566), (1060), (25), (56), (0), (368), (320), (8), (3), (55), (173), (71), (31), (0), (168), (57), (25), (6), (2), (109), (53), (89), (356), (25), (0), (31), (0), (915), (915), (693), (25), (163), (113), (152), (43), (207), (57), (74), (6), (53), (0), (5), (6), (88), (145), (2), (55), (115), (0), (8), (8), (245), (0), (4), (0), (200) }; t.n = 372; return t end)(), (function() local t = { (127), (185), (8), (127), (86), (127), (18), (127), (62), (127), (8), (40), (62), (127), (107), (127), (8), (155), (127), (34), (131), (101), (101), (92), (127), (189), (127), (185), (127), (127), (86), (127), (8), (127), (158), (164), (185), (127), (189), (127), (127), (127), (127), (18), (127), (185), (185), (186), (127), (127), (169), (127), (127), (189), (127), (127), (62), (127), (189), (127), (8), (8), (127), (164), (127), (131), (93), (101), (101), (92), (127), (127), (185), (127), (185), (155), (155), (77), (75), (161), (8), (127), (164), (127), (131), (90), (101), (101), (101), (92), (127), (131), (90), (101), (101), (60), (19), (127), (8), (164), (127), (49), (122), (127), (127), (18), (127), (127), (8), (89), (127), (18), (127), (62), (127), (189), (127), (62), (127), (127), (127), (62), (127), (127), (127), (168), (26), (8), (8), (8), (127), (189), (127), (90), (131), (101), (101), (92), (127), (47), (8), (127), (185), (8), (127), (127), (107), (127), (127), (8), (185), (127), (189), (127), (127), (62), (127), (155), (127), (127), (8), (8), (127), (185), (127), (127), (189), (127), (158), (8), (127), (185), (127), (158), (8), (127), (164), (127), (127), (8), (8), (8), (127), (168), (158), (8), (127), (90), (34), (131), (101), (101), (101), (60), (19), (127), (169), (127), (62), (127), (127), (8), (127), (185), (164), (155), (8), (127), (62), (127), (127), (169), (127), (58), (173), (155), (127), (86), (127), (127), (127), (90), (131), (101), (101), (92), (127), (90), (131), (76), (5), (141), (17), (101), (92), (127), (8), (155), (127), (62), (127), (8), (8), (8), (127), (59), (8), (8), (40), (40), (62), (127), (131), (90), (101), (101), (92), (127), (127), (189), (127), (93), (90), (131), (101), (101), (101), (101), (101), (60), (19), (127), (62), (127), (189), (127), (131), (93), (101), (101), (92), (127), (18), (127), (13), (127), (131), (90), (101), (101), (92), (127), (168), (8), (8), (8), (40), (8), (160), (67), (91), (127), (62), (127), (90), (131), (101), (101), (60), (19), (127), (127), (185), (127), (90), (131), (101), (101), (92), (127), (18), (127), (40), (158), (164), (127), (86), (127), (93), (131), (101), (101), (92), (127), (164), (8), (127), (8), (127), (127), (131), (93), (90), (101), (101), (101), (60), (19), (127), (127), (40), (77), (75), (161), (185), (127), (168), (1), (155), (8), (127), (164), (127), (127), (168), (155), (158), (127), (168), (185), (181), (127) }; t.n = 372; return t end)(), {}, (function() local t = { (0), (5), (0), (0), (12), (0), (211), (0), (12), (0), (0), (6), (7), (0), (566), (0), (0), (0), (0), (0), (32), (30), (32), (0), (0), (7), (0), (2), (0), (0), (12), (0), (0), (0), (6), (0), (2), (0), (7), (0), (0), (0), (0), (8), (0), (3), (6), (0), (0), (0), (7), (0), (0), (7), (0), (0), (7), (0), (12), (0), (0), (0), (0), (0), (0), (32), (0), (31), (32), (0), (0), (0), (4), (0), (4), (0), (0), (59), (59), (219), (0), (0), (0), (0), (32), (26), (26), (26), (32), (0), (0), (32), (26), (26), (32), (35), (198), (0), (0), (0), (0), (414), (139), (0), (0), (155), (0), (0), (0), (3), (0), (4), (0), (7), (0), (9), (0), (7), (0), (0), (0), (7), (0), (0), (0), (0), (8), (0), (0), (0), (0), (7), (0), (26), (32), (26), (32), (0), (0), (5), (0), (0), (1), (0), (0), (0), (900), (0), (0), (0), (4), (0), (7), (0), (0), (12), (0), (0), (0), (0), (0), (0), (0), (0), (0), (0), (7), (0), (6), (0), (0), (1), (0), (6), (0), (0), (0), (0), (0), (0), (0), (0), (0), (0), (6), (0), (0), (26), (0), (32), (30), (26), (32), (145), (118), (0), (7), (0), (7), (0), (0), (0), (0), (3), (0), (0), (0), (0), (9), (0), (0), (12), (0), (1), (2), (0), (0), (12), (0), (0), (0), (26), (32), (26), (32), (0), (0), (16), (22), (417), (23), (23), (674), (22), (0), (0), (0), (0), (0), (7), (0), (0), (0), (0), (0), (0), (0), (0), (9), (9), (7), (0), (32), (26), (26), (32), (0), (0), (0), (7), (0), (0), (26), (32), (32), (26), (31), (26), (32), (164), (10), (0), (7), (0), (7), (0), (32), (0), (31), (32), (0), (0), (363), (0), (3), (0), (32), (26), (26), (32), (0), (0), (0), (0), (0), (0), (9), (0), (189), (2), (48), (0), (7), (0), (26), (32), (26), (32), (165), (233), (0), (0), (5), (0), (26), (32), (26), (32), (0), (0), (178), (0), (4), (6), (0), (0), (7), (0), (0), (32), (31), (32), (0), (0), (0), (0), (0), (0), (0), (0), (32), (0), (26), (31), (26), (32), (134), (84), (0), (0), (9), (155), (117), (67), (2), (0), (0), (4), (0), (0), (0), (0), (0), (0), (0), (0), (6), (0), (0), (2), (4), (0) }; t.n = 372; return t end)(), (function() local t = { (nil), (nil), (38), (nil), (149), (nil), (nil), (nil), (nil), (nil), (66), (nil), (nil), (nil), (nil), (nil), (9), (nil), (nil), (nil), (nil), (84), (179), (nil), (nil), (82), (nil), (nil), (nil), (nil), (158), (nil), (true), (nil), (nil), (nil), (nil), (nil), (32), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (51), (nil), (nil), (35), (nil), (nil), (nil), (nil), (85), (nil), (1), (24), (nil), (nil), (nil), (nil), (nil), (184), (42), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (110), (269), (nil), (nil), (nil), (nil), (nil), (273), (57), (108), (nil), (nil), (nil), (nil), (230), (30), (nil), (nil), (nil), (35), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (93), (nil), (nil), (nil), (nil), (nil), (nil), (176), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (41), (175), (39), (nil), (84), (nil), (nil), (nil), (2), (350), (nil), (nil), (nil), (36), (nil), (nil), (51), (nil), (nil), (nil), (nil), (nil), (98), (nil), (nil), (38), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (118), (100), (nil), (nil), (nil), (nil), (9), (nil), (nil), (84), (nil), (nil), (nil), (nil), (5), (nil), (nil), (nil), (nil), (62), (169), (107), (nil), (nil), (nil), (78), (nil), (nil), (nil), (nil), (44), (212), (121), (nil), (nil), (nil), (24), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (nil), (48), (nil), (nil), (nil), (nil), (12), (nil), (nil), (nil), (nil), (nil), (172), (nil), (nil), (nil), (nil), (nil), (11), (201), (nil), (nil), (nil), (nil), (409), (nil), (-27805), (nil), (340), (nil), (nil), (79), (nil), (nil), (nil), (nil), (12), (172), (80), (nil), (nil), (149), (7), (nil), (nil), (nil), (nil), (nil), (nil), (110), (72), (nil), (nil), (nil), (98), (nil), (nil), (nil), (nil), (366), (366), (366), (158), (221), (nil), (nil), (nil), (nil), (nil), (79), (nil), (nil), (nil), (162), (41), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (209), (364), (nil), (nil), (nil), (90), (206), (59), (nil), (25), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (164), (312), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (169), (160), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (118), (nil), (nil), (nil), (126), (56), (nil), (nil), (nil), (32), (nil), (1), (nil), (nil), (nil), (nil), (nil), (298), (298), (146), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (82), (nil), (nil), (nil), (nil), (nil), (34) }; t.n = 360; return t end)(), (function() local t = { (0), (0), (7), (0), (34), (0), (9), (0), (900), (0), (8), (0), (280), (0), (7), (0), (7), (41), (0), (30), (0), (32), (16), (32), (0), (159), (0), (0), (0), (0), (72), (0), (8), (0), (3), (3), (0), (0), (53), (0), (0), (0), (0), (9), (0), (0), (0), (0), (0), (0), (326), (0), (0), (198), (0), (0), (447), (0), (105), (0), (6), (7), (0), (3), (0), (0), (0), (32), (458), (32), (0), (0), (0), (0), (0), (42), (42), (194), (6), (75), (7), (0), (2), (0), (0), (0), (101), (101), (190), (32), (0), (0), (0), (90), (316), (32), (128), (0), (7), (3), (0), (212), (674), (0), (0), (9), (0), (0), (7), (3), (0), (9), (0), (674), (0), (208), (0), (43), (0), (0), (0), (834), (0), (0), (0), (0), (6), (9), (10), (11), (0), (166), (0), (0), (0), (8), (904), (32), (0), (5), (7), (0), (0), (7), (0), (0), (12), (0), (0), (7), (0), (0), (302), (0), (0), (117), (0), (42), (0), (0), (7), (6), (0), (0), (0), (0), (38), (0), (3), (7), (0), (0), (0), (3), (7), (0), (3), (0), (0), (4), (5), (6), (0), (0), (3), (9), (0), (0), (30), (0), (43), (566), (914), (32), (148), (0), (102), (0), (65), (0), (0), (3), (0), (0), (3), (42), (7), (0), (283), (0), (0), (217), (0), (0), (0), (42), (0), (361), (0), (0), (0), (0), (0), (55), (40), (32), (0), (0), (0), (23), (368), (23), (16), (187), (24), (0), (7), (41), (0), (4), (0), (9), (10), (11), (0), (0), (10), (11), (0), (0), (72), (0), (0), (0), (110), (144), (32), (0), (0), (274), (0), (0), (0), (0), (55), (603), (32), (603), (98), (32), (125), (0), (433), (0), (107), (0), (0), (0), (32), (479), (32), (0), (6), (0), (3), (0), (0), (0), (101), (590), (32), (0), (0), (9), (10), (11), (0), (7), (156), (240), (182), (0), (330), (0), (0), (0), (8), (19), (32), (208), (0), (0), (0), (0), (0), (0), (597), (57), (32), (0), (4), (0), (0), (3), (3), (0), (60), (0), (0), (0), (32), (51), (32), (0), (3), (7), (0), (5), (0), (0), (0), (0), (0), (32), (55), (87), (32), (145), (0), (0), (0), (146), (7), (111), (0), (0), (0), (4), (42), (7), (0), (6), (0), (0), (0), (42), (3), (0), (0), (0), (0), (0) }; t.n = 372; return t end)(), 0, (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (169), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (80), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (69), (nil), (nil), (34) }; t.n = 233; return t end)())), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (4), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (88), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (185), (102), (3957), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (table.pack(table.pack(table.pack(0, 2), table.pack(1, 2), table.pack(2, 2), table.pack(3, 2), table.pack(4, 2), table.pack(5, 2), table.pack(1, 1)), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (table.pack({}, (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (116), (24), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (table.pack({}, (function() local t = { (nil), (nil), (nil), (nil), (0), (79), (nil), (nil), (nil), (0), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (25), (1), (7), (1), (90), (nil), (nil), (nil), (nil), (nil), (nil), (85), (17), (83), (nil), (nil), (nil), (nil), (92), (71), (nil), (nil), (nil), (nil), (nil), (0), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (283), (nil), (nil), (nil), (0), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (nil), (nil), (nil), (1476), (nil), (nil), (11) }; t.n = 98; return t end)(), 27, (function() local t = { (15), (23), (25), (0), (676), (99), (19), (157), (79), (16), (76), (0), (89), (32), (58), (41), (2), (1), (86), (103), (43), (723), (94), (5), (6), (60), (100), (29), (49), (0), (25), (0), (0), (116), (77), (77), (77), (7), (19), (62), (90), (0), (25), (0), (40), (40), (80), (19), (83), (0), (0), (551), (1057), (19), (184), (71), (332), (81), (17), (27), (5), (6), (6), (64), (6), (6), (58), (5), (6), (6), (9), (0), (0), (304), (81), (85), (5), (67), (92), (5), (0), (17), (19), (28), (497), (56), (1), (101), (72), (9), (17), (1), (3), (67), (17), (839), (17), (102), (9), (11), (3), (60) }; t.n = 102; return t end)(), (function() local t = { (127), (127), (93), (131), (101), (101), (60), (19), (127), (62), (127), (58), (178), (8), (127), (127), (127), (48), (127), (77), (75), (161), (127), (182), (182), (248), (127), (127), (127), (34), (93), (131), (90), (101), (101), (101), (101), (101), (60), (19), (127), (131), (93), (90), (101), (101), (101), (92), (127), (90), (131), (101), (101), (60), (19), (127), (8), (127), (62), (127), (246), (4), (1), (127), (4), (96), (127), (1), (4), (96), (127), (131), (90), (143), (32), (127), (182), (62), (127), (185), (65), (39), (127), (127), (57), (127), (160), (67), (91), (127), (62), (127), (47), (127), (5), (141), (17), (101), (153), (127), (47), (127) }; t.n = 102; return t end)(), {}, (function() local t = { (0), (0), (0), (26), (25), (26), (97), (12), (0), (1), (0), (2), (0), (0), (0), (0), (0), (2), (0), (214), (113), (67), (0), (6), (6), (6), (0), (0), (0), (0), (0), (26), (20), (20), (24), (25), (20), (26), (39), (223), (0), (26), (0), (20), (20), (25), (26), (0), (0), (20), (26), (20), (26), (83), (62), (0), (0), (0), (1), (0), (132), (1), (7), (0), (2), (3), (0), (6), (1), (3), (0), (16), (10), (226), (17), (0), (6), (5), (0), (4), (127), (94), (0), (0), (489), (0), (241), (2), (168), (0), (2), (0), (4), (0), (17), (17), (612), (16), (0), (0), (4), (0) }; t.n = 102; return t end)(), (function() local t = { (nil), (nil), (nil), (nil), (81), (17), (nil), (nil), (nil), (nil), (nil), (nil), (1), (0), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (205), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (26), (61), (61), (61), (28), (nil), (nil), (nil), (nil), (nil), (nil), (74), (74), (16), (nil), (nil), (nil), (nil), (99), (29), (nil), (nil), (nil), (511), (nil), (nil), (nil), (nil), (2), (nil), (nil), (2), (2), (nil), (nil), (2), (2), (nil), (nil), (nil), (154), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (-1673), (nil), (84) }; t.n = 98; return t end)(), (function() local t = { (0), (0), (0), (0), (32), (433), (26), (252), (0), (32), (0), (0), (3), (4), (0), (0), (0), (9), (0), (142), (17), (254), (0), (1), (2), (5), (0), (0), (0), (24), (0), (0), (0), (187), (89), (28), (89), (30), (26), (253), (0), (0), (0), (0), (898), (99), (83), (26), (0), (0), (0), (487), (705), (26), (5), (0), (17), (0), (32), (0), (116), (7), (2), (0), (7), (3), (0), (1), (6), (3), (0), (0), (0), (755), (0), (0), (1), (32), (0), (0), (5), (0), (0), (0), (177), (0), (154), (210), (47), (0), (32), (0), (4), (0), (338), (17), (10), (50), (18), (0), (4), (0) }; t.n = 102; return t end)(), 0, (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (2), (2), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (2), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (13) }; t.n = 97; return t end)())), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (373), (4321), (nil), (nil), (2), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (9), (10), (181), (28), (nil), (nil), (nil), (table.pack({}, table.pack(nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 29163, nil, nil, 6, nil, nil, nil, nil, nil, 8, 0, 74, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 47, 4, 65, nil, nil, nil, nil, nil, nil, nil, nil, nil, 5, 2, 6, 6), 26, (function() local t = { (63), (0), (34), (22), (32), (1), (0), (18), (50), (0), (14), (109), (16), (720), (16), (628), (28), (75), (41), (24), (0), (99), (99), (79), (18), (74), (89), (39), (89), (6), (4), (89), (89), (6), (89), (6), (4), (5), (72), (5), (2), (0), (0), (0), (464), (464), (91), (18), (150), (65), (28), (86), (19), (24), (0), (0), (674), (66), (66), (90), (18), (54), (6), (52), (26), (89), (6), (4), (5), (4), (39), (64), (5), (0), (9), (53) }; t.n = 76; return t end)(), (function() local t = { (127), (65), (77), (75), (161), (127), (58), (32), (127), (131), (93), (76), (5), (141), (17), (101), (92), (127), (127), (93), (131), (101), (101), (101), (92), (127), (8), (127), (29), (57), (54), (29), (29), (1), (141), (57), (61), (182), (127), (39), (127), (131), (90), (34), (101), (101), (101), (60), (19), (127), (127), (108), (127), (93), (131), (34), (101), (101), (101), (101), (60), (19), (127), (127), (127), (29), (57), (58), (61), (27), (32), (127), (1), (65), (127), (127) }; t.n = 76; return t end)(), {}, (function() local t = { (0), (0), (91), (86), (140), (0), (3), (3), (0), (15), (0), (221), (16), (16), (65), (15), (189), (0), (0), (0), (25), (25), (24), (25), (0), (0), (0), (0), (2), (4), (4), (34), (204), (151), (5), (5), (4), (89), (0), (1), (0), (25), (19), (0), (19), (23), (25), (18), (87), (0), (0), (251), (0), (0), (25), (0), (24), (24), (23), (25), (79), (121), (0), (0), (0), (2), (4), (5), (1), (5), (5), (0), (5), (0), (0), (0) }; t.n = 76; return t end)(), (function() local t = { (nil), (nil), (nil), (nil), (0), (nil), (nil), (nil), (nil), (nil), (nil), (32), (nil), (-29057), (nil), (75), (nil), (nil), (nil), (nil), (nil), (17), (17), (53), (nil), (nil), (1), (nil), (1), (2), (nil), (1), (1), (nil), (1), (2), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (68), (68), (19), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (34), (33), (33), (76), (nil), (nil), (nil), (nil), (nil), (1), (2) }; t.n = 67; return t end)(), (function() local t = { (0), (5), (47), (5), (149), (0), (0), (0), (0), (0), (0), (16), (129), (16), (14), (51), (17), (0), (0), (0), (0), (55), (32), (40), (25), (0), (5), (0), (4), (4), (1), (5), (176), (5), (5), (5), (5), (4), (0), (0), (0), (0), (0), (23), (58), (71), (48), (25), (24), (0), (0), (47), (0), (0), (0), (23), (4), (6), (51), (51), (25), (162), (0), (0), (0), (4), (4), (161), (5), (5), (0), (0), (4), (5), (0), (0) }; t.n = 76; return t end)(), 0, table.pack(nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 135, nil, nil, 32, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 1))), (table.pack(table.pack(table.pack(1, 1), table.pack(4, 1), table.pack(5, 1)), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (8), (39), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (6), (0), (0), (43), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (6), (0), (185), (15), (nil), (nil), (nil), (nil), (nil), (454), (nil), (nil), (17492), (nil), (nil), (15), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (81) }; t.n = 86; return t end)(), 27, (function() local t = { (57), (179), (7), (80), (0), (71), (29), (0), (0), (431), (3), (19), (122), (39), (58), (71), (5), (5), (17), (76), (1), (45), (0), (599), (38), (1), (2), (89), (14), (0), (0), (6), (6), (580), (28), (19), (46), (43), (7), (6), (7), (65), (6), (113), (553), (6), (1), (0), (0), (0), (396), (91), (91), (91), (705), (19), (15), (82), (0), (15), (165), (987), (64), (17), (619), (17), (85), (9), (70), (2), (47), (104), (6), (6), (7), (118), (77), (55), (0), (6), (0), (25), (0), (0), (116), (23), (19), (81) }; t.n = 88; return t end)(), (function() local t = { (127), (195), (185), (8), (81), (127), (127), (131), (90), (101), (101), (60), (19), (127), (127), (8), (22), (195), (85), (77), (75), (161), (81), (96), (127), (195), (195), (8), (127), (131), (34), (101), (101), (101), (101), (60), (19), (127), (127), (195), (185), (21), (127), (81), (96), (47), (127), (34), (131), (90), (101), (101), (101), (101), (101), (92), (127), (127), (131), (93), (31), (66), (79), (5), (141), (17), (101), (92), (127), (130), (127), (96), (47), (195), (160), (67), (91), (8), (81), (47), (65), (127), (131), (34), (101), (101), (92), (127) }; t.n = 88; return t end)(), {}, (function() local t = { (0), (2), (2), (0), (6), (0), (0), (26), (20), (20), (26), (91), (115), (0), (0), (0), (4), (2), (4), (56), (32), (181), (5), (5), (0), (0), (1), (0), (0), (26), (0), (26), (24), (26), (26), (5), (127), (0), (0), (2), (184), (0), (0), (6), (6), (5), (0), (0), (26), (20), (24), (26), (24), (20), (26), (0), (0), (0), (16), (0), (17), (29), (223), (17), (17), (852), (16), (0), (0), (471), (0), (6), (5), (2), (228), (1), (89), (0), (6), (5), (0), (0), (26), (0), (24), (26), (0), (0) }; t.n = 88; return t end)(), (function() local t = { (nil), (nil), (nil), (16), (nil), (nil), (nil), (nil), (nil), (42), (39), (nil), (nil), (nil), (nil), (4), (nil), (nil), (nil), (nil), (nil), (64), (nil), (16777216), (nil), (nil), (nil), (1), (nil), (nil), (nil), (2), (2), (44), (7), (nil), (nil), (nil), (nil), (nil), (nil), (32), (nil), (nil), (65536), (nil), (nil), (nil), (nil), (nil), (18), (19), (19), (19), (71), (nil), (nil), (nil), (nil), (nil), (nil), (45), (nil), (nil), (-17988), (nil), (15), (nil), (nil), (nil), (nil), (256), (nil), (nil), (nil), (nil), (nil), (8), (nil), (nil), (nil), (nil), (nil), (nil), (26), (58) }; t.n = 86; return t end)(), (function() local t = { (0), (212), (0), (8), (0), (0), (0), (0), (0), (55), (3), (26), (9), (0), (0), (4), (1), (244), (13), (193), (7), (250), (0), (5), (0), (61), (0), (3), (0), (0), (24), (51), (32), (32), (323), (26), (162), (0), (0), (0), (0), (8), (0), (0), (6), (5), (0), (24), (0), (0), (32), (51), (32), (8), (85), (26), (0), (0), (0), (0), (406), (88), (223), (635), (17), (15), (85), (18), (0), (3), (0), (6), (5), (0), (141), (71), (124), (8), (0), (5), (5), (0), (0), (24), (32), (676), (26), (0) }; t.n = 88; return t end)(), 0, (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (41) }; t.n = 66; return t end)())), (table.pack(table.pack(table.pack(7, 1), table.pack(6, 1)), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (1), (0), (8), (96), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (97), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (7), (2), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (8), (10), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (27863), (nil), (nil), (83), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (32), (110), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (12), (6), (6), (52) }; t.n = 122; return t end)(), 28, (function() local t = { (82), (99), (6), (241), (56), (35), (65), (0), (89), (106), (1069), (6), (7), (125), (73), (92), (156), (12), (159), (239), (227), (2), (0), (89), (4), (5), (38), (26), (0), (0), (0), (80), (80), (3), (3), (83), (20), (96), (89), (899), (4), (141), (1), (5), (6), (65), (0), (33), (94), (20), (97), (137), (89), (32), (109), (0), (71), (850), (20), (195), (2), (107), (46), (708), (1), (422), (442), (4), (72), (32), (0), (373), (55), (89), (32), (62), (0), (73), (590), (20), (73), (10), (27), (15), (0), (0), (714), (18), (239), (18), (108), (10), (83), (32), (32), (51), (84), (7), (129), (0), (0), (1038), (6), (20), (116), (110), (115), (32), (69), (113), (7), (62), (14), (61), (76), (0), (0), (0), (79), (79), (79), (1034), (20), (18), (52), (802), (89), (8), (0), (93), (89), (32), (114) }; t.n = 133; return t end)(), (function() local t = { (127), (127), (195), (185), (77), (75), (161), (81), (57), (127), (29), (57), (89), (127), (127), (195), (103), (24), (174), (129), (172), (195), (181), (8), (195), (185), (127), (93), (90), (34), (131), (101), (101), (101), (101), (101), (92), (127), (250), (8), (126), (96), (47), (195), (185), (127), (131), (101), (101), (92), (127), (65), (201), (86), (127), (131), (101), (101), (60), (19), (127), (127), (127), (86), (127), (8), (8), (126), (127), (96), (65), (87), (127), (96), (4), (127), (131), (101), (101), (60), (19), (127), (127), (127), (34), (131), (76), (5), (141), (17), (101), (92), (127), (96), (4), (127), (127), (39), (127), (90), (131), (101), (101), (60), (19), (127), (127), (86), (127), (127), (154), (207), (127), (127), (127), (90), (34), (131), (101), (101), (101), (101), (60), (19), (127), (4), (47), (89), (65), (127), (8), (8), (127) }; t.n = 133; return t end)(), {}, (function() local t = { (0), (0), (1), (2), (32), (126), (11), (6), (6), (0), (5), (7), (6), (0), (0), (0), (1), (169), (158), (245), (164), (0), (2), (0), (1), (2), (0), (0), (21), (0), (27), (25), (27), (26), (21), (27), (0), (0), (73), (0), (0), (4), (4), (1), (2), (0), (27), (27), (27), (0), (0), (0), (0), (5), (0), (27), (27), (27), (42), (48), (0), (0), (0), (5), (0), (0), (0), (0), (0), (7), (0), (246), (0), (7), (7), (0), (27), (27), (27), (40), (215), (0), (0), (0), (0), (17), (142), (18), (18), (331), (17), (0), (0), (7), (7), (0), (0), (51), (0), (21), (27), (21), (27), (38), (73), (0), (0), (4), (0), (0), (4), (7), (0), (0), (0), (21), (0), (27), (21), (25), (27), (27), (203), (45), (0), (8), (8), (7), (0), (0), (0), (0), (0) }; t.n = 133; return t end)(), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (32), (nil), (1), (nil), (1023), (2), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (16), (16), (39), (39), (83), (nil), (nil), (1), (20), (nil), (4294967296), (nil), (nil), (nil), (nil), (nil), (52), (63), (nil), (nil), (nil), (nil), (0), (nil), (nil), (4), (73), (nil), (nil), (nil), (nil), (nil), (2047), (nil), (21), (31), (nil), (nil), (0), (nil), (nil), (nil), (1), (0), (nil), (nil), (127), (115), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (478), (nil), (-28053), (nil), (97), (nil), (nil), (0), (0), (nil), (nil), (nil), (nil), (nil), (nil), (112), (2), (nil), (nil), (nil), (nil), (0), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (53), (53), (53), (107), (nil), (nil), (nil), (4503599627370496), (nil), (nil), (nil), (nil), (1), (0) }; t.n = 132; return t end)(), (function() local t = { (0), (0), (0), (0), (139), (8), (181), (0), (6), (0), (7), (7), (7), (0), (0), (215), (36), (3), (111), (169), (71), (0), (0), (3), (0), (0), (0), (0), (0), (25), (0), (32), (89), (32), (55), (527), (27), (0), (6), (7), (4), (4), (4), (0), (0), (0), (0), (32), (108), (27), (0), (7), (76), (63), (0), (0), (28), (6), (27), (251), (0), (0), (0), (114), (0), (7), (166), (5), (0), (6), (7), (300), (0), (6), (7), (0), (0), (55), (115), (27), (234), (0), (0), (0), (15), (0), (18), (520), (18), (15), (83), (19), (0), (6), (7), (0), (0), (0), (0), (0), (0), (65), (283), (27), (19), (0), (0), (130), (0), (0), (32), (0), (0), (0), (0), (0), (25), (0), (105), (51), (51), (33), (27), (142), (0), (4), (3), (7), (7), (0), (5), (3), (0) }; t.n = 133; return t end)(), 0, (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (280), (nil), (nil), (67) }; t.n = 90; return t end)())), (table.pack(table.pack(table.pack(7, 1), table.pack(5, 1), table.pack(8, 1), table.pack(6, 1)), (function() local t = { (nil), (nil), (nil), (nil), (nil), (195), (113), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (16), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (127), (102), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (22), (12), (61), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (3266), (nil), (nil), (216), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (2), (98), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (12), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (15), (0), (158), (nil), (nil), (nil), (nil), (nil), (5), (0), (231), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (195), (2), (15), (195), (91), (nil), (nil), (nil), (nil), (nil), (0), (18), (222) }; t.n = 187; return t end)(), 36, (function() local t = { (25), (89), (236), (0), (0), (178), (168), (28), (113), (143), (0), (49), (0), (231), (171), (89), (7), (0), (1), (0), (0), (26), (136), (41), (150), (79), (182), (15), (212), (92), (21), (35), (222), (227), (0), (16), (0), (0), (0), (16), (164), (1065), (136), (0), (0), (425), (1003), (28), (102), (0), (236), (0), (0), (34), (0), (52), (52), (52), (1002), (28), (61), (12), (151), (66), (11), (9), (186), (13), (0), (0), (11), (10), (167), (26), (411), (26), (27), (18), (216), (89), (2), (0), (95), (0), (34), (479), (479), (704), (28), (16), (98), (15), (97), (0), (24), (89), (165), (195), (0), (1), (2), (120), (19), (0), (0), (11), (12), (0), (13), (0), (0), (11), (162), (14), (150), (29), (103), (185), (218), (223), (146), (3), (0), (0), (83), (3), (0), (926), (514), (28), (12), (171), (32), (176), (89), (10), (26), (239), (27), (0), (227), (190), (27), (0), (0), (412), (412), (115), (28), (158), (0), (34), (0), (677), (677), (187), (28), (231), (15), (14), (0), (138), (144), (181), (43), (0), (238), (11), (0), (12), (103), (0), (34), (0), (500), (840), (291), (291), (490), (28), (91), (126), (0), (0), (503), (503), (745), (28), (17), (222), (27), (14), (0), (223), (125), (15), (16), (0), (101), (198), (128), (223), (17), (0), (0), (9), (51), (10), (11), (0), (211), (12), (0), (0), (11), (206), (0), (17), (0), (0), (15), (10), (162), (15), (0), (15), (131), (15), (14), (90), (34), (0), (32), (176), (89), (26), (19), (93), (124), (113), (73) }; t.n = 241; return t end)(), (function() local t = { (127), (8), (40), (131), (90), (101), (101), (92), (127), (127), (18), (127), (168), (77), (75), (161), (195), (181), (127), (131), (90), (179), (32), (127), (127), (127), (127), (195), (103), (24), (174), (129), (172), (127), (181), (195), (22), (23), (190), (195), (127), (8), (127), (131), (90), (101), (101), (92), (127), (168), (127), (90), (131), (93), (34), (101), (101), (101), (101), (92), (127), (195), (103), (24), (174), (129), (172), (195), (22), (23), (158), (195), (127), (5), (141), (17), (101), (92), (127), (8), (195), (181), (127), (131), (93), (101), (101), (101), (60), (19), (127), (39), (127), (168), (127), (8), (40), (127), (168), (195), (195), (127), (127), (140), (23), (195), (195), (181), (195), (22), (23), (158), (127), (10), (103), (24), (174), (129), (172), (127), (181), (195), (22), (150), (127), (127), (131), (101), (101), (92), (127), (127), (8), (8), (8), (40), (39), (127), (195), (181), (32), (127), (163), (34), (131), (101), (101), (101), (92), (127), (34), (93), (131), (101), (101), (101), (92), (127), (158), (195), (181), (127), (95), (127), (127), (18), (127), (195), (181), (195), (127), (90), (93), (131), (101), (101), (101), (101), (101), (92), (127), (127), (131), (90), (101), (101), (101), (60), (19), (127), (127), (195), (181), (32), (127), (195), (195), (103), (24), (174), (129), (172), (195), (22), (23), (127), (127), (195), (195), (181), (127), (195), (22), (23), (195), (127), (181), (195), (22), (15), (158), (77), (40), (195), (181), (26), (127), (158), (212), (18), (127), (88), (8), (8), (8), (127), (18), (127), (127), (8), (127) }; t.n = 241; return t end)(), {}, (function() local t = { (0), (0), (6), (35), (29), (29), (35), (0), (0), (0), (191), (0), (0), (68), (223), (4), (0), (7), (0), (25), (19), (517), (26), (0), (0), (0), (0), (2), (15), (47), (137), (132), (188), (0), (15), (0), (1), (0), (15), (2), (0), (0), (0), (35), (29), (29), (35), (0), (0), (0), (0), (29), (35), (0), (0), (34), (29), (33), (35), (0), (0), (0), (12), (156), (77), (93), (38), (0), (1), (0), (10), (1), (0), (26), (26), (456), (25), (0), (0), (0), (0), (2), (0), (35), (0), (35), (34), (35), (81), (138), (0), (9), (0), (0), (0), (0), (1), (0), (0), (1), (2), (0), (0), (99), (0), (1), (0), (12), (0), (1), (0), (10), (0), (0), (14), (177), (232), (69), (46), (0), (222), (0), (1), (0), (0), (0), (35), (35), (35), (0), (0), (0), (0), (0), (0), (10), (73), (0), (2), (15), (15), (0), (294), (0), (35), (35), (33), (35), (0), (0), (0), (0), (35), (34), (33), (35), (0), (0), (14), (0), (14), (0), (207), (0), (0), (24), (0), (0), (11), (0), (0), (29), (0), (35), (29), (34), (35), (29), (35), (0), (0), (0), (35), (29), (35), (29), (35), (65), (49), (0), (0), (2), (14), (14), (0), (1), (170), (16), (196), (169), (128), (151), (2), (1), (0), (0), (0), (1), (0), (11), (0), (0), (1), (0), (1), (0), (16), (0), (1), (15), (14), (0), (6), (2), (15), (15), (0), (14), (3), (2), (0), (26), (0), (0), (0), (0), (132), (0), (0), (0), (0) }; t.n = 241; return t end)(), (function() local t = { (nil), (1), (nil), (nil), (nil), (114), (126), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (84), (nil), (nil), (nil), (222), (165), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (104), (104), (104), (207), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (-3108), (nil), (103), (nil), (nil), (1), (nil), (nil), (nil), (nil), (nil), (121), (121), (125), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (237), (182), (nil), (nil), (nil), (0), (255), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (139), (139), (10), (nil), (nil), (nil), (nil), (nil), (232), (232), (25), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (229), (197), (230), (230), (132), (nil), (nil), (nil), (nil), (nil), (163), (163), (27), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (255), (1), (nil), (nil), (nil), (nil), (13) }; t.n = 240; return t end)(), (function() local t = { (0), (8), (0), (0), (0), (713), (87), (35), (0), (0), (10), (0), (0), (12), (6), (231), (0), (0), (0), (0), (0), (10), (0), (0), (0), (0), (0), (0), (136), (22), (4), (34), (2), (0), (0), (0), (16), (14), (1), (0), (0), (26), (0), (0), (0), (73), (917), (35), (0), (0), (0), (0), (0), (0), (33), (89), (363), (105), (77), (35), (0), (0), (225), (55), (131), (112), (102), (0), (13), (11), (5), (0), (0), (198), (26), (19), (585), (27), (0), (1), (0), (0), (0), (0), (0), (32), (6), (162), (35), (69), (0), (0), (0), (0), (0), (3), (0), (0), (0), (0), (0), (0), (0), (233), (10), (0), (0), (0), (0), (13), (11), (5), (0), (0), (34), (63), (21), (240), (0), (0), (0), (0), (3), (1), (0), (0), (0), (32), (105), (35), (0), (0), (10), (11), (12), (0), (0), (0), (229), (0), (0), (0), (201), (33), (0), (85), (32), (597), (35), (0), (33), (0), (0), (4), (32), (538), (35), (0), (5), (0), (0), (0), (6), (0), (0), (1), (0), (0), (0), (0), (0), (0), (0), (0), (713), (6), (85), (713), (297), (35), (0), (0), (0), (0), (32), (396), (425), (35), (213), (0), (0), (0), (0), (0), (0), (0), (0), (165), (161), (107), (182), (110), (0), (17), (15), (0), (0), (0), (0), (0), (0), (0), (12), (10), (0), (0), (0), (0), (17), (0), (5), (0), (0), (0), (0), (5), (0), (5), (0), (0), (0), (25), (6), (7), (8), (0), (6), (0), (0), (26), (0) }; t.n = 241; return t end)(), 0, (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (290), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (220) }; t.n = 76; return t end)())), (nil), (nil), (nil), (nil), (nil), (1), (1), (12) }; t.n = 72; return t end)(), 29, (function() local t = { (21), (400), (0), (0), (286), (0), (218), (4), (821), (65), (50), (1), (32), (0), (0), (45), (45), (13), (21), (228), (24), (23), (41), (66), (55), (0), (0), (60), (10), (0), (11), (22), (17), (0), (417), (19), (495), (19), (612), (11), (2), (10), (84), (249), (247), (1), (48), (38), (105), (10), (0), (0), (27), (1057), (19), (19), (50), (21), (101), (28), (0), (0), (0), (66), (10), (13), (0), (27), (0), (71), (4), (925), (21), (87), (12) }; t.n = 75; return t end)(), (function() local t = { (127), (133), (28), (84), (117), (84), (117), (185), (8), (127), (127), (59), (127), (90), (131), (101), (101), (101), (60), (19), (127), (127), (127), (127), (8), (81), (116), (127), (185), (40), (32), (127), (93), (131), (151), (5), (141), (17), (101), (92), (127), (185), (187), (170), (77), (73), (146), (110), (172), (127), (131), (90), (93), (101), (101), (101), (101), (60), (19), (127), (116), (116), (116), (119), (127), (127), (34), (93), (131), (101), (101), (101), (60), (19), (127) }; t.n = 75; return t end)(), {}, (function() local t = { (0), (231), (0), (778), (150), (778), (2), (2), (0), (0), (0), (0), (0), (22), (28), (28), (22), (28), (79), (251), (0), (0), (0), (0), (0), (4), (5), (0), (104), (69), (10), (0), (0), (18), (19), (19), (19), (101), (18), (0), (0), (9), (10), (84), (248), (196), (201), (105), (137), (0), (28), (22), (0), (27), (27), (22), (28), (210), (170), (0), (6), (236), (8), (9), (0), (0), (0), (0), (28), (26), (27), (28), (158), (234), (0) }; t.n = 75; return t end)(), (function() local t = { (nil), (nil), (nil), (nil), ("byte"), (nil), ("rep"), (nil), (" "), (nil), (nil), (nil), (nil), (nil), (nil), (64), (64), (66), (nil), (nil), (nil), (nil), (nil), (nil), (8), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (69), (nil), (-4756), (nil), (13), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (29), (30), (30), (11), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (4), (5), (24) }; t.n = 72; return t end)(), (function() local t = { (0), (60), (0), (16), (1), (2), (2), (0), (5), (0), (0), (0), (0), (0), (0), (32), (272), (925), (28), (91), (0), (0), (0), (0), (6), (0), (26), (0), (0), (0), (0), (0), (0), (0), (432), (592), (19), (17), (6), (20), (0), (0), (222), (45), (122), (252), (27), (76), (72), (0), (0), (0), (0), (43), (115), (498), (7), (28), (166), (0), (11), (9), (34), (13), (0), (0), (26), (0), (0), (89), (89), (105), (28), (253), (0) }; t.n = 75; return t end)(), 0, table.pack(nil, nil, nil, "string", nil, "string", nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 62))), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (2), (8), (0), (5), (40), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (76), (12), (61), (nil), (nil), (nil), (nil), (nil), (nil), (22445), (nil), (nil), (45), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (0), (11) }; t.n = 77; return t end)(), 22, (function() local t = { (26), (27), (89), (0), (89), (6), (70), (4), (0), (0), (2), (145), (45), (99), (217), (252), (95), (5), (40), (0), (2), (0), (7), (1), (70), (72), (1), (51), (0), (0), (0), (20), (62), (62), (323), (323), (77), (14), (181), (40), (45), (3), (3), (25), (221), (1), (0), (1), (3), (3), (60), (20), (0), (0), (94), (45), (7), (14), (83), (61), (28), (0), (332), (12), (1005), (12), (6), (4), (182), (45), (0), (71), (0), (20), (105), (105), (116), (14), (11) }; t.n = 79; return t end)(), (function() local t = { (127), (127), (178), (42), (8), (127), (40), (8), (26), (88), (127), (116), (187), (170), (77), (73), (146), (110), (172), (92), (92), (43), (127), (158), (127), (127), (127), (127), (90), (34), (131), (93), (101), (101), (101), (101), (101), (60), (19), (127), (142), (142), (142), (127), (137), (155), (173), (142), (142), (142), (127), (93), (90), (131), (101), (101), (101), (60), (19), (127), (127), (131), (81), (5), (141), (17), (101), (60), (19), (127), (18), (127), (131), (93), (101), (101), (101), (92), (127) }; t.n = 79; return t end)(), {}, (function() local t = { (0), (0), (0), (0), (0), (0), (2), (0), (1), (1), (0), (232), (1), (215), (177), (82), (188), (8), (145), (0), (0), (0), (0), (5), (0), (0), (0), (0), (15), (0), (21), (0), (19), (15), (20), (19), (21), (206), (8), (0), (0), (0), (255), (0), (320), (6), (3), (0), (0), (0), (0), (0), (15), (21), (15), (20), (21), (244), (158), (0), (0), (11), (355), (162), (12), (852), (11), (185), (198), (0), (23), (0), (21), (0), (20), (21), (21), (0), (0) }; t.n = 79; return t end)(), (function() local t = { (nil), (nil), (1), (nil), (1), (nil), (nil), (5), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (3), (3), (43), (43), (61), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (63), (64), (28), (nil), (nil), (nil), (nil), (nil), (511), (nil), (-22604), (nil), (2), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (12), (12), (26) }; t.n = 77; return t end)(), (function() local t = { (0), (0), (232), (3), (4), (0), (0), (1), (0), (0), (0), (2), (97), (82), (230), (254), (206), (71), (226), (2), (4), (0), (0), (0), (0), (0), (0), (0), (0), (19), (0), (0), (6), (55), (32), (4), (739), (21), (234), (0), (3), (4), (193), (0), (498), (42), (0), (0), (1), (2), (0), (0), (0), (0), (90), (105), (77), (21), (179), (0), (0), (0), (12), (220), (12), (11), (146), (13), (205), (0), (2), (0), (0), (0), (89), (32), (50), (21), (0) }; t.n = 79; return t end)(), 0, (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (349), (nil), (nil), (41) }; t.n = 66; return t end)())), (nil), (7), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (106), (nil), (nil), (nil), (nil), (130), (4145), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1978823615), (13172272), (nil), (126), (nil), (table.pack(table.pack(table.pack(60, 0), table.pack(1, 1), table.pack(19, 0), table.pack(53, 0), table.pack(51, 0), table.pack(27, 0), table.pack(42, 0), table.pack(62, 0), table.pack(55, 0), table.pack(54, 0), table.pack(84, 0), table.pack(21, 0)), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (156), (29583), (nil), (nil), (29), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (112), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (6), (10), (0), (248), (nil), (nil), (nil), (nil), (21), (167), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (103), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (105), (nil), (nil), (nil), (114), (nil), (nil), (nil), (nil), (185), (320), (nil), (nil), (52), (nil), (110), (nil), (nil), (nil), (110), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (105), (nil), (nil), (nil), (nil), (nil), (nil), (2), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (107), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (108), (nil), (108), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (85), (nil), (nil), (nil), (nil), (nil), (104), (nil), (nil), (nil), (nil), (90), (nil), (58), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (5), (10), (226), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (164), (14), (0), (0), (68), (nil), (nil), (nil), (nil), (113), (nil), (nil), (nil), (nil), (nil), (155), (390), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (104), (nil), (nil), (nil), (nil), (nil), (nil), (110), (nil), (nil), (nil), (nil), (343), (4601), (nil), (nil), (142), (nil), (nil), (96), (nil), (nil), (nil), (nil), (168), (nil), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (109), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (15), (255), (nil), (nil), (47), (111), (nil), (nil), (table.pack(table.pack(table.pack(10, 0), table.pack(1, 2)), table.pack(nil, nil, nil, 46), 4, table.pack(2, 36, 3, 1, 1, 1), table.pack(127, 162, 127, 155, 142, 59), {}, table.pack(0, 500, 0, 1, 0, 0), {}, table.pack(0, 235, 0, 41, 0, 0), 0, {})), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (110), (nil), (nil), (1), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (4), (0), (221), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (1), (nil), (nil), (nil), (nil), (nil), (13), (380), (nil), (nil), (39), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (106), (nil), (nil), (nil), (nil), (10), (354), (nil), (nil), (nil), (nil), (nil), (nil), (109), (nil), (nil), (nil), (151), (124), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (14), (269) }; t.n = 397; return t end)(), 39, (function() local t = { (169), (97), (8), (14), (13), (287), (25), (369), (27), (0), (725), (29), (951), (29), (162), (21), (29), (0), (19), (0), (244), (203), (6), (19), (1), (74), (20), (0), (164), (0), (163), (0), (37), (0), (1041), (1041), (1041), (33), (31), (6), (248), (0), (642), (312), (31), (167), (85), (6), (0), (430), (176), (248), (0), (5), (2), (7), (6), (308), (320), (96), (203), (108), (689), (843), (946), (164), (87), (232), (132), (380), (141), (213), (9), (7), (4), (86), (0), (5), (11), (399), (0), (0), (877), (36), (31), (320), (293), (70), (10), (8), (6), (11), (12), (0), (18), (154), (68), (29), (0), (8), (9), (0), (386), (7), (11), (12), (0), (324), (7), (5), (4), (8), (7), (386), (98), (305), (69), (30), (157), (0), (0), (5), (25), (288), (787), (97), (97), (0), (8), (9), (0), (352), (0), (15), (3), (81), (97), (25), (244), (22), (56), (365), (107), (7), (11), (12), (0), (335), (14), (8), (14), (9), (352), (354), (117), (879), (161), (49), (6), (11), (294), (246), (127), (326), (0), (21), (76), (172), (318), (0), (1), (176), (117), (219), (22), (58), (1001), (52), (142), (244), (0), (0), (37), (538), (538), (788), (31), (168), (226), (1), (723), (392), (37), (0), (0), (0), (60), (60), (60), (60), (108), (31), (68), (0), (8), (15), (322), (89), (189), (0), (0), (82), (702), (31), (390), (88), (330), (52), (342), (82), (215), (0), (5), (3), (7), (47), (9), (11), (10), (10), (7), (117), (167), (0), (301), (29), (1004), (29), (540), (21), (142), (350), (153), (352), (0), (119), (352), (344), (8), (111), (117), (18), (19), (18), (60), (9), (165), (1018), (171), (13), (613), (62), (0), (15), (16), (0), (243), (66), (279), (15), (14), (10), (166), (0), (0), (45), (182), (31), (255), (10), (11), (11), (11), (0), (0), (42), (207), (207), (124), (350), (56), (352), (255), (390), (12), (0), (117), (8), (9), (206), (156), (93), (289), (48), (382), (898), (148), (221), (0), (149), (176), (0), (0), (425), (425), (414), (31), (221), (178), (103), (514), (216), (269), (225), (692), (117), (0), (6), (7), (51), (10), (19), (20), (0), (164), (226), (37), (0), (180), (120), (31), (380), (267), (319), (0), (5), (16), (15), (16), (17), (87), (297), (0), (19), (0), (9), (10), (10), (0), (119), (0), (578), (175), (31), (354), (17), (16), (0), (262), (4), (97), (0), (0), (50), (730), (31), (165), (124), (492), (307), (940), (59), (0), (5), (84), (86), (276), (441), (17), (179), (967), (61), (5), (326), (0), (601), (583), (31), (269), (7), (0), (0), (1) }; t.n = 403; return t end)(), (function() local t = { (127), (8), (164), (185), (186), (127), (86), (127), (93), (131), (151), (5), (141), (17), (101), (92), (127), (120), (127), (168), (127), (127), (164), (160), (67), (91), (155), (120), (127), (18), (127), (131), (93), (34), (101), (101), (101), (101), (60), (19), (127), (131), (101), (101), (92), (127), (122), (7), (120), (8), (127), (127), (164), (155), (164), (185), (7), (127), (127), (127), (127), (127), (8), (8), (8), (40), (189), (127), (127), (127), (77), (75), (161), (155), (26), (127), (164), (155), (164), (127), (131), (90), (101), (101), (92), (127), (62), (127), (155), (26), (164), (185), (155), (120), (8), (127), (127), (127), (164), (185), (185), (120), (127), (164), (185), (185), (120), (127), (155), (26), (164), (185), (7), (32), (127), (62), (127), (189), (127), (168), (173), (155), (8), (127), (8), (8), (40), (164), (42), (42), (120), (127), (164), (155), (176), (71), (50), (64), (98), (109), (140), (127), (8), (164), (185), (185), (120), (127), (155), (26), (155), (26), (127), (127), (127), (189), (127), (8), (164), (185), (127), (62), (127), (127), (18), (127), (127), (62), (127), (58), (8), (127), (62), (127), (62), (127), (86), (127), (127), (40), (34), (131), (93), (101), (101), (101), (60), (19), (127), (127), (86), (127), (93), (131), (34), (90), (101), (101), (101), (101), (101), (92), (127), (168), (164), (155), (127), (86), (127), (131), (90), (101), (101), (92), (127), (127), (127), (189), (127), (189), (127), (164), (155), (164), (185), (127), (164), (165), (186), (155), (26), (127), (127), (131), (151), (5), (141), (17), (101), (92), (127), (62), (127), (127), (18), (127), (62), (127), (155), (8), (127), (185), (185), (186), (127), (164), (188), (147), (91), (186), (117), (127), (164), (185), (185), (120), (127), (62), (127), (26), (186), (83), (127), (34), (131), (101), (101), (92), (127), (155), (155), (26), (145), (116), (81), (8), (127), (127), (127), (8), (8), (40), (127), (127), (155), (120), (127), (155), (155), (77), (75), (161), (127), (86), (127), (189), (127), (127), (120), (8), (127), (131), (34), (101), (101), (101), (92), (127), (127), (127), (189), (127), (127), (160), (8), (127), (168), (26), (155), (127), (164), (185), (155), (120), (127), (127), (93), (131), (101), (101), (92), (127), (62), (127), (164), (164), (185), (7), (185), (127), (189), (127), (18), (127), (164), (185), (155), (26), (120), (127), (131), (101), (101), (92), (127), (185), (7), (120), (127), (155), (127), (131), (90), (101), (101), (60), (19), (127), (86), (127), (189), (127), (173), (155), (8), (127), (8), (8), (8), (127), (189), (127), (26), (127), (131), (101), (101), (92), (127), (185), (22), (95), (59) }; t.n = 403; return t end)(), {}, (function() local t = { (0), (0), (0), (10), (0), (0), (9), (0), (0), (28), (29), (29), (29), (28), (28), (0), (0), (14), (0), (0), (0), (0), (0), (179), (13), (192), (1), (18), (0), (6), (0), (38), (0), (0), (38), (36), (37), (38), (146), (233), (0), (38), (38), (38), (0), (0), (205), (0), (4), (0), (0), (0), (0), (1), (0), (1), (0), (0), (0), (0), (0), (0), (0), (0), (0), (14), (9), (0), (0), (0), (161), (54), (200), (1), (7), (0), (0), (1), (0), (0), (38), (32), (32), (38), (0), (0), (6), (0), (1), (10), (0), (7), (1), (10), (0), (0), (0), (0), (0), (4), (5), (7), (0), (0), (7), (8), (10), (0), (1), (7), (0), (4), (0), (7), (0), (13), (0), (9), (0), (0), (4), (1), (0), (0), (0), (0), (6), (0), (0), (0), (14), (0), (0), (1), (155), (98), (92), (178), (215), (222), (92), (0), (0), (0), (5), (6), (10), (0), (1), (14), (1), (14), (0), (0), (0), (13), (0), (0), (0), (8), (0), (13), (0), (0), (174), (0), (0), (9), (0), (2), (0), (0), (9), (0), (17), (0), (3), (0), (0), (4), (0), (38), (0), (36), (37), (38), (164), (55), (0), (0), (9), (0), (0), (38), (0), (32), (32), (36), (38), (37), (38), (0), (0), (0), (0), (1), (0), (12), (0), (38), (32), (32), (38), (0), (0), (0), (0), (9), (0), (9), (0), (0), (1), (0), (1), (0), (0), (5), (0), (1), (10), (0), (0), (28), (29), (29), (29), (500), (28), (0), (0), (7), (0), (0), (241), (0), (13), (0), (1), (0), (0), (13), (11), (0), (0), (0), (20), (11), (46), (0), (11), (0), (0), (8), (9), (14), (0), (9), (0), (15), (0), (0), (0), (0), (38), (36), (38), (0), (0), (1), (1), (11), (760), (13), (11), (0), (0), (0), (0), (0), (0), (10), (0), (0), (1), (10), (0), (1), (1), (169), (76), (233), (0), (3), (0), (13), (0), (0), (4), (0), (0), (38), (0), (36), (38), (38), (0), (0), (0), (0), (17), (0), (0), (108), (0), (0), (0), (4), (1), (0), (0), (13), (1), (18), (0), (0), (0), (38), (37), (38), (0), (0), (9), (0), (0), (0), (1), (0), (8), (0), (7), (0), (115), (0), (0), (2), (1), (10), (8), (0), (38), (38), (38), (0), (0), (8), (0), (14), (0), (1), (0), (38), (32), (32), (38), (91), (25), (0), (3), (0), (13), (0), (4), (1), (0), (0), (0), (0), (0), (0), (6), (0), (4), (0), (38), (38), (38), (0), (0), (1), (2), (0), (0) }; t.n = 403; return t end)(), (function() local t = { (nil), (108), (nil), (nil), (nil), (nil), (97), (nil), (nil), (nil), (376), (nil), (-30106), (nil), (98), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (159), (159), (159), (52), (nil), (nil), (nil), (nil), (240), (233), (nil), (nil), (nil), (nil), (nil), (106), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (58), (231), (62), (nil), (113), (nil), (nil), (nil), (nil), (nil), (52), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (252), (59), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (39), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (90), (nil), (nil), (nil), (nil), (97), (nil), (216), (108), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (104), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (251), (nil), (90), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (119), (nil), (nil), (nil), (nil), (nil), (106), (nil), (nil), (nil), (nil), (nil), (nil), (231), (231), (336), (nil), (nil), (nil), (nil), (205), (nil), (nil), (nil), (nil), (nil), (133), (133), (133), (133), (97), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (109), (294), (nil), (nil), (nil), (nil), (104), (nil), (109), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (166), (nil), (-5100), (nil), (179), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (109), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Connected"), (nil), (nil), ("Disconnect"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (64), (293), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (375), (83), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (2), (nil), (65), (nil), (85), (nil), (nil), (nil), (65), (nil), (nil), (nil), (222), (222), (308), (nil), (nil), (nil), (nil), (182), (nil), (nil), (nil), (113), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (381), (70), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (113), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (357), (154), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (11), (289), (nil), (nil), (nil), (119), (nil), (168), (nil), (nil), (nil), (105), (nil), (96), (192), (17), (nil), (105), (nil), (nil), (nil), (nil), (271), (323) }; t.n = 397; return t end)(), (function() local t = { (0), (12), (13), (0), (0), (0), (190), (0), (0), (0), (341), (928), (29), (27), (1057), (30), (0), (0), (0), (0), (0), (0), (18), (169), (249), (74), (188), (0), (0), (6), (0), (0), (0), (36), (51), (115), (32), (452), (38), (3), (0), (0), (422), (1026), (38), (0), (53), (0), (0), (3), (0), (0), (4), (996), (6), (0), (0), (0), (0), (0), (0), (0), (14), (15), (16), (0), (172), (0), (0), (0), (123), (6), (213), (84), (1), (0), (4), (825), (6), (0), (0), (0), (8), (387), (38), (0), (33), (0), (128), (5), (10), (0), (128), (0), (9), (0), (0), (0), (7), (0), (0), (0), (0), (10), (0), (0), (0), (0), (84), (1), (7), (0), (0), (0), (0), (6), (0), (217), (0), (0), (0), (42), (6), (0), (7), (8), (0), (14), (15), (16), (0), (0), (14), (61), (136), (16), (106), (142), (198), (185), (119), (0), (9), (10), (0), (0), (0), (0), (97), (1), (97), (1), (0), (0), (0), (246), (0), (9), (10), (0), (0), (898), (0), (0), (14), (0), (0), (52), (0), (0), (3), (0), (30), (0), (23), (0), (378), (0), (0), (0), (36), (0), (0), (4), (115), (662), (38), (189), (0), (0), (97), (0), (0), (0), (36), (0), (339), (16), (32), (32), (464), (38), (0), (0), (14), (692), (0), (292), (0), (0), (0), (603), (1006), (38), (0), (0), (0), (267), (0), (117), (0), (4), (107), (6), (0), (0), (10), (6), (0), (128), (5), (0), (0), (0), (324), (1047), (29), (28), (509), (30), (0), (527), (0), (0), (4), (0), (940), (0), (42), (9), (0), (0), (0), (0), (0), (13), (14), (175), (119), (0), (13), (0), (14), (0), (0), (0), (0), (82), (0), (11), (0), (0), (0), (36), (0), (85), (176), (38), (0), (118), (897), (1), (11), (35), (0), (12), (0), (0), (0), (11), (12), (0), (0), (0), (128), (0), (0), (42), (42), (204), (10), (195), (0), (176), (0), (155), (0), (0), (0), (3), (0), (0), (36), (71), (32), (631), (38), (0), (0), (0), (251), (0), (0), (241), (9), (0), (0), (1), (42), (0), (18), (0), (42), (0), (0), (0), (0), (0), (612), (270), (38), (0), (3), (0), (14), (15), (0), (0), (0), (0), (244), (0), (10), (0), (8), (0), (430), (1), (0), (0), (0), (115), (208), (38), (0), (0), (0), (0), (0), (111), (0), (0), (0), (822), (481), (38), (67), (0), (303), (0), (305), (0), (0), (42), (6), (0), (4), (5), (6), (0), (86), (0), (1), (0), (0), (16), (478), (38), (0), (0), (6), (4), (0) }; t.n = 403; return t end)(), 0, (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (7), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (229), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Connect") }; t.n = 283; return t end)())), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (106), (1771), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (40), (nil), (nil), (nil), (nil), (nil), (380), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (3), (nil), (nil), (nil), (nil), (nil), (70), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (393), (12298), (nil), (nil), (3788), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (103), (0), (2287), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (8), (9), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (99), (109), (774), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (73), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (467), (13083), (nil), (nil), (4446), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (102), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (435), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (90), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (373), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (nil), (-1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (72), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (17561), (nil), (nil), (1939), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (745400572), (1531529179), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (186), (2131), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (94), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (207), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (22282), (nil), (nil), (2927), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (26320), (nil), (nil), (3584), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (94), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (-5521460872), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (table.pack(table.pack(table.pack(1, 1), table.pack(10, 0), table.pack(6, 1), table.pack(11, 0), table.pack(48, 0), table.pack(17, 0), table.pack(14, 1), table.pack(15, 0), table.pack(16, 0), table.pack(60, 0)), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (127), (167), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (78), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (5), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (19), (16), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (149), (822), (nil), (nil), (340), (nil), (nil), (nil), (nil), (141), (169), (nil), (nil), (nil), (nil), (nil), (0), (58), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (4), (0), (335), (nil), (nil), (nil), (nil), (0), (205), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (1), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (20), (299), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (nil), (1), (1), (nil), (nil), (nil), (7), (305), (nil), (nil), (nil), (nil), (nil), (60), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (185), (63), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (62), (nil), (nil), (132), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (353), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (30), (31), (100), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (11), (323), (nil), (nil), (nil), (nil), (0), (185), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (132), (nil), (nil), (nil), (nil), (17), (nil), (nil), (nil), (nil), (6), (340), (nil), (nil), (nil), (nil), (nil), (nil), (132), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (1), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (132), (table.pack(table.pack(table.pack(7, 0)), {}, 3, table.pack(5, 0, 1, 1, 266, 1), table.pack(127, 58, 142, 59, 187, 127), {}, table.pack(0, 1, 0, 0, 316, 0), {}, table.pack(0, 0, 0, 0, 85, 0), 0, {})), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (7), (4) }; t.n = 375; return t end)(), 40, (function() local t = { (46), (4), (0), (230), (7), (19), (32), (741), (267), (167), (323), (202), (6), (4), (0), (221), (22), (340), (17), (332), (21), (353), (9), (20), (102), (151), (21), (155), (1), (0), (0), (439), (115), (32), (167), (9), (15), (16), (0), (142), (6), (223), (58), (314), (339), (35), (185), (5), (195), (9), (20), (21), (88), (1034), (198), (4), (669), (96), (0), (197), (4), (0), (253), (307), (218), (335), (169), (0), (176), (272), (240), (94), (0), (1), (4), (0), (66), (710), (180), (38), (0), (0), (54), (54), (108), (32), (16), (63), (0), (176), (643), (283), (117), (20), (299), (100), (16), (98), (346), (49), (0), (301), (30), (451), (30), (396), (22), (316), (0), (0), (314), (331), (32), (85), (169), (38), (0), (1043), (323), (32), (58), (0), (3), (195), (0), (38), (6), (6), (13), (32), (335), (38), (0), (876), (1049), (32), (205), (21), (0), (67), (202), (42), (14), (152), (100), (61), (846), (78), (67), (4), (7), (8), (9), (17), (314), (0), (9), (20), (137), (337), (681), (200), (0), (319), (938), (32), (299), (445), (45), (5), (7), (89), (89), (149), (19), (0), (0), (2), (386), (140), (518), (7), (314), (0), (42), (0), (2), (3), (226), (38), (0), (863), (193), (32), (305), (0), (269), (72), (77), (65), (32), (67), (32), (38), (267), (61), (232), (4), (0), (219), (0), (0), (38), (869), (869), (1042), (32), (63), (10), (5), (74), (93), (337), (125), (8), (348), (4), (5), (277), (368), (32), (238), (233), (9), (20), (21), (0), (67), (897), (337), (42), (174), (11), (12), (0), (121), (9), (20), (51), (65), (21), (0), (42), (26), (314), (9), (20), (21), (183), (305), (0), (0), (605), (363), (32), (150), (353), (399), (11), (0), (4), (207), (38), (0), (0), (27), (1034), (527), (32), (14), (100), (2), (60), (9), (20), (21), (0), (67), (0), (686), (50), (32), (323), (38), (0), (316), (58), (32), (185), (255), (101), (246), (32), (875), (267), (848), (345), (3), (11), (12), (3), (4), (47), (314), (53), (92), (340), (0), (38), (28), (1019), (32), (340), (1), (11), (200), (111), (12), (0), (2), (10), (242), (4), (0), (18), (3), (28), (479), (55), (281), (11), (12), (13), (70), (267), (99), (6), (13), (4), (0), (159), (492), (70), (61), (11), (7), (13), (89), (89), (0), (0), (8), (8), (12), (13), (0), (11), (313), (245), (96), (195), (205), (0), (4), (57), (32), (139), (4) }; t.n = 378; return t end)(), (function() local t = { (127), (164), (55), (127), (39), (127), (141), (8), (127), (127), (127), (107), (127), (164), (55), (127), (127), (127), (127), (127), (127), (127), (164), (160), (67), (91), (185), (127), (127), (131), (90), (101), (101), (92), (127), (164), (185), (185), (120), (127), (86), (127), (127), (62), (127), (127), (127), (185), (127), (164), (185), (185), (127), (189), (127), (127), (86), (127), (18), (127), (164), (55), (127), (107), (127), (127), (127), (18), (127), (31), (62), (127), (168), (59), (164), (55), (127), (189), (127), (93), (34), (131), (101), (101), (101), (92), (127), (127), (120), (127), (86), (127), (189), (127), (127), (127), (127), (86), (127), (127), (131), (151), (5), (141), (17), (101), (92), (127), (131), (90), (101), (101), (60), (19), (127), (93), (131), (101), (101), (92), (127), (181), (185), (127), (131), (93), (101), (101), (101), (92), (127), (93), (131), (101), (101), (92), (127), (185), (120), (127), (8), (40), (155), (77), (75), (161), (8), (8), (40), (126), (155), (155), (155), (8), (127), (120), (164), (185), (127), (127), (86), (127), (131), (101), (101), (92), (127), (86), (127), (164), (185), (141), (29), (127), (185), (65), (168), (8), (8), (127), (8), (155), (127), (120), (127), (58), (155), (155), (127), (93), (131), (101), (101), (92), (127), (18), (127), (127), (62), (127), (141), (127), (141), (8), (127), (86), (127), (164), (55), (127), (90), (131), (93), (101), (101), (101), (92), (127), (127), (39), (127), (8), (127), (8), (39), (127), (155), (155), (8), (127), (141), (127), (127), (164), (185), (185), (120), (127), (8), (127), (62), (127), (185), (155), (81), (127), (164), (160), (67), (91), (185), (120), (127), (8), (127), (164), (185), (185), (127), (127), (34), (131), (101), (101), (60), (19), (127), (169), (127), (168), (39), (127), (93), (34), (131), (101), (101), (101), (60), (19), (127), (39), (127), (164), (185), (185), (120), (127), (131), (101), (101), (92), (127), (93), (131), (101), (101), (92), (127), (127), (189), (127), (141), (8), (127), (86), (127), (164), (185), (155), (22), (185), (127), (127), (62), (127), (127), (131), (93), (101), (101), (92), (127), (164), (160), (67), (91), (155), (81), (185), (195), (127), (164), (55), (127), (39), (127), (86), (127), (127), (155), (155), (155), (8), (127), (127), (39), (127), (164), (55), (127), (189), (127), (8), (195), (164), (185), (141), (29), (22), (23), (185), (164), (185), (155), (116), (112), (127), (8), (8), (40), (127), (131), (101), (101), (60), (19), (127) }; t.n = 378; return t end)(), {}, (function() local t = { (0), (0), (11), (0), (18), (0), (6), (0), (0), (0), (0), (834), (0), (0), (11), (0), (0), (0), (0), (0), (0), (0), (0), (147), (8), (59), (7), (0), (0), (39), (33), (33), (39), (0), (0), (0), (2), (3), (14), (0), (10), (0), (0), (10), (0), (0), (0), (11), (0), (0), (9), (12), (0), (10), (0), (0), (18), (0), (300), (0), (0), (11), (0), (1042), (0), (0), (0), (371), (0), (177), (18), (0), (0), (0), (0), (6), (0), (10), (0), (0), (0), (39), (38), (37), (39), (0), (0), (0), (19), (0), (18), (0), (10), (0), (0), (0), (0), (10), (0), (0), (29), (30), (30), (30), (694), (29), (0), (0), (39), (33), (33), (39), (165), (246), (0), (0), (39), (38), (39), (0), (0), (10), (10), (0), (39), (0), (39), (38), (39), (0), (0), (0), (39), (38), (39), (0), (0), (9), (19), (0), (0), (15), (0), (178), (217), (218), (0), (0), (15), (0), (0), (0), (0), (0), (0), (19), (0), (11), (0), (0), (18), (0), (39), (39), (39), (0), (0), (10), (0), (0), (1), (4), (5), (0), (11), (0), (0), (0), (0), (0), (0), (0), (0), (19), (0), (1), (0), (0), (0), (0), (39), (38), (39), (0), (0), (87), (0), (0), (10), (0), (7), (0), (2), (0), (0), (18), (0), (0), (6), (0), (33), (39), (0), (38), (33), (39), (0), (0), (0), (66), (0), (0), (0), (0), (159), (0), (0), (0), (0), (0), (3), (0), (0), (0), (3), (6), (19), (0), (0), (0), (18), (0), (1), (0), (10), (0), (0), (216), (12), (86), (13), (19), (0), (0), (0), (0), (13), (14), (0), (0), (0), (39), (37), (39), (95), (46), (0), (10), (0), (0), (219), (0), (0), (0), (39), (38), (37), (39), (141), (40), (0), (253), (0), (0), (6), (8), (19), (0), (39), (39), (39), (0), (0), (0), (39), (38), (39), (0), (0), (0), (18), (0), (8), (0), (0), (18), (0), (0), (1), (0), (3), (10), (0), (0), (10), (0), (0), (39), (0), (38), (39), (0), (0), (0), (235), (1), (159), (0), (10), (10), (2), (0), (0), (11), (0), (230), (0), (10), (0), (0), (0), (0), (0), (0), (0), (0), (221), (0), (0), (11), (0), (18), (0), (0), (6), (0), (1), (4), (5), (4), (0), (11), (0), (1), (0), (14), (4), (0), (0), (0), (6), (0), (39), (39), (39), (167), (151), (0) }; t.n = 378; return t end)(), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (0), (118), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (305), (10), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (2), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (107), (nil), (nil), (485), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (60), (nil), (nil), (nil), (nil), (23), (23), (97), (nil), (nil), (nil), (nil), (nil), (359), (nil), (78), (nil), (nil), (nil), (nil), (111), (nil), (nil), (nil), (166), (nil), (-1125), (nil), (18), (nil), (nil), (nil), (nil), (172), (67), (nil), (nil), (nil), (nil), (nil), (247), (43), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (2), (2), (66), (nil), (nil), (nil), (nil), (234), (372), (nil), (nil), (nil), (nil), (nil), (57), (nil), (nil), (nil), (nil), (107), (614), (126), (nil), (nil), (nil), (nil), (nil), (17), (nil), (nil), (nil), (nil), (nil), (nil), (233), (nil), (nil), (257), (95), (nil), (nil), (93), (nil), (nil), (nil), (1), (1), (nil), (nil), (nil), (nil), (5), (218), (nil), (60), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (201), (260), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (nil), (0), (51), (nil), (107), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (309), (309), (88), (nil), (nil), (nil), (nil), (nil), (2), (nil), (121), (nil), (nil), (nil), (nil), (63), (nil), (0), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (111), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (78), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (355), (22), (nil), (nil), (nil), (51), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (103), (107), (96), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (243), (11), (nil), (nil), (nil), (nil), (227), (47), (nil), (nil), (nil), (62), (nil), (0), (93), (nil), (611), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (7), (317), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (121), (nil), (nil), (nil), (nil), (nil), (36), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (119), (nil), (107), (nil), (nil), (nil), (1), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (88), (25), (nil), (nil), (nil), (5), (56) }; t.n = 375; return t end)(), (function() local t = { (0), (11), (0), (0), (0), (0), (12), (10), (0), (0), (0), (10), (0), (11), (0), (0), (0), (0), (0), (0), (0), (0), (19), (21), (77), (6), (0), (0), (0), (0), (0), (73), (1026), (39), (0), (14), (0), (0), (0), (0), (97), (0), (0), (117), (0), (0), (0), (0), (0), (19), (0), (0), (0), (77), (0), (0), (90), (0), (15), (0), (11), (0), (0), (9), (0), (0), (0), (15), (0), (448), (4), (0), (0), (0), (6), (0), (0), (43), (0), (0), (37), (0), (32), (91), (80), (39), (0), (0), (0), (0), (259), (0), (53), (0), (0), (0), (0), (337), (0), (0), (0), (194), (589), (30), (29), (922), (31), (0), (0), (0), (656), (566), (39), (37), (0), (0), (0), (32), (23), (39), (0), (0), (0), (0), (0), (0), (71), (32), (687), (39), (0), (0), (0), (32), (381), (39), (0), (0), (0), (0), (17), (0), (42), (71), (15), (227), (16), (17), (0), (6), (42), (42), (42), (10), (0), (0), (19), (0), (0), (0), (67), (0), (0), (899), (703), (39), (0), (302), (0), (6), (0), (8), (9), (0), (0), (19), (0), (15), (16), (0), (10), (42), (0), (0), (0), (0), (42), (42), (0), (0), (0), (28), (439), (39), (0), (6), (0), (0), (710), (0), (14), (0), (11), (10), (0), (56), (0), (6), (0), (0), (0), (0), (0), (89), (8), (94), (39), (0), (0), (0), (0), (10), (0), (10), (0), (0), (42), (42), (6), (0), (9), (0), (0), (19), (0), (0), (0), (0), (10), (0), (101), (0), (0), (317), (0), (0), (19), (15), (241), (95), (0), (0), (0), (10), (0), (19), (0), (0), (0), (0), (37), (0), (32), (608), (39), (224), (0), (9), (0), (0), (0), (0), (0), (37), (0), (19), (442), (20), (39), (54), (0), (0), (0), (19), (0), (0), (0), (0), (0), (50), (583), (39), (0), (0), (0), (32), (8), (39), (0), (0), (351), (0), (13), (10), (0), (160), (0), (10), (0), (317), (10), (0), (0), (0), (99), (0), (0), (0), (0), (51), (922), (39), (0), (10), (85), (91), (32), (317), (0), (0), (0), (0), (11), (0), (0), (0), (0), (40), (0), (0), (42), (42), (42), (10), (0), (0), (0), (0), (11), (0), (0), (240), (0), (10), (0), (12), (0), (14), (15), (12), (11), (0), (11), (0), (317), (1), (0), (0), (7), (8), (0), (0), (0), (28), (71), (39), (149), (0) }; t.n = 378; return t end)(), 0, (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (36), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (88), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (342) }; t.n = 105; return t end)())), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (-1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (56), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (120), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (6), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (table.pack(table.pack(table.pack(71, 1), table.pack(1, 1)), table.pack(nil, nil, nil, nil, 167), 3, table.pack(2, 293, 3, 1, 2, 1, 1), table.pack(127, 39, 127, 195, 155, 186, 59), {}, table.pack(0, 504, 0, 0, 1, 0, 0), {}, table.pack(0, 379, 0, 0, 939, 0, 0), 0, {})), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (27260), (nil), (nil), (410), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (185), (114), (3837), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (8), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (21176), (nil), (nil), (3983), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (32), (nil), (nil), (nil), (nil), (nil), (56), (nil), (70), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (113), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (false), (nil), (table.pack(table.pack(table.pack(50, 0)), {}, 7, table.pack(16, 330, 7, 0, 2, 0, 9, 5, 0, 0, 109, 1, 3, 74, 1, 277, 3, 65, 12), table.pack(127, 86, 127, 58, 185, 164, 127, 185, 65, 137, 8, 127, 26, 8, 127, 127, 127, 86, 127), {}, table.pack(0, 4, 0, 1, 1, 0, 0, 3, 0, 2, 0, 0, 2, 0, 0, 183, 0, 4, 0), table.pack(nil, 82, nil, nil, nil, nil, nil, nil, nil, nil, 32, nil, nil, 82, nil, nil, nil, 32), table.pack(0, 17, 0, 0, 0, 3, 0, 0, 5, 2, 4, 0, 3, 4, 0, 48, 0, 1, 0), 0, {})), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (175), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (22), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (76), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (table.pack(table.pack(table.pack(15, 0), table.pack(88, 0), table.pack(94, 1), table.pack(17, 0), table.pack(49, 0)), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (7), (10), (50), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (0), (101), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (6), (2), (185), (256), (nil), (nil), (nil), (nil), (nil), (nil), (8), (0), (28), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (9), (12), (147), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (600), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (136), (5), (57), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (nil), (nil), (nil), (5), (87), (nil), (nil), (nil), (nil), (nil), (0), (38), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (2), (195), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (17678), (nil), (nil), (37), (22420), (nil), (nil), (126), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (11), (8), (39) }; t.n = 266; return t end)(), 34, (function() local t = { (52), (256), (126), (117), (501), (251), (238), (62), (9), (89), (244), (32), (0), (808), (1002), (58), (26), (50), (173), (2), (248), (195), (94), (12), (12), (89), (6), (43), (24), (161), (3), (6), (6), (0), (19), (89), (248), (180), (121), (89), (89), (89), (22), (22), (0), (1), (50), (32), (149), (228), (0), (247), (0), (89), (6), (854), (123), (0), (125), (32), (0), (60), (60), (224), (26), (101), (0), (2), (248), (0), (0), (32), (65), (65), (942), (6), (26), (28), (256), (32), (0), (0), (314), (314), (699), (26), (28), (6), (0), (14), (15), (252), (89), (168), (0), (32), (952), (952), (54), (26), (147), (0), (6), (6), (6), (4), (5), (132), (0), (46), (12), (7), (5), (1), (13), (5), (244), (12), (89), (13), (23), (0), (139), (0), (248), (66), (0), (13), (14), (0), (12), (110), (1), (7), (5), (2), (6), (49), (260), (0), (7), (168), (89), (4), (32), (30), (170), (11), (3), (248), (2), (248), (28), (0), (0), (87), (87), (753), (26), (123), (57), (171), (13), (5), (1), (13), (5), (37), (35), (138), (101), (959), (234), (0), (0), (882), (91), (26), (87), (1), (0), (0), (3), (447), (26), (179), (38), (0), (0), (0), (233), (152), (224), (89), (121), (778), (179), (12), (108), (89), (92), (8), (89), (9), (6), (10), (11), (23), (120), (226), (2), (129), (69), (11), (11), (108), (32), (0), (27), (363), (26), (195), (92), (197), (26), (87), (999), (152), (0), (59), (241), (62), (2), (193), (24), (157), (24), (136), (24), (791), (24), (62), (16), (126), (57), (362), (47), (44), (62), (1), (62), (46), (0), (13), (13), (162), (0), (5), (89), (142), (32), (0), (0), (431), (431), (412), (26), (0), (39), (319) }; t.n = 270; return t end)(), (function() local t = { (127), (127), (127), (127), (8), (77), (75), (161), (185), (8), (40), (93), (131), (101), (101), (101), (92), (127), (127), (185), (127), (127), (127), (74), (158), (141), (141), (127), (39), (127), (164), (185), (8), (81), (127), (117), (127), (127), (127), (8), (8), (29), (127), (127), (168), (59), (127), (86), (127), (127), (18), (127), (58), (117), (117), (86), (127), (18), (127), (93), (131), (101), (101), (101), (92), (127), (168), (185), (127), (90), (131), (93), (101), (101), (101), (101), (60), (19), (127), (93), (131), (90), (101), (101), (101), (92), (127), (29), (164), (185), (185), (127), (29), (127), (131), (93), (101), (101), (101), (92), (127), (164), (185), (8), (8), (126), (136), (127), (158), (127), (113), (74), (136), (164), (47), (182), (127), (26), (141), (26), (127), (18), (127), (137), (127), (127), (164), (185), (185), (81), (52), (127), (164), (47), (182), (42), (122), (127), (127), (168), (42), (127), (8), (126), (183), (32), (127), (35), (127), (127), (12), (127), (127), (131), (90), (101), (101), (101), (60), (19), (127), (127), (158), (136), (164), (47), (182), (127), (62), (127), (127), (8), (127), (34), (131), (101), (101), (92), (127), (127), (131), (34), (101), (101), (60), (19), (127), (131), (34), (90), (20), (32), (127), (8), (40), (86), (127), (26), (158), (141), (127), (26), (141), (26), (141), (26), (26), (157), (177), (178), (144), (2), (69), (163), (26), (127), (93), (131), (101), (101), (92), (127), (80), (127), (77), (75), (161), (127), (88), (77), (75), (161), (42), (127), (5), (141), (17), (151), (5), (141), (17), (101), (92), (127), (127), (86), (127), (127), (8), (42), (8), (40), (81), (52), (113), (127), (164), (185), (8), (127), (93), (34), (131), (101), (101), (101), (60), (19), (127), (52) }; t.n = 270; return t end)(), {}, (function() local t = { (0), (0), (0), (0), (0), (246), (19), (103), (6), (0), (8), (0), (33), (32), (32), (33), (0), (0), (0), (5), (0), (0), (0), (13), (9), (9), (10), (0), (234), (0), (0), (2), (0), (5), (0), (7), (0), (0), (0), (0), (0), (201), (0), (0), (0), (0), (0), (2), (0), (0), (201), (0), (1), (1), (1), (3), (0), (2), (0), (0), (33), (33), (32), (33), (0), (0), (0), (7), (0), (27), (33), (0), (33), (32), (27), (33), (118), (71), (0), (0), (33), (27), (27), (32), (33), (0), (0), (11), (0), (2), (11), (0), (9), (0), (33), (0), (32), (33), (33), (0), (0), (0), (2), (0), (0), (0), (933), (0), (9), (0), (2), (12), (933), (0), (12), (104), (0), (10), (10), (13), (0), (18), (0), (2), (0), (0), (0), (2), (11), (12), (12), (0), (0), (6), (104), (0), (4), (0), (0), (0), (0), (0), (0), (0), (4), (4), (0), (10), (0), (0), (0), (0), (0), (33), (27), (27), (33), (33), (38), (44), (0), (0), (12), (933), (0), (12), (104), (0), (8), (0), (0), (0), (0), (0), (33), (31), (33), (0), (0), (0), (33), (0), (31), (33), (26), (211), (0), (23), (0), (17), (143), (24), (0), (0), (8), (3), (0), (10), (146), (9), (0), (7), (7), (9), (7), (10), (10), (39), (203), (9), (42), (48), (52), (10), (11), (0), (0), (33), (32), (33), (0), (0), (10), (0), (174), (215), (14), (0), (7), (107), (63), (234), (0), (0), (24), (24), (1038), (24), (24), (24), (1038), (23), (0), (0), (0), (3), (0), (0), (0), (0), (0), (4), (13), (13), (2), (0), (0), (2), (0), (0), (0), (0), (33), (31), (32), (33), (64), (173), (0), (366) }; t.n = 270; return t end)(), (function() local t = { (nil), (nil), (nil), (nil), (""), (nil), (nil), (3), (nil), (1), (nil), (nil), (nil), (202), (207), (47), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (2), (nil), (nil), (nil), (nil), (nil), (2), (nil), (nil), (1), (nil), (nil), (nil), (1), (1), (1), (nil), (nil), (nil), (nil), (nil), (0), (nil), (nil), (nil), (nil), (nil), (1), (2), ("boolean"), (nil), (nil), (nil), (nil), (nil), (133), (133), (171), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (32), (32), (258), (2), (nil), (nil), (nil), (nil), (nil), (nil), (172), (172), (153), (nil), (nil), (2), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (199), (199), (23), (nil), (nil), (nil), (nil), (2), (2), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (0), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (113), (113), (245), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (462), (nil), (nil), (nil), (254), (19), (nil), (nil), (nil), (nil), (nil), (39), (38), (nil), (nil), (nil), (nil), (nil), (nil), (495), (nil), (nil), (1), (nil), ("string"), (nil), (nil), (nil), (1), (nil), (nil), (1), (nil), (2), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (103), (22), (nil), (nil), (nil), (nil), (nil), (nil), (248), (nil), (nil), (nil), (nil), (3), (nil), (nil), (nil), (-18133), (nil), (201), (nil), (-22584), (nil), (3), (nil), (nil), (nil), ("number"), (nil), (nil), (3), (nil), (3), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (nil), (42), (42), (139) }; t.n = 266; return t end)(), (function() local t = { (0), (0), (0), (0), (7), (200), (8), (237), (0), (10), (0), (0), (0), (28), (115), (5), (33), (0), (0), (0), (0), (0), (0), (12), (7), (9), (10), (0), (0), (0), (5), (0), (7), (0), (0), (2), (0), (0), (6), (9), (10), (81), (0), (0), (0), (0), (0), (150), (0), (0), (4), (0), (0), (2), (3), (21), (0), (8), (0), (0), (0), (89), (32), (47), (33), (0), (0), (0), (0), (0), (0), (0), (51), (6), (8), (104), (33), (124), (0), (0), (0), (0), (55), (32), (7), (33), (0), (12), (13), (0), (0), (0), (8), (0), (0), (0), (43), (105), (842), (33), (0), (5), (0), (7), (8), (5), (6), (0), (11), (0), (12), (7), (12), (13), (12), (12), (0), (7), (13), (7), (0), (8), (0), (2), (0), (0), (12), (0), (0), (0), (5), (0), (7), (6), (6), (6), (1070), (0), (0), (0), (8), (0), (7), (4), (4), (0), (0), (222), (0), (0), (2), (0), (0), (0), (0), (614), (4), (891), (33), (41), (0), (0), (7), (12), (13), (12), (12), (0), (89), (0), (0), (24), (0), (31), (0), (4), (629), (33), (0), (0), (0), (31), (32), (447), (33), (89), (0), (0), (21), (0), (24), (0), (0), (10), (0), (245), (0), (7), (7), (9), (0), (1), (9), (1), (10), (1), (8), (11), (196), (112), (15), (11), (205), (4), (8), (0), (0), (0), (6), (713), (33), (0), (8), (0), (74), (24), (244), (0), (0), (60), (8), (221), (9), (0), (851), (24), (21), (790), (351), (24), (17), (168), (25), (0), (0), (248), (0), (0), (4), (5), (6), (0), (0), (8), (13), (0), (4), (0), (6), (0), (0), (31), (0), (50), (55), (3), (33), (133), (0), (12) }; t.n = 270; return t end)(), 0, (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (209), (nil), (nil), (nil), (nil), (nil), (209), (nil), (nil), (256), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (256), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (209), (nil), (nil), (256), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (475), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (112), (nil), (nil), (nil), (112) }; t.n = 241; return t end)())), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (61) }; t.n = 4592; return t end)(), 140, (function() local t = { (1122), (513), (120), (2496), (102), (0), (0), (35), (0), (2946), (1399), (2095), (98), (4581), (0), (0), (0), (528), (528), (528), (976), (132), (4337), (103), (104), (3), (3471), (3942), (2841), (4), (3868), (3422), (2476), (4020), (32), (176), (89), (2160), (105), (106), (0), (106), (105), (3616), (0), (0), (251), (130), (672), (130), (440), (122), (2661), (98), (0), (0), (14), (0), (1840), (90), (91), (0), (92), (0), (2743), (89), (32), (148), (5), (114), (32), (1012), (304), (4365), (375), (1177), (423), (2873), (84), (101), (2870), (0), (4280), (786), (3608), (0), (77), (78), (823), (0), (61), (3587), (0), (42), (240), (1202), (114), (2054), (102), (0), (0), (93), (0), (3684), (2), (113), (107), (108), (109), (4065), (98), (0), (0), (35), (0), (1307), (46), (98), (34), (4260), (107), (3189), (1202), (69), (0), (2946), (770), (81), (225), (103), (3371), (984), (179), (0), (98), (3224), (3), (3675), (900), (3231), (433), (2414), (11), (1351), (87), (2922), (0), (1618), (0), (103), (104), (105), (107), (0), (0), (609), (1184), (399), (1999), (130), (3747), (2129), (1690), (0), (0), (174), (763), (18), (130), (225), (130), (690), (122), (697), (188), (825), (103), (104), (84), (864), (93), (0), (81), (510), (68), (2395), (99), (138), (93), (32), (876), (33), (1193), (3729), (95), (264), (1043), (4361), (410), (3586), (2689), (101), (102), (4363), (0), (42), (42), (522), (614), (4522), (104), (565), (0), (103), (2230), (67), (11), (17), (2243), (2316), (931), (983), (107), (32), (3590), (2695), (1904), (3087), (104), (104), (102), (78), (1093), (28), (32), (71), (4408), (99), (99), (99), (2862), (130), (253), (130), (261), (122), (3223), (0), (86), (0), (26), (147), (97), (3276), (42), (114), (42), (145), (42), (42), (56), (2225), (6), (4493), (0), (3917), (78), (827), (121), (3495), (31), (25), (225), (5), (4119), (3855), (144), (1624), (53), (2757), (116), (32), (62), (32), (2462), (42), (35), (3198), (482), (1991), (46), (78), (49), (4335), (2411), (2573), (77), (78), (335), (2911), (6), (4576), (110), (3728), (32), (51), (0), (0), (112), (113), (32), (62), (388), (660), (5), (114), (4109), (0), (1527), (99), (3589), (0), (64), (0), (119), (962), (718), (4245), (138), (0), (383), (383), (963), (132), (1674), (86), (85), (85), (86), (85), (3053), (0), (3842), (896), (17), (14), (1948), (705), (4215), (632), (185), (32), (2552), (104), (105), (954), (2716), (42), (42), (100), (2243), (3837), (101), (102), (103), (1362), (100), (101), (42), (81), (2770), (30), (1101), (0), (1562), (90), (0), (90), (85), (198), (169), (4381), (4236), (4225), (80), (81), (554), (0), (875), (3154), (132), (113), (905), (3739), (98), (0), (0), (14), (0), (2530), (93), (94), (93), (1459), (105), (0), (4350), (104), (0), (2597), (82), (432), (98), (0), (0), (10), (0), (53), (689), (1891), (3291), (377), (3026), (0), (75), (1791), (97), (104), (105), (2406), (4139), (3713), (4494), (4118), (3599), (59), (346), (2697), (1034), (2967), (1983), (111), (112), (111), (111), (111), (4418), (0), (0), (31), (130), (191), (130), (971), (122), (935), (0), (103), (156), (79), (104), (0), (0), (506), (38), (0), (9), (63), (0), (4548), (18), (39), (64), (2225), (2132), (83), (84), (953), (0), (692), (3632), (3788), (1413), (2694), (0), (0), (815), (664), (132), (2171), (102), (0), (0), (112), (0), (3276), (1748), (147), (490), (138), (745), (829), (0), (63), (0), (2299), (0), (1900), (1756), (3658), (64), (103), (225), (791), (4403), (0), (95), (96), (42), (4135), (54), (1089), (786), (999), (0), (0), (113), (107), (173), (114), (349), (89), (3398), (98), (0), (0), (1777), (4209), (384), (0), (948), (0), (22), (305), (343), (99), (1585), (0), (2770), (351), (448), (76), (77), (74), (1630), (95), (101), (102), (507), (1025), (4), (271), (146), (676), (3534), (80), (81), (132), (0), (107), (1176), (1642), (2596), (40), (918), (109), (888), (26), (807), (98), (0), (0), (10), (0), (394), (299), (1538), (828), (2919), (142), (235), (4), (937), (0), (0), (112), (3178), (590), (110), (104), (906), (0), (3718), (99), (100), (12), (0), (114), (3107), (0), (111), (4335), (0), (1038), (113), (125), (114), (21), (114), (113), (2100), (3), (0), (2722), (0), (138), (0), (661), (661), (661), (169), (132), (240), (1867), (94), (95), (94), (124), (1874), (102), (0), (0), (76), (0), (4012), (263), (4), (732), (0), (3204), (417), (266), (73), (74), (740), (0), (0), (3954), (75), (76), (573), (0), (42), (95), (4266), (139), (38), (174), (397), (299), (105), (153), (106), (981), (0), (4345), (106), (153), (196), (107), (108), (107), (1988), (102), (0), (0), (31), (2981), (0), (0), (112), (0), (2506), (17), (18), (44), (3311), (751), (42), (42), (3400), (98), (0), (0), (95), (1154), (0), (42), (124), (302), (107), (623), (0), (104), (68), (107), (108), (4370), (125), (825), (111), (89), (3449), (3469), (439), (2262), (98), (10), (612), (3481), (35), (1728), (99), (99), (99), (99), (102), (99), (104), (612), (0), (1326), (145), (2559), (0), (0), (31), (3691), (0), (0), (774), (256), (132), (924), (0), (98), (740), (3276), (748), (56), (56), (4022), (113), (0), (2395), (75), (76), (794), (0), (75), (76), (81), (0), (4243), (102), (99), (102), (4131), (0), (0), (1029), (130), (636), (130), (957), (122), (1520), (0), (42), (357), (1864), (93), (94), (42), (13), (93), (4047), (106), (1075), (551), (1694), (101), (0), (726), (2349), (4029), (2359), (130), (916), (130), (1050), (122), (28), (2965), (105), (1048), (106), (1048), (0), (105), (393), (106), (2407), (1305), (2702), (0), (1067), (41), (1785), (1008), (77), (78), (2), (0), (827), (0), (0), (103), (130), (1036), (130), (863), (122), (2689), (1674), (102), (0), (0), (1715), (76), (77), (123), (0), (76), (77), (121), (0), (2632), (0), (0), (334), (398), (132), (4420), (105), (0), (1305), (1158), (2547), (2475), (2659), (1), (102), (0), (0), (762), (0), (4443), (0), (0), (97), (2451), (1859), (0), (0), (42), (42), (1713), (330), (4452), (92), (93), (92), (92), (93), (3333), (49), (3632), (83), (84), (987), (0), (83), (4535), (55), (1570), (240), (4414), (102), (0), (0), (1661), (104), (84), (105), (2501), (130), (278), (0), (75), (2301), (0), (18), (3514), (42), (39), (370), (123), (4178), (5), (1358), (0), (103), (103), (1755), (900), (28), (781), (0), (1093), (225), (4444), (327), (0), (111), (96), (155), (3274), (162), (1114), (2161), (0), (999), (130), (856), (130), (994), (122), (1226), (0), (873), (127), (99), (99), (42), (290), (0), (0), (95), (541), (80), (81), (75), (0), (38), (3154), (93), (63), (111), (76), (111), (264), (0), (39), (202), (2418), (1342), (673), (786), (3597), (107), (108), (109), (3013), (3313), (106), (107), (107), (4293), (959), (142), (161), (1166), (42), (42), (126), (3597), (1236), (745), (3779), (0), (88), (2367), (3104), (44), (10), (357), (715), (103), (104), (4126), (859), (0), (69), (982), (923), (104), (104), (1664), (0), (105), (125), (3642), (102), (0), (0), (67), (1555), (0), (100), (404), (3059), (106), (90), (2082), (837), (3610), (75), (34), (97), (2989), (110), (125), (111), (110), (3671), (102), (103), (102), (102), (570), (104), (105), (4316), (0), (93), (138), (0), (70), (577), (709), (4511), (783), (33), (2479), (4187), (3002), (90), (91), (90), (862), (906), (102), (0), (0), (95), (0), (3186), (3910), (67), (105), (105), (3691), (527), (3352), (168), (2991), (130), (4395), (37), (1184), (124), (79), (970), (3910), (0), (0), (881), (130), (424), (130), (457), (122), (1331), (211), (130), (124), (98), (0), (0), (53), (539), (0), (42), (42), (285), (90), (89), (42), (118), (4414), (0), (1294), (500), (21), (108), (107), (107), (347), (0), (2805), (42), (46), (4556), (92), (86), (1273), (403), (12), (3011), (487), (1925), (3772), (4601), (1732), (1791), (118), (1978), (105), (0), (1313), (880), (4027), (101), (2938), (2543), (343), (1422), (14), (63), (2), (6), (42), (0), (42), (2549), (4335), (4), (123), (4386), (0), (0), (76), (2000), (1356), (2628), (0), (128), (142), (968), (178), (916), (2920), (108), (109), (110), (0), (108), (109), (110), (0), (4363), (363), (2916), (68), (3311), (0), (266), (98), (99), (609), (0), (3424), (4226), (188), (317), (103), (104), (103), (301), (1388), (4139), (69), (0), (913), (2397), (3440), (4232), (114), (113), (0), (3449), (1967), (2507), (1227), (2661), (3545), (4539), (4116), (2831), (101), (99), (99), (101), (99), (732), (102), (0), (0), (92), (2656), (185), (5), (112), (32), (89), (32), (28), (3270), (0), (0), (130), (1914), (2386), (4613), (2515), (93), (94), (93), (859), (2863), (0), (373), (132), (28), (223), (3442), (3411), (102), (0), (0), (86), (0), (1987), (4284), (42), (3489), (967), (1979), (101), (102), (340), (645), (136), (2814), (80), (81), (109), (0), (80), (1909), (31), (533), (573), (2946), (0), (2669), (98), (0), (0), (3171), (149), (3764), (0), (42), (76), (2278), (98), (0), (0), (42), (1206), (98), (99), (118), (2908), (0), (100), (101), (46), (3353), (710), (32), (32), (32), (0), (0), (111), (112), (632), (43), (1610), (2973), (2792), (849), (90), (189), (212), (91), (90), (92), (98), (22), (0), (241), (3622), (1559), (1645), (84), (35), (108), (1421), (849), (644), (883), (883), (5), (361), (42), (3), (430), (2977), (1536), (0), (103), (510), (74), (1906), (106), (194), (107), (797), (5), (327), (995), (290), (3778), (845), (102), (801), (119), (119), (402), (0), (96), (42), (42), (107), (2352), (375), (868), (102), (0), (0), (2345), (88), (89), (90), (91), (1010), (53), (15), (225), (29), (196), (130), (865), (130), (1032), (122), (1422), (929), (417), (104), (105), (589), (113), (751), (113), (228), (943), (0), (3501), (42), (42), (42), (276), (569), (2585), (148), (5), (115), (216), (242), (32), (6), (32), (1012), (524), (98), (99), (871), (0), (18), (1293), (617), (116), (23), (3996), (42), (22), (1874), (92), (93), (42), (0), (64), (1202), (960), (1567), (1), (98), (0), (1887), (76), (0), (98), (0), (0), (896), (0), (1301), (612), (555), (0), (138), (1033), (716), (132), (3907), (10), (15), (84), (3311), (98), (12), (98), (603), (42), (42), (42), (42), (42), (42), (42), (42), (42), (2963), (109), (1133), (14), (42), (42), (3714), (0), (0), (530), (549), (132), (1597), (1832), (3180), (0), (89), (35), (531), (3095), (0), (98), (99), (4246), (80), (81), (223), (0), (4238), (2086), (3158), (102), (35), (104), (407), (100), (100), (75), (3107), (3274), (83), (4520), (621), (1415), (98), (99), (0), (2985), (0), (2047), (464), (219), (0), (783), (3127), (0), (2066), (114), (2830), (2171), (42), (953), (1760), (75), (76), (706), (0), (709), (728), (283), (2118), (102), (565), (104), (105), (0), (0), (3398), (99), (42), (290), (0), (0), (96), (3895), (93), (95), (49), (114), (2301), (563), (20), (104), (135), (134), (107), (207), (0), (42), (4357), (73), (117), (456), (32), (62), (5), (113), (32), (65), (3119), (1165), (55), (1289), (551), (799), (434), (4103), (77), (78), (69), (0), (46), (276), (0), (100), (4266), (103), (104), (105), (3265), (77), (78), (44), (0), (1736), (811), (188), (571), (19), (725), (277), (82), (83), (310), (0), (82), (83), (4485), (0), (4125), (94), (95), (0), (1431), (92), (0), (2047), (1013), (0), (230), (104), (104), (894), (0), (230), (104), (2653), (110), (227), (93), (94), (93), (786), (870), (4291), (1892), (98), (0), (0), (3950), (1077), (168), (1566), (122), (16), (9), (3311), (84), (100), (2870), (0), (0), (317), (130), (771), (130), (742), (122), (1033), (345), (2743), (94), (95), (94), (0), (575), (266), (4335), (44), (0), (2047), (102), (0), (0), (770), (0), (3276), (57), (1964), (74), (888), (112), (13), (69), (1510), (0), (98), (0), (4541), (77), (78), (67), (0), (1857), (81), (82), (783), (0), (42), (81), (2976), (92), (93), (92), (265), (122), (57), (1937), (2483), (85), (86), (85), (3774), (3687), (4362), (0), (68), (144), (75), (238), (14), (35), (0), (701), (106), (107), (108), (109), (744), (3907), (76), (0), (98), (4593), (1033), (103), (42), (1760), (1637), (474), (95), (96), (46), (515), (464), (76), (0), (104), (104), (103), (89), (3881), (444), (40), (12), (2225), (102), (0), (0), (17), (0), (102), (0), (0), (10), (0), (175), (1531), (104), (825), (106), (107), (3627), (105), (106), (42), (4089), (445), (1051), (0), (0), (506), (634), (132), (1732), (4311), (98), (4), (151), (123), (138), (2195), (1405), (98), (0), (95), (231), (133), (30), (182), (182), (0), (2), (0), (98), (0), (247), (111), (110), (1824), (97), (276), (874), (2451), (0), (276), (1093), (623), (114), (612), (104), (344), (105), (104), (317), (297), (3758), (20), (1657), (200), (3039), (128), (0), (607), (130), (201), (130), (400), (122), (2619), (0), (92), (0), (4591), (2278), (215), (1387), (0), (0), (1131), (56), (709), (4266), (0), (0), (692), (2683), (36), (2688), (1562), (1202), (1597), (81), (18), (0), (741), (3154), (130), (1549), (3300), (3294), (81), (105), (1028), (105), (3691), (503), (3476), (100), (66), (161), (106), (12), (2837), (66), (2890), (280), (2763), (0), (3191), (2863), (4484), (46), (0), (95), (96), (2997), (0), (148), (90), (4079), (3311), (107), (0), (1576), (88), (0), (88), (3489), (807), (3286), (1065), (77), (78), (562), (0), (2663), (106), (101), (4178), (110), (899), (441), (0), (100), (101), (109), (793), (4), (2203), (2334), (1056), (108), (109), (110), (3769), (102), (0), (0), (4113), (4511), (61), (0), (3095), (1317), (891), (496), (128), (0), (130), (2745), (2272), (4219), (4566), (0), (1104), (102), (0), (0), (31), (0), (757), (99), (4341), (0), (4073), (554), (30), (574), (3417), (109), (0), (110), (3449), (11), (2224), (362), (82), (1277), (766), (3801), (108), (288), (0), (0), (22), (130), (275), (130), (630), (122), (1144), (138), (0), (0), (668), (668), (438), (132), (4608), (0), (2682), (0), (788), (622), (132), (4172), (2011), (870), (104), (105), (106), (3992), (54), (109), (100), (110), (109), (2819), (0), (5), (63), (78), (47), (65), (156), (42), (0), (3), (42), (42), (3378), (0), (37), (3107), (103), (98), (0), (3212), (1867), (89), (90), (89), (89), (90), (89), (89), (1126), (2808), (34), (2269), (242), (4458), (113), (100), (114), (21), (114), (1426), (4155), (275), (2676), (2331), (90), (38), (4608), (0), (64), (0), (113), (3836), (983), (89), (1949), (162), (634), (121), (2001), (21), (114), (113), (3274), (33), (4121), (3584), (77), (78), (76), (0), (570), (3234), (0), (0), (0), (360), (360), (624), (132), (3440), (0), (82), (748), (1184), (1021), (907), (0), (3634), (106), (2513), (461), (2348), (125), (4386), (1935), (102), (0), (51), (75), (79), (9), (181), (100), (0), (4440), (872), (88), (36), (119), (70), (0), (254), (148), (0), (0), (114), (115), (32), (148), (804), (4), (5), (280), (2131), (0), (231), (298), (132), (2483), (942), (3681), (107), (0), (105), (106), (107), (1265), (939), (0), (113), (1618), (42), (42), (67), (225), (42), (309), (61), (607), (2054), (527), (194), (75), (76), (34), (0), (17), (2351), (2013), (4333), (1382), (22), (693), (950), (104), (105), (0), (2710), (0), (0), (768), (738), (132), (144), (3364), (3154), (2846), (796), (730), (168), (1167), (569), (159), (128), (0), (158), (246), (158), (130), (269), (130), (287), (122), (3251), (479), (201), (42), (93), (181), (25), (2785), (24), (4591), (4513), (115), (3709), (918), (2745), (0), (1970), (796), (3603), (28), (418), (195), (3604), (0), (80), (81), (96), (609), (0), (101), (102), (102), (965), (0), (101), (101), (309), (12), (709), (2399), (2594), (2478), (66), (1931), (2669), (151), (0), (689), (3854), (98), (0), (0), (113), (0), (2267), (309), (2327), (92), (93), (92), (56), (1907), (49), (115), (100), (116), (115), (3514), (953), (44), (357), (4397), (1180), (917), (4498), (119), (100), (120), (1390), (42), (30), (42), (96), (42), (42), (83), (42), (0), (2395), (3554), (479), (1395), (728), (361), (106), (740), (109), (910), (0), (3216), (0), (39), (3011), (343), (1184), (44), (0), (2395), (4570), (101), (4319), (704), (2447), (0), (42), (42), (149), (959), (61), (1075), (109), (110), (109), (2604), (0), (0), (1271), (647), (1914), (52), (1814), (210), (355), (2619), (130), (1045), (0), (3209), (579), (3640), (0), (4050), (58), (1687), (0), (83), (4274), (1771), (393), (0), (100), (1876), (2047), (2280), (4591), (22), (98), (0), (3235), (73), (689), (41), (73), (15), (72), (3571), (109), (125), (110), (109), (3945), (0), (0), (1059), (130), (302), (130), (864), (130), (1010), (130), (177), (122), (2011), (4), (878), (0), (3683), (0), (64), (3011), (999), (130), (742), (398), (912), (0), (897), (499), (77), (78), (245), (4307), (51), (5), (117), (4094), (3162), (98), (0), (0), (122), (0), (98), (0), (2113), (1551), (90), (510), (2724), (42), (42), (42), (2989), (104), (105), (104), (104), (632), (1029), (104), (105), (105), (103), (104), (104), (3989), (85), (86), (85), (111), (104), (84), (106), (0), (113), (3366), (4511), (52), (198), (89), (90), (89), (2098), (3466), (2995), (106), (247), (0), (670), (0), (0), (0), (356), (356), (219), (132), (139), (500), (0), (4223), (75), (209), (125), (341), (1246), (77), (78), (10), (85), (80), (81), (68), (2282), (102), (0), (0), (123), (138), (4540), (42), (92), (2513), (43), (5), (115), (32), (233), (51), (693), (130), (576), (130), (670), (122), (4187), (461), (4407), (0), (936), (0), (103), (100), (2158), (102), (0), (0), (53), (0), (2047), (770), (0), (102), (688), (143), (3169), (395), (264), (0), (85), (786), (4566), (42), (996), (3772), (30), (193), (2798), (2965), (3102), (754), (46), (81), (82), (3394), (108), (121), (109), (110), (111), (0), (563), (156), (948), (0), (42), (70), (24), (96), (2466), (85), (86), (116), (225), (1064), (88), (2587), (29), (1410), (4069), (1455), (199), (2786), (1958), (0), (2397), (71), (32), (0), (99), (99), (99), (99), (237), (107), (108), (107), (106), (107), (108), (107), (42), (689), (563), (604), (99), (3162), (0), (3495), (4422), (3651), (2821), (108), (3916), (77), (78), (24), (0), (223), (1133), (0), (75), (1184), (42), (42), (862), (1236), (85), (86), (0), (86), (85), (2392), (3807), (682), (106), (2274), (3389), (78), (1144), (105), (155), (591), (0), (506), (3251), (31), (2626), (107), (108), (109), (108), (2151), (91), (4619), (0), (689), (999), (100), (4), (1655), (114), (346), (46), (3634), (2228), (2944), (819), (4), (204), (1861), (98), (1384), (0), (4589), (98), (0), (0), (1474), (0), (41), (0), (39), (2225), (4192), (21), (106), (105), (42), (1), (3189), (0), (3162), (1526), (0), (2403), (130), (2630), (4145), (138), (0), (548), (342), (132), (1251), (115), (115), (1833), (130), (627), (130), (401), (122), (1531), (573), (98), (0), (0), (92), (0), (948), (0), (102), (103), (84), (104), (0), (42), (913), (2332), (0), (0), (1015), (229), (132), (4329), (3974), (130), (950), (130), (1016), (122), (3059), (100), (101), (100), (61), (2362), (2973), (81), (82), (126), (32), (574), (0), (1741), (42), (111), (410), (98), (99), (0), (943), (285), (2454), (0), (42), (0), (42), (758), (18), (410), (384), (34), (870), (0), (770), (0), (102), (593), (1251), (990), (42), (101), (403), (4116), (2021), (1072), (108), (0), (101), (547), (924), (0), (978), (37), (2301), (80), (81), (9), (0), (42), (3601), (107), (108), (4), (106), (106), (104), (14), (0), (103), (3922), (774), (4375), (1266), (1787), (652), (4517), (71), (3283), (0), (220), (533), (68), (59), (37), (1155), (28), (3031), (102), (132), (198), (96), (207), (111), (150), (159), (1655), (74), (3489), (0), (0), (69), (2301), (107), (1), (107), (3493), (430), (107), (388), (0), (105), (107), (125), (108), (348), (120), (3), (98), (986), (0), (77), (78), (112), (883), (276), (12), (1202), (3516), (417), (916), (102), (0), (0), (63), (4048), (0), (98), (0), (0), (180), (42), (0), (2047), (110), (1683), (275), (77), (78), (313), (0), (2), (1133), (171), (1781), (0), (1076), (1815), (744), (429), (107), (106), (2852), (481), (3814), (2308), (0), (0), (717), (292), (132), (4311), (245), (2301), (0), (4385), (77), (78), (930), (4189), (382), (4268), (100), (0), (2362), (3440), (104), (370), (105), (3114), (0), (102), (0), (2824), (1014), (476), (985), (131), (144), (4180), (114), (100), (115), (4288), (77), (1014), (46), (0), (95), (96), (3932), (0), (98), (0), (321), (94), (95), (94), (26), (4405), (57), (1147), (108), (107), (0), (3634), (107), (100), (108), (1134), (23), (2379), (42), (46), (1093), (106), (98), (0), (4252), (2863), (103), (104), (3), (100), (101), (23), (196), (2835), (17), (105), (572), (572), (0), (1876), (99), (100), (394), (0), (240), (1022), (128), (1305), (42), (42), (17), (2009), (888), (2865), (234), (73), (24), (2948), (3691), (0), (0), (415), (1056), (132), (2515), (0), (89), (443), (429), (567), (106), (107), (0), (2489), (98), (0), (0), (67), (0), (3337), (562), (3587), (25), (127), (1874), (105), (106), (107), (106), (2197), (0), (230), (102), (103), (104), (105), (210), (0), (740), (88), (0), (2367), (66), (1213), (104), (105), (105), (896), (1793), (104), (317), (917), (2954), (366), (3983), (0), (103), (718), (104), (718), (0), (2303), (99), (3118), (92), (93), (92), (3659), (0), (0), (364), (364), (564), (132), (9), (3957), (13), (4159), (32), (32), (632), (2829), (0), (0), (112), (1592), (4172), (70), (1025), (445), (4085), (461), (1285), (104), (104), (4183), (2672), (0), (2372), (77), (78), (17), (0), (3085), (130), (577), (95), (0), (25), (1413), (0), (113), (728), (0), (341), (102), (0), (0), (76), (0), (1088), (2946), (222), (72), (3017), (3894), (0), (4178), (0), (531), (924), (132), (4145), (102), (4598), (3495), (0), (897), (4386), (101), (102), (102), (300), (3221), (0), (978), (948), (0), (64), (0), (1413), (108), (49), (410), (173), (1622), (2287), (2927), (4463), (99), (0), (776), (1055), (1064), (2395), (3792), (0), (125), (138), (1785), (0), (67), (0), (948), (85), (86), (977), (0), (85), (86), (2304), (0), (818), (529), (132), (1771), (98), (0), (0), (563), (4467), (110), (111), (112), (111), (111), (101), (88), (101), (1935), (104), (327), (0), (103), (4472), (5), (113), (32), (1332), (208), (3479), (0), (3222), (0), (0), (279), (1097), (3420), (42), (101), (4387), (112), (264), (2), (0), (4568), (107), (0), (1891), (102), (0), (0), (14), (0), (825), (102), (0), (0), (2), (0), (3553), (106), (107), (12), (0), (370), (3925), (273), (96), (25), (790), (3806), (1150), (3306), (87), (88), (87), (87), (4074), (0), (0), (895), (130), (1058), (130), (1024), (122), (3788), (92), (42), (1065), (870), (98), (0), (0), (53), (0), (18), (2299), (0), (0), (138), (409), (409), (1035), (132), (2287), (3795), (0), (0), (42), (128), (792), (673), (4319), (100), (221), (101), (3724), (70), (3959), (2332), (42), (317), (346), (3558), (89), (391), (429), (105), (106), (106), (3109), (983), (4386), (4139), (1216), (0), (0), (641), (641), (165), (132), (774), (107), (0), (110), (111), (3143), (83), (444), (0), (1648), (0), (3742), (42), (42), (114), (1791), (42), (42), (42), (673), (849), (987), (2743), (85), (86), (85), (85), (86), (3151), (31), (34), (3597), (389), (1097), (244), (270), (107), (136), (106), (107), (59), (75), (813), (131), (2443), (114), (21), (114), (113), (3754), (498), (2658), (36), (3448), (29), (42), (42), (1003), (2743), (1923), (4218), (0), (4456), (0), (42), (34), (792), (64), (2870), (0), (0), (744), (130), (892), (130), (477), (122), (4446), (95), (24), (2513), (4456), (870), (1313), (867), (428), (449), (304), (375), (29), (3438), (140), (1284), (709), (95), (728), (0), (0), (567), (2393), (4230), (0), (4570), (4166), (2534), (102), (2870), (0), (4012), (188), (563), (0), (2946), (61), (4405), (111), (61), (113), (1228), (107), (177), (137), (906), (108), (107), (1944), (106), (2754), (102), (0), (0), (53), (0), (102), (3566), (0), (0), (130), (3169), (2583), (104), (105), (106), (105), (722), (2740), (109), (110), (111), (0), (3562), (95), (98), (0), (0), (17), (2633), (107), (108), (84), (109), (0), (107), (4), (33), (1067), (102), (0), (0), (2364), (102), (0), (0), (2579), (109), (110), (111), (2146), (0), (0), (63), (0), (3200), (518), (106), (73), (946), (277), (73), (684), (72), (149), (72), (240), (4006), (3223), (704), (4462), (2425), (898), (3999), (765), (942), (32), (616), (5), (3940), (3978), (1977), (3037), (987), (850), (1706), (53), (571), (2218), (102), (0), (0), (2932), (11), (3829), (130), (651), (130), (975), (122), (1939), (100), (1099), (960), (104), (960), (3120), (508), (213), (0), (76), (2450), (0), (0), (104), (194), (4023), (7), (3404), (0), (4211), (692), (2112), (117), (1708), (917), (2467), (106), (21), (106), (4528), (0), (8), (76), (9), (2154), (93), (94), (93), (126), (2055), (510), (4086), (3239), (92), (93), (92), (890), (0), (0), (189), (1052), (132), (2131), (733), (676), (42), (42), (42), (3976), (98), (99), (84), (100), (0), (1494), (3156), (1952), (4050), (4577), (796), (1344), (105), (217), (105), (1782), (108), (1918), (10), (100), (221), (101), (221), (0), (100), (370), (101), (934), (0), (4491), (98), (394), (0), (3045), (105), (105), (25), (3063), (3380), (42), (42), (42), (1204), (692), (623), (69), (1944), (390), (4584), (100), (42), (621), (1214), (1820), (49), (98), (0), (502), (102), (0), (0), (86), (0), (341), (0), (110), (3274), (1373), (104), (105), (78), (706), (154), (241), (93), (94), (93), (953), (3030), (113), (100), (114), (2125), (78), (114), (125), (115), (114), (4556), (1378), (970), (1718), (190), (876), (0), (9), (929), (27), (2509), (266), (2), (3491), (587), (2539), (77), (78), (114), (0), (1508), (87), (898), (83), (3767), (75), (76), (26), (3175), (1401), (801), (2106), (104), (133), (468), (4304), (983), (138), (104), (174), (104), (99), (2274), (225), (0), (109), (933), (2123), (92), (0), (2743), (98), (0), (0), (4391), (710), (3900), (105), (106), (0), (0), (103), (304), (104), (304), (4162), (103), (104), (3), (98), (99), (76), (3608), (2397), (114), (125), (115), (114), (2211), (0), (92), (4591), (122), (0), (1413), (102), (0), (0), (31), (0), (4511), (4566), (106), (156), (106), (2368), (0), (0), (25), (130), (757), (130), (408), (122), (2927), (1082), (61), (3848), (289), (353), (0), (763), (130), (523), (130), (784), (122), (3584), (2722), (102), (0), (0), (93), (0), (341), (940), (126), (0), (106), (741), (4322), (2898), (98), (0), (0), (17), (2704), (75), (224), (68), (76), (786), (0), (658), (0), (63), (4386), (0), (913), (42), (3799), (629), (4432), (2017), (0), (47), (18), (68), (929), (89), (4568), (4420), (967), (1001), (104), (105), (166), (449), (4480), (46), (0), (95), (96), (89), (46), (113), (204), (107), (4319), (105), (0), (3471), (42), (104), (67), (38), (1824), (63), (0), (127), (948), (42), (913), (728), (75), (440), (1278), (1939), (93), (94), (93), (119), (3470), (110), (109), (410), (100), (101), (100), (245), (3127), (0), (2613), (309), (3274), (119), (125), (120), (119), (2054), (102), (0), (0), (122), (0), (2946), (103), (89), (1271), (105), (107), (0), (3528), (121), (0), (2278), (77), (78), (134), (4034), (1520), (117), (3164), (607), (73), (265), (72), (70), (650), (0), (98), (0), (0), (896), (0), (98), (1762), (0), (4184), (876), (105), (890), (0), (3162), (98), (2355), (1547), (2370), (156), (64), (547), (0), (296), (32), (5), (28), (14), (58), (107), (145), (64), (4319), (97), (1470), (4352), (0), (2001), (0), (102), (103), (103), (964), (0), (102), (103), (103), (806), (0), (42), (3023), (484), (4263), (111), (0), (0), (1944), (40), (1264), (12), (3507), (921), (88), (87), (42), (42), (2591), (82), (83), (88), (0), (15), (2976), (1295), (4377), (106), (2056), (0), (127), (105), (475), (4605), (32), (782), (32), (4), (0), (0), (0), (0), (931), (754), (2743), (256), (409), (570), (4491), (32), (1012), (32), (1439), (2), (0), (341), (590), (2023), (2061), (113), (1908), (2557), (1490), (297), (228), (2079), (105), (104), (107), (0), (3974), (99), (102), (99), (1240), (0), (95), (96), (3960), (0), (1388), (40), (1542), (623), (1042), (0), (0), (128), (764), (130), (1046), (130), (517), (159), (4374), (835), (2971), (1184), (4329), (90), (202), (1202), (0), (103), (906), (599), (102), (0), (0), (67), (0), (3495), (85), (85), (86), (85), (85), (335), (0), (3201), (109), (35), (2172), (317), (0), (128), (1576), (0), (2742), (0), (26), (3587), (100), (344), (101), (344), (0), (4310), (72), (1803), (0), (0), (172), (172), (1061), (132), (3837), (26), (2003), (173), (2241), (0), (103), (825), (3820), (37), (100), (728), (2600), (741), (110), (100), (1854), (697), (155), (221), (42), (42), (266), (4031), (462), (2393), (107), (109), (125), (3966), (746), (3583), (49), (18), (4335), (173), (4003), (518), (728), (4337), (937), (100), (99), (98), (69), (4157), (0), (44), (0), (4591), (83), (1462), (20), (426), (960), (684), (506), (845), (101), (1075), (1897), (3685), (395), (107), (32), (32), (32), (4036), (42), (103), (895), (2888), (209), (3882), (118), (299), (609), (2597), (811), (113), (125), (3433), (114), (417), (4556), (312), (4321), (990), (0), (2399), (304), (3733), (130), (473), (130), (163), (122), (3983), (4), (103), (4346), (0), (946), (1133), (3360), (875), (110), (497), (0), (4325), (0), (0), (2597), (0), (3451), (4489), (106), (100), (4319), (109), (1824), (2001), (1521), (98), (0), (0), (3845), (5), (2314), (1385), (371), (44), (790), (126), (2728), (46), (85), (518), (2009), (814), (89), (105), (89), (1131), (554), (1184), (93), (94), (93), (39), (2863), (42), (42), (42), (2207), (4559), (3090), (0), (1776), (683), (0), (6), (42), (787), (623), (0), (32), (1007), (2247), (466), (400), (89), (341), (443), (2949), (90), (91), (0), (3811), (1522), (935), (156), (4116), (20), (2872), (42), (0), (21), (2413), (376), (4298), (335), (46), (987), (47), (42), (1498), (196), (1676), (1034), (3006), (176), (5), (116), (347), (6), (803), (2178), (13), (1345), (2274), (3927), (32), (720), (783), (2047), (102), (0), (112), (47), (177), (4), (220), (237), (0), (3498), (0), (41), (59), (41), (59), (50), (0), (2842), (113), (0), (2047), (4366), (108), (994), (1017), (114), (905), (0), (113), (361), (95), (96), (95), (1726), (0), (1038), (89), (90), (89), (2087), (3129), (106), (107), (42), (3890), (0), (81), (1413), (52), (1449), (825), (105), (134), (145), (106), (0), (0), (2613), (4), (366), (0), (2274), (3749), (563), (0), (42), (896), (2714), (908), (79), (2733), (2567), (30), (4028), (89), (4020), (78), (102), (3743), (881), (0), (99), (196), (55), (100), (84), (101), (0), (4107), (0), (4577), (103), (104), (46), (456), (97), (100), (1075), (3011), (2150), (113), (100), (114), (113), (996), (1546), (105), (105), (100), (106), (2734), (1688), (2156), (84), (83), (673), (3632), (1105), (1208), (0), (563), (0), (98), (0), (0), (1222), (42), (0), (42), (42), (42), (42), (56), (3011), (289), (4447), (3957), (15), (98), (0), (0), (69), (0), (4158), (23), (508), (0), (3070), (0), (83), (42), (42), (34), (4566), (4446), (0), (983), (895), (3924), (0), (93), (4386), (113), (1062), (0), (112), (1141), (0), (1562), (2955), (421), (0), (0), (896), (0), (2611), (93), (1065), (3198), (103), (132), (3772), (3364), (105), (104), (302), (107), (304), (108), (107), (1944), (98), (1071), (0), (99), (100), (4501), (103), (861), (104), (861), (0), (103), (3618) }; t.n = 4626; return t end)(), (function() local t = { (127), (127), (86), (127), (185), (164), (181), (117), (120), (127), (62), (127), (86), (127), (90), (131), (34), (101), (101), (101), (101), (92), (127), (185), (195), (22), (32), (127), (127), (62), (127), (62), (127), (78), (8), (8), (8), (127), (185), (185), (116), (7), (186), (127), (131), (34), (76), (5), (141), (17), (101), (92), (127), (185), (164), (181), (117), (120), (127), (185), (185), (181), (185), (120), (127), (8), (8), (8), (126), (185), (8), (8), (127), (127), (86), (127), (62), (127), (117), (158), (127), (120), (127), (8), (127), (120), (185), (185), (8), (120), (8), (127), (173), (117), (8), (127), (185), (127), (185), (164), (181), (117), (120), (127), (127), (122), (185), (185), (145), (127), (185), (164), (181), (117), (120), (127), (117), (26), (8), (127), (186), (127), (127), (117), (120), (127), (117), (8), (127), (86), (127), (101), (101), (120), (185), (127), (86), (127), (189), (127), (86), (127), (86), (127), (189), (127), (120), (127), (168), (185), (185), (145), (185), (22), (95), (8), (127), (86), (127), (39), (127), (62), (127), (131), (90), (31), (66), (79), (5), (141), (17), (101), (92), (127), (123), (127), (185), (185), (117), (127), (117), (120), (8), (8), (8), (40), (185), (77), (75), (161), (127), (86), (127), (127), (117), (127), (62), (127), (62), (127), (127), (185), (92), (78), (120), (117), (117), (127), (62), (127), (7), (117), (120), (185), (127), (117), (26), (8), (127), (127), (127), (117), (185), (8), (127), (62), (127), (127), (145), (7), (185), (8), (127), (8), (8), (8), (127), (17), (17), (17), (127), (5), (141), (17), (101), (92), (127), (181), (117), (120), (8), (8), (8), (40), (117), (188), (147), (91), (117), (117), (8), (127), (86), (127), (18), (127), (8), (8), (8), (40), (117), (8), (127), (189), (127), (127), (86), (127), (8), (127), (185), (8), (8), (8), (127), (117), (8), (127), (62), (127), (117), (26), (8), (127), (62), (127), (185), (185), (117), (127), (169), (127), (86), (127), (8), (8), (22), (23), (185), (185), (8), (8), (8), (8), (126), (185), (127), (18), (127), (86), (127), (181), (117), (120), (8), (8), (127), (127), (93), (131), (101), (101), (101), (92), (127), (185), (186), (185), (185), (186), (127), (18), (127), (117), (26), (8), (127), (86), (127), (8), (8), (8), (127), (185), (145), (8), (127), (117), (117), (8), (127), (127), (185), (185), (185), (127), (185), (185), (117), (127), (127), (169), (127), (168), (127), (185), (116), (7), (160), (67), (91), (127), (62), (127), (185), (185), (117), (120), (8), (127), (8), (145), (8), (127), (185), (164), (181), (117), (120), (127), (185), (185), (186), (127), (185), (55), (127), (42), (120), (127), (189), (127), (185), (164), (181), (117), (120), (127), (8), (32), (127), (169), (127), (116), (8), (127), (117), (158), (185), (127), (32), (127), (62), (127), (62), (127), (86), (127), (86), (127), (127), (185), (185), (7), (26), (39), (127), (131), (90), (76), (5), (141), (17), (101), (92), (127), (120), (160), (67), (91), (185), (88), (120), (127), (117), (116), (117), (26), (116), (127), (117), (26), (8), (127), (127), (185), (185), (117), (120), (8), (127), (127), (62), (127), (34), (131), (101), (101), (92), (127), (185), (164), (181), (117), (120), (127), (127), (86), (127), (127), (169), (127), (181), (117), (120), (127), (18), (127), (107), (127), (117), (8), (127), (62), (127), (120), (185), (185), (117), (127), (86), (127), (8), (127), (22), (23), (160), (67), (91), (185), (127), (8), (40), (185), (164), (181), (127), (62), (127), (120), (127), (88), (117), (117), (117), (7), (127), (18), (127), (70), (103), (185), (185), (117), (127), (8), (185), (145), (8), (8), (126), (8), (127), (86), (127), (185), (185), (117), (120), (8), (127), (107), (127), (169), (127), (8), (127), (8), (127), (185), (164), (181), (117), (120), (127), (86), (127), (189), (127), (8), (8), (126), (127), (164), (181), (117), (127), (86), (127), (26), (117), (120), (127), (185), (185), (117), (120), (8), (127), (120), (8), (127), (18), (127), (185), (117), (26), (117), (26), (186), (127), (164), (55), (127), (131), (93), (34), (101), (101), (101), (101), (60), (19), (127), (185), (185), (186), (8), (127), (185), (164), (181), (117), (120), (127), (8), (126), (8), (120), (127), (117), (117), (185), (185), (8), (120), (173), (127), (185), (185), (117), (120), (117), (8), (127), (134), (41), (140), (87), (89), (185), (117), (26), (8), (120), (127), (160), (67), (91), (185), (185), (7), (127), (185), (164), (181), (117), (127), (164), (181), (117), (120), (127), (117), (26), (8), (127), (117), (117), (117), (127), (185), (164), (181), (117), (127), (120), (117), (8), (127), (145), (117), (81), (185), (8), (185), (185), (127), (8), (40), (47), (141), (62), (127), (114), (127), (189), (127), (86), (127), (117), (127), (17), (17), (17), (17), (17), (17), (185), (127), (18), (127), (8), (127), (22), (95), (8), (127), (131), (34), (101), (101), (92), (127), (88), (185), (127), (127), (8), (8), (8), (127), (117), (120), (127), (185), (185), (117), (120), (185), (185), (117), (120), (127), (17), (17), (17), (127), (131), (90), (76), (5), (141), (17), (101), (92), (127), (173), (117), (8), (127), (185), (160), (67), (91), (186), (127), (186), (127), (189), (127), (185), (65), (62), (127), (62), (127), (5), (141), (17), (101), (60), (19), (127), (185), (117), (26), (117), (120), (185), (117), (26), (127), (62), (127), (18), (127), (8), (127), (127), (185), (185), (117), (120), (127), (90), (131), (76), (5), (141), (17), (101), (92), (127), (127), (185), (164), (181), (127), (185), (185), (117), (120), (185), (185), (117), (120), (127), (131), (90), (101), (101), (92), (127), (26), (120), (127), (127), (62), (127), (62), (127), (185), (164), (181), (127), (18), (127), (34), (131), (20), (32), (127), (120), (173), (117), (117), (127), (189), (127), (185), (185), (186), (185), (185), (127), (8), (127), (185), (185), (117), (120), (185), (127), (86), (127), (8), (127), (185), (164), (181), (127), (185), (117), (26), (127), (39), (127), (116), (8), (127), (168), (8), (127), (117), (8), (8), (8), (40), (86), (127), (168), (145), (7), (127), (86), (127), (8), (120), (127), (62), (127), (68), (81), (160), (67), (91), (127), (86), (127), (127), (131), (151), (5), (141), (17), (101), (92), (127), (88), (117), (117), (7), (145), (8), (8), (22), (171), (185), (127), (185), (185), (117), (120), (8), (127), (117), (117), (17), (117), (17), (127), (88), (117), (117), (127), (127), (117), (8), (127), (185), (185), (185), (127), (127), (185), (145), (7), (127), (62), (127), (62), (127), (117), (117), (8), (127), (127), (189), (127), (81), (7), (32), (127), (117), (26), (127), (117), (185), (185), (127), (117), (88), (185), (127), (117), (26), (145), (127), (81), (185), (117), (127), (185), (164), (181), (117), (127), (168), (35), (127), (127), (127), (189), (127), (8), (127), (117), (26), (8), (127), (185), (117), (26), (186), (127), (185), (195), (186), (185), (117), (185), (195), (127), (120), (8), (127), (168), (8), (8), (8), (40), (117), (26), (127), (127), (127), (185), (185), (186), (117), (127), (185), (164), (181), (117), (120), (127), (127), (8), (145), (186), (127), (86), (127), (86), (127), (39), (127), (8), (127), (117), (26), (127), (127), (131), (90), (76), (5), (141), (17), (101), (92), (127), (77), (75), (161), (185), (164), (181), (117), (127), (58), (117), (117), (127), (185), (186), (117), (8), (127), (18), (127), (127), (117), (26), (186), (145), (8), (81), (127), (117), (8), (127), (117), (117), (127), (117), (8), (127), (189), (127), (62), (127), (127), (127), (86), (127), (185), (55), (127), (86), (127), (86), (127), (127), (127), (127), (117), (117), (117), (26), (117), (173), (117), (127), (127), (38), (8), (127), (116), (116), (8), (127), (62), (127), (131), (93), (31), (66), (148), (32), (127), (185), (185), (185), (120), (185), (185), (185), (120), (127), (86), (127), (8), (127), (120), (127), (185), (185), (117), (120), (127), (127), (8), (40), (185), (185), (7), (117), (25), (127), (117), (120), (8), (127), (127), (127), (185), (7), (81), (32), (127), (62), (127), (127), (107), (127), (62), (127), (17), (17), (17), (17), (17), (127), (185), (164), (181), (117), (127), (8), (126), (185), (8), (8), (8), (8), (127), (90), (131), (44), (32), (127), (127), (127), (185), (185), (186), (8), (127), (18), (127), (117), (26), (117), (127), (127), (185), (164), (181), (117), (120), (127), (127), (117), (127), (86), (127), (185), (145), (8), (127), (127), (127), (185), (185), (117), (120), (185), (127), (8), (8), (8), (40), (18), (127), (185), (164), (181), (127), (86), (127), (173), (117), (8), (127), (185), (164), (181), (117), (127), (185), (185), (117), (127), (168), (185), (185), (117), (127), (81), (8), (8), (8), (22), (23), (185), (185), (8), (8), (127), (32), (127), (127), (160), (67), (91), (185), (186), (127), (185), (117), (88), (101), (127), (62), (127), (8), (117), (17), (127), (117), (8), (117), (117), (126), (117), (117), (22), (127), (62), (127), (168), (8), (8), (8), (127), (185), (117), (26), (127), (122), (127), (127), (62), (127), (127), (70), (127), (186), (145), (8), (81), (127), (117), (117), (8), (127), (189), (127), (185), (164), (181), (127), (185), (185), (185), (185), (127), (117), (8), (127), (189), (127), (5), (141), (17), (101), (92), (127), (127), (8), (185), (145), (127), (186), (8), (145), (8), (127), (120), (127), (117), (117), (117), (8), (8), (127), (8), (126), (160), (67), (91), (8), (8), (8), (8), (127), (185), (185), (117), (120), (8), (127), (86), (127), (86), (127), (117), (8), (127), (185), (185), (117), (120), (8), (127), (86), (127), (8), (185), (164), (127), (117), (120), (185), (164), (181), (117), (120), (127), (86), (127), (131), (93), (101), (101), (92), (127), (117), (26), (8), (127), (185), (117), (7), (127), (117), (117), (117), (117), (117), (117), (117), (117), (117), (127), (8), (127), (26), (117), (117), (127), (34), (131), (101), (101), (92), (127), (127), (127), (168), (8), (8), (127), (127), (168), (185), (185), (127), (185), (185), (117), (120), (127), (62), (127), (185), (8), (195), (127), (145), (186), (8), (127), (127), (189), (127), (8), (127), (185), (185), (88), (127), (120), (127), (86), (127), (194), (8), (127), (18), (127), (86), (127), (127), (117), (8), (127), (185), (185), (117), (120), (8), (127), (86), (127), (185), (117), (185), (113), (22), (95), (127), (145), (8), (8), (22), (171), (185), (127), (101), (101), (185), (8), (127), (117), (82), (68), (45), (16), (184), (69), (173), (117), (127), (91), (176), (172), (8), (8), (126), (185), (8), (127), (107), (127), (86), (127), (169), (127), (62), (127), (185), (185), (117), (120), (8), (127), (120), (8), (127), (185), (185), (185), (127), (185), (185), (117), (120), (127), (117), (8), (127), (189), (127), (78), (185), (185), (8), (120), (185), (185), (127), (159), (127), (185), (185), (88), (127), (117), (120), (127), (117), (81), (117), (26), (145), (117), (81), (117), (26), (127), (86), (127), (185), (185), (186), (8), (127), (62), (127), (185), (164), (181), (127), (127), (189), (127), (117), (26), (8), (127), (117), (158), (127), (34), (131), (151), (5), (141), (17), (101), (92), (127), (8), (127), (185), (185), (186), (88), (127), (8), (127), (117), (120), (127), (185), (164), (181), (117), (120), (127), (86), (127), (8), (127), (117), (26), (117), (127), (120), (185), (164), (127), (185), (185), (117), (120), (127), (185), (185), (117), (120), (117), (8), (127), (185), (185), (186), (8), (127), (189), (127), (127), (185), (185), (186), (127), (107), (127), (164), (103), (24), (174), (129), (172), (117), (120), (127), (185), (185), (185), (185), (127), (127), (117), (120), (185), (127), (127), (185), (8), (127), (107), (127), (185), (185), (117), (127), (62), (127), (81), (155), (1), (5), (8), (127), (117), (26), (8), (127), (185), (164), (181), (117), (120), (185), (164), (181), (117), (120), (127), (127), (185), (117), (185), (185), (127), (185), (185), (117), (127), (86), (127), (34), (131), (101), (101), (92), (127), (127), (83), (77), (75), (161), (127), (62), (127), (185), (176), (71), (50), (64), (98), (109), (140), (181), (117), (120), (185), (164), (127), (26), (186), (127), (8), (127), (8), (127), (120), (8), (127), (8), (8), (40), (185), (117), (26), (186), (127), (86), (127), (86), (127), (107), (127), (93), (131), (151), (5), (141), (17), (101), (92), (127), (181), (117), (120), (127), (127), (189), (127), (164), (55), (127), (117), (8), (127), (168), (173), (8), (127), (189), (127), (40), (127), (127), (185), (117), (120), (8), (127), (39), (127), (107), (127), (8), (185), (117), (186), (127), (189), (127), (160), (67), (91), (185), (117), (127), (86), (127), (86), (127), (18), (127), (62), (127), (117), (120), (185), (185), (127), (18), (127), (86), (127), (127), (185), (55), (127), (185), (116), (186), (127), (86), (127), (117), (185), (185), (117), (120), (127), (5), (182), (127), (42), (189), (127), (168), (185), (145), (8), (8), (126), (127), (127), (127), (185), (185), (185), (127), (185), (164), (181), (127), (127), (117), (120), (127), (127), (86), (127), (93), (131), (179), (32), (127), (127), (127), (18), (127), (185), (164), (181), (117), (120), (127), (169), (127), (18), (127), (117), (26), (117), (127), (185), (181), (92), (78), (189), (127), (127), (86), (127), (189), (127), (189), (127), (131), (34), (151), (5), (141), (17), (101), (92), (127), (93), (131), (34), (101), (101), (101), (92), (127), (18), (127), (131), (101), (101), (92), (127), (127), (127), (185), (185), (185), (127), (6), (185), (117), (26), (186), (127), (168), (176), (71), (50), (64), (98), (109), (140), (181), (38), (117), (117), (127), (168), (8), (127), (8), (185), (164), (127), (127), (185), (185), (186), (185), (185), (186), (185), (127), (127), (86), (127), (8), (127), (185), (117), (26), (117), (26), (127), (62), (127), (107), (127), (86), (127), (127), (181), (117), (120), (8), (127), (8), (169), (127), (86), (127), (8), (40), (117), (26), (186), (127), (189), (127), (127), (185), (185), (117), (120), (8), (127), (34), (131), (90), (101), (101), (101), (92), (127), (120), (185), (8), (127), (127), (117), (120), (127), (8), (127), (189), (127), (8), (127), (40), (185), (176), (71), (50), (64), (98), (109), (140), (181), (127), (127), (117), (26), (117), (117), (173), (127), (8), (22), (23), (185), (185), (8), (8), (8), (8), (126), (127), (127), (131), (101), (101), (92), (127), (189), (127), (117), (120), (185), (185), (185), (127), (8), (120), (8), (127), (117), (117), (8), (127), (117), (8), (8), (8), (40), (169), (127), (185), (185), (117), (120), (8), (127), (127), (62), (127), (64), (189), (127), (185), (26), (120), (127), (131), (90), (101), (101), (60), (19), (127), (62), (127), (189), (127), (86), (127), (8), (127), (93), (131), (77), (37), (192), (5), (141), (17), (101), (92), (127), (86), (127), (117), (8), (8), (8), (127), (8), (127), (127), (86), (127), (8), (127), (18), (127), (86), (127), (169), (127), (189), (127), (120), (185), (185), (117), (127), (120), (185), (145), (7), (8), (120), (145), (7), (8), (8), (8), (40), (62), (127), (169), (127), (127), (8), (120), (8), (127), (185), (164), (181), (117), (120), (127), (117), (127), (185), (185), (186), (8), (127), (8), (185), (117), (26), (186), (127), (117), (26), (117), (127), (127), (189), (127), (185), (117), (26), (127), (117), (188), (147), (91), (117), (117), (127), (117), (120), (127), (127), (189), (127), (127), (8), (8), (40), (145), (8), (81), (127), (116), (8), (127), (8), (127), (117), (120), (127), (127), (185), (127), (189), (127), (168), (117), (117), (8), (8), (8), (40), (185), (185), (7), (127), (164), (55), (127), (8), (127), (86), (127), (28), (102), (127), (39), (127), (18), (127), (62), (127), (18), (127), (86), (127), (168), (83), (127), (127), (117), (120), (8), (127), (62), (127), (127), (8), (185), (164), (127), (158), (117), (117), (158), (117), (94), (127), (185), (117), (26), (186), (127), (131), (90), (151), (5), (141), (17), (76), (5), (141), (17), (101), (92), (127), (126), (8), (120), (127), (116), (8), (127), (127), (39), (127), (156), (101), (120), (8), (127), (185), (185), (117), (127), (8), (126), (185), (127), (40), (185), (164), (181), (117), (120), (185), (164), (127), (127), (189), (127), (127), (117), (117), (8), (127), (185), (185), (186), (145), (8), (127), (7), (155), (47), (7), (155), (47), (127), (185), (185), (186), (8), (127), (117), (26), (120), (8), (127), (127), (189), (127), (185), (185), (186), (127), (62), (127), (7), (117), (120), (127), (131), (90), (34), (101), (101), (101), (60), (19), (127), (116), (127), (8), (8), (8), (40), (127), (185), (185), (117), (127), (185), (185), (117), (127), (185), (164), (181), (127), (62), (127), (117), (8), (127), (8), (126), (185), (8), (127), (189), (127), (5), (141), (17), (101), (92), (127), (189), (127), (88), (117), (116), (158), (185), (127), (185), (164), (181), (117), (120), (127), (117), (120), (185), (127), (8), (127), (8), (40), (81), (186), (8), (127), (117), (8), (127), (189), (127), (127), (127), (107), (127), (117), (26), (185), (127), (185), (8), (185), (185), (185), (120), (127), (8), (127), (168), (117), (8), (8), (8), (127), (185), (185), (77), (75), (161), (185), (127), (189), (127), (62), (127), (8), (127), (127), (120), (127), (4), (8), (88), (17), (17), (17), (17), (127), (185), (185), (7), (185), (185), (185), (7), (117), (8), (127), (117), (26), (127), (120), (127), (127), (107), (127), (122), (127), (185), (185), (117), (120), (8), (127), (168), (8), (127), (117), (117), (8), (127), (185), (185), (116), (7), (186), (127), (127), (8), (8), (40), (107), (127), (127), (185), (117), (117), (120), (127), (127), (62), (127), (185), (185), (185), (7), (127), (39), (127), (120), (8), (127), (145), (22), (78), (8), (8), (8), (40), (62), (127), (8), (126), (8), (127), (189), (127), (18), (127), (185), (164), (181), (127), (81), (185), (116), (8), (127), (127), (117), (26), (186), (117), (8), (127), (120), (127), (127), (18), (127), (39), (127), (127), (93), (131), (101), (101), (92), (127), (145), (186), (127), (5), (141), (17), (101), (92), (127), (8), (185), (164), (181), (117), (120), (127), (168), (185), (185), (117), (26), (120), (117), (8), (127), (131), (34), (101), (101), (92), (127), (40), (5), (141), (17), (101), (92), (127), (185), (185), (7), (117), (25), (127), (185), (160), (67), (91), (117), (120), (127), (117), (8), (127), (185), (185), (88), (101), (101), (127), (168), (117), (173), (117), (127), (8), (127), (117), (8), (127), (181), (117), (120), (185), (127), (127), (127), (117), (70), (8), (127), (62), (127), (185), (81), (185), (127), (127), (116), (117), (8), (127), (185), (185), (117), (120), (117), (127), (155), (155), (126), (155), (47), (7), (8), (81), (5), (127), (127), (62), (127), (127), (86), (127), (86), (127), (18), (127), (127), (117), (26), (8), (127), (86), (127), (185), (187), (170), (77), (73), (146), (110), (172), (127), (8), (40), (116), (116), (8), (127), (185), (117), (7), (127), (8), (145), (8), (81), (185), (185), (117), (26), (117), (127), (22), (39), (127), (120), (185), (185), (117), (127), (117), (8), (127), (127), (8), (127), (185), (164), (181), (117), (127), (168), (185), (164), (181), (127), (117), (120), (127), (86), (127), (0), (185), (185), (8), (120), (8), (127), (189), (127), (18), (127), (127), (117), (117), (155), (7), (127), (127), (107), (127), (131), (34), (101), (101), (92), (127), (8), (127), (18), (127), (185), (185), (8), (127), (62), (127), (185), (55), (127), (127), (185), (117), (26), (127), (120), (185), (164), (127), (101), (101), (101), (127), (86), (127), (185), (117), (26), (127), (86), (127), (117), (120), (185), (185), (127), (168), (185), (164), (127), (185), (185), (186), (8), (127), (189), (127), (7), (117), (120), (127), (185), (117), (26), (127), (86), (127), (117), (8), (127), (8), (185), (164), (127), (127), (185), (195), (22), (185), (185), (127), (189), (127), (8), (185), (117), (8), (120), (127), (185), (185), (117), (120), (8), (8), (8), (40), (117), (117), (8), (127), (62), (127), (86), (127), (86), (127), (127), (131), (90), (101), (101), (92), (127), (168), (8), (117), (117), (117), (155), (155), (81), (127), (185), (164), (181), (117), (120), (127), (8), (127), (117), (8), (127), (185), (185), (185), (7), (127), (168), (117), (26), (185), (185), (185), (127), (116), (127), (185), (55), (127), (169), (127), (7), (155), (47), (8), (127), (186), (127), (86), (127), (127), (127), (120), (185), (117), (26), (117), (120), (127), (122), (127), (185), (185), (186), (127), (90), (131), (101), (101), (101), (60), (19), (127), (86), (127), (8), (8), (8), (127), (116), (88), (101), (127), (127), (86), (127), (189), (127), (189), (127), (145), (7), (32), (127), (18), (127), (185), (185), (117), (120), (127), (39), (127), (117), (120), (8), (127), (120), (8), (127), (120), (127), (185), (164), (181), (117), (120), (127), (127), (114), (18), (62), (127), (168), (127), (131), (101), (101), (92), (127), (189), (127), (127), (168), (8), (127), (185), (145), (7), (8), (127), (168), (8), (127), (181), (117), (120), (127), (185), (8), (127), (189), (127), (127), (127), (127), (185), (88), (101), (101), (127), (62), (127), (116), (8), (127), (127), (181), (117), (120), (127), (185), (185), (8), (120), (185), (185), (127), (131), (101), (101), (92), (127), (185), (164), (181), (117), (127), (130), (185), (185), (7), (158), (136), (47), (182), (127), (7), (8), (120), (185), (127), (126), (185), (8), (127), (62), (127), (18), (127), (34), (131), (85), (32), (127), (117), (70), (127), (117), (127), (164), (55), (127), (185), (55), (127), (185), (164), (181), (117), (120), (127), (185), (164), (181), (117), (120), (127), (185), (185), (117), (120), (127), (62), (127), (117), (26), (8), (127), (62), (127), (185), (185), (186), (185), (127), (90), (131), (151), (5), (141), (17), (101), (92), (127), (186), (117), (8), (127), (185), (164), (181), (117), (120), (8), (127), (131), (34), (93), (101), (101), (101), (92), (127), (127), (120), (173), (117), (8), (8), (8), (40), (185), (117), (26), (127), (86), (127), (127), (117), (127), (86), (127), (8), (117), (117), (155), (155), (47), (127), (8), (127), (32), (127), (131), (34), (101), (101), (101), (92), (127), (145), (190), (185), (185), (127), (185), (117), (120), (127), (18), (127), (117), (117), (8), (127), (117), (117), (117), (8), (8), (8), (40), (185), (185), (186), (185), (185), (127), (26), (8), (127), (8), (127), (189), (127), (8), (127), (185), (145), (77), (75), (161), (8), (127), (26), (117), (26), (186), (127), (169), (127), (86), (127), (26), (117), (117), (127), (62), (127), (127), (159), (127), (168), (117), (8), (8), (8), (40), (131), (90), (151), (5), (141), (17), (101), (92), (127), (117), (8), (127), (127), (127), (32), (127), (7), (84), (71), (127), (62), (127), (169), (127), (117), (8), (127), (131), (90), (162), (32), (127), (18), (127), (107), (127), (185), (127), (18), (127), (49), (117), (120), (127), (8), (127), (185), (117), (185), (127), (160), (67), (91), (117), (26), (186), (127), (122), (127), (185), (164), (181), (117), (120), (185), (127), (131), (34), (44), (32), (127), (185), (185), (185), (7), (117), (127), (185), (185), (185), (120), (127), (8), (185), (164), (181), (117), (127), (185), (185), (117), (26), (120), (145), (22), (127), (127), (185), (164), (181), (127), (185), (164), (181), (127), (185), (185), (185), (127), (164), (181), (117), (120), (127), (117), (117), (158), (117), (117), (158), (117), (94), (117), (94), (117), (127), (127), (86), (127), (127), (86), (127), (127), (8), (8), (8), (126), (127), (107), (127), (62), (127), (189), (127), (8), (127), (127), (185), (164), (181), (127), (86), (127), (5), (141), (17), (101), (92), (127), (83), (127), (117), (26), (117), (127), (101), (101), (120), (8), (127), (22), (95), (185), (117), (127), (169), (127), (18), (127), (86), (127), (86), (127), (86), (127), (26), (117), (26), (127), (88), (185), (117), (26), (127), (185), (185), (186), (8), (127), (86), (127), (127), (185), (185), (186), (127), (90), (131), (101), (101), (92), (127), (86), (127), (117), (117), (117), (127), (185), (185), (117), (26), (120), (127), (62), (127), (127), (127), (86), (127), (185), (8), (7), (127), (86), (127), (8), (185), (117), (26), (117), (120), (185), (117), (26), (8), (120), (127), (145), (117), (81), (127), (145), (186), (8), (127), (127), (117), (117), (117), (127), (8), (8), (8), (40), (107), (127), (186), (8), (8), (127), (127), (8), (185), (164), (127), (185), (164), (181), (117), (120), (127), (81), (185), (127), (127), (185), (185), (117), (127), (8), (127), (185), (185), (186), (8), (127), (185), (117), (26), (127), (8), (185), (117), (26), (186), (127), (127), (86), (127), (8), (127), (120), (8), (127), (189), (127), (8), (127), (62), (127), (127), (185), (185), (117), (120), (127), (86), (127), (189), (127), (185), (185), (117), (127), (127), (189), (127), (145), (8), (8), (127), (8), (127), (185), (8), (7), (185), (127), (127), (168), (8), (8), (127), (185), (120), (127), (185), (164), (181), (127), (86), (127), (185), (185), (22), (95), (185), (117), (26), (117), (127), (185), (195), (22), (185), (185), (8), (127), (127), (185), (117), (26), (186), (127), (168), (8), (127), (117), (120), (127), (185), (164), (181), (117), (120), (127), (127), (185), (117), (7), (127), (90), (131), (76), (5), (141), (17), (101), (92), (127), (127), (86), (127), (86), (127), (131), (76), (5), (141), (17), (101), (92), (127), (40), (185), (164), (181), (117), (120), (127), (62), (127), (120), (185), (117), (127), (127), (185), (164), (181), (117), (127), (160), (67), (91), (185), (117), (120), (127), (168), (8), (127), (168), (117), (117), (127), (169), (127), (127), (168), (77), (75), (161), (127), (8), (40), (127), (189), (127), (185), (145), (8), (8), (127), (117), (120), (185), (185), (188), (147), (91), (127), (158), (127), (185), (55), (127), (117), (77), (75), (161), (127), (117), (120), (8), (127), (117), (8), (127), (86), (127), (127), (127), (185), (185), (186), (8), (127), (26), (186), (127), (185), (185), (186), (8), (127), (18), (127), (8), (127), (185), (117), (26), (186), (127), (185), (164), (181), (117), (120), (127), (5), (8), (40), (7), (117), (120), (127), (8), (116), (127), (185), (185), (8), (127), (127), (86), (127), (117), (158), (117), (94), (185), (127), (168), (185), (164), (181), (117), (120), (185), (127), (159), (127), (40), (26), (8), (120), (127), (127), (127), (62), (127), (8), (8), (40), (120), (127), (8), (126), (157), (177), (178), (144), (2), (69), (127), (122), (127), (127), (120), (127), (168), (185), (145), (7), (8), (120), (185), (145), (7), (8), (120), (117), (127), (86), (127), (185), (22), (95), (127), (189), (127), (86), (127), (127), (185), (186), (117), (117), (127), (185), (185), (117), (120), (8), (127), (127), (127), (86), (127), (120), (8), (185), (8), (127), (8), (8), (8), (8), (22), (22), (171), (120), (127), (8), (127), (22), (86), (8), (127), (8), (8), (8), (127), (117), (120), (127), (189), (127), (127), (117), (127), (62), (127), (86), (127), (127), (185), (7), (117), (120), (127), (17), (17), (17), (127), (120), (185), (185), (127), (116), (127), (86), (127), (86), (127), (131), (90), (93), (76), (5), (141), (17), (85), (32), (127), (189), (127), (127), (127), (185), (8), (127), (120), (185), (117), (127), (185), (164), (181), (117), (120), (127), (186), (185), (185), (186), (185), (127), (18), (127), (117), (26), (127), (127), (168), (8), (127), (18), (127), (120), (8), (127), (185), (117), (26), (117), (120), (127), (169), (127), (90), (131), (101), (101), (101), (92), (127), (86), (127), (189), (127), (168), (185), (117), (127), (117), (8), (127), (127), (8), (185), (117), (127), (127), (137), (127), (117), (117), (8), (127), (8), (127), (8), (185), (117), (127), (189), (127), (117), (8), (127), (86), (127), (8), (127), (127), (117), (26), (7), (186), (8), (127), (181), (117), (120), (127), (86), (127), (86), (127), (8), (8), (40), (117), (26), (127), (62), (127), (117), (185), (8), (8), (8), (127), (117), (8), (8), (127), (86), (127), (8), (8), (8), (40), (8), (185), (117), (127), (186), (8), (127), (189), (127), (8), (120), (127), (86), (127), (5), (141), (17), (101), (92), (127), (126), (182), (127), (120), (8), (127), (127), (8), (145), (8), (81), (127), (22), (95), (127), (18), (127), (127), (7), (185), (127), (185), (127), (62), (127), (185), (164), (181), (127), (122), (127), (62), (127), (185), (117), (117), (127), (117), (26), (8), (127), (127), (8), (185), (8), (40), (8), (127), (185), (185), (186), (8), (127), (117), (117), (117), (127), (127), (127), (159), (127), (127), (168), (4), (117), (127), (117), (120), (8), (127), (127), (189), (127), (8), (117), (117), (127), (185), (185), (181), (127), (127), (127), (8), (127), (86), (127), (117), (120), (8), (127), (8), (127), (117), (26), (117), (26), (117), (127), (169), (127), (86), (127), (127), (126), (185), (8), (8), (8), (127), (86), (127), (62), (127), (8), (127), (8), (40), (185), (176), (71), (50), (64), (98), (109), (140), (181), (127), (88), (117), (17), (117), (94), (185), (116), (127), (117), (120), (127), (127), (189), (127), (127), (145), (8), (81), (185), (127), (185), (185), (186), (127), (168), (127), (185), (185), (186), (127), (127), (185), (185), (117), (127), (120), (8), (127), (86), (127), (117), (160), (67), (91), (185), (22), (95), (127), (126), (8), (120), (127), (127), (117), (120), (117), (127), (62), (127), (189), (127), (127), (189), (127), (141), (127), (117), (26), (127), (117), (120), (160), (67), (91), (185), (117), (26), (120), (127), (18), (127), (185), (185), (117), (127), (117), (26), (127), (62), (127), (185), (117), (26), (186), (8), (127), (186), (185), (117), (26), (127), (62), (127), (185), (186), (8), (127), (127), (127), (181), (117), (120), (185), (164), (181), (127), (117), (173), (117), (117), (117), (117), (8), (127), (86), (127), (127), (8), (185), (164), (181), (117), (120), (127), (169), (127), (18), (127), (168), (83), (117), (117), (8), (127), (127), (168), (8), (8), (127), (116), (8), (127), (145), (8), (81), (185), (127), (168), (127), (62), (127), (164), (181), (117), (120), (127), (117), (8), (127), (117), (8), (127), (127), (7), (185), (127), (185), (117), (26), (186), (127), (145), (8), (81), (185), (185), (127), (185), (117), (26), (117), (120), (185), (127) }; t.n = 4626; return t end)(), {}, (function() local t = { (0), (0), (5), (0), (60), (0), (103), (96), (102), (0), (5), (0), (5), (0), (133), (139), (0), (139), (133), (137), (139), (0), (0), (2), (8), (2), (98), (0), (0), (101), (0), (5), (0), (107), (0), (0), (0), (0), (55), (2), (107), (0), (0), (0), (129), (0), (126), (130), (130), (830), (129), (0), (0), (60), (0), (99), (95), (98), (0), (60), (85), (91), (84), (90), (0), (0), (0), (0), (0), (76), (0), (0), (0), (0), (5), (0), (5), (0), (1), (107), (0), (100), (0), (0), (0), (77), (42), (16), (0), (77), (0), (0), (90), (1), (0), (0), (119), (0), (60), (0), (103), (96), (102), (0), (0), (109), (60), (99), (437), (0), (60), (0), (99), (95), (98), (0), (1), (98), (0), (0), (0), (0), (0), (96), (102), (0), (1), (0), (0), (101), (0), (100), (100), (98), (67), (0), (5), (0), (5), (0), (97), (0), (97), (0), (101), (0), (101), (0), (0), (60), (99), (649), (101), (3), (0), (0), (0), (106), (0), (241), (0), (5), (0), (129), (123), (130), (63), (58), (130), (130), (571), (129), (0), (0), (266), (0), (60), (87), (1), (0), (95), (98), (0), (0), (0), (98), (98), (32), (164), (32), (0), (107), (0), (0), (103), (0), (97), (0), (106), (0), (0), (90), (0), (101), (95), (1), (1), (0), (106), (0), (0), (1), (103), (60), (0), (1), (13), (0), (0), (0), (0), (1), (76), (0), (0), (5), (0), (0), (155), (0), (104), (0), (0), (0), (0), (0), (0), (920), (560), (637), (0), (130), (130), (724), (129), (0), (0), (99), (95), (98), (0), (0), (0), (98), (1), (106), (1), (180), (1), (1), (0), (0), (5), (0), (2216), (0), (0), (0), (0), (98), (1), (0), (0), (5), (0), (0), (5), (0), (0), (0), (76), (0), (0), (0), (0), (1), (0), (0), (97), (0), (1), (80), (0), (0), (101), (0), (42), (46), (1), (0), (102), (0), (103), (0), (0), (0), (5), (0), (38), (76), (0), (0), (0), (0), (0), (76), (0), (1371), (0), (5), (0), (99), (96), (98), (0), (0), (0), (0), (0), (139), (138), (139), (139), (0), (0), (74), (0), (84), (22), (0), (0), (4296), (0), (1), (20), (0), (0), (5), (0), (0), (0), (0), (0), (60), (59), (0), (0), (1), (1), (0), (0), (0), (2), (43), (9), (0), (26), (98), (1), (0), (0), (5), (0), (0), (0), (63), (91), (0), (28), (90), (162), (0), (105), (0), (42), (30), (1), (80), (0), (0), (0), (1007), (0), (0), (60), (0), (99), (96), (98), (0), (84), (36), (0), (0), (48), (105), (0), (0), (102), (0), (106), (0), (60), (0), (99), (95), (98), (0), (0), (103), (0), (97), (0), (60), (0), (0), (1), (105), (60), (0), (101), (0), (106), (0), (89), (0), (106), (0), (5), (0), (0), (65), (110), (0), (111), (720), (0), (129), (123), (119), (130), (130), (326), (129), (0), (0), (103), (9), (84), (183), (98), (105), (103), (0), (1), (62), (1), (63), (64), (0), (1), (44), (0), (0), (0), (42), (44), (1), (83), (0), (0), (0), (97), (0), (0), (139), (137), (139), (0), (0), (60), (0), (103), (95), (102), (0), (0), (101), (0), (0), (5), (0), (99), (96), (98), (0), (1468), (0), (23), (0), (1), (0), (0), (5), (0), (95), (84), (78), (1), (0), (103), (0), (0), (0), (5), (0), (127), (38), (137), (76), (0), (0), (98), (60), (0), (99), (0), (5), (0), (98), (0), (98), (1), (99), (1), (0), (0), (3317), (0), (360), (433), (42), (22), (1), (0), (0), (60), (59), (0), (0), (0), (0), (0), (102), (0), (42), (28), (1), (80), (0), (0), (422), (0), (5), (0), (0), (0), (0), (0), (60), (0), (99), (96), (98), (0), (101), (0), (101), (0), (0), (0), (0), (0), (0), (103), (96), (0), (97), (0), (104), (1), (103), (0), (97), (98), (1), (99), (0), (0), (80), (0), (0), (1235), (0), (99), (1), (114), (1), (115), (0), (0), (0), (106), (0), (139), (0), (0), (138), (137), (139), (139), (221), (57), (0), (84), (40), (0), (0), (0), (60), (0), (103), (96), (102), (0), (0), (0), (0), (101), (0), (1), (1), (42), (21), (0), (73), (73), (0), (42), (66), (1), (75), (1), (0), (0), (255), (338), (369), (152), (257), (42), (1), (106), (0), (105), (0), (103), (60), (220), (53), (100), (0), (0), (60), (0), (103), (96), (0), (0), (103), (96), (102), (0), (1), (20), (0), (0), (1), (1), (1), (0), (60), (0), (99), (96), (0), (104), (1), (0), (0), (385), (1), (107), (107), (0), (97), (104), (0), (0), (98), (100), (103), (103), (0), (106), (0), (5), (0), (5), (0), (1), (0), (927), (728), (264), (379), (203), (762), (109), (0), (2598), (0), (0), (0), (3), (0), (0), (0), (139), (0), (137), (139), (0), (0), (104), (104), (0), (0), (0), (0), (0), (0), (95), (102), (0), (42), (73), (1), (75), (42), (74), (1), (75), (0), (542), (961), (1008), (0), (129), (123), (109), (130), (130), (214), (129), (0), (0), (103), (1), (0), (0), (84), (13), (30), (155), (0), (0), (0), (0), (106), (0), (98), (0), (5), (0), (5), (0), (130), (130), (337), (129), (56), (208), (0), (42), (1), (106), (1), (105), (42), (1), (106), (0), (102), (0), (4198), (0), (0), (0), (0), (42), (6), (1), (77), (0), (123), (129), (871), (130), (130), (584), (129), (0), (0), (0), (60), (0), (103), (0), (42), (71), (1), (76), (42), (2), (1), (76), (0), (139), (133), (133), (139), (0), (0), (105), (103), (0), (0), (5), (0), (5), (0), (60), (0), (103), (0), (3786), (0), (0), (129), (279), (130), (0), (77), (77), (1), (1), (0), (5), (0), (84), (13), (0), (84), (59), (0), (0), (0), (42), (47), (1), (83), (42), (0), (5), (0), (0), (0), (60), (0), (103), (0), (60), (1), (105), (0), (2757), (0), (54), (0), (0), (0), (0), (0), (1), (0), (0), (0), (102), (107), (0), (0), (226), (0), (0), (5), (0), (0), (104), (0), (5), (0), (170), (113), (222), (113), (93), (0), (97), (0), (0), (129), (130), (130), (130), (817), (129), (0), (0), (98), (1), (1), (0), (286), (0), (0), (4), (98), (98), (0), (42), (34), (1), (80), (0), (0), (103), (103), (32), (103), (32), (0), (71), (1), (1), (0), (0), (1), (0), (0), (60), (53), (102), (0), (0), (60), (1011), (0), (0), (97), (0), (5), (0), (1), (1), (0), (0), (0), (5), (0), (89), (0), (88), (0), (1), (11), (0), (1), (60), (53), (0), (1), (71), (71), (0), (1), (104), (437), (0), (104), (99), (1), (0), (60), (0), (103), (96), (0), (0), (98), (0), (0), (0), (97), (0), (0), (0), (1), (36), (0), (0), (99), (1), (111), (0), (0), (54), (9), (0), (60), (1), (53), (9), (0), (98), (0), (0), (0), (0), (0), (0), (98), (1), (34), (0), (0), (0), (84), (15), (0), (1), (0), (60), (0), (103), (96), (102), (0), (0), (0), (255), (0), (0), (100), (0), (106), (0), (4298), (0), (0), (0), (1), (80), (0), (0), (129), (123), (652), (130), (130), (966), (129), (0), (0), (154), (138), (5), (60), (0), (99), (95), (0), (1), (1), (1), (0), (11), (0), (1), (0), (0), (1894), (0), (0), (1), (109), (0), (427), (0), (107), (0), (1), (0), (0), (1), (1), (0), (1), (0), (0), (105), (0), (5), (0), (0), (0), (101), (0), (48), (105), (0), (101), (0), (5), (0), (0), (0), (0), (1), (1), (1), (6), (1), (8), (1), (0), (0), (90), (0), (0), (83), (84), (0), (0), (5), (0), (129), (0), (130), (171), (48), (130), (0), (26), (105), (100), (108), (26), (106), (100), (108), (0), (5), (0), (0), (0), (98), (0), (97), (87), (1), (98), (0), (0), (0), (100), (53), (102), (0), (1), (104), (0), (96), (98), (0), (0), (0), (0), (110), (0), (111), (111), (0), (106), (0), (0), (5), (0), (5), (0), (872), (267), (973), (853), (1053), (0), (60), (0), (103), (96), (0), (0), (0), (76), (0), (0), (0), (0), (0), (123), (129), (39), (130), (0), (0), (0), (84), (31), (0), (0), (0), (2383), (0), (1), (28), (1), (0), (0), (60), (0), (103), (96), (102), (0), (0), (1), (0), (107), (0), (60), (59), (0), (0), (0), (0), (42), (35), (1), (80), (42), (0), (0), (0), (0), (98), (2565), (0), (60), (0), (99), (0), (105), (0), (105), (1), (0), (0), (60), (0), (99), (96), (0), (2), (22), (1), (0), (0), (42), (38), (1), (0), (0), (0), (0), (0), (5), (0), (38), (76), (0), (0), (0), (99), (0), (0), (170), (84), (18), (16), (0), (0), (67), (1), (100), (100), (0), (5), (0), (0), (103), (32), (0), (1), (0), (1), (1), (0), (1), (1), (5), (0), (103), (0), (0), (0), (0), (0), (0), (84), (1), (107), (0), (470), (0), (0), (5), (0), (0), (0), (0), (0), (197), (0), (119), (0), (1), (1), (0), (0), (5), (0), (60), (0), (103), (0), (52), (2), (39), (83), (0), (1), (0), (0), (97), (0), (130), (130), (868), (129), (0), (0), (0), (0), (60), (59), (0), (0), (0), (1007), (0), (0), (94), (0), (1), (1), (1), (0), (0), (0), (0), (0), (177), (76), (33), (0), (0), (0), (0), (0), (97), (96), (1), (98), (0), (0), (5), (0), (102), (0), (1), (0), (0), (84), (14), (1), (92), (0), (0), (102), (0), (0), (60), (0), (0), (96), (98), (60), (0), (99), (96), (98), (0), (100), (0), (139), (0), (138), (139), (0), (0), (1), (20), (0), (0), (78), (1), (0), (0), (1), (1), (1), (1), (1), (1), (1), (1), (1), (0), (0), (0), (14), (1), (1), (0), (0), (139), (137), (139), (0), (0), (0), (0), (0), (0), (0), (0), (0), (0), (55), (2), (0), (42), (29), (1), (80), (0), (103), (0), (60), (0), (9), (0), (255), (0), (0), (0), (0), (5), (0), (0), (0), (67), (41), (100), (0), (102), (0), (5), (0), (98), (0), (0), (3656), (0), (106), (0), (0), (1), (0), (0), (42), (32), (1), (75), (0), (0), (106), (0), (60), (1), (53), (9), (2), (0), (0), (286), (0), (0), (4), (98), (98), (0), (58), (58), (58), (0), (0), (1), (35), (147), (137), (20), (108), (140), (21), (1), (0), (163), (113), (422), (0), (0), (0), (76), (0), (0), (278), (0), (100), (0), (106), (0), (89), (0), (42), (14), (1), (77), (0), (0), (76), (0), (0), (60), (19), (98), (0), (42), (10), (1), (77), (0), (1), (0), (0), (5), (0), (508), (42), (79), (0), (82), (42), (80), (0), (100), (0), (84), (79), (96), (0), (96), (102), (0), (1), (104), (1), (105), (437), (1), (104), (1), (105), (0), (5), (0), (84), (39), (0), (0), (0), (101), (0), (60), (0), (99), (0), (0), (101), (0), (1), (20), (0), (0), (1), (107), (0), (0), (129), (130), (130), (130), (519), (129), (0), (0), (0), (0), (84), (44), (0), (94), (0), (0), (0), (96), (102), (0), (60), (0), (103), (95), (102), (0), (105), (0), (0), (0), (1), (13), (1), (0), (98), (60), (0), (0), (42), (11), (1), (77), (0), (42), (33), (1), (81), (1), (0), (0), (84), (16), (0), (0), (0), (5), (0), (0), (84), (21), (0), (0), (431), (0), (0), (99), (236), (122), (90), (99), (96), (98), (0), (101), (102), (100), (104), (0), (0), (95), (98), (60), (0), (0), (105), (0), (0), (79), (0), (42), (78), (1), (0), (5), (0), (103), (9), (103), (103), (0), (0), (1), (44), (0), (0), (60), (0), (103), (96), (102), (60), (0), (103), (96), (102), (0), (0), (60), (1), (21), (99), (0), (84), (102), (1), (0), (106), (0), (0), (139), (137), (139), (0), (0), (0), (0), (92), (194), (232), (0), (87), (0), (60), (158), (0), (248), (155), (221), (228), (10), (99), (95), (98), (60), (0), (0), (111), (0), (0), (0), (0), (0), (0), (104), (0), (0), (0), (0), (105), (84), (1), (105), (0), (0), (106), (0), (5), (0), (99), (0), (0), (129), (130), (130), (130), (558), (129), (0), (0), (99), (96), (98), (0), (0), (101), (0), (0), (108), (0), (1), (0), (0), (0), (99), (0), (0), (5), (0), (98), (0), (0), (39), (1), (80), (0), (0), (1415), (0), (329), (0), (0), (55), (101), (0), (0), (89), (0), (250), (98), (44), (78), (1), (0), (5), (0), (97), (0), (3256), (0), (5), (0), (1), (95), (42), (85), (0), (4143), (0), (5), (0), (0), (48), (107), (0), (33), (89), (0), (0), (110), (0), (1), (42), (53), (1), (77), (0), (88), (104), (0), (0), (111), (0), (0), (60), (59), (0), (0), (0), (0), (0), (0), (26), (104), (100), (0), (60), (0), (103), (0), (0), (1), (106), (0), (0), (5), (0), (0), (129), (844), (130), (0), (0), (0), (144), (0), (60), (0), (103), (95), (102), (0), (5), (0), (3595), (0), (1), (34), (1), (0), (68), (109), (0), (109), (5), (0), (0), (5), (0), (103), (0), (97), (0), (129), (0), (130), (130), (130), (303), (129), (0), (0), (0), (139), (0), (138), (137), (139), (0), (0), (1681), (0), (139), (139), (139), (0), (0), (0), (0), (60), (53), (99), (0), (238), (99), (1), (110), (0), (0), (0), (114), (134), (89), (191), (253), (61), (100), (98), (86), (1), (1), (0), (0), (0), (0), (0), (60), (0), (0), (0), (84), (9), (0), (84), (10), (0), (84), (0), (0), (102), (0), (0), (0), (99), (1), (114), (1), (115), (0), (105), (0), (196), (0), (103), (0), (0), (99), (96), (98), (0), (0), (0), (105), (0), (5), (0), (0), (98), (1), (115), (0), (0), (5), (0), (0), (42), (9), (1), (77), (0), (0), (0), (139), (133), (133), (137), (139), (0), (0), (109), (106), (0), (0), (0), (1), (107), (0), (0), (0), (101), (0), (0), (0), (106), (60), (184), (183), (182), (56), (223), (157), (59), (103), (0), (0), (1), (36), (1), (1), (39), (0), (0), (5), (0), (38), (76), (0), (0), (0), (0), (0), (0), (0), (139), (139), (139), (0), (0), (87), (0), (1), (105), (60), (19), (103), (0), (0), (100), (0), (0), (1), (1), (0), (0), (1), (0), (0), (0), (115), (110), (0), (42), (27), (1), (75), (0), (0), (0), (5), (0), (44), (101), (0), (99), (100), (103), (0), (139), (133), (133), (139), (26), (84), (0), (5), (0), (5), (0), (100), (0), (0), (0), (0), (129), (160), (1), (36), (130), (130), (428), (129), (0), (0), (5), (0), (1), (0), (0), (0), (0), (0), (0), (0), (103), (0), (0), (0), (2026), (0), (5), (0), (102), (0), (101), (0), (80), (42), (25), (1), (0), (101), (60), (1011), (0), (0), (101), (155), (0), (0), (0), (0), (102), (97), (0), (5), (0), (0), (0), (85), (0), (0), (60), (0), (99), (96), (98), (0), (1), (0), (84), (18), (0), (0), (0), (0), (99), (1), (116), (0), (0), (1), (44), (1), (0), (0), (103), (0), (99), (1), (120), (0), (1), (195), (1), (172), (1), (1), (0), (95), (102), (0), (0), (5), (0), (0), (0), (0), (100), (427), (0), (109), (0), (67), (0), (0), (0), (0), (95), (102), (0), (0), (106), (0), (5), (0), (0), (1), (1), (0), (0), (0), (102), (105), (104), (0), (0), (0), (106), (0), (0), (0), (5), (0), (242), (82), (0), (3610), (0), (4533), (0), (97), (0), (2720), (0), (5), (0), (0), (0), (0), (0), (1), (105), (0), (0), (101), (0), (0), (0), (60), (0), (0), (72), (1), (1), (72), (1), (71), (0), (99), (1), (110), (0), (0), (129), (123), (130), (130), (130), (982), (875), (130), (130), (982), (129), (0), (0), (0), (0), (106), (0), (65), (0), (0), (0), (2559), (0), (167), (100), (98), (0), (0), (42), (68), (1), (0), (0), (0), (76), (0), (100), (60), (0), (99), (96), (98), (60), (0), (0), (0), (5), (0), (0), (1), (1), (0), (0), (99), (103), (0), (997), (0), (0), (0), (9), (104), (0), (9), (103), (0), (84), (26), (0), (0), (0), (1), (106), (104), (0), (0), (0), (106), (0), (84), (19), (0), (0), (5), (0), (0), (1), (105), (0), (139), (133), (0), (137), (133), (139), (242), (33), (0), (57), (0), (0), (0), (0), (98), (0), (42), (15), (1), (0), (42), (59), (1), (0), (60), (0), (103), (0), (5), (0), (1), (0), (0), (0), (0), (76), (0), (0), (5), (0), (130), (130), (807), (129), (0), (0), (102), (0), (101), (1), (103), (102), (101), (0), (60), (0), (103), (96), (102), (0), (96), (102), (60), (0), (0), (0), (0), (107), (86), (0), (0), (0), (1), (0), (0), (97), (0), (0), (0), (1003), (0), (1), (82), (42), (0), (109), (0), (60), (106), (107), (109), (0), (0), (0), (0), (1), (0), (0), (0), (0), (39), (40), (112), (157), (225), (48), (0), (5), (0), (5), (0), (0), (0), (0), (98), (0), (102), (0), (109), (697), (615), (480), (758), (0), (105), (99), (0), (107), (105), (101), (0), (1), (0), (0), (1), (105), (0), (102), (0), (0), (72), (0), (2635), (0), (42), (7), (1), (77), (0), (0), (0), (0), (0), (1), (1), (0), (0), (39), (33), (87), (0), (0), (0), (0), (0), (0), (100), (657), (0), (0), (42), (103), (1), (105), (0), (0), (5), (0), (60), (19), (102), (0), (0), (2303), (0), (98), (0), (0), (816), (2), (100), (0), (0), (0), (103), (101), (0), (0), (0), (0), (0), (105), (0), (621), (0), (60), (0), (99), (0), (44), (44), (42), (0), (0), (0), (1), (107), (0), (1), (0), (0), (104), (0), (0), (3219), (0), (2786), (0), (0), (0), (139), (138), (139), (0), (0), (255), (0), (0), (130), (130), (1027), (129), (0), (0), (0), (60), (0), (99), (95), (98), (0), (0), (60), (100), (1), (104), (102), (1), (0), (0), (139), (0), (137), (139), (0), (0), (99), (130), (130), (373), (129), (0), (0), (53), (99), (0), (1), (101), (0), (42), (30), (31), (174), (1), (81), (0), (1), (0), (0), (67), (75), (100), (100), (100), (0), (0), (1), (99), (1), (0), (0), (0), (41), (0), (0), (103), (96), (102), (60), (0), (0), (0), (1), (0), (0), (0), (5), (0), (100), (106), (106), (0), (0), (52), (1), (0), (0), (42), (63), (1), (80), (1), (0), (9), (9), (0), (9), (105), (0), (0), (103), (103), (0), (0), (5), (0), (0), (105), (0), (5), (0), (1620), (0), (0), (1), (63), (0), (0), (102), (0), (48), (102), (13), (84), (91), (112), (94), (115), (0), (0), (84), (55), (56), (0), (0), (78), (1), (0), (0), (0), (997), (0), (107), (107), (99), (1), (108), (108), (0), (3), (2973), (0), (77), (42), (13), (1), (0), (1), (0), (0), (0), (0), (0), (60), (0), (103), (96), (0), (0), (60), (0), (99), (0), (96), (102), (0), (97), (0), (193), (42), (58), (0), (77), (0), (0), (101), (0), (3477), (0), (0), (1), (1), (9), (0), (0), (0), (77), (0), (139), (0), (137), (139), (0), (0), (0), (0), (1156), (0), (42), (17), (0), (0), (105), (0), (48), (100), (0), (0), (84), (1), (105), (0), (102), (60), (0), (0), (100), (100), (100), (0), (5), (0), (99), (1), (115), (0), (5), (0), (1), (95), (42), (76), (0), (0), (60), (0), (0), (84), (80), (0), (0), (0), (5), (0), (0), (1), (107), (0), (99), (1), (108), (0), (102), (0), (1), (0), (0), (0), (60), (0), (0), (0), (2), (7), (2), (103), (104), (0), (5), (0), (0), (42), (103), (0), (105), (0), (97), (98), (1), (99), (0), (0), (0), (99), (1), (1), (0), (0), (5), (0), (101), (0), (103), (0), (0), (139), (133), (133), (139), (0), (0), (0), (0), (1), (1), (1), (9), (9), (105), (0), (60), (0), (99), (96), (98), (0), (0), (0), (1), (0), (0), (60), (53), (103), (0), (0), (0), (1), (102), (60), (53), (101), (0), (99), (0), (48), (88), (0), (99), (0), (0), (9), (104), (0), (0), (0), (0), (5), (0), (0), (0), (103), (42), (1), (104), (1), (103), (0), (3969), (0), (84), (20), (0), (0), (133), (139), (133), (139), (139), (10), (96), (0), (5), (0), (0), (0), (0), (0), (48), (58), (58), (0), (0), (103), (0), (5), (0), (87), (0), (588), (0), (104), (0), (3152), (0), (42), (18), (1), (77), (0), (807), (0), (95), (98), (0), (0), (75), (0), (0), (102), (0), (60), (0), (103), (96), (102), (0), (0), (138), (381), (106), (0), (0), (0), (139), (139), (139), (0), (0), (5), (0), (0), (0), (0), (0), (60), (1011), (0), (0), (0), (0), (0), (0), (99), (95), (98), (0), (109), (0), (0), (89), (0), (0), (0), (0), (24), (100), (100), (100), (0), (101), (0), (97), (0), (0), (0), (99), (95), (98), (0), (84), (68), (0), (85), (84), (58), (0), (139), (139), (139), (0), (0), (60), (0), (99), (95), (0), (159), (14), (101), (0), (110), (933), (110), (104), (0), (0), (0), (103), (60), (0), (0), (76), (0), (0), (106), (0), (4207), (0), (0), (129), (130), (130), (0), (1), (0), (0), (103), (0), (0), (106), (0), (48), (107), (0), (60), (0), (103), (96), (102), (0), (60), (0), (103), (96), (102), (0), (97), (101), (1), (106), (0), (5), (0), (1), (28), (0), (0), (105), (0), (84), (53), (0), (84), (0), (123), (129), (130), (130), (130), (903), (129), (0), (0), (0), (1), (0), (0), (60), (0), (99), (96), (98), (0), (0), (139), (0), (0), (137), (138), (139), (0), (0), (0), (100), (100), (1), (0), (0), (0), (102), (84), (1), (101), (0), (101), (0), (0), (1), (0), (101), (0), (0), (1), (1), (9), (9), (105), (0), (0), (0), (102), (0), (139), (0), (139), (137), (139), (0), (0), (958), (109), (38), (76), (0), (40), (1), (82), (0), (1578), (0), (1), (1), (0), (0), (1), (1), (1), (0), (0), (0), (86), (84), (32), (0), (84), (27), (0), (34), (0), (0), (0), (0), (5), (0), (0), (0), (60), (59), (171), (157), (193), (0), (0), (114), (1), (115), (0), (0), (101), (0), (5), (0), (29), (1), (1), (0), (89), (0), (0), (109), (0), (0), (1), (0), (0), (0), (103), (129), (123), (130), (130), (130), (307), (129), (0), (0), (1), (0), (0), (0), (0), (100), (0), (16), (474), (76), (0), (101), (0), (106), (0), (1), (0), (0), (129), (123), (130), (130), (0), (1838), (0), (1002), (0), (107), (0), (3776), (0), (84), (96), (102), (0), (0), (0), (56), (1), (53), (0), (183), (84), (91), (1), (108), (0), (0), (2321), (0), (60), (0), (103), (96), (102), (60), (0), (129), (0), (554), (130), (0), (60), (19), (99), (0), (1), (0), (60), (107), (108), (109), (0), (0), (60), (0), (99), (96), (0), (60), (87), (1), (109), (107), (816), (2), (0), (0), (60), (0), (103), (0), (60), (0), (103), (0), (60), (108), (106), (0), (0), (103), (96), (102), (0), (1), (1), (72), (1), (1), (72), (1), (71), (1), (71), (1), (0), (0), (5), (0), (0), (5), (0), (0), (0), (0), (0), (0), (0), (1034), (0), (5), (0), (89), (0), (0), (0), (0), (60), (0), (103), (0), (102), (0), (130), (130), (767), (129), (0), (0), (0), (0), (1), (104), (1), (0), (100), (100), (98), (0), (0), (2), (0), (42), (1), (0), (5), (0), (436), (0), (106), (0), (5), (0), (97), (0), (106), (1), (107), (0), (11), (11), (1), (11), (0), (84), (34), (0), (0), (0), (101), (0), (0), (84), (46), (0), (0), (133), (139), (133), (139), (0), (0), (105), (0), (1), (1), (1), (0), (60), (87), (1), (100), (98), (0), (87), (0), (0), (0), (5), (0), (98), (0), (0), (0), (103), (0), (0), (42), (1), (101), (1), (100), (42), (1), (101), (0), (100), (0), (385), (1), (98), (0), (255), (0), (0), (0), (0), (1), (1), (1), (0), (0), (0), (0), (103), (27), (0), (0), (0), (0), (0), (0), (0), (60), (0), (0), (60), (0), (103), (96), (102), (0), (113), (113), (0), (0), (42), (102), (1), (0), (0), (0), (84), (33), (0), (0), (0), (99), (1), (114), (0), (0), (99), (1), (115), (0), (0), (0), (101), (0), (0), (0), (108), (0), (0), (5), (0), (0), (0), (101), (0), (0), (42), (19), (1), (77), (0), (5), (0), (104), (0), (42), (26), (1), (0), (0), (105), (0), (59), (0), (0), (0), (0), (0), (98), (0), (0), (104), (0), (0), (0), (0), (0), (0), (83), (90), (0), (60), (0), (99), (0), (5), (0), (21), (102), (2), (0), (42), (1), (104), (1), (0), (2), (6), (2), (103), (104), (0), (0), (0), (99), (1), (115), (0), (0), (0), (0), (0), (95), (98), (0), (60), (0), (103), (96), (102), (0), (0), (78), (1), (0), (0), (123), (129), (844), (130), (130), (974), (129), (0), (0), (0), (101), (0), (100), (0), (129), (895), (130), (130), (824), (129), (0), (0), (102), (60), (0), (103), (96), (102), (0), (5), (0), (106), (78), (1), (0), (0), (60), (0), (99), (95), (0), (126), (42), (50), (72), (1), (75), (0), (0), (0), (0), (0), (1), (1), (0), (5), (0), (0), (0), (13), (93), (110), (0), (0), (102), (0), (5), (0), (60), (59), (0), (0), (0), (1), (95), (42), (89), (98), (1), (45), (0), (106), (0), (48), (105), (0), (1), (51), (107), (108), (0), (95), (98), (0), (0), (1), (0), (0), (101), (0), (0), (0), (84), (29), (0), (0), (0), (110), (0), (0), (64), (98), (0), (0), (0), (300), (0), (0), (0), (99), (1), (120), (0), (0), (60), (0), (103), (96), (102), (0), (103), (0), (102), (0), (1), (104), (0), (0), (105), (0), (42), (20), (0), (0), (0), (5), (0), (1), (72), (1), (71), (71), (0), (0), (60), (0), (99), (96), (98), (60), (0), (107), (0), (101), (105), (0), (104), (0), (0), (0), (5), (0), (0), (0), (102), (77), (0), (0), (0), (140), (109), (106), (176), (157), (119), (0), (3079), (0), (0), (102), (0), (0), (60), (1011), (0), (0), (102), (60), (1011), (0), (0), (102), (1), (0), (105), (0), (100), (3), (0), (0), (5), (0), (106), (0), (0), (7), (0), (1), (1), (0), (42), (36), (1), (82), (0), (0), (0), (0), (103), (0), (105), (0), (27), (0), (0), (0), (0), (0), (0), (5), (0), (109), (107), (0), (0), (0), (329), (350), (0), (0), (0), (0), (0), (0), (96), (102), (0), (5), (0), (0), (1), (0), (5), (0), (100), (0), (0), (98), (0), (1), (103), (0), (902), (328), (413), (0), (95), (42), (81), (0), (102), (0), (99), (0), (106), (0), (129), (123), (0), (22), (130), (130), (724), (130), (130), (0), (105), (0), (0), (0), (0), (0), (0), (103), (42), (1), (0), (60), (0), (103), (96), (102), (0), (0), (84), (73), (0), (84), (0), (1724), (0), (1), (36), (0), (0), (0), (0), (0), (1311), (0), (77), (0), (0), (42), (1), (101), (1), (100), (0), (101), (0), (133), (139), (133), (139), (139), (0), (0), (101), (0), (5), (0), (0), (60), (1), (0), (1), (0), (0), (0), (0), (99), (1), (0), (0), (443), (0), (1), (1), (0), (0), (0), (0), (0), (99), (1), (0), (105), (0), (1), (0), (0), (106), (0), (0), (0), (0), (1), (100), (0), (0), (0), (0), (99), (96), (98), (0), (5), (0), (103), (0), (0), (0), (99), (1), (106), (0), (5), (0), (1), (76), (0), (0), (0), (0), (1), (0), (0), (0), (101), (0), (0), (0), (0), (98), (0), (99), (1), (0), (0), (0), (0), (101), (0), (0), (106), (0), (101), (0), (130), (130), (184), (129), (0), (0), (0), (88), (0), (77), (0), (0), (0), (0), (427), (0), (110), (0), (2), (0), (0), (3793), (0), (0), (0), (106), (0), (110), (0), (101), (0), (60), (0), (99), (0), (1799), (0), (5), (0), (22), (1), (1), (0), (1), (87), (0), (0), (0), (0), (103), (0), (104), (0), (0), (84), (63), (0), (0), (0), (1), (1), (1), (0), (0), (0), (101), (0), (0), (0), (101), (1), (0), (1), (107), (0), (0), (0), (5), (0), (0), (1), (1), (0), (60), (85), (91), (0), (0), (0), (0), (0), (97), (0), (96), (98), (0), (0), (0), (0), (1), (46), (1), (47), (1), (0), (5), (0), (5), (0), (0), (0), (76), (0), (0), (0), (0), (5), (0), (103), (0), (0), (0), (0), (98), (60), (205), (85), (41), (100), (250), (187), (159), (103), (0), (58), (1), (618), (1), (58), (58), (51), (0), (96), (102), (0), (0), (5), (0), (0), (197), (0), (114), (114), (0), (84), (43), (0), (0), (0), (0), (84), (6), (0), (0), (0), (84), (38), (1), (0), (98), (0), (0), (5), (0), (1), (197), (21), (70), (98), (2), (0), (0), (0), (0), (104), (0), (0), (1), (82), (1), (0), (101), (0), (99), (0), (0), (106), (0), (105), (0), (1), (104), (0), (1), (99), (37), (60), (214), (87), (1), (101), (99), (0), (4604), (0), (42), (98), (1), (0), (1), (106), (0), (5), (0), (99), (1), (114), (0), (0), (0), (0), (99), (1), (106), (0), (101), (0), (43), (0), (0), (0), (0), (0), (99), (96), (98), (60), (0), (99), (0), (1), (66), (1), (1), (1), (1), (0), (0), (106), (0), (0), (0), (60), (0), (99), (95), (98), (0), (5), (0), (3288), (0), (0), (0), (1), (1), (0), (0), (0), (0), (0), (0), (0), (99), (0), (0), (197), (0), (113), (113), (0), (0), (0), (97), (0), (0), (99), (95), (98), (0), (1), (0), (0), (1), (0), (0), (0), (0), (105), (0), (84), (1), (108), (0), (0), (385), (0), (98), (97), (98), (0), (42), (1), (104), (1), (103), (42), (0) }; t.n = 4626; return t end)(), (function() local t = { (nil), (nil), (70), (nil), (nil), (nil), (nil), (9), (nil), (nil), (nil), (nil), (111), (nil), (nil), (nil), (nil), (2729), (2729), (2729), (4246), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (255), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (369), (nil), (-25197), (nil), (1236), (nil), (nil), (nil), (nil), (nil), (3), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (0), (-8), (nil), (nil), (0), (-4), (nil), (nil), (117), (nil), (nil), (nil), (105), (nil), (nil), (nil), (nil), (72), (nil), (nil), (nil), (nil), ("gsub"), (nil), (107), (nil), (nil), (1), (66), (nil), (nil), (nil), (nil), (nil), (nil), (2), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (9), (nil), (nil), (91), (nil), (77), (nil), (nil), (nil), (nil), (12), (nil), (nil), (24), (76), (nil), (94), (nil), (1178022828), (2995308416), (nil), (nil), (nil), (39), (nil), (80), (nil), (79), (nil), (72), (nil), (113), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (123), (nil), (51), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (261), (nil), (nil), (-23355), (nil), (4224), (nil), (nil), (nil), (nil), (nil), (nil), (105), (nil), (2), (nil), (76), (176), (50), (nil), (nil), (nil), (nil), (0), (nil), (52), (nil), (nil), (8), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (1), (nil), (nil), (nil), (nil), (152), (nil), (nil), (nil), (10), (nil), (17), (nil), (nil), (nil), (117), (nil), (0), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (126), (nil), (7), (0), (4), (nil), (nil), (nil), (nil), (nil), (nil), (-18536), (nil), (3584), (nil), (nil), (nil), (20), (nil), (78), (294), (108), (nil), (1), (nil), (1), (nil), (1), (1), (83), (nil), (2), (nil), (nil), (nil), (126), (439), (81), (nil), (23), (97), (nil), (50), (nil), (nil), (108), (nil), (21), (nil), (nil), (0), (3), (0), (nil), (1), (9), (nil), (nil), (nil), (91), (nil), (90), (nil), (nil), (nil), (nil), (nil), (44), (nil), (2), (nil), (89), (nil), (0), (6), (nil), (nil), (nil), (nil), (0), (3), (0.25), (-6), (nil), (nil), (nil), (nil), (nil), (17), (nil), (nil), (22), (nil), (35), (370), (nil), (nil), (nil), (nil), (635), (635), (845), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (14), (nil), (3), (nil), (71), (nil), (0.5), (-3), (0), (nil), (nil), (nil), (858), (nil), (1), (1), (122), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (90), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (30), (nil), (93), (nil), (26), (nil), (0.66666668653488159), (nil), (nil), (nil), (nil), (3), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (109), (nil), (nil), (nil), (nil), (16), (nil), (nil), (58), (nil), (nil), (86), (nil), (nil), (33), (nil), (108), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (178), (nil), (107), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (23), (nil), (-24044), (nil), (4387), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (51), (nil), (52), (nil), (nil), (nil), (39), (nil), (22), (nil), (nil), (nil), (nil), (42), (nil), (113), (nil), (nil), (nil), (nil), (nil), (nil), (763), (1567), (nil), (nil), (nil), (nil), (nil), (11), (nil), (nil), (nil), (294), (nil), (nil), (27), (nil), (nil), (4), (nil), (nil), (nil), (nil), (nil), (nil), (22), (94), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (23), (nil), (72), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (98), ("nfdnormalize"), (101), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (82), (nil), (8), (nil), (nil), (481), (1405), (nil), (1281), (nil), (81), (nil), (nil), (nil), (26), (nil), (104), (nil), (nil), (nil), (74), (nil), (32), (nil), (78), (nil), (nil), (nil), (nil), (16), (nil), (nil), (170), (nil), (369), (nil), (280), (1150), (nil), (nil), (nil), (nil), (11), (nil), (115), (nil), (nil), (155), (nil), (nil), (nil), (nil), (125), (nil), (87), (nil), (nil), (109), (nil), (nil), (nil), (nil), (121), (nil), (120), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1868), (1868), (1868), (2087), (nil), (nil), (nil), (nil), (nil), (nil), (89), (nil), (nil), (nil), (nil), (7), (nil), (nil), (1209), (nil), (450), (nil), (nil), (69), (70), (nil), (nil), ("getmetatable"), (nil), (nil), (nil), (nil), (nil), (79), (nil), (1), (8), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (128), (nil), ("NextUnitVector"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (23), (nil), (nil), (nil), (11), (nil), (nil), (17), (nil), (6), (nil), (49), (1), (1), (nil), (nil), (nil), (nil), (8), (nil), (nil), (1), (89), (nil), (nil), (137), (nil), (nil), (50), (nil), (nil), (nil), (121), (nil), (nil), (1), (nil), (nil), (nil), (nil), (111), (nil), (13), (nil), (9), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (362), (nil), (nil), (nil), (23), (nil), (nil), (nil), (925), (2842), (nil), (nil), (nil), (nil), (nil), (nil), (0), (83), (83), (nil), (13), (nil), (nil), (nil), (nil), (75), (nil), (nil), (nil), (76), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (395), (nil), (-29929), (nil), (4004), (nil), (nil), (nil), (1), (43), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (99), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (-22481), (nil), (2598), (nil), (nil), (nil), (nil), (129), (nil), (129), (nil), (nil), (130), (nil), (nil), (nil), (nil), (nil), (nil), (46), (nil), (nil), (nil), (nil), (5), (nil), (nil), (nil), (nil), (94), (nil), (-4974), (nil), (201), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (80), (nil), (nil), (nil), (81), (nil), (nil), (nil), (nil), (2048), (3925), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (108), (nil), (nil), (nil), (nil), (1), (1), (nil), (82), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (90), (nil), (nil), (nil), (45), (nil), (nil), (nil), (8), (nil), (66), (nil), (nil), (nil), (nil), (nil), (nil), (105), (nil), (nil), (nil), (nil), (nil), (33), (nil), (nil), (39), (nil), (1), (56), (136), (80), (nil), (50), (nil), (nil), (nil), (nil), (nil), (80), (nil), (791), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (98), (nil), (nil), (nil), (248), (nil), (-17254), (nil), (2977), (nil), (nil), (nil), (99), (100), (nil), (nil), (1), (-1), (nil), (nil), (nil), (nil), (nil), (nil), (33), (nil), (51), (nil), (2), (4), (nil), (7), (nil), (nil), (nil), (56), (57), (nil), (nil), (28), (72), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (1), (38), (nil), (nil), (27), (nil), (nil), (nil), (nil), (nil), (6), (nil), (nil), (143), (nil), (nil), (nil), (55), (nil), (nil), (nil), (146), (nil), (nil), (nil), (nil), (nil), (121), (nil), (nil), (nil), (nil), (10), (nil), (nil), (nil), (nil), (nil), (nil), (76), (nil), (480), (nil), (33), (nil), (108), (nil), (nil), (121), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (53), (nil), (nil), (nil), (nil), (2), (nil), (nil), (36), (281), (71), (nil), (29), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (95), (nil), (nil), (nil), (nil), (8), (nil), (nil), (nil), (10), (nil), (nil), (nil), (96), (nil), (126), (nil), (nil), (nil), (74), (nil), (89), (nil), (nil), (nil), (nil), (nil), (133), (nil), (-26669), (nil), (4540), (nil), (nil), (nil), (nil), (89), (nil), (nil), (nil), (21), (nil), (nil), (1), (1), (nil), (nil), (nil), (1), (47), (nil), (nil), (nil), (nil), (120), (nil), (nil), (nil), (0.0625), (nil), (nil), (1), (91), (nil), (19), (20), (nil), (54), (125), (nil), (92), (nil), (nil), (nil), (nil), (nil), (47), (nil), (nil), (nil), (nil), (249), (nil), (62), (nil), (nil), (nil), (nil), (3), (4), (5), (nil), (1), (nil), (1), (nil), (nil), (nil), (80), (nil), (nil), (nil), (7), (nil), (nil), (nil), (nil), (nil), (nil), (182), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (22), (nil), (50), (nil), (nil), (nil), (nil), (nil), (123), (nil), (nil), (nil), (112), (nil), (nil), (nil), (nil), (166), (nil), (nil), (12), (nil), (102), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (19), (nil), (-3), (nil), (nil), (0), (1), (0), (7), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (55), (nil), (nil), (nil), (26), (nil), (27), (nil), (nil), (nil), (nil), (nil), (20), (nil), (nil), (nil), (1), (nil), (105), (nil), (nil), (nil), (404), (nil), (nil), (nil), (nil), (nil), (32), (nil), (nil), (nil), (23), (339), (79), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (65), (nil), (nil), (1), (7), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (47), (nil), (nil), (nil), (nil), (91), (nil), (nil), (0), (0), (0), (nil), (nil), (nil), (nil), (0.5), (9), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (98), (nil), (3469019433), (nil), (nil), (nil), (105), (9), (nil), (nil), (163), ([[

				 .@%(/*,.......      ...,,*/(#%&@@.
			 (*   ,/(#%%&&@@@@&%((////(((##%###((/**,,.     ,//(&.
		   /* .%@@@@@@@@%,  .(&@@@&&&&&&@@@@@@&#(*,........*%@@@(.  ,#.
		 */ .&@@@@@@@*  (%,   *(&&@@@@@&%(*,.             .,*(#%(*@@&*  *,
		#, /@@@@@@* *&( ,&&/.,/#%&&@@@&(&@@@@@@@@@@@@#*,.....,/&@@@@@@@@( .%
	   #  #@@@@@*/@% .#%./(,.,/*,//*,.,/(*@@@@@@@@@@@@%@@@@@@@@@#.#@@@@@@&. %
	  /  &@@@@@@@@(%@# *&&*&@@@@#/&@@@@/%%.,%@@@@@@@%/@@&(,  ,,,...  *%@@@# *
	#  .&@@@@@@@@@@@,((%@@@@@#.    ,&@@#@@&* .&@@@@@&,.#@@@@/&@@%(@@@&(/,(&, /,
 (/   (@&&&%&@@@&/, ,@#(@@@@,        #@@/,&@& /@@@@@,%#%@@@@@(     *@@@@@&,%%. .
/  #/,#@@@&#(//#@@@/ %@@@&@@@(.    ,&@@(.*/*  %@@*   %@@@@@@%       (@@&(*...%&.
 ///@@&,  (&@@#,   /@/ ,*&@@@@#&@@%#%((%@&* /@@@@@@&. #@@@#&@@@&%%@@@@@@&,/(*@/#
%%.&@# .&@@@# /@@@@%&@@@&/.   ,/((/*,  ./&@@@@@@@@@@,*&(./%@@#*&@@@(#(....,&#*@/
@%.&& .&@@@&*    /&@@@@@@@@@@@@@@@@&@@#/(%@@@@@@@@@@&,  (@@@@@@@@@@@@/,@@@@@#.&*
&&,%% .&*    /@@@(.  ,(@@@@@&/(////#( /&@@@@@@@@@@@@@@@(  ,&@@@@@@@@&, (@@&*/@(/
.%*#@( /@@@@( *@@@@@@/     *%@@@@@@@&.,@& ,#, .&@@@@@@# .#*%&/,#@@@@*   *@@&/*&*
 .&/.#@@@@@@@,   *&@@%.,&@@&(,    ,(%@%&@@@@@@@@@(.*,  /@@@@@@@@@&,      %@@@@..
@* .%@@@@@@@@(       .   (@@@@@@@@(       .*(%&@@@@@@@@@@@@&(,  ./.*@%   /@@% ./
  @* .&@@@@@@&.             ./&@@@*.&@@@@@@@&, ,**,.    .,*(&(.%@@# %@*  ,@@% ,#
	&, /@@@@@@*                    .#@@@@@@@@*.%@@@@@(,@@@@@@& ,%(.      .&@% ,#
	  / *@@@@@#                                                           %@&.,#
	  (( .&@@@@*                                                          #@&.,#
	   .&. ,&@@@,                                                         (@&.,#
		  #. .%@@* /@@/                                                   /@&.,(
			./  #@%. %@&,,#,                                              /@@,./
			  *(  #@%. . (@@@@@%/,                                        /@@,.*
				//  %@&, *@@@@@@@@( (@%/.                                 #@@, (
				  #* .&@@#. (@@@@&.*@@@@@@@@%. */.                  *..%*.&@@, /
					@* .%@@@%, ,/ .@@@@@@@@@@,.%@@@@@% .&@@@* #@&..&@*,* %@@&. *
					   /  *&@@@@%,   *(&@@@@&. #@@@@@* #@@@% (@@* ,.   /@@@@* (
						 @#. .#@@@@@@&(,.                      .,*(%&@@@@@&..(
							 &(.   ./%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@(. ((
								  ,#/*.       ..,,,,,,,,....          ,/#

]]), (164), (164), (nil), (165), (1), (nil), (nil), (nil), (nil), (nil), (94), (176), (82), (nil), (nil), (149), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0.1428571492433548), (nil), (nil), (1), (1), (104), (nil), (117), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (21), (59), (nil), (94), (nil), (nil), (-26515), (nil), (1168), (nil), (nil), (nil), (69), (nil), (nil), (nil), (nil), (49), (nil), (0.3333333432674408), (nil), (nil), (nil), (1), (1), (1), (96), (328), (nil), (-8), (nil), (nil), (nil), (nil), (0), (2), (0), (-4), (nil), (nil), (nil), (124), (nil), (39), (nil), (123), (nil), (58), (nil), (1), (98), (nil), (nil), (nil), (1), (nil), (22), (nil), (141), (nil), (119), (nil), (nil), (nil), (7), (nil), (nil), (nil), (nil), (14), (nil), (nil), (13), (nil), (nil), (nil), (3909), (1777), (nil), (nil), (16), (nil), (105), (nil), (nil), (125), (nil), (nil), (1), (1), (1), (1), (1), (1), (1), (1), (1), (nil), (32), (nil), (nil), (1), (1), (nil), (nil), (nil), (1598), (1909), (nil), (nil), (nil), (nil), (nil), (1), (9), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (27), (nil), (nil), (nil), (nil), (nil), (9), (nil), (nil), (nil), (nil), (33), (nil), (nil), (83), (nil), (225), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (68), (nil), (nil), (29), (nil), (nil), (nil), (87), (nil), (nil), (1), (42), (nil), (nil), (nil), (73), (nil), (71), (nil), (110), (nil), (nil), (152), (nil), (nil), (nil), (nil), (nil), (nil), (1), (-1), (nil), (nil), (nil), (nil), (2), (8), (nil), (87), (nil), (18), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (nil), (0), (3), (nil), (nil), (0), (nil), (nil), (nil), (8), (nil), (99), (nil), (nil), (nil), (nil), (nil), (12), (nil), (91), (nil), (nil), (122), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (6), (nil), (nil), (92), (112), (nil), (30), (nil), (nil), (nil), (nil), ("wait"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (19), (nil), (nil), (147), (nil), (145), (nil), (nil), (148), (nil), (145), (nil), (nil), (89), (nil), (nil), (nil), (nil), (72), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (126), (nil), (15), (nil), (52), (nil), (105), (nil), (nil), (nil), (nil), (132), (nil), (-848), (nil), (1782), (nil), (nil), (1833939216), (nil), (nil), (nil), (nil), (nil), (nil), (70), (nil), (6), (nil), (nil), (nil), (nil), (nil), (24), (nil), (nil), (56), (nil), (82), (nil), (11), (nil), (12), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (10), (nil), (nil), (nil), (nil), (29), (nil), (1), (76), (nil), (nil), (nil), (nil), (68), (nil), (56), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (9), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (7), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (nil), (nil), (91), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (41), (nil), (125), (nil), (nil), (nil), (nil), (17), (nil), (nil), (nil), (nil), (16), (nil), (nil), (nil), (nil), (114), (nil), (nil), (nil), (nil), (nil), (1), (nil), (93), (nil), (nil), (nil), (4543), (1155), (nil), (nil), (nil), (nil), (nil), (nil), (80), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (5), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (108), (nil), (472), (nil), (nil), (96), (nil), (137), (87), (nil), (nil), (134), (nil), (nil), (nil), (91), (nil), (100), (nil), (nil), (nil), (nil), (nil), (67), (nil), (-4795), (nil), (2393), (nil), (nil), (nil), (19), (nil), (nil), (nil), (175), (nil), (nil), (nil), (nil), (83), (71), (nil), (nil), (nil), (113), (nil), (59), (nil), (nil), (nil), (nil), (nil), (39), (nil), (118), (nil), (nil), (nil), (nil), (nil), (76), (nil), ("Parent"), (nil), (nil), (163), (nil), (nil), (nil), (nil), (nil), (125), (nil), (33), (nil), (48), (nil), (nil), (nil), (nil), (nil), (91), (nil), (nil), (nil), (nil), (nil), (nil), (76), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (212), (nil), (84), (nil), (nil), (85), (nil), (nil), (nil), (nil), (nil), (nil), (20), (nil), (nil), (nil), (nil), (32), (240), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (107), (nil), (nil), (nil), (57), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (23), (nil), (nil), (17), (nil), (nil), (nil), (30), (nil), (31), (nil), (nil), (nil), (nil), (nil), (72), (nil), (nil), (109), (nil), (174), (nil), (97), (nil), (nil), (nil), (98), (nil), (-26728), (nil), (2689), (nil), (nil), (nil), (nil), (nil), (4609), (4609), (2113), (nil), (nil), (nil), (nil), (nil), (336), (3152), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (122), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (1), (nil), (nil), (74), (nil), (94), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (77), (nil), (181), (nil), (nil), (122), (nil), (120), (nil), (nil), (nil), (nil), (nil), (nil), (76), (nil), (nil), (nil), (22), (nil), (13), (nil), (117), (1), (nil), (98), (nil), (81), (nil), (120), (nil), (nil), (nil), (52), (nil), (nil), (nil), (nil), (7), (nil), (53), (nil), (nil), (nil), (nil), (4219), (4219), (1227), (nil), (nil), (nil), (nil), (0), (nil), (nil), (153), (nil), (nil), (61), (nil), (176), (nil), (121), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (34), (nil), (35), (36), (nil), (nil), (-8), (nil), (nil), (nil), (nil), (0), (-8), (0.375), (5), (nil), (nil), (nil), (nil), (2485), (1756), (nil), (nil), (258), (nil), (104), (nil), (nil), (nil), (nil), (nil), (167), (nil), (13), (nil), (1), (1), (10), (nil), (1), (40), (107), (67), (nil), (96), (nil), (nil), (nil), (77), (nil), (17), (nil), (nil), (nil), (nil), (nil), (146), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (4028), (4605), (nil), (nil), (nil), (nil), (nil), (122), (nil), (126), (nil), (328), (nil), (nil), (nil), (nil), (465), (nil), (nil), (-2039), (nil), (2695), (nil), (nil), (121), (nil), (1), (2), (169), (97), (nil), (86), (nil), (nil), (10), (nil), (433), (nil), (nil), (nil), (122), (nil), (7), (nil), (204), (nil), (nil), (nil), (nil), (25), (nil), (nil), (nil), (nil), (nil), (0.14363916737736382), (nil), (nil), (nil), (40), (125), (71), (nil), (nil), (nil), (33), (nil), (nil), (-32071), (nil), (58), (nil), (nil), (nil), (nil), (13), (nil), (nil), (40), (nil), (nil), (nil), (nil), (83), (nil), (90), (nil), (122), (nil), (nil), (nil), (42), (nil), (43), (nil), (nil), (102), (nil), (nil), (122), (nil), (nil), (1), (nil), (1), (nil), (1), (1), (nil), (1), (nil), (nil), (nil), (121), (nil), (nil), (165), (61), (nil), (nil), (0.63636362552642822), (nil), (nil), (nil), (56), (nil), (101), (nil), (6), (nil), (nil), (nil), (nil), (nil), (125), (nil), (nil), (1), (1), (65), (462), (107), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (268), (nil), (104), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (47), (nil), (nil), (nil), (nil), (nil), (130), (nil), (122), (nil), (nil), (nil), (nil), (98), (nil), (nil), (nil), (nil), (58), (46), (nil), (59), (nil), (nil), (nil), (121), (nil), (nil), (nil), (nil), (nil), (171), (nil), (-12264), (nil), (392), (nil), (-24269), (nil), (2055), (nil), (nil), (nil), (801), (nil), (nil), (nil), (22), (nil), (nil), (nil), (nil), (nil), (2533944237), (nil), (111), (nil), (nil), (nil), (88), (nil), (6), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (15), (nil), (nil), (nil), (nil), (nil), (76), (nil), (nil), (1), (1), (1), (nil), (nil), (nil), (nil), (nil), (0.5), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (109), (nil), (105), (nil), (nil), (13), (nil), (nil), (104), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (127), (nil), (nil), (nil), (nil), (nil), (2939), (2939), (1134), (nil), (nil), (nil), (nil), (nil), (33), (396), (121), (nil), (nil), (nil), (nil), (16), (nil), (nil), (nil), (50), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (19), (nil), (9), (nil), (nil), (0), (nil), (6), (nil), (nil), (-27681), (nil), (1076), (nil), (nil), (176), (nil), (nil), (162), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (21), (nil), (nil), (24), (nil), (nil), (nil), (475), (nil), (116), (nil), (nil), (nil), (72), (nil), (1), (103), (nil), (90), (nil), (nil), (nil), (nil), (nil), (91), (nil), (nil), (nil), (nil), (81), (nil), (nil), (nil), (nil), (nil), (115), (nil), (nil), (1), (36), (86), (25), (nil), (nil), (nil), (nil), (nil), (535), (nil), (nil), (94), (nil), (nil), (nil), (423), (nil), (nil), (nil), (nil), (4), (0), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (58), (nil), (144), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (86), (nil), (27), (nil), (nil), (33), (nil), (1), (1), (95), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (174), (61), (nil), (nil), (nil), (nil), (nil), ("Clone"), (131), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (58), (nil), (nil), (nil), (nil), (87), (178), (91), (nil), (nil), (nil), (1401), (nil), (909), (nil), (111), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (56), (nil), (nil), (120), (nil), (nil), (1), (119), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (3271), (2830), (nil), (nil), (nil), (nil), (nil), (nil), (-13425), (nil), (1815), (nil), (nil), (79), (nil), (nil), (nil), (19), (nil), (nil), (nil), (nil), (nil), (105), (nil), (nil), (1), (102), (nil), (nil), (nil), (3848), (4159), (nil), (nil), (nil), (nil), (-25363), (nil), (1042), (nil), (nil), (nil), (nil), (nil), (107), (nil), (nil), (nil), (nil), (nil), (nil), (31), (nil), (nil), (1), (109), (nil), (nil), (nil), (nil), (11122353), (1522207), (nil), (nil), (1), (nil), (1), (nil), (39), (nil), ("getinfo"), (77), (nil), (nil), (24), (nil), (nil), (nil), (nil), (nil), (1), (nil), (54), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (48), (74), (nil), (nil), (nil), (52), (nil), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (3), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (172), (nil), (4), (nil), (nil), (nil), (nil), (50), (nil), (74), (nil), (7), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (82), (nil), (nil), (nil), (12), (nil), (nil), (119), (nil), (nil), (106), (nil), (0.25), (nil), (nil), (nil), (121), (nil), ("Scale"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (11), (nil), (96), (125), (nil), (nil), (69), (nil), (nil), (nil), (nil), (4), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (89), (nil), (nil), (nil), (nil), ("setfenv"), (nil), (5), (nil), (262), (nil), (nil), (nil), (nil), (158), (159), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (4316), (1833), (nil), (nil), (88), (nil), (nil), (nil), (nil), (nil), ("sub"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (136), (nil), (nil), (nil), (nil), (nil), (nil), (419872559), (3004856468), (769292275), (nil), (108), (nil), (nil), (122), (nil), (nil), (61), (nil), (91), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (78), (nil), (56), (nil), (nil), (104), (nil), (nil), (nil), (122), (nil), (nil), (58), (nil), (1), (91), (nil), (61), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (77), (nil), (17), (nil), ("Shuffle"), ("Shuffle"), (nil), (nil), (nil), (nil), (139), (nil), (66), (270), (110), (nil), (1), (1), (17), (nil), (nil), (nil), (275), (nil), (86), (nil), (nil), (nil), (nil), (817), (1266), (nil), (nil), (nil), (1), (157), (159), (160), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (10), (nil), (nil), (85), (nil), (97), (100), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (145), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (33), (nil), (nil), (nil), (nil), (14), (nil), (nil), (nil), (102), (nil), (nil), (nil), (nil), (nil), (142), (nil), (142), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1984), (1984), (4559), (nil), (nil), (nil), (66), (nil), (0), (0), (0.5), (nil), (nil), (nil), (11), (nil), (nil), (36), (nil), (93), (nil), (176), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (17), (nil), (nil), (nil), (nil), (8), (nil), (97), (nil), (nil), (13), (nil), (nil), (nil), (nil), (nil), (nil), (7), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (4150), (2748), (nil), (nil), (84), (nil), (nil), (nil), (111), (nil), (nil), (nil), (nil), (0.83288135349178705), (nil), (nil), (48), (nil), (nil), (22), (nil), (nil), (nil), (90), (nil), (118), (nil), (nil), (nil), (nil), (nil), (nil), (1486636538), (3922974191), (nil), (nil), (nil), (nil), (121), (nil), (nil), (nil), (10), (nil), (nil), (nil), (nil), (-12976), (nil), (nil), (nil), (nil), (nil), (1772), (2407), (nil), (nil), (nil), (nil), (nil), (18), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Enums"), (nil), (nil), (nil), (nil), (nil), (0), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (219), (nil), (nil), (1), (nil), (nil), (11), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (3), (nil), (nil), (nil), (nil), (nil), (5), (nil), (nil), (nil), (nil), (125), (nil), (nil), (nil), (nil), (25), (nil), (37), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (262), (nil), (-12768), (nil), (482), (nil), (nil), (nil), (1), (84), (nil), (nil), (nil), (nil), (21), (nil), (39), (nil), (nil), (nil), (nil), (2292), (2292), (3222), (nil), (nil), (nil), (nil), (nil), (1), (110), (194), (28), (nil), (nil), (135), (nil), (nil), (36), (nil), (nil), (1), (nil), (178), (nil), (1), (161), (159), (nil), (nil), (nil), (nil), (117), (nil), (nil), (nil), (nil), (nil), (776), (776), (2863), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (41), (nil), (nil), (nil), (nil), (1), (1), (87), (nil), (1), (1), (1), (28), (163), (45), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (77), (nil), (256), (nil), (37), (nil), (104), (nil), (nil), (nil), (nil), (nil), (605), (842), (nil), (nil), (120), (nil), (nil), (nil), (181), (nil), (59), (nil), (nil), (1), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (77), (194), (22), (nil), (nil), (nil), (158), (nil), (-13523), (nil), (4577), (nil), (nil), (8), (86), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (49), (nil), (71), (8), (nil), (nil), (nil), (160), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (18), (nil), (nil), (107), (nil), (nil), (107), (nil), (nil), (nil), (nil), (nil), (155), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (21), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (150), (nil), (nil), (nil), (nil), (nil), (nil), (8), (nil), (nil), (nil), (17), (nil), (nil), (nil), (105), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (4), (nil), (nil), (60), (61), (nil), (62), (63), (nil), (64), (nil), (65), (nil), (66), (nil), (nil), (125), (nil), (nil), (85), (nil), (nil), (258), (0), (278), (nil), (nil), (nil), (nil), (nil), (nil), (73), (nil), (21), (nil), (nil), (nil), (nil), (nil), (nil), (72), (nil), (nil), (-17856), (nil), (3961), (nil), (nil), (nil), (nil), (141), (nil), (141), (nil), (1003189466), (2761076462), (nil), (7), (nil), (nil), (nil), (nil), (149), (nil), (28), (nil), (nil), (nil), (113), (nil), (78), (nil), (102), (nil), (nil), (120), (nil), (nil), (nil), (nil), (7), (nil), (nil), (nil), (nil), (nil), (38), (nil), (176), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (3132), (2190), (nil), (nil), (386), (nil), (1), (1), (1), (nil), (nil), (nil), (105), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (122), (nil), (nil), (439243635), (nil), (nil), (97), (nil), (16), (nil), (135), (nil), (135), (nil), (nil), (136), (nil), ("IsClient"), (nil), (nil), (nil), (139), (nil), (nil), (nil), (nil), (97), (nil), (nil), (1), (1), (1), (nil), (113), (137), (12), (nil), (nil), (nil), (nil), (1), (225), (nil), (nil), (90), (nil), (nil), (nil), (nil), (nil), (nil), (20), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (126), (nil), (381), (nil), (nil), (nil), (nil), (42), (nil), (nil), (122), (nil), (nil), (126), (nil), (121), (nil), (nil), (nil), (nil), (186), (nil), (272), (nil), (nil), (52), (nil), (103), (nil), (70), (nil), (nil), (nil), (nil), (nil), (nil), (87), (nil), (nil), (113), (nil), (83), (nil), (nil), (nil), (78), (nil), (nil), (166), (nil), (nil), (646), (1527), (nil), (117), (nil), (nil), (196988968), (nil), (nil), (nil), (nil), (nil), (32), (209), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (60), (nil), (nil), (nil), (nil), (nil), (nil), (154), (nil), (154), (nil), (nil), (nil), (nil), (nil), (nil), (7), (nil), (nil), (nil), (121), (nil), (nil), (nil), (nil), (19), (nil), (15), (nil), (nil), (nil), (nil), (nil), (23), (nil), (nil), (nil), (nil), (115), (nil), (nil), (nil), (nil), (97), (nil), (-21933), (nil), (3223), (nil), (nil), (nil), (107), (nil), (69), (nil), (nil), (261), (nil), (-26227), (nil), (2132), (nil), (nil), (nil), (nil), (nil), (nil), (2), (nil), (nil), (nil), (nil), (nil), (nil), (118), (nil), (nil), (nil), (nil), (nil), (17), (nil), (nil), (nil), (nil), (nil), (72), (nil), (nil), (nil), (4), (nil), (nil), (102), (1), (nil), (87), (nil), (nil), (nil), (nil), (nil), (50), (nil), (1), (nil), (nil), (105), (nil), (nil), (nil), (551), (1365), (nil), (91), (nil), (nil), (nil), (nil), (91), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (51), (nil), (4), (nil), (100), (nil), (1), (102), (nil), (33), (nil), (nil), (nil), (nil), (nil), (nil), (35), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (88), (nil), (nil), (nil), (40), (nil), (nil), (121), (nil), (nil), (nil), (nil), (nil), (nil), (15), (nil), (nil), (nil), (1), (nil), (nil), (104), (nil), (nil), (81), (nil), (nil), (nil), (nil), ("unpack"), (nil), (nil), (78), (nil), (67), (nil), (68), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (14), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("IsA"), (nil), (nil), (nil), (nil), (nil), (nil), (115), (22), (nil), (nil), (nil), (0), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0.094194665086865428), (nil), (nil), (nil), (nil), (0.0057600076948723941), (nil), (1), (nil), (279), (nil), (nil), (nil), (nil), (nil), (74), (nil), (125), (nil), (nil), (nil), (nil), (1), (1), (nil), (nil), (nil), (34), (nil), (59), (nil), (nil), (nil), (61), (nil), (nil), (100), (nil), (1903078976), (nil), (0), (-7), (0), (5), (nil), (nil), (nil), (nil), (nil), (1152363122), (nil), (nil), (nil), (53), (nil), (0), (-4), (0), (nil), (5), (nil), (nil), (115), (nil), (nil), (13), (nil), (nil), (nil), (91), (nil), (nil), (nil), (nil), (104), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (74), (nil), (137), (nil), (nil), (nil), (nil), (251), (nil), (-27329), (nil), (290), (nil), (nil), (194), (nil), (nil), (nil), (nil), (57), (nil), (nil), (nil), (155), (nil), (nil), (nil), (nil), (10), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (32), (nil), (nil), (nil), (nil), (110), (nil), (nil), (nil), (nil), (78), (nil), (nil), (134), (nil), (134), (nil), (nil), (35), (nil), (nil), (nil), (3838), (3838), (362), (nil), (nil), (78), (nil), (118), (nil), (nil), (nil), (114), (nil), (74), (122), (nil), (nil), (118), (nil), (122), (nil), (nil), (nil), (nil), (1), (1), (70), (nil), (298), (nil), (104), (nil), (121), (nil), (138), (nil), (90), (39), (nil), (118), (nil), (60), (nil), (nil), (138), (nil), (nil), (nil), (12), (nil), (nil), (6), (nil), (nil), (83), (nil), (100), (nil), (141), (64), (nil), (151), (nil), (nil), (nil), (nil), (116), (nil), (0), (0), (0), (nil), (1), (94), (262), (nil), (396), (nil), (47), (170), (123), (nil), (92), (nil), (121), (nil), (nil), (69), (nil), (233), (nil), (0.67418527901770742), (nil), (nil), (154), (nil), (nil), (-21317), (nil), (3120), (nil), (nil), (nil), (nil), (nil), (nil), (62), (nil), (nil), (93), (nil), (0.1666666716337204), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (37), (38), (nil), (91), (nil), (60), (nil), (nil), (1), (nil), (1), (nil), (30), (nil), (nil), (nil), (nil), (56), (nil), (1), (1), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (2), (1), (nil), (137), (nil), (0), (nil), (nil), (55), (nil), (1), (156), (157), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (115), (nil), (100), (nil), (1), (nil), (120), (nil), (244), (nil), (44), (nil), (45), (nil), (1), (nil), (77), (nil), (107), (nil), (nil), (nil), (nil), (0.0625), (2), (-0.125), (nil), (66), (nil), (nil), (nil), (0), (nil), (29), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (46), (nil), (46), (nil), (nil), (nil), (nil), (13), (nil), (nil), (nil), (97), (nil), (nil), (nil), (0.66666668653488159), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (76), (nil), (104), (nil), (114), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (860), (nil), (nil), (nil), (18), (nil), (1), (nil), (nil), (nil), (53), (nil), (nil), (90), (nil), (1), (nil), (126), (nil), (nil), (133), (nil), (nil), (nil), (nil), (nil), (105), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (91), (nil), (108), (nil), (nil), (nil), (nil), (nil), (122), (nil), (nil), (103), (nil), (nil), (nil), (122), (nil), (nil), (nil), (nil), (nil), (nil), (28), (nil), (nil), (nil), (nil), (18), (nil), (nil), (nil), (nil), (nil), (1), (nil), (1), (1), (1), (1), (83), (nil), (69), (nil), (nil), (59), (nil), (nil), (nil), (12), (nil), (nil), (58), (nil), (nil), (nil), (nil), (nil), (1), (1), (77), (nil), (nil), (nil), (117), (262), (nil), (nil), (2), (nil), (nil), (0.10000000149011612), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (14), (nil), (nil), (2), (84), (nil), (94), (26), (nil), (nil), (nil), (nil), (nil), (nil), (154), (nil), (nil), (nil), (nil), ("RunService"), (nil), (nil), (nil), (nil), (nil), (140), (nil), (140) }; t.n = 4623; return t end)(), (function() local t = { (0), (0), (2024), (0), (0), (103), (0), (104), (0), (0), (6), (0), (2260), (0), (0), (0), (137), (32), (676), (32), (491), (139), (0), (0), (0), (103), (0), (0), (0), (54), (0), (244), (0), (0), (106), (107), (108), (0), (0), (0), (20), (0), (0), (0), (0), (127), (130), (555), (130), (127), (320), (131), (0), (0), (99), (0), (100), (0), (0), (0), (0), (0), (0), (0), (0), (115), (116), (117), (113), (0), (115), (116), (0), (0), (262), (0), (40), (0), (107), (102), (0), (0), (0), (102), (0), (0), (0), (0), (79), (0), (5), (0), (0), (91), (5), (0), (0), (0), (0), (103), (0), (104), (0), (0), (0), (391), (0), (0), (102), (0), (0), (99), (0), (100), (0), (0), (98), (23), (99), (0), (0), (0), (0), (104), (0), (0), (22), (5), (0), (1562), (0), (671), (455), (0), (0), (0), (4470), (0), (803), (0), (4389), (0), (412), (0), (4327), (0), (0), (0), (0), (0), (0), (102), (0), (105), (103), (5), (0), (4241), (0), (0), (0), (33), (0), (0), (0), (69), (177), (128), (935), (130), (123), (450), (131), (0), (365), (0), (0), (0), (105), (0), (100), (0), (98), (99), (100), (0), (0), (182), (100), (150), (0), (929), (0), (0), (104), (0), (36), (0), (3), (0), (0), (0), (103), (0), (0), (95), (96), (0), (116), (0), (0), (105), (0), (0), (0), (13), (3), (5), (0), (0), (0), (106), (0), (108), (0), (115), (0), (0), (99), (0), (0), (100), (0), (117), (118), (119), (0), (109), (109), (109), (0), (522), (130), (123), (408), (131), (0), (0), (100), (0), (98), (99), (100), (0), (40), (41), (191), (242), (42), (43), (5), (0), (2868), (0), (107), (0), (98), (99), (100), (0), (21), (5), (0), (3925), (0), (0), (2535), (0), (130), (0), (0), (117), (118), (119), (0), (4), (5), (0), (90), (0), (80), (61), (5), (0), (312), (0), (0), (0), (79), (0), (1633), (0), (4258), (0), (117), (118), (114), (111), (0), (0), (114), (115), (116), (117), (113), (0), (0), (100), (0), (2276), (0), (0), (100), (0), (98), (99), (0), (0), (0), (0), (102), (29), (502), (139), (0), (0), (0), (0), (0), (0), (0), (98), (0), (20), (3), (5), (0), (319), (0), (115), (116), (117), (0), (0), (99), (107), (0), (11), (12), (5), (0), (0), (0), (0), (0), (0), (0), (0), (102), (0), (0), (2388), (0), (0), (0), (0), (10), (0), (45), (187), (184), (0), (801), (0), (0), (0), (82), (0), (5), (0), (106), (102), (115), (0), (0), (99), (0), (100), (0), (0), (0), (0), (0), (0), (0), (0), (0), (104), (0), (0), (4494), (0), (0), (99), (0), (100), (0), (0), (102), (0), (0), (4045), (0), (31), (5), (0), (105), (101), (0), (0), (0), (0), (30), (0), (173), (0), (1564), (0), (4004), (0), (0), (0), (0), (0), (104), (0), (0), (0), (0), (130), (831), (130), (123), (407), (131), (0), (0), (59), (144), (115), (0), (0), (0), (0), (61), (22), (63), (12), (4), (0), (44), (12), (5), (0), (0), (0), (0), (85), (0), (5), (0), (0), (29), (0), (137), (0), (52), (516), (139), (0), (0), (103), (0), (104), (0), (0), (0), (3765), (0), (0), (1163), (0), (0), (100), (0), (0), (99), (0), (5), (0), (24), (5), (0), (11), (0), (0), (0), (0), (97), (0), (2270), (0), (97), (0), (115), (112), (226), (203), (133), (0), (0), (100), (0), (0), (99), (0), (0), (445), (0), (0), (0), (0), (99), (99), (100), (0), (0), (102), (0), (28), (239), (0), (0), (78), (0), (100), (0), (99), (104), (105), (102), (103), (0), (3021), (0), (0), (0), (82), (0), (5), (0), (5), (0), (3914), (0), (5), (0), (130), (0), (0), (99), (0), (100), (0), (0), (2597), (0), (639), (0), (107), (108), (105), (0), (103), (0), (104), (0), (140), (0), (102), (105), (0), (0), (0), (0), (101), (0), (99), (0), (0), (5), (0), (105), (0), (0), (114), (110), (115), (114), (0), (0), (106), (0), (0), (0), (0), (137), (102), (32), (52), (236), (139), (191), (0), (0), (0), (0), (5), (0), (0), (103), (0), (104), (0), (0), (105), (102), (103), (0), (0), (71), (72), (0), (0), (75), (0), (0), (0), (0), (0), (77), (0), (75), (5), (0), (195), (237), (348), (495), (442), (0), (106), (103), (107), (0), (0), (113), (57), (43), (0), (0), (0), (0), (0), (103), (0), (104), (0), (103), (0), (104), (0), (0), (20), (3), (5), (0), (58), (59), (60), (0), (0), (99), (0), (100), (0), (0), (104), (103), (0), (87), (109), (0), (0), (106), (0), (0), (0), (100), (0), (100), (103), (5), (0), (245), (0), (1399), (0), (3818), (0), (12), (0), (109), (109), (109), (109), (109), (109), (0), (0), (100), (0), (130), (0), (107), (105), (103), (0), (0), (137), (47), (392), (139), (0), (0), (0), (0), (0), (101), (102), (103), (0), (104), (0), (0), (0), (0), (77), (0), (0), (0), (77), (0), (0), (109), (109), (109), (0), (0), (0), (130), (170), (130), (123), (579), (131), (0), (0), (104), (105), (0), (0), (226), (100), (214), (0), (0), (0), (0), (2894), (0), (0), (101), (98), (0), (83), (0), (775), (130), (127), (544), (131), (118), (0), (0), (106), (103), (107), (0), (0), (106), (103), (0), (13), (0), (98), (0), (5), (0), (0), (0), (0), (79), (0), (0), (0), (0), (130), (471), (130), (123), (630), (131), (0), (0), (0), (103), (0), (0), (0), (0), (78), (0), (0), (0), (78), (0), (0), (0), (0), (396), (759), (139), (0), (98), (0), (0), (0), (900), (0), (447), (0), (0), (103), (0), (0), (101), (0), (127), (0), (130), (0), (0), (0), (0), (78), (79), (0), (3057), (0), (0), (0), (0), (0), (0), (0), (5), (0), (0), (0), (85), (0), (0), (0), (347), (0), (5), (0), (0), (103), (0), (0), (0), (105), (101), (0), (0), (0), (25), (5), (0), (0), (106), (0), (101), (102), (103), (104), (0), (1287), (0), (0), (102), (0), (0), (74), (0), (106), (0), (0), (90), (0), (154), (0), (102), (177), (174), (0), (1933), (0), (0), (0), (372), (258), (130), (129), (454), (131), (0), (0), (99), (100), (0), (99), (101), (102), (99), (0), (0), (0), (0), (0), (82), (0), (5), (0), (106), (111), (104), (111), (105), (0), (0), (72), (73), (0), (0), (32), (5), (0), (0), (0), (0), (0), (0), (0), (101), (0), (0), (28), (0), (5), (0), (32), (33), (5), (0), (0), (2458), (0), (0), (0), (0), (0), (11), (3), (0), (98), (0), (0), (0), (68), (0), (0), (0), (104), (98), (104), (0), (0), (0), (106), (0), (0), (103), (0), (104), (0), (0), (4350), (0), (0), (0), (2028), (0), (130), (0), (36), (12), (5), (0), (0), (111), (109), (0), (0), (0), (0), (0), (0), (103), (0), (0), (0), (0), (5), (0), (0), (98), (99), (100), (0), (34), (24), (0), (0), (0), (0), (0), (0), (89), (0), (0), (103), (0), (104), (0), (0), (0), (103), (100), (0), (0), (4123), (0), (1872), (0), (0), (0), (5), (0), (80), (24), (0), (0), (0), (0), (130), (595), (130), (123), (135), (131), (0), (51), (97), (142), (0), (99), (0), (100), (0), (0), (2), (3), (0), (0), (0), (89), (5), (0), (104), (0), (0), (109), (108), (0), (102), (109), (0), (0), (113), (106), (0), (26), (27), (0), (66), (5), (0), (547), (0), (116), (0), (0), (0), (585), (0), (0), (0), (0), (3369), (0), (830), (0), (0), (0), (0), (3), (4), (6), (3), (7), (0), (9), (0), (0), (0), (5), (0), (33), (27), (5), (0), (19), (0), (0), (0), (86), (21), (2), (0), (0), (0), (0), (0), (0), (0), (0), (0), (0), (0), (1557), (0), (5), (0), (0), (0), (0), (0), (100), (0), (0), (0), (102), (0), (0), (0), (0), (104), (103), (0), (100), (0), (97), (0), (0), (0), (0), (0), (0), (0), (0), (52), (0), (0), (106), (0), (593), (0), (109), (109), (109), (109), (109), (0), (0), (103), (0), (104), (0), (115), (111), (0), (113), (114), (115), (116), (0), (0), (0), (764), (0), (0), (0), (0), (0), (0), (0), (5), (0), (102), (0), (28), (12), (29), (0), (0), (0), (103), (0), (104), (0), (0), (0), (83), (0), (191), (0), (0), (99), (104), (0), (0), (0), (0), (0), (82), (0), (0), (0), (98), (99), (100), (0), (99), (0), (0), (99), (0), (0), (4063), (0), (0), (106), (102), (0), (0), (99), (0), (100), (0), (0), (0), (100), (0), (0), (0), (0), (102), (0), (0), (115), (116), (117), (113), (110), (0), (0), (113), (114), (0), (0), (0), (0), (13), (105), (226), (0), (0), (0), (0), (99), (0), (832), (0), (32), (0), (107), (108), (106), (0), (104), (105), (106), (107), (103), (104), (105), (101), (0), (89), (0), (0), (98), (99), (100), (0), (0), (107), (99), (0), (704), (0), (0), (3), (0), (0), (2), (0), (0), (102), (121), (0), (0), (98), (99), (100), (0), (2547), (0), (0), (103), (0), (0), (0), (0), (0), (0), (0), (23), (5), (0), (1043), (0), (655), (130), (123), (598), (131), (0), (0), (100), (0), (101), (0), (0), (106), (102), (115), (0), (0), (0), (104), (105), (106), (107), (108), (0), (118), (114), (123), (83), (45), (116), (117), (118), (119), (0), (0), (0), (100), (0), (5), (0), (2338), (0), (2643), (0), (93), (5), (0), (0), (0), (94), (0), (5), (0), (2096), (0), (97), (0), (99), (0), (100), (0), (0), (99), (0), (100), (0), (0), (1618), (0), (0), (0), (32), (582), (139), (0), (20), (3), (5), (0), (0), (99), (0), (0), (49), (50), (51), (52), (53), (54), (55), (56), (57), (0), (5), (0), (3), (15), (16), (0), (137), (0), (899), (667), (139), (0), (0), (0), (0), (98), (99), (0), (0), (0), (0), (0), (0), (0), (0), (82), (0), (0), (87), (0), (0), (103), (0), (0), (98), (0), (99), (0), (0), (3011), (0), (130), (0), (0), (0), (0), (0), (0), (0), (1992), (0), (0), (99), (0), (98), (0), (3634), (0), (0), (103), (104), (0), (0), (0), (77), (0), (5), (0), (3367), (0), (0), (103), (0), (101), (104), (102), (0), (99), (101), (102), (99), (0), (0), (0), (35), (63), (0), (5), (0), (20), (42), (3), (116), (204), (191), (5), (0), (22), (0), (169), (388), (74), (115), (116), (112), (0), (114), (0), (101), (0), (1482), (0), (2686), (0), (7), (0), (0), (0), (79), (0), (5), (0), (0), (5), (0), (0), (0), (0), (0), (0), (0), (79), (0), (0), (80), (5), (0), (1322), (0), (355), (0), (0), (84), (0), (0), (0), (0), (2879), (0), (0), (0), (0), (0), (104), (0), (0), (106), (0), (105), (104), (104), (106), (0), (105), (104), (0), (2121), (0), (0), (0), (0), (5), (0), (375), (0), (0), (99), (0), (0), (0), (3229), (0), (20), (3), (5), (0), (107), (101), (0), (127), (0), (829), (416), (130), (127), (901), (131), (0), (83), (0), (0), (0), (0), (0), (0), (5), (0), (104), (0), (0), (0), (103), (0), (104), (0), (0), (34), (0), (5), (0), (13), (4), (14), (0), (0), (0), (99), (0), (0), (0), (79), (0), (0), (0), (0), (83), (0), (81), (5), (0), (0), (0), (0), (5), (0), (2863), (0), (0), (0), (0), (0), (0), (104), (0), (99), (93), (180), (116), (95), (20), (100), (0), (0), (0), (0), (0), (0), (0), (0), (100), (0), (0), (0), (0), (0), (104), (0), (5), (0), (0), (0), (97), (0), (66), (0), (0), (63), (103), (561), (104), (0), (44), (24), (5), (0), (0), (103), (0), (104), (0), (0), (103), (0), (104), (0), (0), (0), (0), (105), (0), (0), (0), (0), (0), (107), (0), (157), (0), (137), (0), (20), (993), (139), (0), (0), (0), (143), (5), (181), (0), (461), (0), (0), (121), (99), (33), (172), (128), (205), (44), (0), (100), (0), (0), (99), (0), (108), (0), (0), (5), (0), (130), (0), (0), (100), (0), (106), (107), (0), (0), (105), (98), (0), (0), (4556), (0), (844), (0), (104), (0), (0), (0), (262), (232), (130), (128), (436), (131), (0), (0), (100), (0), (0), (0), (4291), (0), (108), (0), (0), (75), (5), (0), (0), (0), (100), (0), (2695), (0), (0), (0), (0), (0), (82), (0), (5), (0), (0), (0), (101), (0), (103), (0), (106), (0), (0), (2743), (0), (56), (239), (125), (0), (107), (0), (2528), (0), (2935), (0), (106), (0), (431), (0), (97), (0), (0), (0), (0), (103), (0), (2976), (0), (0), (0), (0), (0), (0), (21), (0), (0), (976), (0), (76), (0), (0), (79), (0), (0), (919), (106), (0), (111), (3449), (0), (0), (0), (99), (103), (104), (101), (0), (0), (0), (0), (0), (0), (0), (0), (103), (0), (0), (0), (108), (0), (0), (0), (2189), (0), (0), (0), (26), (0), (0), (0), (0), (98), (0), (0), (103), (0), (104), (0), (0), (3319), (0), (115), (0), (34), (12), (34), (0), (0), (0), (111), (0), (3597), (0), (0), (2), (0), (4416), (0), (482), (0), (0), (127), (130), (887), (130), (127), (420), (131), (0), (0), (0), (137), (102), (32), (315), (139), (0), (98), (0), (0), (377), (712), (139), (0), (0), (0), (0), (0), (0), (0), (62), (0), (110), (107), (0), (0), (0), (33), (98), (71), (207), (126), (64), (110), (0), (0), (99), (100), (0), (0), (99), (0), (97), (0), (99), (0), (0), (0), (0), (0), (0), (0), (0), (0), (0), (0), (506), (0), (88), (0), (0), (114), (110), (115), (114), (0), (283), (0), (5), (0), (520), (0), (0), (0), (100), (0), (97), (0), (106), (1576), (0), (1874), (0), (100), (0), (115), (114), (0), (0), (2557), (0), (0), (0), (0), (79), (0), (5), (0), (137), (0), (0), (73), (32), (454), (139), (0), (0), (0), (5), (0), (0), (109), (0), (0), (5), (0), (1688), (0), (5), (0), (0), (0), (162), (103), (95), (239), (222), (54), (192), (0), (0), (0), (36), (24), (37), (38), (0), (0), (120), (116), (113), (0), (0), (116), (117), (118), (119), (115), (0), (0), (0), (967), (1068), (139), (0), (3156), (0), (107), (0), (0), (0), (0), (0), (102), (0), (100), (0), (26), (27), (5), (0), (114), (115), (116), (117), (0), (1956), (0), (0), (0), (77), (0), (5), (0), (0), (57), (0), (263), (294), (0), (0), (102), (0), (0), (0), (0), (73), (200), (139), (28), (0), (399), (0), (215), (0), (3871), (0), (130), (0), (0), (0), (129), (130), (113), (183), (130), (128), (941), (131), (0), (4386), (0), (98), (99), (100), (101), (0), (97), (0), (0), (3691), (0), (130), (0), (100), (0), (3116), (0), (1457), (0), (2047), (0), (0), (0), (0), (82), (0), (0), (0), (99), (0), (103), (0), (99), (0), (102), (103), (104), (0), (3), (0), (573), (0), (0), (87), (0), (5), (0), (0), (99), (0), (100), (0), (0), (43), (0), (0), (0), (0), (5), (0), (106), (0), (116), (114), (0), (0), (44), (41), (45), (0), (0), (912), (0), (0), (120), (113), (0), (98), (99), (231), (33), (100), (101), (0), (104), (0), (0), (0), (726), (0), (0), (101), (102), (0), (102), (111), (0), (0), (29), (5), (0), (5), (0), (104), (0), (0), (0), (0), (0), (1547), (0), (0), (100), (101), (102), (103), (104), (0), (0), (0), (0), (0), (106), (0), (0), (130), (0), (565), (0), (39), (490), (0), (0), (0), (98), (0), (55), (0), (102), (0), (4414), (0), (0), (0), (0), (0), (107), (0), (104), (0), (693), (0), (0), (97), (0), (99), (0), (71), (72), (73), (71), (72), (663), (0), (0), (110), (108), (0), (0), (0), (0), (620), (1030), (130), (129), (130), (472), (130), (123), (653), (131), (0), (107), (108), (0), (0), (8), (5), (0), (0), (0), (0), (485), (719), (0), (5), (0), (0), (0), (79), (0), (120), (116), (0), (0), (0), (0), (99), (0), (100), (0), (0), (99), (0), (0), (3422), (0), (0), (34), (35), (5), (0), (0), (0), (0), (102), (106), (0), (0), (95), (104), (0), (76), (103), (0), (0), (0), (0), (5), (0), (106), (101), (0), (103), (0), (0), (410), (0), (0), (0), (0), (0), (91), (0), (0), (107), (0), (0), (0), (0), (137), (32), (8), (281), (139), (132), (0), (6), (0), (98), (99), (100), (0), (0), (0), (0), (79), (0), (0), (0), (82), (0), (0), (103), (0), (0), (375), (0), (10), (5), (0), (118), (114), (0), (116), (0), (3311), (0), (600), (130), (127), (294), (131), (0), (823), (0), (0), (102), (15), (101), (0), (0), (0), (103), (0), (104), (0), (0), (104), (0), (0), (0), (130), (0), (109), (0), (0), (0), (5), (0), (88), (5), (0), (2299), (0), (0), (0), (103), (0), (82), (45), (0), (0), (0), (102), (0), (0), (0), (0), (0), (97), (0), (0), (99), (100), (101), (102), (0), (0), (0), (122), (87), (114), (0), (0), (31), (0), (40), (0), (130), (0), (0), (0), (0), (98), (103), (0), (109), (109), (109), (109), (0), (0), (0), (0), (0), (0), (0), (0), (108), (102), (0), (105), (104), (0), (0), (0), (0), (5), (0), (610), (0), (0), (0), (79), (0), (5), (0), (0), (5), (0), (104), (105), (106), (0), (0), (0), (28), (0), (0), (0), (0), (101), (102), (0), (106), (0), (0), (0), (106), (107), (0), (0), (0), (36), (0), (0), (0), (0), (0), (0), (0), (0), (0), (97), (0), (98), (100), (0), (103), (104), (105), (0), (195), (0), (108), (105), (106), (0), (3426), (0), (102), (0), (0), (99), (0), (0), (0), (0), (5), (5), (0), (0), (107), (106), (0), (105), (106), (0), (0), (0), (0), (86), (0), (0), (0), (0), (0), (0), (32), (721), (139), (0), (100), (0), (0), (378), (130), (128), (161), (131), (0), (97), (0), (99), (0), (100), (0), (0), (0), (0), (0), (104), (101), (0), (102), (103), (0), (0), (137), (32), (273), (139), (0), (0), (729), (130), (128), (711), (131), (0), (0), (0), (0), (101), (100), (0), (0), (70), (73), (133), (83), (0), (0), (108), (106), (0), (0), (0), (0), (353), (467), (0), (0), (98), (0), (100), (0), (106), (0), (92), (5), (0), (0), (104), (0), (0), (0), (0), (0), (101), (4), (5), (0), (447), (0), (0), (0), (0), (0), (0), (19), (53), (5), (0), (0), (0), (82), (0), (80), (0), (35), (95), (105), (2), (105), (0), (105), (0), (374), (0), (0), (466), (0), (0), (3669), (0), (12), (0), (103), (0), (0), (63), (4), (5), (0), (3608), (0), (0), (124), (209), (95), (68), (147), (163), (197), (0), (86), (0), (30), (7), (5), (0), (0), (108), (0), (0), (106), (102), (109), (0), (0), (0), (108), (105), (108), (0), (98), (0), (0), (0), (0), (0), (79), (0), (91), (5), (0), (0), (130), (0), (0), (103), (0), (104), (0), (0), (0), (99), (0), (0), (104), (0), (0), (597), (0), (3), (0), (0), (79), (0), (5), (0), (2228), (0), (98), (0), (0), (105), (106), (95), (0), (0), (0), (97), (0), (0), (137), (32), (602), (139), (0), (5), (0), (98), (0), (0), (0), (79), (0), (746), (0), (0), (0), (0), (0), (0), (105), (98), (0), (0), (0), (103), (0), (911), (367), (248), (0), (1047), (0), (0), (115), (112), (0), (3646), (0), (97), (0), (0), (0), (0), (0), (0), (99), (0), (0), (0), (0), (5), (0), (805), (0), (0), (109), (0), (0), (0), (108), (105), (0), (563), (0), (103), (100), (0), (97), (0), (99), (0), (0), (0), (0), (103), (0), (0), (0), (2021), (0), (104), (0), (106), (107), (0), (0), (0), (0), (101), (0), (99), (100), (101), (0), (85), (86), (5), (0), (65), (0), (4558), (0), (4087), (0), (0), (0), (0), (116), (944), (139), (0), (0), (102), (103), (104), (105), (76), (42), (0), (0), (0), (99), (0), (100), (0), (0), (5), (0), (93), (5), (0), (0), (0), (0), (0), (0), (0), (102), (99), (0), (0), (0), (0), (18), (0), (0), (0), (0), (4141), (0), (0), (63), (104), (105), (0), (0), (0), (728), (0), (0), (0), (0), (0), (104), (98), (105), (0), (0), (1042), (0), (0), (0), (0), (0), (0), (0), (8), (917), (587), (139), (199), (0), (4256), (0), (112), (113), (114), (0), (24), (0), (76), (0), (0), (3061), (0), (537), (0), (3489), (0), (98), (0), (0), (0), (100), (0), (0), (0), (79), (0), (0), (0), (0), (100), (0), (97), (0), (0), (5), (0), (0), (0), (0), (103), (0), (104), (0), (0), (0), (466), (253), (1001), (0), (0), (0), (0), (610), (820), (139), (0), (1168), (0), (0), (0), (5), (0), (0), (99), (0), (103), (0), (0), (97), (0), (0), (100), (0), (0), (0), (106), (0), (434), (0), (0), (0), (0), (0), (0), (756), (795), (0), (168), (0), (23), (5), (0), (0), (0), (100), (0), (0), (0), (0), (87), (0), (0), (0), (0), (0), (1001), (726), (139), (0), (0), (99), (0), (100), (0), (101), (0), (0), (0), (94), (110), (110), (110), (0), (0), (105), (0), (0), (0), (112), (0), (114), (0), (739), (0), (98), (0), (127), (0), (885), (0), (0), (101), (3), (0), (105), (0), (106), (0), (0), (0), (0), (0), (0), (103), (0), (104), (0), (0), (0), (103), (0), (104), (0), (0), (0), (0), (108), (0), (0), (62), (0), (28), (12), (5), (0), (120), (0), (0), (0), (0), (0), (0), (0), (0), (358), (789), (130), (123), (625), (131), (0), (0), (92), (5), (0), (0), (99), (0), (100), (0), (97), (0), (0), (137), (0), (27), (32), (640), (139), (0), (0), (0), (0), (101), (102), (103), (104), (0), (0), (101), (98), (0), (1161), (0), (0), (104), (0), (3869), (0), (102), (103), (104), (95), (35), (105), (0), (5), (0), (0), (0), (0), (137), (551), (82), (359), (139), (0), (102), (4), (0), (0), (0), (0), (84), (0), (0), (98), (0), (61), (62), (5), (0), (83), (84), (85), (86), (87), (88), (0), (0), (0), (0), (0), (0), (0), (24), (5), (0), (130), (0), (3888), (0), (5), (0), (0), (99), (123), (109), (105), (110), (0), (111), (115), (114), (0), (0), (1616), (0), (1946), (0), (12), (30), (31), (0), (850), (0), (0), (3503), (0), (0), (102), (103), (104), (105), (0), (0), (0), (150), (288), (130), (123), (969), (131), (0), (7), (5), (0), (0), (0), (0), (0), (415), (451), (411), (0), (917), (0), (3722), (0), (73), (5), (0), (0), (0), (419), (0), (0), (84), (0), (101), (0), (0), (0), (98), (0), (180), (104), (0), (0), (5), (0), (0), (112), (0), (0), (50), (179), (71), (108), (102), (0), (0), (30), (0), (0), (103), (0), (104), (0), (0), (0), (0), (127), (432), (0), (0), (0), (0), (0), (0), (106), (0), (0), (0), (0), (0), (0), (97), (0), (99), (0), (100), (0), (0), (0), (109), (104), (0), (104), (107), (0), (0), (0), (103), (0), (0), (0), (103), (0), (0), (0), (0), (0), (0), (103), (0), (104), (0), (0), (72), (73), (71), (72), (73), (71), (72), (32), (72), (663), (72), (0), (0), (3141), (0), (0), (438), (0), (0), (109), (110), (111), (107), (0), (118), (0), (11), (0), (3446), (0), (5), (0), (0), (0), (103), (0), (0), (2877), (0), (1031), (130), (123), (654), (131), (0), (0), (0), (104), (98), (105), (0), (870), (779), (0), (97), (0), (106), (104), (0), (105), (0), (3784), (0), (103), (0), (1944), (0), (4405), (0), (3539), (0), (104), (107), (106), (0), (0), (0), (11), (3), (0), (0), (0), (0), (5), (0), (129), (0), (0), (0), (0), (0), (0), (0), (0), (448), (465), (139), (0), (1075), (0), (110), (111), (112), (0), (0), (0), (100), (96), (0), (0), (29), (0), (0), (0), (551), (0), (0), (106), (0), (0), (2110), (0), (99), (0), (101), (98), (102), (0), (0), (101), (98), (102), (0), (0), (87), (100), (0), (0), (101), (0), (103), (0), (0), (17), (18), (19), (0), (103), (104), (105), (0), (106), (0), (0), (100), (101), (0), (0), (97), (0), (99), (0), (0), (103), (0), (104), (0), (0), (0), (0), (0), (0), (0), (0), (106), (0), (130), (0), (0), (0), (0), (5), (0), (0), (114), (111), (0), (106), (0), (115), (112), (0), (0), (0), (3276), (0), (98), (0), (0), (107), (0), (1152), (0), (5), (0), (1002), (0), (0), (0), (0), (79), (0), (0), (475), (0), (186), (0), (0), (0), (77), (0), (0), (4155), (0), (99), (106), (107), (0), (5), (0), (0), (105), (0), (0), (0), (0), (0), (98), (99), (0), (0), (0), (0), (0), (99), (0), (0), (904), (0), (0), (0), (105), (103), (0), (104), (102), (105), (0), (0), (0), (103), (0), (0), (102), (0), (0), (0), (115), (113), (0), (0), (0), (97), (0), (100), (0), (0), (0), (103), (0), (104), (0), (0), (0), (0), (107), (0), (0), (0), (0), (130), (639), (130), (123), (841), (131), (0), (0), (4511), (0), (1093), (0), (0), (130), (333), (130), (129), (261), (131), (0), (0), (0), (103), (0), (104), (0), (0), (29), (0), (0), (0), (107), (0), (0), (0), (99), (0), (100), (0), (46), (151), (111), (0), (77), (0), (0), (0), (5), (0), (0), (96), (97), (0), (3147), (0), (0), (0), (37), (107), (167), (0), (104), (0), (0), (161), (0), (0), (99), (107), (108), (0), (97), (0), (0), (0), (97), (221), (208), (0), (101), (0), (0), (0), (0), (109), (107), (106), (158), (0), (100), (0), (97), (0), (74), (5), (0), (4278), (0), (0), (0), (0), (0), (0), (5), (0), (107), (0), (0), (0), (0), (0), (99), (0), (99), (0), (106), (0), (0), (120), (114), (0), (0), (0), (103), (0), (104), (0), (0), (680), (104), (0), (0), (106), (0), (0), (102), (3), (0), (0), (0), (79), (0), (0), (3587), (0), (73), (71), (72), (663), (0), (0), (0), (0), (99), (0), (100), (0), (0), (0), (4496), (0), (0), (99), (106), (0), (0), (0), (0), (57), (0), (103), (104), (0), (0), (0), (111), (107), (101), (130), (250), (28), (146), (175), (0), (747), (0), (0), (0), (0), (0), (0), (101), (0), (104), (0), (0), (99), (0), (104), (0), (102), (0), (2866), (0), (0), (109), (107), (0), (3705), (0), (3636), (0), (0), (0), (0), (86), (87), (0), (0), (0), (84), (0), (5), (0), (0), (0), (3162), (0), (0), (103), (0), (106), (0), (118), (119), (120), (121), (117), (114), (0), (0), (0), (84), (0), (453), (165), (99), (0), (115), (116), (117), (0), (104), (0), (0), (1238), (0), (0), (19), (0), (51), (0), (2245), (0), (0), (0), (0), (105), (0), (0), (109), (109), (109), (0), (0), (0), (0), (0), (12), (0), (2707), (0), (4071), (0), (0), (0), (0), (130), (511), (130), (128), (929), (0), (0), (382), (0), (0), (0), (0), (5), (0), (0), (0), (104), (0), (0), (103), (0), (104), (0), (0), (0), (0), (0), (0), (0), (0), (102), (0), (36), (12), (0), (0), (0), (106), (0), (102), (0), (0), (5), (0), (0), (101), (98), (102), (0), (0), (1916), (0), (0), (0), (8), (178), (543), (139), (0), (497), (0), (3154), (0), (0), (0), (104), (0), (74), (5), (0), (0), (106), (0), (111), (0), (0), (0), (0), (100), (101), (102), (0), (130), (0), (106), (0), (110), (0), (4319), (0), (77), (5), (0), (1824), (0), (5), (0), (0), (100), (87), (0), (0), (5), (0), (0), (100), (0), (0), (1202), (0), (302), (0), (100), (101), (0), (106), (99), (0), (55), (0), (106), (0), (108), (109), (110), (0), (83), (84), (85), (0), (341), (0), (98), (99), (100), (0), (106), (0), (114), (0), (0), (106), (0), (2714), (0), (108), (0), (0), (1041), (0), (659), (130), (127), (888), (131), (0), (104), (104), (0), (0), (5), (0), (0), (106), (102), (112), (0), (0), (104), (102), (0), (102), (0), (0), (0), (0), (0), (0), (0), (65), (0), (0), (99), (0), (0), (57), (0), (120), (0), (0), (45), (46), (0), (87), (37), (5), (0), (0), (104), (0), (106), (0), (5), (0), (0), (0), (0), (5), (0), (23), (24), (25), (0), (0), (0), (1433), (0), (0), (0), (98), (102), (0), (109), (0), (105), (0), (0), (1753), (0), (102), (103), (104), (0), (0), (0), (0), (0), (0), (0), (5), (0), (948), (0), (100), (0), (97), (0), (130), (0), (46), (3), (47), (41), (48), (0), (3961), (0), (3638), (0), (0), (115), (0), (117), (118), (119), (0), (2401), (0), (87), (0), (111), (0), (100), (0), (0), (229), (103), (218), (12), (149), (181), (194), (0), (0), (0), (59), (58), (59), (618), (0), (32), (0), (104), (0), (0), (0), (225), (0), (0), (102), (116), (0), (0), (0), (0), (0), (0), (0), (0), (0), (0), (0), (0), (0), (0), (0), (0), (108), (0), (0), (97), (0), (136), (0), (104), (152), (148), (178), (0), (105), (103), (0), (105), (106), (0), (0), (0), (84), (0), (82), (0), (215), (0), (3693), (0), (0), (1233), (0), (105), (0), (104), (100), (0), (101), (0), (222), (123), (19), (0), (101), (98), (0), (0), (98), (0), (0), (0), (105), (0), (106), (99), (0), (363), (0), (0), (114), (109), (0), (106), (0), (0), (0), (106), (104), (0), (90), (0), (0), (0), (5), (0), (0), (0), (0), (100), (0), (0), (99), (0), (0), (65), (0), (67), (68), (69), (70), (5), (0), (1095), (0), (0), (97), (0), (99), (0), (100), (0), (0), (2108), (0), (102), (0), (0), (0), (83), (84), (5), (0), (0), (0), (98), (99), (0), (16), (5), (0), (102), (115), (0), (0), (0), (0), (0), (77), (0), (99), (0), (100), (0), (0), (2), (5), (0), (87), (5), (0), (0), (0), (0), (0), (0), (108), (102), (0), (0), (87), (100), (0), (0), (0), (0), (0), (104), (98), (105), (0), (0), (0) }; t.n = 4626; return t end)(), 0, (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (38), (nil), (nil), (775), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("FromName"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("FromValue"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (701), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Clone"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (641283877), (2512572763), (1682885963), (nil), (nil), (nil), (4464), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("NextInteger"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("GetPositionOnCurveArcLength"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (35), (nil), (nil), (4179), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (58), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("NextInteger"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (21), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("GetService"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (3288702418), (2487459757), (2591472795), (2677700713), (1001479288), (231653223), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (3779724099), (3304176315), (2995112660), (nil), (nil), (nil), (32), (nil), (nil), (4315), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1525), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (124), (nil), (nil), (2690), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (219), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("GetLength"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (4080), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("byte"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (nil), (0), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("NextNumber"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("FromName"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Destroy"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (172), (nil), (nil), (1332), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("GetTangentOnCurve"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (50), (nil), (nil), (nil), (167518855), (2782587929), (3402845767), (1196513919), (2901247048), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (56), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("NextInteger"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("GetTangentOnCurveArcLength"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (591), (nil), (nil), (nil), (nil), (nil), (nil), ("NextInteger"), (nil), (nil), (nil), ("GetPositionOnCurveArcLength"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Destroy"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("byte"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (339), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("FromName"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1035), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (42), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (53), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (17), (nil), (nil), (nil), (nil), (nil), (nil), (2621), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (277), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (256), (nil), (nil), (nil), (nil), (nil), (nil), ("NextInteger"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (438), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (3443), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (77), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (119), (nil), (nil), (nil), (3255), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("NextNumber"), (nil), (nil), (nil), ("Clone"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("GetTangentOnCurve"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (2325), (93), (nil), (nil), (2325), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("GetPositionOnCurve"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (212), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (165), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (803742363), (852065409), (1993780189), (609914759), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (35), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (143), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("GetChildren"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Destroy"), (nil), (nil), (nil), (nil), (1535), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (3958), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("GetPositionOnCurve"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (61), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("IsServer"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("NextNumber"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (245), (nil), (nil), (nil), (nil), (209), (nil), (256), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (3790), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("SetControlPoints"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("NextInteger"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (4127), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (207), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (30), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("GetChildren"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (107), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (3936), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("GetService"), (nil), (nil), (nil), ("Destroy"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (103), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("NextInteger"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (438), (nil), (nil), (184), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (262), (nil), (nil), (3130), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("NextInteger"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("NextNumber"), (nil), (nil), (nil), (nil), ("NextNumber"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1832664038), (3231652369), (2124568941), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (98), (nil), (nil), (4464), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (3985), (nil), (nil), (nil), (nil), (34), (nil), (nil), (nil), (nil), (nil), (nil), ("GetTangentOnCurve"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (false), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("GetTangentOnCurveArcLength"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("GetTangentOnCurveArcLength"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("GetService") }; t.n = 4614; return t end)()), {}))
	;(nil --[[ constant not decoded ]])[49](v[1], t3[1])
	;(t1[1])[15] = v[1]

	if t3[6] then
		if (t3[6])[7] then
			if (t3[6])[8] then
				if (t3[6])[9] then
					if (t3[6])[10] then
						if (t3[6])[11] then
							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						else
							(t3[6])[11] = { 11, t1[1] }

							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						end
					else
						(t3[6])[10] = { 10, t1[1] }

						if (t3[6])[11] then
							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						else
							(t3[6])[11] = { 11, t1[1] }

							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						end
					end
				else
					(t3[6])[9] = { 9, t1[1] }

					if (t3[6])[10] then
						if (t3[6])[11] then
							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						else
							(t3[6])[11] = { 11, t1[1] }

							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						end
					else
						(t3[6])[10] = { 10, t1[1] }

						if (t3[6])[11] then
							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						else
							(t3[6])[11] = { 11, t1[1] }

							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						end
					end
				end
			else
				(t3[6])[8] = { 8, t1[1] }

				if (t3[6])[9] then
					if (t3[6])[10] then
						if (t3[6])[11] then
							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						else
							(t3[6])[11] = { 11, t1[1] }

							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						end
					else
						(t3[6])[10] = { 10, t1[1] }

						if (t3[6])[11] then
							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						else
							(t3[6])[11] = { 11, t1[1] }

							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						end
					end
				else
					(t3[6])[9] = { 9, t1[1] }

					if (t3[6])[10] then
						if (t3[6])[11] then
							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						else
							(t3[6])[11] = { 11, t1[1] }

							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						end
					else
						(t3[6])[10] = { 10, t1[1] }

						if (t3[6])[11] then
							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						else
							(t3[6])[11] = { 11, t1[1] }

							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						end
					end
				end
			end
		else
			(t3[6])[7] = { 7, t1[1] }

			if (t3[6])[8] then
				if (t3[6])[9] then
					if (t3[6])[10] then
						if (t3[6])[11] then
							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						else
							(t3[6])[11] = { 11, t1[1] }

							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						end
					else
						(t3[6])[10] = { 10, t1[1] }

						if (t3[6])[11] then
							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						else
							(t3[6])[11] = { 11, t1[1] }

							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						end
					end
				else
					(t3[6])[9] = { 9, t1[1] }

					if (t3[6])[10] then
						if (t3[6])[11] then
							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						else
							(t3[6])[11] = { 11, t1[1] }

							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						end
					else
						(t3[6])[10] = { 10, t1[1] }

						if (t3[6])[11] then
							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						else
							(t3[6])[11] = { 11, t1[1] }

							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						end
					end
				end
			else
				(t3[6])[8] = { 8, t1[1] }

				if (t3[6])[9] then
					if (t3[6])[10] then
						if (t3[6])[11] then
							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						else
							(t3[6])[11] = { 11, t1[1] }

							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						end
					else
						(t3[6])[10] = { 10, t1[1] }

						if (t3[6])[11] then
							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						else
							(t3[6])[11] = { 11, t1[1] }

							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						end
					end
				else
					(t3[6])[9] = { 9, t1[1] }

					if (t3[6])[10] then
						if (t3[6])[11] then
							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						else
							(t3[6])[11] = { 11, t1[1] }

							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						end
					else
						(t3[6])[10] = { 10, t1[1] }

						if (t3[6])[11] then
							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						else
							(t3[6])[11] = { 11, t1[1] }

							if not (t3[6])[3] then
								(t3[6])[3] = { 3, t1[1] }
							end
						end
					end
				end
			end
		end
	end
	;(t1[1])[14][0] = (t1[1])[15]
	;(t1[1])[14][103] = "Instance"
	;(t1[1])[14][140] = "GetAsync"
	;(t1[1])[14][10] = "find"
	;(t1[1])[15] = (t3[1]).tonumber
	;(t1[1])[14][28] = (t1[1])[15]
	;(t1[1])[14][72] = "select"
	;(t1[1])[15] = (t3[1]).typeof
	;(t1[1])[14][13] = (t1[1])[15]
	;(t1[1])[14][125] = "Folder"
	;(t1[1])[14][5] = "gmatch"
	;(t1[1])[14][39] = "close"
	;(t1[1])[15] = (t3[1]).select
	;(t1[1])[14][70] = (t1[1])[15]
	;(t1[1])[14][64] = "nparams"
	;(t1[1])[14][11] = "concat"
	;(t1[1])[14][147] = "Left"
	;(t1[1])[14][66] = "namewhat"
	;(t1[1])[14][30] = "resume"
	;(t1[1])[14][17] = "rep"
	;(t1[1])[14][136] = "IsClient"
	;(t1[1])[14][112] = "Disconnect"
	;(t1[1])[14][63] = "C"
	;(t1[1])[14][138] = "GetChildren"
	;(t1[1])[14][29] = "spawn"
	;(t1[1])[14][133] = "RunService"
	;(t1[1])[15] = (t3[1]).tostring
	;(t1[1])[14][20] = (t1[1])[15]
	;(t1[1])[14][113] = "Connected"
	;(t1[1])[15] = (t3[1]).type
	;(t1[1])[14][48] = (t1[1])[15]
	;(t1[1])[15] = (t3[1]).error
	;(t1[1])[14][69] = (t1[1])[15]
	;(t1[1])[14][1] = (t1[1])[0]
	;(t1[1])[15] = (t3[1]).bit32
	;(t1[1])[15] = (t1[1])[15].bnot
	;(t1[1])[14][157] = (t1[1])[15]
	;(t1[1])[14][89] = "wait"
	;(t1[1])[14][108] = "Name"
	;(t1[1])[14][91] = "new"
	;(t1[1])[15] = (t3[1]).setfenv
	;(t1[1])[14][49] = (t1[1])[15]
	;(t1[1])[15] = (t3[1]).string
	;(t1[1])[14][3] = (t1[1])[15]
	;(t1[1])[14][166] = "function"
	;(t1[1])[14][79] = "xpcall"
	;(t1[1])[14][80] = "error"
	;(t1[1])[15] = (t3[1]).debug
	;(t1[1])[14][14] = "sub"
	;(t1[1])[15] = (t3[1]).setmetatable
	;(t1[1])[14][19] = (t1[1])[15]
	;(t1[1])[14][47] = false
	;(t1[1])[14][58] = "isvararg"
	;(t1[1])[14][146] = "NormalId"
	;(t1[1])[15] = (t3[1]).xpcall
	;(t1[1])[14][54] = (t1[1])[15]
	;(t1[1])[15] = (t3[1]).iscclosure
	;(t1[1])[14][97] = (t1[1])[15]
	;(t1[1])[14][61] = "=[C]"
	;(t1[1])[15] = (t3[1]).bit32
	;(t1[1])[15] = (t1[1])[15].countlz
	;(t1[1])[14][159] = (t1[1])[15]
	;(t1[1])[14][121] = "X"
	;(t1[1])[14][77] = "tostring"
	;(t1[1])[15] = (t3[1]).CFrame
	;(t1[1])[14][90] = (t1[1])[15]
	;(t1[1])[14][78] = "setmetatable"
	;(t1[1])[15] = (t3[1]).utf8
	;(t1[1])[15] = (t1[1])[15].nfcnormalize
	;(t1[1])[14][99] = (t1[1])[15]
	;(t1[1])[14][149] = "IsA"
	;(t1[1])[14][127] = "Random"
	;(t1[1])[14][131] = "Clone"
	;(t1[1])[15] = (t3[1]).getmetatable
	;(t1[1])[14][23] = (t1[1])[15]
	;(t1[1])[14][67] = ""
	;(t1[1])[15] = (t3[1]).utf8
	;(t1[1])[14][98] = (t1[1])[15]
	;(t1[1])[14][7] = "format"
	;(t1[1])[14][105] = "Parent"
	;(t1[1])[14][162] = "__index"
	;(t1[1])[14][86] = "next"
	;(t1[1])[14][106] = "ClassName"
	;(t1[1])[14][107] = "string"
	;(t1[1])[14][117] = "Size"
	;(t1[1])[15] = (t3[1]).bit32
	;(t1[1])[15] = (t1[1])[15].bor
	;(t1[1])[14][158] = (t1[1])[15]
	;(t1[1])[15] = (t3[1]).coroutine
	;(t1[1])[14][9] = (t1[1])[15]
	;(t1[1])[15] = (t3[1]).pcall
	;(t1[1])[14][2] = (t1[1])[15]
	;(t1[1])[15] = (t3[1]).bit32
	;(t1[1])[15] = (t1[1])[15].lshift
	;(t1[1])[14][156] = (t1[1])[15]
	;(t1[1])[15] = (t3[1]).UDim
	;(t1[1])[15] = (t1[1])[15].new
	;(t1[1])[14][95] = (t1[1])[15]
	;(t1[1])[15] = (t1[1])[14]
	;(t1[1])[14] = (t1[1])[14][0]
	error("devirt: symbolic generic for (at 0:378)")
end

-- proto 3: vm sequence 3, 0 opcodes
local function proto_3()
	(t1[1])[1] = (t2[2])[1]
	;(t1[1])[2] = (t2[2])[2]
	error("devirt: symbolic generic for (at 0:5)")
end

-- proto t424: vm sequence 4, 0 opcodes
local function proto_t424()
	(t1[1])[20] = {
		0,
		0,
		0,
		0,
		0,
		0,
		2,
		0,
		1,
		1,
		0,
		232,
		1,
		215,
		177,
		82,
		188,
		8,
		145,
		0,
		0,
		0,
		0,
		5,
		0,
		0,
		0,
		0,
		15,
		0,
		21,
		0,
		19,
		15,
		20,
		19,
		21,
		206,
		8,
		0,
		0,
		0,
		255,
		0,
		320,
		6,
		3,
		0,
		0,
		0,
		0,
		0,
		15,
		21,
		15,
		20,
		21,
		244,
		158,
		0,
		0,
		11,
		355,
		162,
		12,
		852,
		11,
		185,
		198,
		0,
		23,
		0,
		21,
		0,
		20,
		21,
		21,
		0,
		0,
	}
	;(t1[1])[15] = {
		127,
		127,
		178,
		42,
		8,
		127,
		40,
		8,
		26,
		88,
		127,
		116,
		187,
		170,
		77,
		73,
		146,
		110,
		172,
		92,
		92,
		43,
		127,
		158,
		127,
		127,
		127,
		127,
		90,
		34,
		131,
		93,
		101,
		101,
		101,
		101,
		101,
		60,
		19,
		127,
		142,
		142,
		142,
		127,
		137,
		155,
		173,
		142,
		142,
		142,
		127,
		93,
		90,
		131,
		101,
		101,
		101,
		60,
		19,
		127,
		127,
		131,
		81,
		5,
		141,
		17,
		101,
		60,
		19,
		127,
		18,
		127,
		131,
		93,
		101,
		101,
		101,
		92,
		127,
	}
	;(t1[1])[21] = {
		26,
		27,
		89,
		0,
		89,
		6,
		70,
		4,
		0,
		0,
		2,
		145,
		45,
		99,
		217,
		252,
		95,
		5,
		40,
		0,
		2,
		0,
		7,
		1,
		70,
		72,
		1,
		51,
		0,
		0,
		0,
		20,
		62,
		62,
		323,
		323,
		77,
		14,
		181,
		40,
		45,
		3,
		3,
		25,
		221,
		1,
		0,
		1,
		3,
		3,
		60,
		20,
		0,
		0,
		94,
		45,
		7,
		14,
		83,
		61,
		28,
		0,
		332,
		12,
		1005,
		12,
		6,
		4,
		182,
		45,
		0,
		71,
		0,
		20,
		105,
		105,
		116,
		14,
		11,
	}
	;(t1[1])[15][63] = 76
	;(t1[1])[20][64] = 12
	;(t1[1])[21][28] = 61
	;(t1[1])[11] = {
		26,
		27,
		89,
		0,
		89,
		6,
		70,
		4,
		0,
		0,
		2,
		145,
		45,
		99,
		217,
		252,
		95,
		5,
		40,
		0,
		2,
		0,
		7,
		1,
		70,
		72,
		1,
		51,
		0,
		0,
		0,
		20,
		62,
		62,
		323,
		323,
		77,
		14,
		181,
		40,
		45,
		3,
		3,
		25,
		221,
		1,
		0,
		1,
		3,
		3,
		60,
		20,
		0,
		0,
		94,
		45,
		7,
		14,
		83,
		61,
		28,
		0,
		332,
		12,
		1005,
		12,
		6,
		4,
		182,
		45,
		0,
		71,
		0,
		20,
		105,
		105,
		116,
		14,
		11,
	}
	;(t1[1])[355] = (t1[1])[355]((t1[1])[356], (t1[1])[357])
	;(t1[1])[12] = 22445 + (t1[1])[162]
	;(t1[1])[12] = (t1[1])[12] + -22604
	;(t1[1])[11][41] = (t1[1])[12]
	;(t1[1])[11][2] = 45
	;(t1[1])[1] = upv6[1]
	;(t1[1])[3] = nil
	upv0 = (t1[1])[1]
	upv1 = (t1[1])[3]

	upv2 = (t1[1])[3]
	;(t1[1])[15] = {
		127,
		127,
		178,
		42,
		8,
		127,
		40,
		8,
		26,
		88,
		127,
		116,
		187,
		170,
		77,
		73,
		146,
		110,
		172,
		92,
		92,
		43,
		127,
		158,
		127,
		127,
		127,
		127,
		90,
		34,
		131,
		93,
		101,
		101,
		101,
		101,
		101,
		60,
		19,
		127,
		142,
		142,
		142,
		127,
		137,
		155,
		173,
		142,
		142,
		142,
		127,
		93,
		90,
		131,
		101,
		101,
		101,
		60,
		19,
		127,
		127,
		131,
		81,
		5,
		141,
		17,
		101,
		60,
		19,
		127,
		18,
		127,
		131,
		93,
		101,
		101,
		101,
		92,
		127,
	}
	;(t1[1])[19] = {
		0,
		0,
		232,
		3,
		4,
		0,
		0,
		1,
		0,
		0,
		0,
		2,
		97,
		82,
		230,
		254,
		206,
		71,
		226,
		2,
		4,
		0,
		0,
		0,
		0,
		0,
		0,
		0,
		0,
		19,
		0,
		0,
		6,
		55,
		32,
		4,
		739,
		21,
		234,
		0,
		3,
		4,
		193,
		0,
		498,
		42,
		0,
		0,
		1,
		2,
		0,
		0,
		0,
		0,
		90,
		105,
		77,
		21,
		179,
		0,
		0,
		0,
		12,
		220,
		12,
		11,
		146,
		13,
		205,
		0,
		2,
		0,
		0,
		0,
		89,
		32,
		50,
		21,
		0,
	}
	;(t1[1])[21] = {
		26,
		27,
		89,
		0,
		89,
		6,
		70,
		4,
		0,
		0,
		2,
		145,
		45,
		99,
		217,
		252,
		95,
		5,
		40,
		0,
		2,
		0,
		7,
		1,
		70,
		72,
		1,
		51,
		0,
		0,
		0,
		20,
		62,
		62,
		323,
		323,
		77,
		14,
		181,
		40,
		45,
		3,
		3,
		25,
		221,
		1,
		0,
		1,
		3,
		3,
		60,
		20,
		0,
		0,
		94,
		45,
		7,
		14,
		83,
		61,
		28,
		0,
		332,
		12,
		1005,
		12,
		6,
		4,
		182,
		45,
		0,
		71,
		0,
		20,
		105,
		105,
		116,
		14,
		11,
	}
	;(t1[1])[20] = {
		0,
		0,
		0,
		0,
		0,
		0,
		2,
		0,
		1,
		1,
		0,
		232,
		1,
		215,
		177,
		82,
		188,
		8,
		145,
		0,
		0,
		0,
		0,
		5,
		0,
		0,
		0,
		0,
		15,
		0,
		21,
		0,
		19,
		15,
		20,
		19,
		21,
		206,
		8,
		0,
		0,
		0,
		255,
		0,
		320,
		6,
		3,
		0,
		0,
		0,
		0,
		0,
		15,
		21,
		15,
		20,
		21,
		244,
		158,
		0,
		0,
		11,
		355,
		162,
		12,
		852,
		11,
		185,
		198,
		0,
		23,
		0,
		21,
		0,
		20,
		21,
		21,
		0,
		0,
	}
	;(t1[1])[19][3] = 2
	;(t1[1])[15][3] = 8
	;(t1[1])[20][43] = 0
	;(t1[1])[19][43] = 5
	;(t1[1])[21][61] = 40
	upv3 = (t1[1])[45]
	upv4 = (t1[1])[3]

	upv193 = (t1[1])[3]
	;(t1[1])[21] = {
		26,
		27,
		89,
		0,
		89,
		6,
		70,
		4,
		0,
		0,
		2,
		145,
		45,
		99,
		217,
		252,
		95,
		5,
		40,
		0,
		2,
		0,
		7,
		1,
		70,
		72,
		1,
		51,
		0,
		0,
		0,
		20,
		62,
		62,
		323,
		323,
		77,
		14,
		181,
		40,
		45,
		3,
		3,
		25,
		221,
		1,
		0,
		1,
		3,
		3,
		60,
		20,
		0,
		0,
		94,
		45,
		7,
		14,
		83,
		61,
		28,
		0,
		332,
		12,
		1005,
		12,
		6,
		4,
		182,
		45,
		0,
		71,
		0,
		20,
		105,
		105,
		116,
		14,
		11,
	}
	;(t1[1])[20] = {
		0,
		0,
		0,
		0,
		0,
		0,
		2,
		0,
		1,
		1,
		0,
		232,
		1,
		215,
		177,
		82,
		188,
		8,
		145,
		0,
		0,
		0,
		0,
		5,
		0,
		0,
		0,
		0,
		15,
		0,
		21,
		0,
		19,
		15,
		20,
		19,
		21,
		206,
		8,
		0,
		0,
		0,
		255,
		0,
		320,
		6,
		3,
		0,
		0,
		0,
		0,
		0,
		15,
		21,
		15,
		20,
		21,
		244,
		158,
		0,
		0,
		11,
		355,
		162,
		12,
		852,
		11,
		185,
		198,
		0,
		23,
		0,
		21,
		0,
		20,
		21,
		21,
		0,
		0,
	}
	;(t1[1])[20][12] = 1
	;(t1[1])[21][12] = 0
	;(t1[1])[21][26] = 11
	;(t1[1])[14] = nil
	;(t1[1])[15] = nil
	;(t1[1])[16] = nil
	;(t1[1])[17] = nil
	;(t1[1])[18] = nil
	;(t1[1])[19] = nil
	;(t1[1])[20] = nil
	;(t1[1])[21] = nil

	local v = table.pack((nil --[[ constant not decoded ]])[57](table.pack({}, (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (116), (24), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (table.pack({}, (function() local t = { (nil), (nil), (nil), (nil), (0), (79), (nil), (nil), (nil), (0), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (25), (1), (7), (1), (90), (nil), (nil), (nil), (nil), (nil), (nil), (85), (17), (83), (nil), (nil), (nil), (nil), (92), (71), (nil), (nil), (nil), (nil), (nil), (0), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (283), (nil), (nil), (nil), (0), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (nil), (nil), (nil), (1476), (nil), (nil), (11) }; t.n = 98; return t end)(), 27, (function() local t = { (15), (23), (25), (0), (676), (99), (19), (157), (79), (16), (76), (0), (89), (32), (58), (41), (2), (1), (86), (103), (43), (723), (94), (5), (6), (60), (100), (29), (49), (0), (25), (0), (0), (116), (77), (77), (77), (7), (19), (62), (90), (0), (25), (0), (40), (40), (80), (19), (83), (0), (0), (551), (1057), (19), (184), (71), (332), (81), (17), (27), (5), (6), (6), (64), (6), (6), (58), (5), (6), (6), (9), (0), (0), (304), (81), (85), (5), (67), (92), (5), (0), (17), (19), (28), (497), (56), (1), (101), (72), (9), (17), (1), (3), (67), (17), (839), (17), (102), (9), (11), (3), (60) }; t.n = 102; return t end)(), (function() local t = { (127), (127), (93), (131), (101), (101), (60), (19), (127), (62), (127), (58), (178), (8), (127), (127), (127), (48), (127), (77), (75), (161), (127), (182), (182), (248), (127), (127), (127), (34), (93), (131), (90), (101), (101), (101), (101), (101), (60), (19), (127), (131), (93), (90), (101), (101), (101), (92), (127), (90), (131), (101), (101), (60), (19), (127), (8), (127), (62), (127), (246), (4), (1), (127), (4), (96), (127), (1), (4), (96), (127), (131), (90), (143), (32), (127), (182), (62), (127), (185), (65), (39), (127), (127), (57), (127), (160), (67), (91), (127), (62), (127), (47), (127), (5), (141), (17), (101), (153), (127), (47), (127) }; t.n = 102; return t end)(), {}, (function() local t = { (0), (0), (0), (26), (25), (26), (97), (12), (0), (1), (0), (2), (0), (0), (0), (0), (0), (2), (0), (214), (113), (67), (0), (6), (6), (6), (0), (0), (0), (0), (0), (26), (20), (20), (24), (25), (20), (26), (39), (223), (0), (26), (0), (20), (20), (25), (26), (0), (0), (20), (26), (20), (26), (83), (62), (0), (0), (0), (1), (0), (132), (1), (7), (0), (2), (3), (0), (6), (1), (3), (0), (16), (10), (226), (17), (0), (6), (5), (0), (4), (127), (94), (0), (0), (489), (0), (241), (2), (168), (0), (2), (0), (4), (0), (17), (17), (612), (16), (0), (0), (4), (0) }; t.n = 102; return t end)(), (function() local t = { (nil), (nil), (nil), (nil), (81), (17), (nil), (nil), (nil), (nil), (nil), (nil), (1), (0), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (205), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (26), (61), (61), (61), (28), (nil), (nil), (nil), (nil), (nil), (nil), (74), (74), (16), (nil), (nil), (nil), (nil), (99), (29), (nil), (nil), (nil), (511), (nil), (nil), (nil), (nil), (2), (nil), (nil), (2), (2), (nil), (nil), (2), (2), (nil), (nil), (nil), (154), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (-1673), (nil), (84) }; t.n = 98; return t end)(), (function() local t = { (0), (0), (0), (0), (32), (433), (26), (252), (0), (32), (0), (0), (3), (4), (0), (0), (0), (9), (0), (142), (17), (254), (0), (1), (2), (5), (0), (0), (0), (24), (0), (0), (0), (187), (89), (28), (89), (30), (26), (253), (0), (0), (0), (0), (898), (99), (83), (26), (0), (0), (0), (487), (705), (26), (5), (0), (17), (0), (32), (0), (116), (7), (2), (0), (7), (3), (0), (1), (6), (3), (0), (0), (0), (755), (0), (0), (1), (32), (0), (0), (5), (0), (0), (0), (177), (0), (154), (210), (47), (0), (32), (0), (4), (0), (338), (17), (10), (50), (18), (0), (4), (0) }; t.n = 102; return t end)(), 0, (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (2), (2), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (2), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (13) }; t.n = 97; return t end)())), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (373), (4321), (nil), (nil), (2), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (9), (10), (181), (28), (nil), (nil), (nil), (table.pack({}, table.pack(nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 29163, nil, nil, 6, nil, nil, nil, nil, nil, 8, 0, 74, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 47, 4, 65, nil, nil, nil, nil, nil, nil, nil, nil, nil, 5, 2, 6, 6), 26, (function() local t = { (63), (0), (34), (22), (32), (1), (0), (18), (50), (0), (14), (109), (16), (720), (16), (628), (28), (75), (41), (24), (0), (99), (99), (79), (18), (74), (89), (39), (89), (6), (4), (89), (89), (6), (89), (6), (4), (5), (72), (5), (2), (0), (0), (0), (464), (464), (91), (18), (150), (65), (28), (86), (19), (24), (0), (0), (674), (66), (66), (90), (18), (54), (6), (52), (26), (89), (6), (4), (5), (4), (39), (64), (5), (0), (9), (53) }; t.n = 76; return t end)(), (function() local t = { (127), (65), (77), (75), (161), (127), (58), (32), (127), (131), (93), (76), (5), (141), (17), (101), (92), (127), (127), (93), (131), (101), (101), (101), (92), (127), (8), (127), (29), (57), (54), (29), (29), (1), (141), (57), (61), (182), (127), (39), (127), (131), (90), (34), (101), (101), (101), (60), (19), (127), (127), (108), (127), (93), (131), (34), (101), (101), (101), (101), (60), (19), (127), (127), (127), (29), (57), (58), (61), (27), (32), (127), (1), (65), (127), (127) }; t.n = 76; return t end)(), {}, (function() local t = { (0), (0), (91), (86), (140), (0), (3), (3), (0), (15), (0), (221), (16), (16), (65), (15), (189), (0), (0), (0), (25), (25), (24), (25), (0), (0), (0), (0), (2), (4), (4), (34), (204), (151), (5), (5), (4), (89), (0), (1), (0), (25), (19), (0), (19), (23), (25), (18), (87), (0), (0), (251), (0), (0), (25), (0), (24), (24), (23), (25), (79), (121), (0), (0), (0), (2), (4), (5), (1), (5), (5), (0), (5), (0), (0), (0) }; t.n = 76; return t end)(), (function() local t = { (nil), (nil), (nil), (nil), (0), (nil), (nil), (nil), (nil), (nil), (nil), (32), (nil), (-29057), (nil), (75), (nil), (nil), (nil), (nil), (nil), (17), (17), (53), (nil), (nil), (1), (nil), (1), (2), (nil), (1), (1), (nil), (1), (2), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (68), (68), (19), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (34), (33), (33), (76), (nil), (nil), (nil), (nil), (nil), (1), (2) }; t.n = 67; return t end)(), (function() local t = { (0), (5), (47), (5), (149), (0), (0), (0), (0), (0), (0), (16), (129), (16), (14), (51), (17), (0), (0), (0), (0), (55), (32), (40), (25), (0), (5), (0), (4), (4), (1), (5), (176), (5), (5), (5), (5), (4), (0), (0), (0), (0), (0), (23), (58), (71), (48), (25), (24), (0), (0), (47), (0), (0), (0), (23), (4), (6), (51), (51), (25), (162), (0), (0), (0), (4), (4), (161), (5), (5), (0), (0), (4), (5), (0), (0) }; t.n = 76; return t end)(), 0, table.pack(nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 135, nil, nil, 32, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 1))), (table.pack(table.pack(table.pack(1, 1), table.pack(4, 1), table.pack(5, 1)), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (8), (39), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (6), (0), (0), (43), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (6), (0), (185), (15), (nil), (nil), (nil), (nil), (nil), (454), (nil), (nil), (17492), (nil), (nil), (15), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (81) }; t.n = 86; return t end)(), 27, (function() local t = { (57), (179), (7), (80), (0), (71), (29), (0), (0), (431), (3), (19), (122), (39), (58), (71), (5), (5), (17), (76), (1), (45), (0), (599), (38), (1), (2), (89), (14), (0), (0), (6), (6), (580), (28), (19), (46), (43), (7), (6), (7), (65), (6), (113), (553), (6), (1), (0), (0), (0), (396), (91), (91), (91), (705), (19), (15), (82), (0), (15), (165), (987), (64), (17), (619), (17), (85), (9), (70), (2), (47), (104), (6), (6), (7), (118), (77), (55), (0), (6), (0), (25), (0), (0), (116), (23), (19), (81) }; t.n = 88; return t end)(), (function() local t = { (127), (195), (185), (8), (81), (127), (127), (131), (90), (101), (101), (60), (19), (127), (127), (8), (22), (195), (85), (77), (75), (161), (81), (96), (127), (195), (195), (8), (127), (131), (34), (101), (101), (101), (101), (60), (19), (127), (127), (195), (185), (21), (127), (81), (96), (47), (127), (34), (131), (90), (101), (101), (101), (101), (101), (92), (127), (127), (131), (93), (31), (66), (79), (5), (141), (17), (101), (92), (127), (130), (127), (96), (47), (195), (160), (67), (91), (8), (81), (47), (65), (127), (131), (34), (101), (101), (92), (127) }; t.n = 88; return t end)(), {}, (function() local t = { (0), (2), (2), (0), (6), (0), (0), (26), (20), (20), (26), (91), (115), (0), (0), (0), (4), (2), (4), (56), (32), (181), (5), (5), (0), (0), (1), (0), (0), (26), (0), (26), (24), (26), (26), (5), (127), (0), (0), (2), (184), (0), (0), (6), (6), (5), (0), (0), (26), (20), (24), (26), (24), (20), (26), (0), (0), (0), (16), (0), (17), (29), (223), (17), (17), (852), (16), (0), (0), (471), (0), (6), (5), (2), (228), (1), (89), (0), (6), (5), (0), (0), (26), (0), (24), (26), (0), (0) }; t.n = 88; return t end)(), (function() local t = { (nil), (nil), (nil), (16), (nil), (nil), (nil), (nil), (nil), (42), (39), (nil), (nil), (nil), (nil), (4), (nil), (nil), (nil), (nil), (nil), (64), (nil), (16777216), (nil), (nil), (nil), (1), (nil), (nil), (nil), (2), (2), (44), (7), (nil), (nil), (nil), (nil), (nil), (nil), (32), (nil), (nil), (65536), (nil), (nil), (nil), (nil), (nil), (18), (19), (19), (19), (71), (nil), (nil), (nil), (nil), (nil), (nil), (45), (nil), (nil), (-17988), (nil), (15), (nil), (nil), (nil), (nil), (256), (nil), (nil), (nil), (nil), (nil), (8), (nil), (nil), (nil), (nil), (nil), (nil), (26), (58) }; t.n = 86; return t end)(), (function() local t = { (0), (212), (0), (8), (0), (0), (0), (0), (0), (55), (3), (26), (9), (0), (0), (4), (1), (244), (13), (193), (7), (250), (0), (5), (0), (61), (0), (3), (0), (0), (24), (51), (32), (32), (323), (26), (162), (0), (0), (0), (0), (8), (0), (0), (6), (5), (0), (24), (0), (0), (32), (51), (32), (8), (85), (26), (0), (0), (0), (0), (406), (88), (223), (635), (17), (15), (85), (18), (0), (3), (0), (6), (5), (0), (141), (71), (124), (8), (0), (5), (5), (0), (0), (24), (32), (676), (26), (0) }; t.n = 88; return t end)(), 0, (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (41) }; t.n = 66; return t end)())), (table.pack(table.pack(table.pack(7, 1), table.pack(6, 1)), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (1), (0), (8), (96), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (97), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (7), (2), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (8), (10), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (27863), (nil), (nil), (83), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (32), (110), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (12), (6), (6), (52) }; t.n = 122; return t end)(), 28, (function() local t = { (82), (99), (6), (241), (56), (35), (65), (0), (89), (106), (1069), (6), (7), (125), (73), (92), (156), (12), (159), (239), (227), (2), (0), (89), (4), (5), (38), (26), (0), (0), (0), (80), (80), (3), (3), (83), (20), (96), (89), (899), (4), (141), (1), (5), (6), (65), (0), (33), (94), (20), (97), (137), (89), (32), (109), (0), (71), (850), (20), (195), (2), (107), (46), (708), (1), (422), (442), (4), (72), (32), (0), (373), (55), (89), (32), (62), (0), (73), (590), (20), (73), (10), (27), (15), (0), (0), (714), (18), (239), (18), (108), (10), (83), (32), (32), (51), (84), (7), (129), (0), (0), (1038), (6), (20), (116), (110), (115), (32), (69), (113), (7), (62), (14), (61), (76), (0), (0), (0), (79), (79), (79), (1034), (20), (18), (52), (802), (89), (8), (0), (93), (89), (32), (114) }; t.n = 133; return t end)(), (function() local t = { (127), (127), (195), (185), (77), (75), (161), (81), (57), (127), (29), (57), (89), (127), (127), (195), (103), (24), (174), (129), (172), (195), (181), (8), (195), (185), (127), (93), (90), (34), (131), (101), (101), (101), (101), (101), (92), (127), (250), (8), (126), (96), (47), (195), (185), (127), (131), (101), (101), (92), (127), (65), (201), (86), (127), (131), (101), (101), (60), (19), (127), (127), (127), (86), (127), (8), (8), (126), (127), (96), (65), (87), (127), (96), (4), (127), (131), (101), (101), (60), (19), (127), (127), (127), (34), (131), (76), (5), (141), (17), (101), (92), (127), (96), (4), (127), (127), (39), (127), (90), (131), (101), (101), (60), (19), (127), (127), (86), (127), (127), (154), (207), (127), (127), (127), (90), (34), (131), (101), (101), (101), (101), (60), (19), (127), (4), (47), (89), (65), (127), (8), (8), (127) }; t.n = 133; return t end)(), {}, (function() local t = { (0), (0), (1), (2), (32), (126), (11), (6), (6), (0), (5), (7), (6), (0), (0), (0), (1), (169), (158), (245), (164), (0), (2), (0), (1), (2), (0), (0), (21), (0), (27), (25), (27), (26), (21), (27), (0), (0), (73), (0), (0), (4), (4), (1), (2), (0), (27), (27), (27), (0), (0), (0), (0), (5), (0), (27), (27), (27), (42), (48), (0), (0), (0), (5), (0), (0), (0), (0), (0), (7), (0), (246), (0), (7), (7), (0), (27), (27), (27), (40), (215), (0), (0), (0), (0), (17), (142), (18), (18), (331), (17), (0), (0), (7), (7), (0), (0), (51), (0), (21), (27), (21), (27), (38), (73), (0), (0), (4), (0), (0), (4), (7), (0), (0), (0), (21), (0), (27), (21), (25), (27), (27), (203), (45), (0), (8), (8), (7), (0), (0), (0), (0), (0) }; t.n = 133; return t end)(), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (32), (nil), (1), (nil), (1023), (2), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (16), (16), (39), (39), (83), (nil), (nil), (1), (20), (nil), (4294967296), (nil), (nil), (nil), (nil), (nil), (52), (63), (nil), (nil), (nil), (nil), (0), (nil), (nil), (4), (73), (nil), (nil), (nil), (nil), (nil), (2047), (nil), (21), (31), (nil), (nil), (0), (nil), (nil), (nil), (1), (0), (nil), (nil), (127), (115), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (478), (nil), (-28053), (nil), (97), (nil), (nil), (0), (0), (nil), (nil), (nil), (nil), (nil), (nil), (112), (2), (nil), (nil), (nil), (nil), (0), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (53), (53), (53), (107), (nil), (nil), (nil), (4503599627370496), (nil), (nil), (nil), (nil), (1), (0) }; t.n = 132; return t end)(), (function() local t = { (0), (0), (0), (0), (139), (8), (181), (0), (6), (0), (7), (7), (7), (0), (0), (215), (36), (3), (111), (169), (71), (0), (0), (3), (0), (0), (0), (0), (0), (25), (0), (32), (89), (32), (55), (527), (27), (0), (6), (7), (4), (4), (4), (0), (0), (0), (0), (32), (108), (27), (0), (7), (76), (63), (0), (0), (28), (6), (27), (251), (0), (0), (0), (114), (0), (7), (166), (5), (0), (6), (7), (300), (0), (6), (7), (0), (0), (55), (115), (27), (234), (0), (0), (0), (15), (0), (18), (520), (18), (15), (83), (19), (0), (6), (7), (0), (0), (0), (0), (0), (0), (65), (283), (27), (19), (0), (0), (130), (0), (0), (32), (0), (0), (0), (0), (0), (25), (0), (105), (51), (51), (33), (27), (142), (0), (4), (3), (7), (7), (0), (5), (3), (0) }; t.n = 133; return t end)(), 0, (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (280), (nil), (nil), (67) }; t.n = 90; return t end)())), (table.pack(table.pack(table.pack(7, 1), table.pack(5, 1), table.pack(8, 1), table.pack(6, 1)), (function() local t = { (nil), (nil), (nil), (nil), (nil), (195), (113), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (16), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (127), (102), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (22), (12), (61), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (3266), (nil), (nil), (216), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (2), (98), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (12), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (15), (0), (158), (nil), (nil), (nil), (nil), (nil), (5), (0), (231), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (195), (2), (15), (195), (91), (nil), (nil), (nil), (nil), (nil), (0), (18), (222) }; t.n = 187; return t end)(), 36, (function() local t = { (25), (89), (236), (0), (0), (178), (168), (28), (113), (143), (0), (49), (0), (231), (171), (89), (7), (0), (1), (0), (0), (26), (136), (41), (150), (79), (182), (15), (212), (92), (21), (35), (222), (227), (0), (16), (0), (0), (0), (16), (164), (1065), (136), (0), (0), (425), (1003), (28), (102), (0), (236), (0), (0), (34), (0), (52), (52), (52), (1002), (28), (61), (12), (151), (66), (11), (9), (186), (13), (0), (0), (11), (10), (167), (26), (411), (26), (27), (18), (216), (89), (2), (0), (95), (0), (34), (479), (479), (704), (28), (16), (98), (15), (97), (0), (24), (89), (165), (195), (0), (1), (2), (120), (19), (0), (0), (11), (12), (0), (13), (0), (0), (11), (162), (14), (150), (29), (103), (185), (218), (223), (146), (3), (0), (0), (83), (3), (0), (926), (514), (28), (12), (171), (32), (176), (89), (10), (26), (239), (27), (0), (227), (190), (27), (0), (0), (412), (412), (115), (28), (158), (0), (34), (0), (677), (677), (187), (28), (231), (15), (14), (0), (138), (144), (181), (43), (0), (238), (11), (0), (12), (103), (0), (34), (0), (500), (840), (291), (291), (490), (28), (91), (126), (0), (0), (503), (503), (745), (28), (17), (222), (27), (14), (0), (223), (125), (15), (16), (0), (101), (198), (128), (223), (17), (0), (0), (9), (51), (10), (11), (0), (211), (12), (0), (0), (11), (206), (0), (17), (0), (0), (15), (10), (162), (15), (0), (15), (131), (15), (14), (90), (34), (0), (32), (176), (89), (26), (19), (93), (124), (113), (73) }; t.n = 241; return t end)(), (function() local t = { (127), (8), (40), (131), (90), (101), (101), (92), (127), (127), (18), (127), (168), (77), (75), (161), (195), (181), (127), (131), (90), (179), (32), (127), (127), (127), (127), (195), (103), (24), (174), (129), (172), (127), (181), (195), (22), (23), (190), (195), (127), (8), (127), (131), (90), (101), (101), (92), (127), (168), (127), (90), (131), (93), (34), (101), (101), (101), (101), (92), (127), (195), (103), (24), (174), (129), (172), (195), (22), (23), (158), (195), (127), (5), (141), (17), (101), (92), (127), (8), (195), (181), (127), (131), (93), (101), (101), (101), (60), (19), (127), (39), (127), (168), (127), (8), (40), (127), (168), (195), (195), (127), (127), (140), (23), (195), (195), (181), (195), (22), (23), (158), (127), (10), (103), (24), (174), (129), (172), (127), (181), (195), (22), (150), (127), (127), (131), (101), (101), (92), (127), (127), (8), (8), (8), (40), (39), (127), (195), (181), (32), (127), (163), (34), (131), (101), (101), (101), (92), (127), (34), (93), (131), (101), (101), (101), (92), (127), (158), (195), (181), (127), (95), (127), (127), (18), (127), (195), (181), (195), (127), (90), (93), (131), (101), (101), (101), (101), (101), (92), (127), (127), (131), (90), (101), (101), (101), (60), (19), (127), (127), (195), (181), (32), (127), (195), (195), (103), (24), (174), (129), (172), (195), (22), (23), (127), (127), (195), (195), (181), (127), (195), (22), (23), (195), (127), (181), (195), (22), (15), (158), (77), (40), (195), (181), (26), (127), (158), (212), (18), (127), (88), (8), (8), (8), (127), (18), (127), (127), (8), (127) }; t.n = 241; return t end)(), {}, (function() local t = { (0), (0), (6), (35), (29), (29), (35), (0), (0), (0), (191), (0), (0), (68), (223), (4), (0), (7), (0), (25), (19), (517), (26), (0), (0), (0), (0), (2), (15), (47), (137), (132), (188), (0), (15), (0), (1), (0), (15), (2), (0), (0), (0), (35), (29), (29), (35), (0), (0), (0), (0), (29), (35), (0), (0), (34), (29), (33), (35), (0), (0), (0), (12), (156), (77), (93), (38), (0), (1), (0), (10), (1), (0), (26), (26), (456), (25), (0), (0), (0), (0), (2), (0), (35), (0), (35), (34), (35), (81), (138), (0), (9), (0), (0), (0), (0), (1), (0), (0), (1), (2), (0), (0), (99), (0), (1), (0), (12), (0), (1), (0), (10), (0), (0), (14), (177), (232), (69), (46), (0), (222), (0), (1), (0), (0), (0), (35), (35), (35), (0), (0), (0), (0), (0), (0), (10), (73), (0), (2), (15), (15), (0), (294), (0), (35), (35), (33), (35), (0), (0), (0), (0), (35), (34), (33), (35), (0), (0), (14), (0), (14), (0), (207), (0), (0), (24), (0), (0), (11), (0), (0), (29), (0), (35), (29), (34), (35), (29), (35), (0), (0), (0), (35), (29), (35), (29), (35), (65), (49), (0), (0), (2), (14), (14), (0), (1), (170), (16), (196), (169), (128), (151), (2), (1), (0), (0), (0), (1), (0), (11), (0), (0), (1), (0), (1), (0), (16), (0), (1), (15), (14), (0), (6), (2), (15), (15), (0), (14), (3), (2), (0), (26), (0), (0), (0), (0), (132), (0), (0), (0), (0) }; t.n = 241; return t end)(), (function() local t = { (nil), (1), (nil), (nil), (nil), (114), (126), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (84), (nil), (nil), (nil), (222), (165), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (104), (104), (104), (207), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (-3108), (nil), (103), (nil), (nil), (1), (nil), (nil), (nil), (nil), (nil), (121), (121), (125), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (237), (182), (nil), (nil), (nil), (0), (255), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (139), (139), (10), (nil), (nil), (nil), (nil), (nil), (232), (232), (25), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (229), (197), (230), (230), (132), (nil), (nil), (nil), (nil), (nil), (163), (163), (27), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (255), (1), (nil), (nil), (nil), (nil), (13) }; t.n = 240; return t end)(), (function() local t = { (0), (8), (0), (0), (0), (713), (87), (35), (0), (0), (10), (0), (0), (12), (6), (231), (0), (0), (0), (0), (0), (10), (0), (0), (0), (0), (0), (0), (136), (22), (4), (34), (2), (0), (0), (0), (16), (14), (1), (0), (0), (26), (0), (0), (0), (73), (917), (35), (0), (0), (0), (0), (0), (0), (33), (89), (363), (105), (77), (35), (0), (0), (225), (55), (131), (112), (102), (0), (13), (11), (5), (0), (0), (198), (26), (19), (585), (27), (0), (1), (0), (0), (0), (0), (0), (32), (6), (162), (35), (69), (0), (0), (0), (0), (0), (3), (0), (0), (0), (0), (0), (0), (0), (233), (10), (0), (0), (0), (0), (13), (11), (5), (0), (0), (34), (63), (21), (240), (0), (0), (0), (0), (3), (1), (0), (0), (0), (32), (105), (35), (0), (0), (10), (11), (12), (0), (0), (0), (229), (0), (0), (0), (201), (33), (0), (85), (32), (597), (35), (0), (33), (0), (0), (4), (32), (538), (35), (0), (5), (0), (0), (0), (6), (0), (0), (1), (0), (0), (0), (0), (0), (0), (0), (0), (713), (6), (85), (713), (297), (35), (0), (0), (0), (0), (32), (396), (425), (35), (213), (0), (0), (0), (0), (0), (0), (0), (0), (165), (161), (107), (182), (110), (0), (17), (15), (0), (0), (0), (0), (0), (0), (0), (12), (10), (0), (0), (0), (0), (17), (0), (5), (0), (0), (0), (0), (5), (0), (5), (0), (0), (0), (25), (6), (7), (8), (0), (6), (0), (0), (26), (0) }; t.n = 241; return t end)(), 0, (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (290), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (220) }; t.n = 76; return t end)())), (nil), (nil), (nil), (nil), (nil), (1), (1), (12) }; t.n = 72; return t end)(), 29, (function() local t = { (21), (400), (0), (0), (286), (0), (218), (4), (821), (65), (50), (1), (32), (0), (0), (45), (45), (13), (21), (228), (24), (23), (41), (66), (55), (0), (0), (60), (10), (0), (11), (22), (17), (0), (417), (19), (495), (19), (612), (11), (2), (10), (84), (249), (247), (1), (48), (38), (105), (10), (0), (0), (27), (1057), (19), (19), (50), (21), (101), (28), (0), (0), (0), (66), (10), (13), (0), (27), (0), (71), (4), (925), (21), (87), (12) }; t.n = 75; return t end)(), (function() local t = { (127), (133), (28), (84), (117), (84), (117), (185), (8), (127), (127), (59), (127), (90), (131), (101), (101), (101), (60), (19), (127), (127), (127), (127), (8), (81), (116), (127), (185), (40), (32), (127), (93), (131), (151), (5), (141), (17), (101), (92), (127), (185), (187), (170), (77), (73), (146), (110), (172), (127), (131), (90), (93), (101), (101), (101), (101), (60), (19), (127), (116), (116), (116), (119), (127), (127), (34), (93), (131), (101), (101), (101), (60), (19), (127) }; t.n = 75; return t end)(), {}, (function() local t = { (0), (231), (0), (778), (150), (778), (2), (2), (0), (0), (0), (0), (0), (22), (28), (28), (22), (28), (79), (251), (0), (0), (0), (0), (0), (4), (5), (0), (104), (69), (10), (0), (0), (18), (19), (19), (19), (101), (18), (0), (0), (9), (10), (84), (248), (196), (201), (105), (137), (0), (28), (22), (0), (27), (27), (22), (28), (210), (170), (0), (6), (236), (8), (9), (0), (0), (0), (0), (28), (26), (27), (28), (158), (234), (0) }; t.n = 75; return t end)(), (function() local t = { (nil), (nil), (nil), (nil), ("byte"), (nil), ("rep"), (nil), (" "), (nil), (nil), (nil), (nil), (nil), (nil), (64), (64), (66), (nil), (nil), (nil), (nil), (nil), (nil), (8), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (69), (nil), (-4756), (nil), (13), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (29), (30), (30), (11), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (4), (5), (24) }; t.n = 72; return t end)(), (function() local t = { (0), (60), (0), (16), (1), (2), (2), (0), (5), (0), (0), (0), (0), (0), (0), (32), (272), (925), (28), (91), (0), (0), (0), (0), (6), (0), (26), (0), (0), (0), (0), (0), (0), (0), (432), (592), (19), (17), (6), (20), (0), (0), (222), (45), (122), (252), (27), (76), (72), (0), (0), (0), (0), (43), (115), (498), (7), (28), (166), (0), (11), (9), (34), (13), (0), (0), (26), (0), (0), (89), (89), (105), (28), (253), (0) }; t.n = 75; return t end)(), 0, table.pack(nil, nil, nil, "string", nil, "string", nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 62)), false))
	;(nil --[[ constant not decoded ]])[49](v[1], t3[1])
	;(t1[1])[232] = v[1]
	;(nil --[[?NilIndex]])()
	;(t1[1])[0] = nil
	;(t1[1])[1] = nil
	;(t1[1])[2] = nil
	;(t1[1])[2] = nil
	;(t1[1])[3] = nil
	;(t1[1])[4] = nil
	LPH_CRASH()
end

-- proto 17: vm sequence 5, 0 opcodes
local function proto_17()
	(t1[1])[1] = (t2[2])[1]
	;(t1[1])[2] = (t1[1])[1]
	;(t1[1])[3] = upv0
	;(t1[1])[2] = not (t1[1])[2]
	;(t1[1])[4] = 32

	while (t1[1])[4] ~= 82 do
		if (t1[1])[4] == 32 then
			(t1[1])[3] = (t1[1])[3][(t1[1])[2]]
			;(t1[1])[4] = 82
		end
	end
	;(t1[1])[5] = (t1[1])[3]
	error("devirt: symbolic generic for (at 0:9)")
end

-- proto 8: vm sequence 6, 0 opcodes
local function proto_8()
	(t1[1])[1] = (t2[2])[1]
	;(t1[1])[2] = upv0[1]
	;(t1[1])[3] = nil
	;(t1[1])[4] = 116

	while true do
		if not ((t1[1])[4] > 70) then
			if not ((t1[1])[4] > 109) then
				if (t1[1])[4] < 70 then
					(t1[1])[3] = upv1
					;(t1[1])[4] = 70
				elseif (t1[1])[4] > 67 then
					if (t1[1])[4] < 109 then
						(t1[1])[2] = not (t1[1])[2]
						;(t1[1])[4] = 109
					end
				end
			else
				(t1[1])[4] = 67
				;(t1[1])[2] = (t1[1])[1]
			end

			continue
		end

		if not ((t1[1])[4] < 116) then
			if not ((t1[1])[4] > 109) then
				if (t1[1])[4] < 70 then
					(t1[1])[3] = upv1
					;(t1[1])[4] = 70
				elseif (t1[1])[4] > 67 then
					if (t1[1])[4] < 109 then
						(t1[1])[2] = not (t1[1])[2]
						;(t1[1])[4] = 109
					end
				end
			else
				(t1[1])[4] = 67
				;(t1[1])[2] = (t1[1])[1]
			end

			continue
		end

		break
	end
	;(t1[1])[3] = (t1[1])[3][(t1[1])[2]]
	;(t1[1])[3] = not (t1[1])[3]
	;(t1[1])[5] = (t1[1])[3]
	error("devirt: symbolic generic for (at 0:75)")
end

-- proto 15: vm sequence 7, 0 opcodes
local function proto_15()
	(t1[1])[1] = (t2[2])[1]
	;(t1[1])[4] = (t1[1])[1]
	;(t1[1])[3] = (t1[1])[3]((t1[1])[4])
	;(t1[1])[2] = (t1[1])[3]

	if (t1[1])[2] then
		(t1[1])[25] = {
			25,
			0,
			0,
			988,
			16,
			731,
			16,
			3,
			8,
			18,
			0,
			24,
			0,
			94,
			94,
			739,
			18,
			28,
			34,
			7,
			58,
			4,
			0,
			77,
			36,
			38,
			1060,
			62,
			119,
			167,
			254,
			567,
			12,
			77,
			65,
			393,
			0,
			64,
			18,
			10,
			4,
			3,
			2,
			64,
			86,
			0,
			0,
			244,
			117,
			18,
			54,
			77,
			19,
			24,
			0,
			53,
			0,
			43,
			4,
			116,
			18,
			38,
			1,
			77,
			1,
			0,
			0,
			62,
			73,
			245,
			146,
			184,
			57,
			3,
			24,
			215,
			40,
			45,
			0,
			0,
			0,
			629,
			629,
			72,
			18,
			65,
			39,
		}
		;(t1[1])[24] = {
			0,
			15,
			9,
			16,
			16,
			16,
			323,
			15,
			0,
			0,
			25,
			0,
			19,
			19,
			24,
			25,
			0,
			0,
			0,
			180,
			2,
			104,
			7,
			0,
			0,
			0,
			6,
			0,
			0,
			37,
			94,
			101,
			0,
			3,
			0,
			81,
			0,
			0,
			0,
			0,
			1,
			0,
			3,
			2,
			0,
			25,
			0,
			23,
			25,
			0,
			0,
			6,
			0,
			0,
			26,
			0,
			25,
			25,
			25,
			25,
			0,
			0,
			173,
			0,
			0,
			1,
			1,
			217,
			200,
			105,
			76,
			139,
			64,
			23,
			2,
			28,
			0,
			0,
			19,
			25,
			0,
			23,
			19,
			25,
			0,
			0,
			0,
		}
		;(t1[1])[19] = {
			127,
			131,
			90,
			151,
			5,
			141,
			17,
			101,
			92,
			127,
			131,
			93,
			90,
			101,
			101,
			101,
			92,
			127,
			127,
			160,
			67,
			91,
			55,
			127,
			127,
			127,
			189,
			127,
			8,
			77,
			75,
			161,
			8,
			40,
			127,
			159,
			168,
			127,
			127,
			127,
			185,
			7,
			185,
			32,
			127,
			131,
			34,
			101,
			101,
			92,
			127,
			62,
			127,
			127,
			18,
			127,
			131,
			101,
			101,
			101,
			92,
			127,
			69,
			127,
			59,
			58,
			176,
			71,
			50,
			64,
			98,
			109,
			140,
			160,
			67,
			91,
			127,
			127,
			90,
			131,
			34,
			101,
			101,
			101,
			92,
			127,
			127,
		}
		;(t1[1])[19][63] = 164
		;(t1[1])[24][63] = 0
		;(t1[1])[25][40] = 28
		;(t1[1])[18] = nil
		;(t1[1])[19] = nil
		;(t1[1])[20] = nil
		;(t1[1])[21] = nil
		;(t1[1])[22] = nil
		;(t1[1])[23] = nil
		;(t1[1])[24] = nil
		;(t1[1])[25] = nil
		;(t1[1])[3] = 35
		;(t1[1])[5] = 125
		local exitTo = nil

		while true do
			(t1[1])[25] = {
				25,
				0,
				0,
				988,
				16,
				731,
				16,
				3,
				8,
				18,
				0,
				24,
				0,
				94,
				94,
				739,
				18,
				28,
				34,
				7,
				58,
				4,
				0,
				77,
				36,
				38,
				1060,
				62,
				119,
				167,
				254,
				567,
				12,
				77,
				65,
				393,
				0,
				64,
				18,
				10,
				4,
				3,
				2,
				64,
				86,
				0,
				0,
				244,
				117,
				18,
				54,
				77,
				19,
				24,
				0,
				53,
				0,
				43,
				4,
				116,
				18,
				38,
				1,
				77,
				1,
				0,
				0,
				62,
				73,
				245,
				146,
				184,
				57,
				3,
				24,
				215,
				40,
				45,
				0,
				0,
				0,
				629,
				629,
				72,
				18,
				65,
				39,
			}
			;(t1[1])[23] = {
				0,
				0,
				0,
				1044,
				1000,
				16,
				9,
				396,
				17,
				0,
				0,
				0,
				0,
				339,
				32,
				7,
				25,
				0,
				0,
				248,
				230,
				152,
				0,
				0,
				0,
				0,
				51,
				0,
				3,
				251,
				4,
				59,
				5,
				0,
				0,
				293,
				162,
				0,
				0,
				0,
				0,
				0,
				0,
				0,
				0,
				0,
				23,
				32,
				593,
				25,
				0,
				72,
				0,
				0,
				3,
				0,
				0,
				55,
				80,
				447,
				25,
				0,
				2,
				0,
				0,
				0,
				79,
				2,
				108,
				163,
				52,
				236,
				101,
				56,
				136,
				46,
				0,
				0,
				0,
				0,
				23,
				32,
				73,
				48,
				25,
				0,
				0,
			}
			;(t1[1])[23][37] = 0
			;(t1[1])[25][78] = 54
			;(t1[1])[18] = nil
			;(t1[1])[19] = nil
			;(t1[1])[20] = nil
			;(t1[1])[21] = nil
			;(t1[1])[22] = nil
			;(t1[1])[23] = nil
			;(t1[1])[24] = nil
			;(t1[1])[25] = nil

			if d_1 <= 0 then
				exitTo = 1
				break
			else
				if h_1 <= E_1 then
					(t1[1])[6] = h_1

					if not ((t1[1])[6] < 160) then
						if (t1[1])[6] > 35 then
							(t1[1])[7]()
						end
					end

					continue
				end

				break
			end
		end

		if exitTo == 1 then
			if h_1 >= E_1 then
				(t1[1])[6] = h_1

				while true do
					if (t1[1])[6] < 160 then
						local exitTo2 = nil

						while true do
							(t1[1])[25] = {
								25,
								0,
								0,
								988,
								16,
								731,
								16,
								3,
								8,
								18,
								0,
								24,
								0,
								94,
								94,
								739,
								18,
								28,
								34,
								7,
								58,
								4,
								0,
								77,
								36,
								38,
								1060,
								62,
								119,
								167,
								254,
								567,
								12,
								77,
								65,
								393,
								0,
								64,
								18,
								10,
								4,
								3,
								2,
								64,
								86,
								0,
								0,
								244,
								117,
								18,
								54,
								77,
								19,
								24,
								0,
								53,
								0,
								43,
								4,
								116,
								18,
								38,
								1,
								77,
								1,
								0,
								0,
								62,
								73,
								245,
								146,
								184,
								57,
								3,
								24,
								215,
								40,
								45,
								0,
								0,
								0,
								629,
								629,
								72,
								18,
								65,
								39,
							}
							;(t1[1])[23] = {
								0,
								0,
								0,
								1044,
								1000,
								16,
								9,
								396,
								17,
								0,
								0,
								0,
								0,
								339,
								32,
								7,
								25,
								0,
								0,
								248,
								230,
								152,
								0,
								0,
								0,
								0,
								51,
								0,
								3,
								251,
								4,
								59,
								5,
								0,
								0,
								293,
								162,
								0,
								0,
								0,
								0,
								0,
								0,
								0,
								0,
								0,
								23,
								32,
								593,
								25,
								0,
								72,
								0,
								0,
								3,
								0,
								0,
								55,
								80,
								447,
								25,
								0,
								2,
								0,
								0,
								0,
								79,
								2,
								108,
								163,
								52,
								236,
								101,
								56,
								136,
								46,
								0,
								0,
								0,
								0,
								23,
								32,
								73,
								48,
								25,
								0,
								0,
							}
							;(t1[1])[23][37] = 0
							;(t1[1])[25][78] = 54
							;(t1[1])[18] = nil
							;(t1[1])[19] = nil
							;(t1[1])[20] = nil
							;(t1[1])[21] = nil
							;(t1[1])[22] = nil
							;(t1[1])[23] = nil
							;(t1[1])[24] = nil
							;(t1[1])[25] = nil

							if d_1 <= 0 then
								exitTo2 = 1
								break
							else
								if h_1 <= E_1 then
									(t1[1])[6] = h_1

									if not ((t1[1])[6] < 160) then
										if (t1[1])[6] > 35 then
											(t1[1])[7]()
										end
									end

									continue
								end

								break
							end
						end

						if exitTo2 == 1 then
							if h_1 >= E_1 then
								(t1[1])[6] = h_1
								continue
							end
						end

						break
					else
						if not ((t1[1])[6] > 35) then
							local exitTo3 = nil

							while true do
								(t1[1])[25] = {
									25,
									0,
									0,
									988,
									16,
									731,
									16,
									3,
									8,
									18,
									0,
									24,
									0,
									94,
									94,
									739,
									18,
									28,
									34,
									7,
									58,
									4,
									0,
									77,
									36,
									38,
									1060,
									62,
									119,
									167,
									254,
									567,
									12,
									77,
									65,
									393,
									0,
									64,
									18,
									10,
									4,
									3,
									2,
									64,
									86,
									0,
									0,
									244,
									117,
									18,
									54,
									77,
									19,
									24,
									0,
									53,
									0,
									43,
									4,
									116,
									18,
									38,
									1,
									77,
									1,
									0,
									0,
									62,
									73,
									245,
									146,
									184,
									57,
									3,
									24,
									215,
									40,
									45,
									0,
									0,
									0,
									629,
									629,
									72,
									18,
									65,
									39,
								}
								;(t1[1])[23] = {
									0,
									0,
									0,
									1044,
									1000,
									16,
									9,
									396,
									17,
									0,
									0,
									0,
									0,
									339,
									32,
									7,
									25,
									0,
									0,
									248,
									230,
									152,
									0,
									0,
									0,
									0,
									51,
									0,
									3,
									251,
									4,
									59,
									5,
									0,
									0,
									293,
									162,
									0,
									0,
									0,
									0,
									0,
									0,
									0,
									0,
									0,
									23,
									32,
									593,
									25,
									0,
									72,
									0,
									0,
									3,
									0,
									0,
									55,
									80,
									447,
									25,
									0,
									2,
									0,
									0,
									0,
									79,
									2,
									108,
									163,
									52,
									236,
									101,
									56,
									136,
									46,
									0,
									0,
									0,
									0,
									23,
									32,
									73,
									48,
									25,
									0,
									0,
								}
								;(t1[1])[23][37] = 0
								;(t1[1])[25][78] = 54
								;(t1[1])[18] = nil
								;(t1[1])[19] = nil
								;(t1[1])[20] = nil
								;(t1[1])[21] = nil
								;(t1[1])[22] = nil
								;(t1[1])[23] = nil
								;(t1[1])[24] = nil
								;(t1[1])[25] = nil

								if d_1 <= 0 then
									exitTo3 = 1
									break
								else
									if h_1 <= E_1 then
										(t1[1])[6] = h_1

										if not ((t1[1])[6] < 160) then
											if (t1[1])[6] > 35 then
												(t1[1])[7]()
											end
										end

										continue
									end

									break
								end
							end

							if exitTo3 == 1 then
								if h_1 >= E_1 then
									(t1[1])[6] = h_1
									continue
								end
							end
						else
							(t1[1])[7]()
							local exitTo4 = nil

							while true do
								(t1[1])[25] = {
									25,
									0,
									0,
									988,
									16,
									731,
									16,
									3,
									8,
									18,
									0,
									24,
									0,
									94,
									94,
									739,
									18,
									28,
									34,
									7,
									58,
									4,
									0,
									77,
									36,
									38,
									1060,
									62,
									119,
									167,
									254,
									567,
									12,
									77,
									65,
									393,
									0,
									64,
									18,
									10,
									4,
									3,
									2,
									64,
									86,
									0,
									0,
									244,
									117,
									18,
									54,
									77,
									19,
									24,
									0,
									53,
									0,
									43,
									4,
									116,
									18,
									38,
									1,
									77,
									1,
									0,
									0,
									62,
									73,
									245,
									146,
									184,
									57,
									3,
									24,
									215,
									40,
									45,
									0,
									0,
									0,
									629,
									629,
									72,
									18,
									65,
									39,
								}
								;(t1[1])[23] = {
									0,
									0,
									0,
									1044,
									1000,
									16,
									9,
									396,
									17,
									0,
									0,
									0,
									0,
									339,
									32,
									7,
									25,
									0,
									0,
									248,
									230,
									152,
									0,
									0,
									0,
									0,
									51,
									0,
									3,
									251,
									4,
									59,
									5,
									0,
									0,
									293,
									162,
									0,
									0,
									0,
									0,
									0,
									0,
									0,
									0,
									0,
									23,
									32,
									593,
									25,
									0,
									72,
									0,
									0,
									3,
									0,
									0,
									55,
									80,
									447,
									25,
									0,
									2,
									0,
									0,
									0,
									79,
									2,
									108,
									163,
									52,
									236,
									101,
									56,
									136,
									46,
									0,
									0,
									0,
									0,
									23,
									32,
									73,
									48,
									25,
									0,
									0,
								}
								;(t1[1])[23][37] = 0
								;(t1[1])[25][78] = 54
								;(t1[1])[18] = nil
								;(t1[1])[19] = nil
								;(t1[1])[20] = nil
								;(t1[1])[21] = nil
								;(t1[1])[22] = nil
								;(t1[1])[23] = nil
								;(t1[1])[24] = nil
								;(t1[1])[25] = nil

								if d_1 <= 0 then
									exitTo4 = 1
									break
								else
									if h_1 <= E_1 then
										(t1[1])[6] = h_1

										if not ((t1[1])[6] < 160) then
											if (t1[1])[6] > 35 then
												(t1[1])[7]()
											end
										end

										continue
									end

									break
								end
							end

							if exitTo4 == 1 then
								if h_1 >= E_1 then
									(t1[1])[6] = h_1
									continue
								end
							end
						end

						break
					end
				end
			end
		end
	end

	error("devirt: symbolic generic for (at 0:65)")
end

-- proto 19: vm sequence 8, 0 opcodes
local function proto_19()
	(t1[1])[1] = (t2[2])[1]
	;(t1[1])[4] = (t1[1])[1]
	;(t1[1])[3] = (t1[1])[3]((t1[1])[4])
	;(t1[1])[2] = (t1[1])[3]

	if (t1[1])[2] then
		(t1[1])[20] = {
			0,
			2,
			3,
			0,
			0,
			63,
			0,
			0,
			0,
			32,
			710,
			22,
			73,
			0,
			0,
			0,
			0,
			0,
			0,
			0,
			0,
			0,
			13,
			426,
			13,
			6,
			85,
			14,
			0,
			20,
			0,
			32,
			94,
			22,
			151,
			0,
			0,
			20,
			0,
			0,
			0,
			32,
			89,
			23,
			32,
			16,
			22,
			0,
			0,
			48,
			2,
			161,
			210,
			65,
			92,
			177,
			138,
			210,
			251,
			0,
			3,
			0,
			0,
			3,
			0,
			230,
			0,
			0,
			0,
			0,
			0,
			0,
			0,
		}
		;(t1[1])[22] = {
			68,
			1,
			67,
			72,
			69,
			445,
			71,
			0,
			21,
			6,
			850,
			15,
			245,
			60,
			48,
			4,
			3,
			2,
			70,
			4,
			0,
			0,
			814,
			13,
			186,
			13,
			94,
			5,
			15,
			0,
			0,
			13,
			11,
			15,
			196,
			63,
			65,
			0,
			21,
			0,
			0,
			140,
			140,
			140,
			140,
			289,
			15,
			14,
			0,
			0,
			39,
			8,
			212,
			107,
			172,
			8,
			3,
			172,
			189,
			62,
			1,
			36,
			15,
			31,
			72,
			4,
			0,
			70,
			14,
			6,
			1,
			29,
			7,
		}
		;(t1[1])[20][66] = 0
		;(t1[1])[22][72] = 63
		;(t1[1])[3] = 23

		while true do
			(t1[1])[22] = {
				68,
				1,
				67,
				72,
				69,
				445,
				71,
				0,
				21,
				6,
				850,
				15,
				245,
				60,
				48,
				4,
				3,
				2,
				70,
				4,
				0,
				0,
				814,
				13,
				186,
				13,
				94,
				5,
				15,
				0,
				0,
				13,
				11,
				15,
				196,
				63,
				65,
				0,
				21,
				0,
				0,
				140,
				140,
				140,
				140,
				289,
				15,
				14,
				0,
				0,
				39,
				8,
				212,
				107,
				172,
				8,
				3,
				172,
				189,
				62,
				1,
				36,
				15,
				31,
				72,
				4,
				0,
				70,
				14,
				6,
				1,
				29,
				7,
			}
			;(t1[1])[21] = {
				0,
				83,
				0,
				0,
				0,
				169,
				0,
				22,
				0,
				21,
				22,
				252,
				184,
				0,
				0,
				1,
				0,
				3,
				2,
				0,
				12,
				6,
				156,
				13,
				13,
				120,
				12,
				0,
				0,
				0,
				22,
				20,
				22,
				139,
				61,
				0,
				0,
				0,
				0,
				22,
				16,
				20,
				21,
				16,
				22,
				22,
				0,
				0,
				1,
				187,
				87,
				62,
				76,
				45,
				18,
				216,
				74,
				2,
				100,
				0,
				54,
				0,
				0,
				0,
				0,
				2,
				4,
				0,
				0,
				0,
				0,
				0,
				0,
			}
			;(t1[1])[21][2] = 0
			;(t1[1])[22][73] = 60

			if (t1[1])[3] == 23 then
				(t1[1])[2] = upv1
				;(t1[1])[3] = 10
			else
				break
			end
		end
		;(t1[1])[4] = (t1[1])[2]
		;(t1[1])[4]()
	end

	error("devirt: symbolic generic for (at 0:71)")
end

-- proto 7: vm sequence 9, 0 opcodes
local function proto_7()
	(t1[1])[1] = (t2[2])[1]
	;(t1[1])[2] = (t2[2])[2]
	;(t1[1])[3] = upv0[1]
	;(t1[1])[4] = upv0[1]
	;(t1[1])[5] = 34
	;(t1[1])[6] = 251
	;(t1[1])[7] = 92
	local exitTo = nil

	while true do
		if d_1 <= 0 then
			exitTo = 1
			break
		else
			if h_1 <= E_1 then
				(t1[1])[8] = h_1

				if (t1[1])[8] == 126 then
					exitTo = 2
					break
				else
					if (t1[1])[8] == 34 then
						(t1[1])[3] = upv1
						;(t1[1])[4] = (t1[1])[1]
					end

					continue
				end
			end

			break
		end
	end

	if exitTo == 1 then
		if h_1 >= E_1 then
			(t1[1])[8] = h_1

			while true do
				if (t1[1])[8] == 126 then
					(t1[1])[9] = (t1[1])[3]
					;(t1[1])[10] = (t1[1])[4]
					;(t1[1])[9] = (t1[1])[9]((t1[1])[10])
					;(t1[1])[3] = (t1[1])[9]
					break
				else
					if (t1[1])[8] == 34 then
						(t1[1])[3] = upv1
						;(t1[1])[4] = (t1[1])[1]
						local exitTo2 = nil

						while true do
							if d_1 <= 0 then
								exitTo2 = 1
								break
							else
								if h_1 <= E_1 then
									(t1[1])[8] = h_1

									if (t1[1])[8] == 126 then
										exitTo2 = 2
										break
									else
										if (t1[1])[8] == 34 then
											(t1[1])[3] = upv1
											;(t1[1])[4] = (t1[1])[1]
										end

										continue
									end
								end

								break
							end
						end

						if exitTo2 == 1 then
							if h_1 >= E_1 then
								(t1[1])[8] = h_1
								continue
							end
						else
							if exitTo2 == 2 then
								(t1[1])[9] = (t1[1])[3]
								;(t1[1])[10] = (t1[1])[4]
								;(t1[1])[9] = (t1[1])[9]((t1[1])[10])
								;(t1[1])[3] = (t1[1])[9]
							end

							break
						end
					else
						local exitTo3 = nil

						while true do
							if d_1 <= 0 then
								exitTo3 = 1
								break
							else
								if h_1 <= E_1 then
									(t1[1])[8] = h_1

									if (t1[1])[8] == 126 then
										exitTo3 = 2
										break
									else
										if (t1[1])[8] == 34 then
											(t1[1])[3] = upv1
											;(t1[1])[4] = (t1[1])[1]
										end

										continue
									end
								end

								break
							end
						end

						if exitTo3 == 1 then
							if h_1 >= E_1 then
								(t1[1])[8] = h_1
								continue
							end
						else
							if exitTo3 == 2 then
								(t1[1])[9] = (t1[1])[3]
								;(t1[1])[10] = (t1[1])[4]
								;(t1[1])[9] = (t1[1])[9]((t1[1])[10])
								;(t1[1])[3] = (t1[1])[9]
							end

							break
						end
					end

					break
				end
			end
		end
	elseif exitTo == 2 then
		(t1[1])[9] = (t1[1])[3]
		;(t1[1])[10] = (t1[1])[4]
		;(t1[1])[9] = (t1[1])[9]((t1[1])[10])
		;(t1[1])[3] = (t1[1])[9]
	end
	;(t1[1])[5] = upv0[46]
	;(t1[1])[6] = upv0[1]
	;(t1[1])[7] = 3
	;(t1[1])[8] = 461
	;(t1[1])[9] = 100

	while true do
		if d_1 <= 0 then
			if not (h_1 >= E_1) then
				break
			end
			;(t1[1])[10] = h_1
		else
			if not (h_1 <= E_1) then
				break
			end
			;(t1[1])[10] = h_1
		end

		if (t1[1])[10] < 103 then
			if (t1[1])[3] then
				(t1[1])[11] = upv0[1]
				;(t1[1])[12] = 67
				;(t1[1])[13] = 195
				;(t1[1])[14] = 49
				local exitTo4 = nil

				while true do
					if d_2 <= 0 then
						exitTo4 = 1
						break
					else
						if h_2 <= E_2 then
							(t1[1])[15] = h_2

							if (t1[1])[15] == 67 then
								(t1[1])[4] = (t1[1])[1]
								continue
							elseif (t1[1])[15] == 116 then
								exitTo4 = 2
								break
							else
								continue
							end
						end

						break
					end
				end

				if exitTo4 == 1 then
					if h_2 >= E_2 then
						(t1[1])[15] = h_2

						while true do
							if (t1[1])[15] == 67 then
								(t1[1])[4] = (t1[1])[1]
								local exitTo5 = nil

								while true do
									if d_2 <= 0 then
										exitTo5 = 1
										break
									else
										if h_2 <= E_2 then
											(t1[1])[15] = h_2

											if (t1[1])[15] == 67 then
												(t1[1])[4] = (t1[1])[1]
												continue
											elseif (t1[1])[15] == 116 then
												exitTo5 = 2
												break
											else
												continue
											end
										end

										break
									end
								end

								if exitTo5 == 1 then
									if h_2 >= E_2 then
										(t1[1])[15] = h_2
										continue
									end
								else
									if exitTo5 == 2 then
										(t1[1])[11] = upv0[1]
									end

									break
								end

								break
							else
								if (t1[1])[15] == 116 then
									(t1[1])[11] = upv0[1]
									break
								else
									local exitTo6 = nil

									while true do
										if d_2 <= 0 then
											exitTo6 = 1
											break
										else
											if h_2 <= E_2 then
												(t1[1])[15] = h_2

												if (t1[1])[15] == 67 then
													(t1[1])[4] = (t1[1])[1]
													continue
												elseif (t1[1])[15] == 116 then
													exitTo6 = 2
													break
												else
													continue
												end
											end

											break
										end
									end

									if exitTo6 == 1 then
										if h_2 >= E_2 then
											(t1[1])[15] = h_2
											continue
										end
									else
										if exitTo6 == 2 then
											(t1[1])[11] = upv0[1]
										end

										break
									end
								end

								break
							end
						end
					end
				elseif exitTo4 == 2 then
					(t1[1])[11] = upv0[1]
				end
				;(t1[1])[3] = (t1[1])[4] == (t1[1])[11]
			end

			continue
		end

		if (t1[1])[10] < 403 then
			if (t1[1])[10] > 203 then
				continue
			end
		end

		if not ((t1[1])[10] > 303) then
			if (t1[1])[10] > 103 then
				if (t1[1])[10] < 303 then
					(t1[1])[6] = upv0[47]
					continue
				end
			end

			if (t1[1])[10] < 203 then
				if not ((t1[1])[10] > 3) then
					continue
				end

				if not (t1[1])[3] then
					(t1[1])[3] = upv2
					continue
				end
				;(t1[1])[11] = 88

				while true do
					if not ((t1[1])[11] <= 74) then
						if not ((t1[1])[11] >= 88) then
							(t1[1])[11] = 74
							;(t1[1])[4] = (t1[1])[2]
						else
							(t1[1])[3] = upv1
						end

						continue
					end

					if (t1[1])[11] > 33 then
						(t1[1])[11] = 33
						;(t1[1])[12] = (t1[1])[3]
						;(t1[1])[13] = (t1[1])[4]
						;(t1[1])[12] = (t1[1])[12]((t1[1])[13])
						continue
					end

					break
				end

				if (t1[1])[3] then
					(t1[1])[4] = (t1[1])[2]
					;(t1[1])[12] = upv0[1]
					;(t1[1])[3] = (t1[1])[4] == (t1[1])[12]
				end

				if not (t1[1])[3] then
					(t1[1])[3] = upv0[47]
					;(t1[1])[12] = (t1[1])[3]
					error("devirt: symbolic generic for (at 0:226)")
				end
				;(t1[1])[3] = upv0[46]
				;(t1[1])[12] = (t1[1])[3]
				error("devirt: symbolic generic for (at 0:65)")
			end

			continue
		end
		;(t1[1])[3][(t1[1])[4]] = (t1[1])[5]
		;(t1[1])[3] = upv2
		break
	end
	;(t1[1])[4] = (t1[1])[2]
	;(t1[1])[3] = (t1[1])[3][(t1[1])[4]]
	;(t1[1])[6] = (t1[1])[3]

	while true do
		if not ((t1[1])[7] > 46) then
			if not ((t1[1])[7] > 16) then
				(t1[1])[7] = 47
				;(t1[1])[5] = upv0[1]
			else
				(t1[1])[7] = 53
				;(t1[1])[3] = upv2
			end

			continue
		end

		if (t1[1])[7] <= 47 then
			(t1[1])[7] = 66
			;(t1[1])[3][(t1[1])[4]] = (t1[1])[5]
			continue
		end

		if (t1[1])[7] == 53 then
			(t1[1])[4] = (t1[1])[1]
			;(t1[1])[7] = 16
			continue
		end

		break
	end
	;(t1[1])[3] = (t1[1])[6]
	;(t1[1])[8] = (t1[1])[3]
	error("devirt: symbolic generic for (at 0:62)")
end

-- proto 6: vm sequence 10, 0 opcodes
local function proto_6()
	(t1[1])[1] = (t2[2])[1]
	;(t1[1])[2] = (t2[2])[2]
	;(t1[1])[3] = upv0[1]
	;(t1[1])[4] = upv0[1]
	;(t1[1])[5] = upv0[1]
	;(t1[1])[6] = 21

	while true do
		if (t1[1])[6] == 21 then
			(t1[1])[3] = (t1[1])[1]
			;(t1[1])[6] = 112
			continue
		end

		if (t1[1])[6] ~= 15 then
			if (t1[1])[6] == 112 then
				(t1[1])[4] = (t1[1])[2]
			end

			continue
		end

		break
	end
	;(t1[1])[5] = upv1
	;(t1[1])[7] = (t1[1])[5]
	;(t1[1])[8] = (t1[1])[3]
	;(t1[1])[7] = (t1[1])[7]((t1[1])[8], (t1[1])[9])
	;(t1[1])[5] = (t1[1])[7]
	;(t1[1])[5] = not (t1[1])[5]
	;(t1[1])[7] = (t1[1])[5]
	error("devirt: symbolic generic for (at 0:44)")
end

-- proto 5: vm sequence 11, 0 opcodes
local function proto_5()
	(t1[1])[1] = (t2[2])[1]
	;(t1[1])[2] = (t2[2])[2]
	;(t1[1])[3] = upv0[1]
	;(t1[1])[4] = upv0[1]
	;(t1[1])[5] = upv0[1]
	;(t1[1])[6] = 68
	;(t1[1])[7] = 270
	;(t1[1])[8] = 42
	local exitTo = nil

	while true do
		if d_1 <= 0 then
			exitTo = 1
			break
		else
			if h_1 <= E_1 then
				(t1[1])[9] = h_1

				if (t1[1])[9] == 152 then
					(t1[1])[5] = upv1
					continue
				elseif (t1[1])[9] == 68 then
					(t1[1])[3] = (t1[1])[1]
					continue
				elseif (t1[1])[9] == 194 then
					(t1[1])[11] = (t1[1])[3]
					;(t1[1])[12] = (t1[1])[4]
					;(t1[1])[10] = (t1[1])[10]((t1[1])[11], (t1[1])[12])
					;(t1[1])[5] = (t1[1])[10]
					continue
				elseif (t1[1])[9] == 110 then
					continue
				elseif (t1[1])[9] == 236 then
					exitTo = 2
					break
				else
					continue
				end
			end

			break
		end
	end

	local exitTo9, exitTo10

	if exitTo == 1 then
		if h_1 >= E_1 then
			(t1[1])[9] = h_1
			local exitTo3 = nil
			local exitTo2

			while true do
				if (t1[1])[9] == 152 then
					(t1[1])[5] = upv1
					exitTo2 = nil

					while true do
						if d_1 <= 0 then
							exitTo2 = 1
							break
						else
							if h_1 <= E_1 then
								(t1[1])[9] = h_1

								if (t1[1])[9] == 152 then
									(t1[1])[5] = upv1
									continue
								elseif (t1[1])[9] == 68 then
									(t1[1])[3] = (t1[1])[1]
									continue
								elseif (t1[1])[9] == 194 then
									(t1[1])[11] = (t1[1])[3]
									;(t1[1])[12] = (t1[1])[4]
									;(t1[1])[10] = (t1[1])[10]((t1[1])[11], (t1[1])[12])
									;(t1[1])[5] = (t1[1])[10]
									continue
								elseif (t1[1])[9] == 110 then
									continue
								elseif (t1[1])[9] == 236 then
									exitTo2 = 2
									break
								else
									continue
								end
							end

							break
						end
					end

					if exitTo2 == 1 then
						if h_1 >= E_1 then
							(t1[1])[9] = h_1
							continue
						end
					else
						exitTo3 = 6
						break
					end

					break
				else
					if (t1[1])[9] == 68 then
						(t1[1])[3] = (t1[1])[1]
						local exitTo4 = nil

						while true do
							if d_1 <= 0 then
								exitTo4 = 1
								break
							else
								if h_1 <= E_1 then
									(t1[1])[9] = h_1

									if (t1[1])[9] == 152 then
										(t1[1])[5] = upv1
										continue
									elseif (t1[1])[9] == 68 then
										(t1[1])[3] = (t1[1])[1]
										continue
									elseif (t1[1])[9] == 194 then
										(t1[1])[11] = (t1[1])[3]
										;(t1[1])[12] = (t1[1])[4]
										;(t1[1])[10] = (t1[1])[10]((t1[1])[11], (t1[1])[12])
										;(t1[1])[5] = (t1[1])[10]
										continue
									elseif (t1[1])[9] == 110 then
										continue
									elseif (t1[1])[9] == 236 then
										exitTo4 = 2
										break
									else
										continue
									end
								end

								break
							end
						end

						if exitTo4 == 1 then
							if h_1 >= E_1 then
								(t1[1])[9] = h_1
								continue
							end
						else
							if exitTo4 == 2 then
								exitTo3 = 5
							end

							break
						end
					elseif (t1[1])[9] == 194 then
						(t1[1])[11] = (t1[1])[3]
						;(t1[1])[12] = (t1[1])[4]
						;(t1[1])[10] = (t1[1])[10]((t1[1])[11], (t1[1])[12])
						;(t1[1])[5] = (t1[1])[10]
						local exitTo5 = nil

						while true do
							if d_1 <= 0 then
								exitTo5 = 1
								break
							else
								if h_1 <= E_1 then
									(t1[1])[9] = h_1

									if (t1[1])[9] == 152 then
										(t1[1])[5] = upv1
										continue
									elseif (t1[1])[9] == 68 then
										(t1[1])[3] = (t1[1])[1]
										continue
									elseif (t1[1])[9] == 194 then
										(t1[1])[11] = (t1[1])[3]
										;(t1[1])[12] = (t1[1])[4]
										;(t1[1])[10] = (t1[1])[10]((t1[1])[11], (t1[1])[12])
										;(t1[1])[5] = (t1[1])[10]
										continue
									elseif (t1[1])[9] == 110 then
										continue
									elseif (t1[1])[9] == 236 then
										exitTo5 = 2
										break
									else
										continue
									end
								end

								break
							end
						end

						if exitTo5 == 1 then
							if h_1 >= E_1 then
								(t1[1])[9] = h_1
								continue
							end
						else
							if exitTo5 == 2 then
								exitTo3 = 4
							end

							break
						end
					elseif (t1[1])[9] == 110 then
						local exitTo6 = nil

						while true do
							if d_1 <= 0 then
								exitTo6 = 1
								break
							else
								if h_1 <= E_1 then
									(t1[1])[9] = h_1

									if (t1[1])[9] == 152 then
										(t1[1])[5] = upv1
										continue
									elseif (t1[1])[9] == 68 then
										(t1[1])[3] = (t1[1])[1]
										continue
									elseif (t1[1])[9] == 194 then
										(t1[1])[11] = (t1[1])[3]
										;(t1[1])[12] = (t1[1])[4]
										;(t1[1])[10] = (t1[1])[10]((t1[1])[11], (t1[1])[12])
										;(t1[1])[5] = (t1[1])[10]
										continue
									elseif (t1[1])[9] == 110 then
										continue
									elseif (t1[1])[9] == 236 then
										exitTo6 = 2
										break
									else
										continue
									end
								end

								break
							end
						end

						if exitTo6 == 1 then
							if h_1 >= E_1 then
								(t1[1])[9] = h_1
								continue
							end
						else
							if exitTo6 == 2 then
								exitTo3 = 3
							end

							break
						end
					elseif (t1[1])[9] == 236 then
						exitTo3 = 1
						break
					else
						local exitTo7 = nil

						while true do
							if d_1 <= 0 then
								exitTo7 = 1
								break
							else
								if h_1 <= E_1 then
									(t1[1])[9] = h_1

									if (t1[1])[9] == 152 then
										(t1[1])[5] = upv1
										continue
									elseif (t1[1])[9] == 68 then
										(t1[1])[3] = (t1[1])[1]
										continue
									elseif (t1[1])[9] == 194 then
										(t1[1])[11] = (t1[1])[3]
										;(t1[1])[12] = (t1[1])[4]
										;(t1[1])[10] = (t1[1])[10]((t1[1])[11], (t1[1])[12])
										;(t1[1])[5] = (t1[1])[10]
										continue
									elseif (t1[1])[9] == 110 then
										continue
									elseif (t1[1])[9] == 236 then
										exitTo7 = 2
										break
									else
										continue
									end
								end

								break
							end
						end

						if exitTo7 == 1 then
							if h_1 >= E_1 then
								(t1[1])[9] = h_1
								continue
							end
						else
							if exitTo7 == 2 then
								exitTo3 = 2
							end

							break
						end
					end

					break
				end
			end

			if exitTo3 == 1 then
				if (t1[1])[5] then
					(t1[1])[10] = 21
					;(t1[1])[11] = 204
					;(t1[1])[12] = 82
					local exitTo8 = nil

					while true do
						if d_2 <= 0 then
							exitTo8 = 1
							break
						else
							if h_2 <= E_2 then
								(t1[1])[13] = h_2

								if (t1[1])[13] == 21 then
									continue
								elseif (t1[1])[13] == 103 then
									exitTo8 = 2
									break
								else
									continue
								end
							end

							break
						end
					end

					if exitTo8 == 1 then
						if h_2 >= E_2 then
							(t1[1])[13] = h_2

							while true do
								if (t1[1])[13] == 21 then
									exitTo9 = nil

									while true do
										if d_2 <= 0 then
											exitTo9 = 1
											break
										else
											if h_2 <= E_2 then
												(t1[1])[13] = h_2

												if (t1[1])[13] == 21 then
													continue
												elseif (t1[1])[13] == 103 then
													exitTo9 = 2
													break
												else
													continue
												end
											end

											break
										end
									end

									if exitTo9 == 1 then
										if h_2 >= E_2 then
											(t1[1])[13] = h_2
											continue
										end
									else
										if exitTo9 == 2 then
											(t1[1])[14] = (t1[1])[5]
											;(t1[1])[14]()
										end

										break
									end

									break
								else
									if (t1[1])[13] == 103 then
										(t1[1])[14] = (t1[1])[5]
										;(t1[1])[14]()
										break
									else
										exitTo10 = nil

										while true do
											if d_2 <= 0 then
												exitTo10 = 1
												break
											else
												if h_2 <= E_2 then
													(t1[1])[13] = h_2

													if (t1[1])[13] == 21 then
														continue
													elseif (t1[1])[13] == 103 then
														exitTo10 = 2
														break
													else
														continue
													end
												end

												break
											end
										end

										if exitTo10 == 1 then
											if h_2 >= E_2 then
												(t1[1])[13] = h_2
												continue
											end
										else
											if exitTo10 == 2 then
												(t1[1])[14] = (t1[1])[5]
												;(t1[1])[14]()
											end

											break
										end
									end

									break
								end
							end
						end
					elseif exitTo8 == 2 then
						(t1[1])[14] = (t1[1])[5]
						;(t1[1])[14]()
					end
				end
			elseif exitTo3 == 2 then
				if (t1[1])[5] then
					(t1[1])[10] = 21
					;(t1[1])[11] = 204
					;(t1[1])[12] = 82
					local exitTo11 = nil

					while true do
						if d_2 <= 0 then
							exitTo11 = 1
							break
						else
							if h_2 <= E_2 then
								(t1[1])[13] = h_2

								if (t1[1])[13] == 21 then
									continue
								elseif (t1[1])[13] == 103 then
									exitTo11 = 2
									break
								else
									continue
								end
							end

							break
						end
					end

					if exitTo11 == 1 then
						if h_2 >= E_2 then
							(t1[1])[13] = h_2

							while true do
								if (t1[1])[13] == 21 then
									exitTo9 = nil

									while true do
										if d_2 <= 0 then
											exitTo9 = 1
											break
										else
											if h_2 <= E_2 then
												(t1[1])[13] = h_2

												if (t1[1])[13] == 21 then
													continue
												elseif (t1[1])[13] == 103 then
													exitTo9 = 2
													break
												else
													continue
												end
											end

											break
										end
									end

									if exitTo9 == 1 then
										if h_2 >= E_2 then
											(t1[1])[13] = h_2
											continue
										end
									else
										if exitTo9 == 2 then
											(t1[1])[14] = (t1[1])[5]
											;(t1[1])[14]()
										end

										break
									end

									break
								else
									if (t1[1])[13] == 103 then
										(t1[1])[14] = (t1[1])[5]
										;(t1[1])[14]()
										break
									else
										exitTo10 = nil

										while true do
											if d_2 <= 0 then
												exitTo10 = 1
												break
											else
												if h_2 <= E_2 then
													(t1[1])[13] = h_2

													if (t1[1])[13] == 21 then
														continue
													elseif (t1[1])[13] == 103 then
														exitTo10 = 2
														break
													else
														continue
													end
												end

												break
											end
										end

										if exitTo10 == 1 then
											if h_2 >= E_2 then
												(t1[1])[13] = h_2
												continue
											end
										else
											if exitTo10 == 2 then
												(t1[1])[14] = (t1[1])[5]
												;(t1[1])[14]()
											end

											break
										end
									end

									break
								end
							end
						end
					elseif exitTo11 == 2 then
						(t1[1])[14] = (t1[1])[5]
						;(t1[1])[14]()
					end
				end
			elseif exitTo3 == 3 then
				if (t1[1])[5] then
					(t1[1])[10] = 21
					;(t1[1])[11] = 204
					;(t1[1])[12] = 82
					local exitTo12 = nil

					while true do
						if d_2 <= 0 then
							exitTo12 = 1
							break
						else
							if h_2 <= E_2 then
								(t1[1])[13] = h_2

								if (t1[1])[13] == 21 then
									continue
								elseif (t1[1])[13] == 103 then
									exitTo12 = 2
									break
								else
									continue
								end
							end

							break
						end
					end

					if exitTo12 == 1 then
						if h_2 >= E_2 then
							(t1[1])[13] = h_2

							while true do
								if (t1[1])[13] == 21 then
									exitTo9 = nil

									while true do
										if d_2 <= 0 then
											exitTo9 = 1
											break
										else
											if h_2 <= E_2 then
												(t1[1])[13] = h_2

												if (t1[1])[13] == 21 then
													continue
												elseif (t1[1])[13] == 103 then
													exitTo9 = 2
													break
												else
													continue
												end
											end

											break
										end
									end

									if exitTo9 == 1 then
										if h_2 >= E_2 then
											(t1[1])[13] = h_2
											continue
										end
									else
										if exitTo9 == 2 then
											(t1[1])[14] = (t1[1])[5]
											;(t1[1])[14]()
										end

										break
									end

									break
								else
									if (t1[1])[13] == 103 then
										(t1[1])[14] = (t1[1])[5]
										;(t1[1])[14]()
										break
									else
										exitTo10 = nil

										while true do
											if d_2 <= 0 then
												exitTo10 = 1
												break
											else
												if h_2 <= E_2 then
													(t1[1])[13] = h_2

													if (t1[1])[13] == 21 then
														continue
													elseif (t1[1])[13] == 103 then
														exitTo10 = 2
														break
													else
														continue
													end
												end

												break
											end
										end

										if exitTo10 == 1 then
											if h_2 >= E_2 then
												(t1[1])[13] = h_2
												continue
											end
										else
											if exitTo10 == 2 then
												(t1[1])[14] = (t1[1])[5]
												;(t1[1])[14]()
											end

											break
										end
									end

									break
								end
							end
						end
					elseif exitTo12 == 2 then
						(t1[1])[14] = (t1[1])[5]
						;(t1[1])[14]()
					end
				end
			elseif exitTo3 == 4 then
				if (t1[1])[5] then
					(t1[1])[10] = 21
					;(t1[1])[11] = 204
					;(t1[1])[12] = 82
					local exitTo13 = nil

					while true do
						if d_2 <= 0 then
							exitTo13 = 1
							break
						else
							if h_2 <= E_2 then
								(t1[1])[13] = h_2

								if (t1[1])[13] == 21 then
									continue
								elseif (t1[1])[13] == 103 then
									exitTo13 = 2
									break
								else
									continue
								end
							end

							break
						end
					end

					if exitTo13 == 1 then
						if h_2 >= E_2 then
							(t1[1])[13] = h_2

							while true do
								if (t1[1])[13] == 21 then
									exitTo9 = nil

									while true do
										if d_2 <= 0 then
											exitTo9 = 1
											break
										else
											if h_2 <= E_2 then
												(t1[1])[13] = h_2

												if (t1[1])[13] == 21 then
													continue
												elseif (t1[1])[13] == 103 then
													exitTo9 = 2
													break
												else
													continue
												end
											end

											break
										end
									end

									if exitTo9 == 1 then
										if h_2 >= E_2 then
											(t1[1])[13] = h_2
											continue
										end
									else
										if exitTo9 == 2 then
											(t1[1])[14] = (t1[1])[5]
											;(t1[1])[14]()
										end

										break
									end

									break
								else
									if (t1[1])[13] == 103 then
										(t1[1])[14] = (t1[1])[5]
										;(t1[1])[14]()
										break
									else
										exitTo10 = nil

										while true do
											if d_2 <= 0 then
												exitTo10 = 1
												break
											else
												if h_2 <= E_2 then
													(t1[1])[13] = h_2

													if (t1[1])[13] == 21 then
														continue
													elseif (t1[1])[13] == 103 then
														exitTo10 = 2
														break
													else
														continue
													end
												end

												break
											end
										end

										if exitTo10 == 1 then
											if h_2 >= E_2 then
												(t1[1])[13] = h_2
												continue
											end
										else
											if exitTo10 == 2 then
												(t1[1])[14] = (t1[1])[5]
												;(t1[1])[14]()
											end

											break
										end
									end

									break
								end
							end
						end
					elseif exitTo13 == 2 then
						(t1[1])[14] = (t1[1])[5]
						;(t1[1])[14]()
					end
				end
			elseif exitTo3 == 5 then
				if (t1[1])[5] then
					(t1[1])[10] = 21
					;(t1[1])[11] = 204
					;(t1[1])[12] = 82
					local exitTo14 = nil

					while true do
						if d_2 <= 0 then
							exitTo14 = 1
							break
						else
							if h_2 <= E_2 then
								(t1[1])[13] = h_2

								if (t1[1])[13] == 21 then
									continue
								elseif (t1[1])[13] == 103 then
									exitTo14 = 2
									break
								else
									continue
								end
							end

							break
						end
					end

					if exitTo14 == 1 then
						if h_2 >= E_2 then
							(t1[1])[13] = h_2

							while true do
								if (t1[1])[13] == 21 then
									exitTo9 = nil

									while true do
										if d_2 <= 0 then
											exitTo9 = 1
											break
										else
											if h_2 <= E_2 then
												(t1[1])[13] = h_2

												if (t1[1])[13] == 21 then
													continue
												elseif (t1[1])[13] == 103 then
													exitTo9 = 2
													break
												else
													continue
												end
											end

											break
										end
									end

									if exitTo9 == 1 then
										if h_2 >= E_2 then
											(t1[1])[13] = h_2
											continue
										end
									else
										if exitTo9 == 2 then
											(t1[1])[14] = (t1[1])[5]
											;(t1[1])[14]()
										end

										break
									end

									break
								else
									if (t1[1])[13] == 103 then
										(t1[1])[14] = (t1[1])[5]
										;(t1[1])[14]()
										break
									else
										exitTo10 = nil

										while true do
											if d_2 <= 0 then
												exitTo10 = 1
												break
											else
												if h_2 <= E_2 then
													(t1[1])[13] = h_2

													if (t1[1])[13] == 21 then
														continue
													elseif (t1[1])[13] == 103 then
														exitTo10 = 2
														break
													else
														continue
													end
												end

												break
											end
										end

										if exitTo10 == 1 then
											if h_2 >= E_2 then
												(t1[1])[13] = h_2
												continue
											end
										else
											if exitTo10 == 2 then
												(t1[1])[14] = (t1[1])[5]
												;(t1[1])[14]()
											end

											break
										end
									end

									break
								end
							end
						end
					elseif exitTo14 == 2 then
						(t1[1])[14] = (t1[1])[5]
						;(t1[1])[14]()
					end
				end
			elseif exitTo3 == 6 then
				if exitTo2 == 2 then
					if (t1[1])[5] then
						(t1[1])[10] = 21
						;(t1[1])[11] = 204
						;(t1[1])[12] = 82
						local exitTo15 = nil

						while true do
							if d_2 <= 0 then
								exitTo15 = 1
								break
							else
								if h_2 <= E_2 then
									(t1[1])[13] = h_2

									if (t1[1])[13] == 21 then
										continue
									elseif (t1[1])[13] == 103 then
										exitTo15 = 2
										break
									else
										continue
									end
								end

								break
							end
						end

						if exitTo15 == 1 then
							if h_2 >= E_2 then
								(t1[1])[13] = h_2

								while true do
									if (t1[1])[13] == 21 then
										exitTo9 = nil

										while true do
											if d_2 <= 0 then
												exitTo9 = 1
												break
											else
												if h_2 <= E_2 then
													(t1[1])[13] = h_2

													if (t1[1])[13] == 21 then
														continue
													elseif (t1[1])[13] == 103 then
														exitTo9 = 2
														break
													else
														continue
													end
												end

												break
											end
										end

										if exitTo9 == 1 then
											if h_2 >= E_2 then
												(t1[1])[13] = h_2
												continue
											end
										else
											if exitTo9 == 2 then
												(t1[1])[14] = (t1[1])[5]
												;(t1[1])[14]()
											end

											break
										end

										break
									else
										if (t1[1])[13] == 103 then
											(t1[1])[14] = (t1[1])[5]
											;(t1[1])[14]()
											break
										else
											exitTo10 = nil

											while true do
												if d_2 <= 0 then
													exitTo10 = 1
													break
												else
													if h_2 <= E_2 then
														(t1[1])[13] = h_2

														if (t1[1])[13] == 21 then
															continue
														elseif (t1[1])[13] == 103 then
															exitTo10 = 2
															break
														else
															continue
														end
													end

													break
												end
											end

											if exitTo10 == 1 then
												if h_2 >= E_2 then
													(t1[1])[13] = h_2
													continue
												end
											else
												if exitTo10 == 2 then
													(t1[1])[14] = (t1[1])[5]
													;(t1[1])[14]()
												end

												break
											end
										end

										break
									end
								end
							end
						elseif exitTo15 == 2 then
							(t1[1])[14] = (t1[1])[5]
							;(t1[1])[14]()
						end
					end
				end
			end
		end
	elseif exitTo == 2 then
		if (t1[1])[5] then
			(t1[1])[10] = 21
			;(t1[1])[11] = 204
			;(t1[1])[12] = 82
			local exitTo16 = nil

			while true do
				if d_2 <= 0 then
					exitTo16 = 1
					break
				else
					if h_2 <= E_2 then
						(t1[1])[13] = h_2

						if (t1[1])[13] == 21 then
							continue
						elseif (t1[1])[13] == 103 then
							exitTo16 = 2
							break
						else
							continue
						end
					end

					break
				end
			end

			if exitTo16 == 1 then
				if h_2 >= E_2 then
					(t1[1])[13] = h_2

					while true do
						if (t1[1])[13] == 21 then
							exitTo9 = nil

							while true do
								if d_2 <= 0 then
									exitTo9 = 1
									break
								else
									if h_2 <= E_2 then
										(t1[1])[13] = h_2

										if (t1[1])[13] == 21 then
											continue
										elseif (t1[1])[13] == 103 then
											exitTo9 = 2
											break
										else
											continue
										end
									end

									break
								end
							end

							if exitTo9 == 1 then
								if h_2 >= E_2 then
									(t1[1])[13] = h_2
									continue
								end
							else
								if exitTo9 == 2 then
									(t1[1])[14] = (t1[1])[5]
									;(t1[1])[14]()
								end

								break
							end

							break
						else
							if (t1[1])[13] == 103 then
								(t1[1])[14] = (t1[1])[5]
								;(t1[1])[14]()
								break
							else
								exitTo10 = nil

								while true do
									if d_2 <= 0 then
										exitTo10 = 1
										break
									else
										if h_2 <= E_2 then
											(t1[1])[13] = h_2

											if (t1[1])[13] == 21 then
												continue
											elseif (t1[1])[13] == 103 then
												exitTo10 = 2
												break
											else
												continue
											end
										end

										break
									end
								end

								if exitTo10 == 1 then
									if h_2 >= E_2 then
										(t1[1])[13] = h_2
										continue
									end
								else
									if exitTo10 == 2 then
										(t1[1])[14] = (t1[1])[5]
										;(t1[1])[14]()
									end

									break
								end
							end

							break
						end
					end
				end
			elseif exitTo16 == 2 then
				(t1[1])[14] = (t1[1])[5]
				;(t1[1])[14]()
			end
		end
	end

	error("devirt: symbolic generic for (at 0:102)")
end

-- proto 18: vm sequence 12, 0 opcodes
local function proto_18()
	(t1[1])[1] = (t2[2])[1]
	;(t1[1])[2] = (t2[2])[2]
	;(t1[1])[3] = upv0
	;(t1[1])[4] = upv1[1]
	;(t1[1])[5] = 37

	while (t1[1])[5] ~= 64 do
		if (t1[1])[5] == 37 then
			(t1[1])[5] = 64
			;(t1[1])[4] = (t1[1])[2]
		end
	end
	;(t1[1])[6] = (t1[1])[3]
	;(t1[1])[7] = (t1[1])[1]
	;(t1[1])[8] = (t1[1])[4]
	;(t1[1])[6] = (t1[1])[6]((t1[1])[7], (t1[1])[8])
	;(t1[1])[3] = (t1[1])[6]

	if (t1[1])[3] then
		(t1[1])[3] = upv2
		;(t1[1])[6] = (t1[1])[3]
		;(t1[1])[6]()
	end

	error("devirt: symbolic generic for (at 0:55)")
end

-- proto 23: vm sequence 13, 0 opcodes
local function proto_23()
	(t1[1])[1] = (t2[2])[1]
	;(t1[1])[2] = 120

	while not ((t1[1])[2] < 120) do
		if (t1[1])[2] > 119 then
			(t1[1])[2] = 119
			;(t1[1])[3] = upv4
			;(t1[1])[4] = (t1[1])[1]
			;(t1[1])[3]((t1[1])[4])
		end
	end
	;(t1[1])[3] = upv0
	;(t1[1])[4] = upv1[53]
	;(t1[1])[5] = upv2
	;(t1[1])[6] = (t1[1])[1]
	;(t1[1])[5] = (t1[1])[5]((t1[1])[6])
	;(t1[1])[3]((t1[1])[4], (t1[1])[5])
	;(t1[1])[3] = upv0
	;(t1[1])[4] = upv1[1]
	;(t1[1])[5] = upv3
	;(t1[1])[6] = (t1[1])[1]
	;(t1[1])[5] = (t1[1])[5]((t1[1])[6])
	;(t1[1])[3]((t1[1])[4], (t1[1])[5])
	;(t1[1])[3] = upv5
	;(t1[1])[4] = upv6
	;(t1[1])[5] = (t1[1])[1]
	;(t1[1])[6] = nil
	;(t1[1])[3]((nil --[[ constant not decoded ]])[26](t1[1], 6, 4))
	error("devirt: symbolic generic for (at 0:19)")
end

-- proto 13: vm sequence 14, 0 opcodes
local function proto_13()
	(t1[1])[1] = (t2[2])[1]
	;(t1[1])[2] = upv0[1]
	;(t1[1])[3] = upv0[1]
	;(t1[1])[4] = 12

	while (t1[1])[4] ~= 123 do
		(t1[1])[4] = 123
		;(t1[1])[2] = 2166136261
	end
	;(t1[1])[5] = {}
	;(t1[1])[6] = upv1
	;(t1[1])[7] = (t1[1])[1]
	;(t1[1])[8] = 1
	;(t1[1])[9] = -1
	error("devirt: numeric for with symbolic bounds (at 0:102)")
end

-- proto 12: vm sequence 15, 0 opcodes
local function proto_12()
	(t1[1])[1] = (t2[2])[1]
	;(t1[1])[2] = (t2[2])[2]
	;(t1[1])[3] = upv0
	;(t1[1])[4] = (t1[1])[1]
	;(t1[1])[5] = upv1[1]
	;(t1[1])[6] = upv1[1]
	;(t1[1])[7] = upv1[1]
	;(t1[1])[8] = 79
	local v

	while true do
		if not ((t1[1])[8] > 79) then
			(t1[1])[8] = 98
			;(t1[1])[5] = upv1[1]
			;(t1[1])[6] = nil
			;(t1[1])[7] = nil
			continue
		end

		if (t1[1])[8] ~= 89 then
			(t1[1])[8] = 89
			;(t1[1])[5] = (t1[1])[3]
			;(t1[1])[6] = (t1[1])[4]
			;(t1[1])[7] = nil
			;(t1[1])[9] = (t1[1])[5]
			;(t1[1])[10] = (t1[1])[6]
			;(t1[1])[11] = (t1[1])[7]
			;(nil --[[ constant not decoded ]])[18](function(...) end)((t1[1])[9], (t1[1])[10], (t1[1])[11])

			while true do
				v = table.pack((h_1()))

				if v[1] then
					(t1[1])[10] = v[2]
					;(t1[1])[11] = v[3]
					;(t1[1])[11] = upv1[1]
					;(t1[1])[12] = upv1[1]
					;(t1[1])[13] = upv1[1]
					;(t1[1])[14] = 80
					;(t1[1])[15] = 214
					;(t1[1])[16] = 7
					local exitTo = nil

					while true do
						if d_2 <= 0 then
							exitTo = 1
							break
						else
							if h_2 <= E_2 then
								(t1[1])[17] = h_2

								if (t1[1])[17] == 94 then
									(t1[1])[18] = (t1[1])[13]
									;(t1[1])[19] = (t1[1])[12]
									;(t1[1])[18] = (t1[1])[18]((t1[1])[19])
									;(t1[1])[13] = (t1[1])[18]
									continue
								elseif (t1[1])[17] == 80 then
									(t1[1])[11] = (t1[1])[2]
									continue
								elseif (t1[1])[17] == 101 then
									exitTo = 2
									break
								else
									if (t1[1])[17] == 87 then
										(t1[1])[12] = (t1[1])[10]
										;(t1[1])[13] = upv2
									end

									continue
								end
							end

							break
						end
					end

					if exitTo == 1 then
						if h_2 >= E_2 then
							(t1[1])[17] = h_2

							while true do
								if (t1[1])[17] == 94 then
									(t1[1])[18] = (t1[1])[13]
									;(t1[1])[19] = (t1[1])[12]
									;(t1[1])[18] = (t1[1])[18]((t1[1])[19])
									;(t1[1])[13] = (t1[1])[18]
									local exitTo2 = nil

									while true do
										if d_2 <= 0 then
											exitTo2 = 1
											break
										else
											if h_2 <= E_2 then
												(t1[1])[17] = h_2

												if (t1[1])[17] == 94 then
													(t1[1])[18] = (t1[1])[13]
													;(t1[1])[19] = (t1[1])[12]
													;(t1[1])[18] = (t1[1])[18]((t1[1])[19])
													;(t1[1])[13] = (t1[1])[18]
													continue
												elseif (t1[1])[17] == 80 then
													(t1[1])[11] = (t1[1])[2]
													continue
												elseif (t1[1])[17] == 101 then
													exitTo2 = 2
													break
												else
													if (t1[1])[17] == 87 then
														(t1[1])[12] = (t1[1])[10]
														;(t1[1])[13] = upv2
													end

													continue
												end
											end

											break
										end
									end

									if exitTo2 == 1 then
										if h_2 >= E_2 then
											(t1[1])[17] = h_2
											continue
										end
									else
										if exitTo2 == 2 then
											(t1[1])[12] = upv1[1]
										end

										break
									end

									break
								else
									if (t1[1])[17] == 80 then
										(t1[1])[11] = (t1[1])[2]
										local exitTo3 = nil

										while true do
											if d_2 <= 0 then
												exitTo3 = 1
												break
											else
												if h_2 <= E_2 then
													(t1[1])[17] = h_2

													if (t1[1])[17] == 94 then
														(t1[1])[18] = (t1[1])[13]
														;(t1[1])[19] = (t1[1])[12]
														;(t1[1])[18] = (t1[1])[18]((t1[1])[19])
														;(t1[1])[13] = (t1[1])[18]
														continue
													elseif (t1[1])[17] == 80 then
														(t1[1])[11] = (t1[1])[2]
														continue
													elseif (t1[1])[17] == 101 then
														exitTo3 = 2
														break
													else
														if (t1[1])[17] == 87 then
															(t1[1])[12] = (t1[1])[10]
															;(t1[1])[13] = upv2
														end

														continue
													end
												end

												break
											end
										end

										if exitTo3 == 1 then
											if h_2 >= E_2 then
												(t1[1])[17] = h_2
												continue
											end
										else
											if exitTo3 == 2 then
												(t1[1])[12] = upv1[1]
											end

											break
										end
									elseif (t1[1])[17] == 101 then
										(t1[1])[12] = upv1[1]
										break
									elseif (t1[1])[17] == 87 then
										(t1[1])[12] = (t1[1])[10]
										;(t1[1])[13] = upv2
										local exitTo4 = nil

										while true do
											if d_2 <= 0 then
												exitTo4 = 1
												break
											else
												if h_2 <= E_2 then
													(t1[1])[17] = h_2

													if (t1[1])[17] == 94 then
														(t1[1])[18] = (t1[1])[13]
														;(t1[1])[19] = (t1[1])[12]
														;(t1[1])[18] = (t1[1])[18]((t1[1])[19])
														;(t1[1])[13] = (t1[1])[18]
														continue
													elseif (t1[1])[17] == 80 then
														(t1[1])[11] = (t1[1])[2]
														continue
													elseif (t1[1])[17] == 101 then
														exitTo4 = 2
														break
													else
														if (t1[1])[17] == 87 then
															(t1[1])[12] = (t1[1])[10]
															;(t1[1])[13] = upv2
														end

														continue
													end
												end

												break
											end
										end

										if exitTo4 == 1 then
											if h_2 >= E_2 then
												(t1[1])[17] = h_2
												continue
											end
										else
											if exitTo4 == 2 then
												(t1[1])[12] = upv1[1]
											end

											break
										end
									else
										local exitTo5 = nil

										while true do
											if d_2 <= 0 then
												exitTo5 = 1
												break
											else
												if h_2 <= E_2 then
													(t1[1])[17] = h_2

													if (t1[1])[17] == 94 then
														(t1[1])[18] = (t1[1])[13]
														;(t1[1])[19] = (t1[1])[12]
														;(t1[1])[18] = (t1[1])[18]((t1[1])[19])
														;(t1[1])[13] = (t1[1])[18]
														continue
													elseif (t1[1])[17] == 80 then
														(t1[1])[11] = (t1[1])[2]
														continue
													elseif (t1[1])[17] == 101 then
														exitTo5 = 2
														break
													else
														if (t1[1])[17] == 87 then
															(t1[1])[12] = (t1[1])[10]
															;(t1[1])[13] = upv2
														end

														continue
													end
												end

												break
											end
										end

										if exitTo5 == 1 then
											if h_2 >= E_2 then
												(t1[1])[17] = h_2
												continue
											end
										else
											if exitTo5 == 2 then
												(t1[1])[12] = upv1[1]
											end

											break
										end
									end

									break
								end
							end
						end
					elseif exitTo == 2 then
						(t1[1])[12] = upv1[1]
					end
				else
					break
				end
			end

			continue
		end

		break
	end
	;(t1[1])[3] = upv0
	;(t1[1])[4] = (t1[1])[2]

	while not ((t1[1])[8] < 64) do
		(t1[1])[8] = 31
		;(t1[1])[6] = (t1[1])[4]
		;(t1[1])[7] = nil
	end
	;(t1[1])[9] = (t1[1])[5]
	;(t1[1])[10] = (t1[1])[6]
	;(t1[1])[11] = (t1[1])[7]
	;(nil --[[ constant not decoded ]])[18](function(...) end)((t1[1])[9], (t1[1])[10], (t1[1])[11])
	local v2

	while true do
		v2 = table.pack((h_1()))

		if v2[1] then
			(t1[1])[10] = v2[2]
			;(t1[1])[11] = v2[3]
			;(t1[1])[11] = upv3
			;(t1[1])[12] = (t1[1])[11]
			;(t1[1])[12]()
		else
			break
		end
	end

	error("devirt: symbolic generic for (at 0:68)")
end

-- proto 4: vm sequence 16, 0 opcodes
local function proto_4()
	(t1[1])[1] = upv0
	;(t1[1])[2] = upv1
	;(t1[1])[1]((t1[1])[2])
	;(t1[1])[1] = upv0
	;(t1[1])[2] = upv2
	;(t1[1])[1]((t1[1])[2])
	error("devirt: symbolic generic for (at 0:9)")
end

-- proto 9: vm sequence 17, 0 opcodes
local function proto_9()
	(t1[1])[1] = upv1
	;(t1[1])[1] = (t1[1])[1]()
	upv0 = (t1[1])[1]
	error("devirt: symbolic generic for (at 0:5)")
end

-- proto 10: vm sequence 18, 0 opcodes
local function proto_10()
	(t1[1])[1] = upv0
	;(t1[1])[1]()
	error("devirt: symbolic generic for (at 0:5)")
end

-- proto t317: vm sequence 19, 0 opcodes
local function proto_t317()
	(t1[1])[21] = {
		0,
		298,
		0,
		32,
		55,
		23,
		226,
		0,
		0,
		21,
		0,
		0,
		16,
		16,
		72,
		23,
		0,
		0,
		2,
		0,
		0,
		5,
		0,
		3,
		0,
		0,
		151,
		446,
		14,
		12,
		55,
		15,
		195,
		0,
		0,
		0,
		0,
	}
	;(t1[1])[23] = {
		34,
		280,
		0,
		925,
		244,
		16,
		242,
		8,
		17,
		0,
		0,
		22,
		7,
		745,
		72,
		16,
		35,
		0,
		62,
		3,
		4,
		336,
		0,
		87,
		0,
		12,
		346,
		14,
		212,
		14,
		834,
		6,
		89,
		36,
		9,
		24,
		2,
	}
	;(t1[1])[22] = {
		0,
		502,
		23,
		23,
		23,
		238,
		59,
		0,
		0,
		0,
		23,
		0,
		22,
		21,
		23,
		0,
		0,
		1,
		1,
		0,
		2,
		0,
		131,
		0,
		13,
		0,
		69,
		72,
		14,
		54,
		13,
		200,
		125,
		0,
		0,
		0,
		0,
	}
	;(t1[1])[22][28] = 14
	;(t1[1])[21][27] = 14
	;(t1[1])[23][35] = 35
	;(t1[1])[16] = nil
	;(t1[1])[17] = nil
	;(t1[1])[18] = nil
	;(t1[1])[19] = nil
	;(t1[1])[20] = nil
	;(t1[1])[21] = nil
	;(t1[1])[22] = nil
	;(t1[1])[23] = nil
	;(t1[1])[13] = {
		34,
		280,
		0,
		925,
		244,
		16,
		242,
		8,
		17,
		0,
		0,
		22,
		7,
		745,
		72,
		16,
		35,
		0,
		62,
		3,
		4,
		336,
		0,
		87,
		0,
		12,
		346,
		14,
		212,
		14,
		834,
		6,
		89,
		36,
		9,
		24,
		2,
	}
	;(t1[1])[12] = {
		0,
		502,
		23,
		23,
		23,
		238,
		59,
		0,
		0,
		0,
		23,
		0,
		22,
		21,
		23,
		0,
		0,
		1,
		1,
		0,
		2,
		0,
		131,
		0,
		13,
		0,
		69,
		72,
		14,
		54,
		13,
		200,
		125,
		0,
		0,
		0,
		0,
	}
	;(t1[1])[151] = 166
	;(t1[1])[14] = 21998 + (t1[1])[72]
	;(t1[1])[14] = (t1[1])[14] + -22161
	;(t1[1])[12][23] = (t1[1])[14]
	;(t1[1])[13][36] = 8
	;(t1[1])[23] = {
		34,
		280,
		0,
		925,
		244,
		16,
		242,
		8,
		17,
		0,
		0,
		22,
		7,
		745,
		72,
		16,
		35,
		0,
		62,
		3,
		4,
		336,
		0,
		87,
		0,
		12,
		346,
		14,
		212,
		14,
		834,
		6,
		89,
		36,
		9,
		24,
		2,
	}
	;(t1[1])[23][24] = 0
	;(t1[1])[23][37] = 8
	;(t1[1])[1] = (t2[2])[1]
	;(t1[1])[2] = (t1[1])[1] + 3
	;(t1[1])[3] = upv0
	;(t1[1])[4] = (t1[1])[2]
	;(t1[1])[5] = "f"
	;(t1[1])[131] = (t1[1])[131]((t1[1])[132], (t1[1])[133])
	error("devirt: symbolic generic for (at 0:24)")
end

-- proto 11: vm sequence 20, 0 opcodes
local function proto_11()
	(t1[1])[1] = (t2[2])[1]
	error("devirt: symbolic generic for (at 0:5)")
end

-- proto 14: vm sequence 21, 0 opcodes
local function proto_14()
	(t1[1])[1] = (t2[2])[1]
	;(t1[1])[2] = nil
	;(t1[1])[3] = upv0[1]
	;(t1[1])[4] = 62
	;(t1[1])[5] = 169
	;(t1[1])[6] = 107
	local exitTo18 = nil

	while true do
		if d_1 <= 0 then
			exitTo18 = 1
			break
		else
			if h_1 <= E_1 then
				(t1[1])[7] = h_1

				if (t1[1])[7] == 169 then
					(t1[1])[3] = 1
				else
					(t1[1])[2] = upv1
				end

				continue
			end

			break
		end
	end

	if exitTo18 == 1 then
		if not (h_1 >= E_1) then
			(t1[1])[4] = (t1[1])[2]
			;(t1[1])[4] = (t1[1])[4]()
			;(t1[1])[2] = (t1[1])[4]
			;(t1[1])[4] = upv0[1]
			;(t1[1])[5] = upv0[1]
			;(t1[1])[7] = 269
			;(t1[1])[8] = 66
		else
			(t1[1])[7] = h_1

			while true do
				if (t1[1])[7] == 169 then
					(t1[1])[3] = 1
					local exitTo = nil

					while true do
						if d_1 <= 0 then
							exitTo = 1
							break
						else
							if h_1 <= E_1 then
								(t1[1])[7] = h_1

								if (t1[1])[7] == 169 then
									(t1[1])[3] = 1
								else
									(t1[1])[2] = upv1
								end

								continue
							end

							break
						end
					end

					if exitTo == 1 then
						if not (h_1 >= E_1) then
							(t1[1])[4] = (t1[1])[2]
							;(t1[1])[4] = (t1[1])[4]()
							;(t1[1])[2] = (t1[1])[4]
							;(t1[1])[4] = upv0[1]
							;(t1[1])[5] = upv0[1]
							;(t1[1])[7] = 269
							;(t1[1])[8] = 66
							break
						end
						;(t1[1])[7] = h_1
						continue
					end
					;(t1[1])[4] = (t1[1])[2]
					;(t1[1])[4] = (t1[1])[4]()
					;(t1[1])[2] = (t1[1])[4]
					;(t1[1])[4] = upv0[1]
					;(t1[1])[5] = upv0[1]
					;(t1[1])[7] = 269
					;(t1[1])[8] = 66
					break
				else
					(t1[1])[2] = upv1
					local exitTo2 = nil

					while true do
						if d_1 <= 0 then
							exitTo2 = 1
							break
						else
							if h_1 <= E_1 then
								(t1[1])[7] = h_1

								if (t1[1])[7] == 169 then
									(t1[1])[3] = 1
								else
									(t1[1])[2] = upv1
								end

								continue
							end

							break
						end
					end

					if exitTo2 == 1 then
						if not (h_1 >= E_1) then
							(t1[1])[4] = (t1[1])[2]
							;(t1[1])[4] = (t1[1])[4]()
							;(t1[1])[2] = (t1[1])[4]
							;(t1[1])[4] = upv0[1]
							;(t1[1])[5] = upv0[1]
							;(t1[1])[7] = 269
							;(t1[1])[8] = 66
							break
						end
						;(t1[1])[7] = h_1
						continue
					end
					;(t1[1])[4] = (t1[1])[2]
					;(t1[1])[4] = (t1[1])[4]()
					;(t1[1])[2] = (t1[1])[4]
					;(t1[1])[4] = upv0[1]
					;(t1[1])[5] = upv0[1]
					;(t1[1])[7] = 269
					;(t1[1])[8] = 66
					break
				end
			end
		end
	else
		(t1[1])[4] = (t1[1])[2]
		;(t1[1])[4] = (t1[1])[4]()
		;(t1[1])[2] = (t1[1])[4]
		;(t1[1])[4] = upv0[1]
		;(t1[1])[5] = upv0[1]
		;(t1[1])[7] = 269
		;(t1[1])[8] = 66
	end

	local exitTo3 = nil

	while true do
		if d_1 <= 0 then
			exitTo3 = 1
			break
		else
			if h_1 <= E_1 then
				(t1[1])[9] = h_1

				if (t1[1])[9] < 176 then
					(t1[1])[4] = (t1[1])[2]
					continue
				elseif not ((t1[1])[9] > 110) then
					continue
				else
					exitTo3 = 2
					break
				end
			end

			break
		end
	end

	if exitTo3 == 1 then
		if h_1 >= E_1 then
			(t1[1])[9] = h_1

			while true do
				if (t1[1])[9] < 176 then
					(t1[1])[4] = (t1[1])[2]
					local exitTo4 = nil

					while true do
						if d_1 <= 0 then
							exitTo4 = 1
							break
						else
							if h_1 <= E_1 then
								(t1[1])[9] = h_1

								if (t1[1])[9] < 176 then
									(t1[1])[4] = (t1[1])[2]
									continue
								elseif not ((t1[1])[9] > 110) then
									continue
								else
									exitTo4 = 2
									break
								end
							end

							break
						end
					end

					if exitTo4 == 1 then
						if h_1 >= E_1 then
							(t1[1])[9] = h_1
							continue
						end
					else
						if exitTo4 == 2 then
							(t1[1])[5] = 1
						end

						break
					end

					break
				else
					if not ((t1[1])[9] > 110) then
						local exitTo5 = nil

						while true do
							if d_1 <= 0 then
								exitTo5 = 1
								break
							else
								if h_1 <= E_1 then
									(t1[1])[9] = h_1

									if (t1[1])[9] < 176 then
										(t1[1])[4] = (t1[1])[2]
										continue
									elseif not ((t1[1])[9] > 110) then
										continue
									else
										exitTo5 = 2
										break
									end
								end

								break
							end
						end

						if exitTo5 == 1 then
							if h_1 >= E_1 then
								(t1[1])[9] = h_1
								continue
							end
						else
							if exitTo5 == 2 then
								(t1[1])[5] = 1
							end

							break
						end
					else
						(t1[1])[5] = 1
						break
					end

					break
				end
			end
		end
	elseif exitTo3 == 2 then
		(t1[1])[5] = 1
	end
	;(t1[1])[4] = (t1[1])[4] - (t1[1])[5]
	;(t1[1])[6] = upv0[1]
	;(t1[1])[7] = 34

	while true do
		if (t1[1])[7] > 34 then
			if (t1[1])[7] <= 51 then
				if not ((t1[1])[7] > 36) then
					(t1[1])[3] = (t1[1])[1]
					;(t1[1])[7] = 51
				else
					(t1[1])[7] = 118
					;(t1[1])[6] = 100
				end
			elseif (t1[1])[7] == 118 then
				(t1[1])[7] = 93
				;(t1[1])[3] = (t1[1])[3] * (t1[1])[6]
			else
				(t1[1])[6] = 1
				;(t1[1])[7] = 24
			end

			continue
		end

		if not ((t1[1])[7] <= 24) then
			if not ((t1[1])[7] >= 34) then
				(t1[1])[5] = (t1[1])[5] + (t1[1])[3]
				;(t1[1])[7] = 36
			else
				(t1[1])[7] = 25
			end

			continue
		end

		break
	end
	;(t1[1])[3] = (t1[1])[3] // (t1[1])[6]
	;(t1[1])[1] = (t1[1])[3]
	;(t1[1])[3] = upv2
	;(t1[1])[8] = upv0[1]
	;(t1[1])[7] = 48

	while true do
		if (t1[1])[7] > 48 then
			if (t1[1])[7] < 98 then
				(t1[1])[7] = 98
				;(t1[1])[6] = (t1[1])[4]
				continue
			end
		end

		if (t1[1])[7] < 79 then
			(t1[1])[7] = 79
			;(t1[1])[8] = upv0[46]
			continue
		end

		if not ((t1[1])[7] > 79) then
			continue
		end
		break
	end
	;(t1[1])[3][(t1[1])[6]] = (t1[1])[8]
	;(t1[1])[7] = 5

	while true do
		if (t1[1])[7] < 35 then
			if (t1[1])[7] > 9 then
				(t1[1])[6] = (t1[1])[2]
				continue
			end
		end

		if (t1[1])[7] > 32 then
			if (t1[1])[7] < 38 then
				(t1[1])[6] = (t1[1])[5]
				;(t1[1])[7] = 38
				continue
			end
		end

		if (t1[1])[7] > 82 then
			(t1[1])[7] = 35
			;(t1[1])[3] = upv2
			continue
		end

		if not ((t1[1])[7] > 35) then
			if not ((t1[1])[7] > 38) then
				if (t1[1])[7] < 9 then
					(t1[1])[3] = upv2
					;(t1[1])[7] = 32
				elseif (t1[1])[7] < 32 then
					if (t1[1])[7] > 5 then
						(t1[1])[3][(t1[1])[6]] = (t1[1])[8]
						;(t1[1])[7] = 84
					end
				end
			elseif (t1[1])[7] < 84 then
				(t1[1])[7] = 9
				;(t1[1])[8] = upv0[46]
			elseif (t1[1])[7] < 9 then
				(t1[1])[3] = upv2
				;(t1[1])[7] = 32
			elseif (t1[1])[7] < 32 then
				if (t1[1])[7] > 5 then
					(t1[1])[3][(t1[1])[6]] = (t1[1])[8]
					;(t1[1])[7] = 84
				end
			end

			continue
		end

		if not ((t1[1])[7] < 82) then
			if not ((t1[1])[7] > 38) then
				if (t1[1])[7] < 9 then
					(t1[1])[3] = upv2
					;(t1[1])[7] = 32
				elseif (t1[1])[7] < 32 then
					if (t1[1])[7] > 5 then
						(t1[1])[3][(t1[1])[6]] = (t1[1])[8]
						;(t1[1])[7] = 84
					end
				end
			elseif (t1[1])[7] < 84 then
				(t1[1])[7] = 9
				;(t1[1])[8] = upv0[46]
			elseif (t1[1])[7] < 9 then
				(t1[1])[3] = upv2
				;(t1[1])[7] = 32
			elseif (t1[1])[7] < 32 then
				if (t1[1])[7] > 5 then
					(t1[1])[3][(t1[1])[6]] = (t1[1])[8]
					;(t1[1])[7] = 84
				end
			end

			continue
		end

		break
	end
	;(t1[1])[8] = true
	;(t1[1])[9] = 12
	;(t1[1])[10] = 172
	;(t1[1])[11] = 80
	local exitTo19 = nil

	while true do
		if d_1 <= 0 then
			exitTo19 = 1
			break
		else
			if h_1 <= E_1 then
				(t1[1])[12] = h_1

				if (t1[1])[12] <= 12 then
					(t1[1])[3][(t1[1])[6]] = (t1[1])[8]
					;(t1[1])[3] = upv3
				elseif (t1[1])[12] == 172 then
					(t1[1])[8] = (t1[1])[1]
				else
					(t1[1])[6] = upv2
				end

				continue
			end

			break
		end
	end

	if exitTo19 == 1 then
		if not (h_1 >= E_1) then
			(t1[1])[6] = (t1[1])[6][(t1[1])[8]]
			;(t1[1])[9] = 41
			;(t1[1])[10] = 175
			;(t1[1])[11] = 39
		else
			(t1[1])[12] = h_1

			while true do
				if (t1[1])[12] <= 12 then
					(t1[1])[3][(t1[1])[6]] = (t1[1])[8]
					;(t1[1])[3] = upv3
					local exitTo6 = nil

					while true do
						if d_1 <= 0 then
							exitTo6 = 1
							break
						else
							if h_1 <= E_1 then
								(t1[1])[12] = h_1

								if (t1[1])[12] <= 12 then
									(t1[1])[3][(t1[1])[6]] = (t1[1])[8]
									;(t1[1])[3] = upv3
								elseif (t1[1])[12] == 172 then
									(t1[1])[8] = (t1[1])[1]
								else
									(t1[1])[6] = upv2
								end

								continue
							end

							break
						end
					end

					if exitTo6 == 1 then
						if not (h_1 >= E_1) then
							(t1[1])[6] = (t1[1])[6][(t1[1])[8]]
							;(t1[1])[9] = 41
							;(t1[1])[10] = 175
							;(t1[1])[11] = 39
							break
						end
						;(t1[1])[12] = h_1
						continue
					end
					;(t1[1])[6] = (t1[1])[6][(t1[1])[8]]
					;(t1[1])[9] = 41
					;(t1[1])[10] = 175
					;(t1[1])[11] = 39
					break
				else
					if (t1[1])[12] == 172 then
						(t1[1])[8] = (t1[1])[1]
						local exitTo7 = nil

						while true do
							if d_1 <= 0 then
								exitTo7 = 1
								break
							else
								if h_1 <= E_1 then
									(t1[1])[12] = h_1

									if (t1[1])[12] <= 12 then
										(t1[1])[3][(t1[1])[6]] = (t1[1])[8]
										;(t1[1])[3] = upv3
									elseif (t1[1])[12] == 172 then
										(t1[1])[8] = (t1[1])[1]
									else
										(t1[1])[6] = upv2
									end

									continue
								end

								break
							end
						end

						if exitTo7 == 1 then
							if not (h_1 >= E_1) then
								(t1[1])[6] = (t1[1])[6][(t1[1])[8]]
								;(t1[1])[9] = 41
								;(t1[1])[10] = 175
								;(t1[1])[11] = 39
								break
							end
							;(t1[1])[12] = h_1
							continue
						end
						;(t1[1])[6] = (t1[1])[6][(t1[1])[8]]
						;(t1[1])[9] = 41
						;(t1[1])[10] = 175
						;(t1[1])[11] = 39
						break
					end
					;(t1[1])[6] = upv2
					local exitTo8 = nil

					while true do
						if d_1 <= 0 then
							exitTo8 = 1
							break
						else
							if h_1 <= E_1 then
								(t1[1])[12] = h_1

								if (t1[1])[12] <= 12 then
									(t1[1])[3][(t1[1])[6]] = (t1[1])[8]
									;(t1[1])[3] = upv3
								elseif (t1[1])[12] == 172 then
									(t1[1])[8] = (t1[1])[1]
								else
									(t1[1])[6] = upv2
								end

								continue
							end

							break
						end
					end

					if exitTo8 == 1 then
						if not (h_1 >= E_1) then
							(t1[1])[6] = (t1[1])[6][(t1[1])[8]]
							;(t1[1])[9] = 41
							;(t1[1])[10] = 175
							;(t1[1])[11] = 39
							break
						end
						;(t1[1])[12] = h_1
						continue
					end
					;(t1[1])[6] = (t1[1])[6][(t1[1])[8]]
					;(t1[1])[9] = 41
					;(t1[1])[10] = 175
					;(t1[1])[11] = 39
					break
				end
			end
		end
	else
		(t1[1])[6] = (t1[1])[6][(t1[1])[8]]
		;(t1[1])[9] = 41
		;(t1[1])[10] = 175
		;(t1[1])[11] = 39
	end

	local exitTo9 = nil

	while true do
		if d_1 <= 0 then
			exitTo9 = 1
			break
		else
			if h_1 <= E_1 then
				(t1[1])[12] = h_1

				if not ((t1[1])[12] > 80) then
					if (t1[1])[12] == 80 then
						(t1[1])[3] = upv2
					else
						(t1[1])[13] = (t1[1])[3]
						;(t1[1])[14] = (t1[1])[6]
						;(t1[1])[13]((t1[1])[14])
					end

					continue
				elseif (t1[1])[12] == 158 then
					exitTo9 = 2
					break
				else
					(t1[1])[6] = (t1[1])[4]
					continue
				end
			end

			break
		end
	end

	if exitTo9 == 1 then
		if h_1 >= E_1 then
			(t1[1])[12] = h_1

			while true do
				if not ((t1[1])[12] > 80) then
					if (t1[1])[12] == 80 then
						(t1[1])[3] = upv2
						local exitTo10 = nil

						while true do
							if d_1 <= 0 then
								exitTo10 = 1
								break
							else
								if h_1 <= E_1 then
									(t1[1])[12] = h_1

									if not ((t1[1])[12] > 80) then
										if (t1[1])[12] == 80 then
											(t1[1])[3] = upv2
										else
											(t1[1])[13] = (t1[1])[3]
											;(t1[1])[14] = (t1[1])[6]
											;(t1[1])[13]((t1[1])[14])
										end

										continue
									elseif (t1[1])[12] == 158 then
										exitTo10 = 2
										break
									else
										(t1[1])[6] = (t1[1])[4]
										continue
									end
								end

								break
							end
						end

						if exitTo10 == 1 then
							if h_1 >= E_1 then
								(t1[1])[12] = h_1
								continue
							end
						else
							if exitTo10 == 2 then
								(t1[1])[8] = (t1[1])[0]
							end

							break
						end
					else
						(t1[1])[13] = (t1[1])[3]
						;(t1[1])[14] = (t1[1])[6]
						;(t1[1])[13]((t1[1])[14])
						local exitTo11 = nil

						while true do
							if d_1 <= 0 then
								exitTo11 = 1
								break
							else
								if h_1 <= E_1 then
									(t1[1])[12] = h_1

									if not ((t1[1])[12] > 80) then
										if (t1[1])[12] == 80 then
											(t1[1])[3] = upv2
										else
											(t1[1])[13] = (t1[1])[3]
											;(t1[1])[14] = (t1[1])[6]
											;(t1[1])[13]((t1[1])[14])
										end

										continue
									elseif (t1[1])[12] == 158 then
										exitTo11 = 2
										break
									else
										(t1[1])[6] = (t1[1])[4]
										continue
									end
								end

								break
							end
						end

						if exitTo11 == 1 then
							if h_1 >= E_1 then
								(t1[1])[12] = h_1
								continue
							end
						else
							if exitTo11 == 2 then
								(t1[1])[8] = (t1[1])[0]
							end

							break
						end
					end

					break
				else
					if (t1[1])[12] == 158 then
						(t1[1])[8] = (t1[1])[0]
						break
					else
						(t1[1])[6] = (t1[1])[4]
						local exitTo12 = nil

						while true do
							if d_1 <= 0 then
								exitTo12 = 1
								break
							else
								if h_1 <= E_1 then
									(t1[1])[12] = h_1

									if not ((t1[1])[12] > 80) then
										if (t1[1])[12] == 80 then
											(t1[1])[3] = upv2
										else
											(t1[1])[13] = (t1[1])[3]
											;(t1[1])[14] = (t1[1])[6]
											;(t1[1])[13]((t1[1])[14])
										end

										continue
									elseif (t1[1])[12] == 158 then
										exitTo12 = 2
										break
									else
										(t1[1])[6] = (t1[1])[4]
										continue
									end
								end

								break
							end
						end

						if exitTo12 == 1 then
							if h_1 >= E_1 then
								(t1[1])[12] = h_1
								continue
							end
						else
							if exitTo12 == 2 then
								(t1[1])[8] = (t1[1])[0]
							end

							break
						end
					end

					break
				end
			end
		end
	elseif exitTo9 == 2 then
		(t1[1])[8] = (t1[1])[0]
	end
	;(t1[1])[9] = 90
	;(t1[1])[10] = 206
	;(t1[1])[11] = 59
	local exitTo13 = nil

	while true do
		if d_1 <= 0 then
			exitTo13 = 1
			break
		else
			if h_1 <= E_1 then
				(t1[1])[12] = h_1

				if (t1[1])[12] == 149 then
					exitTo13 = 2
					break
				else
					(t1[1])[3][(t1[1])[6]] = (t1[1])[8]
					;(t1[1])[3] = upv2
					;(t1[1])[6] = (t1[1])[2]
					continue
				end
			end

			break
		end
	end

	if exitTo13 == 1 then
		if h_1 >= E_1 then
			(t1[1])[12] = h_1

			while true do
				if (t1[1])[12] == 149 then
					(t1[1])[8] = upv0[1]
					break
				else
					(t1[1])[3][(t1[1])[6]] = (t1[1])[8]
					;(t1[1])[3] = upv2
					;(t1[1])[6] = (t1[1])[2]
					local exitTo14 = nil

					while true do
						if d_1 <= 0 then
							exitTo14 = 1
							break
						else
							if h_1 <= E_1 then
								(t1[1])[12] = h_1

								if (t1[1])[12] == 149 then
									exitTo14 = 2
									break
								else
									(t1[1])[3][(t1[1])[6]] = (t1[1])[8]
									;(t1[1])[3] = upv2
									;(t1[1])[6] = (t1[1])[2]
									continue
								end
							end

							break
						end
					end

					if exitTo14 == 1 then
						if h_1 >= E_1 then
							(t1[1])[12] = h_1
							continue
						end
					else
						if exitTo14 == 2 then
							(t1[1])[8] = upv0[1]
						end

						break
					end

					break
				end
			end
		end
	elseif exitTo13 == 2 then
		(t1[1])[8] = upv0[1]
	end
	;(t1[1])[3][(t1[1])[6]] = (t1[1])[8]
	;(t1[1])[9] = 78
	;(t1[1])[10] = 149
	;(t1[1])[11] = 7
	local exitTo15 = nil

	while true do
		if d_1 <= 0 then
			exitTo15 = 1
			break
		else
			if h_1 <= E_1 then
				(t1[1])[12] = h_1

				if not ((t1[1])[12] > 78) then
					if (t1[1])[12] < 85 then
						(t1[1])[3] = upv2
					end

					continue
				else
					exitTo15 = 2
					break
				end
			end

			break
		end
	end

	if exitTo15 == 1 then
		if h_1 >= E_1 then
			(t1[1])[12] = h_1

			while true do
				if not ((t1[1])[12] > 78) then
					if (t1[1])[12] < 85 then
						(t1[1])[3] = upv2
						local exitTo16 = nil

						while true do
							if d_1 <= 0 then
								exitTo16 = 1
								break
							else
								if h_1 <= E_1 then
									(t1[1])[12] = h_1

									if not ((t1[1])[12] > 78) then
										if (t1[1])[12] < 85 then
											(t1[1])[3] = upv2
										end

										continue
									else
										exitTo16 = 2
										break
									end
								end

								break
							end
						end

						if exitTo16 == 1 then
							if h_1 >= E_1 then
								(t1[1])[12] = h_1
								continue
							end
						else
							if exitTo16 == 2 then
								(t1[1])[6] = (t1[1])[5]
							end

							break
						end
					else
						local exitTo17 = nil

						while true do
							if d_1 <= 0 then
								exitTo17 = 1
								break
							else
								if h_1 <= E_1 then
									(t1[1])[12] = h_1

									if not ((t1[1])[12] > 78) then
										if (t1[1])[12] < 85 then
											(t1[1])[3] = upv2
										end

										continue
									else
										exitTo17 = 2
										break
									end
								end

								break
							end
						end

						if exitTo17 == 1 then
							if h_1 >= E_1 then
								(t1[1])[12] = h_1
								continue
							end
						else
							if exitTo17 == 2 then
								(t1[1])[6] = (t1[1])[5]
							end

							break
						end
					end

					break
				else
					(t1[1])[6] = (t1[1])[5]
					break
				end
			end
		end
	elseif exitTo15 == 2 then
		(t1[1])[6] = (t1[1])[5]
	end
	;(t1[1])[8] = upv0[1]
	;(t1[1])[3][(t1[1])[6]] = (t1[1])[8]
	error("devirt: symbolic generic for (at 0:246)")
end

-- proto 16: vm sequence 22, 0 opcodes
local function proto_16()
	local state = 1
	local v

	while true do
		if state == 1 then
			(t1[1])[1] = (t2[2])[1]
			;(t1[1])[2] = (t2[2])[2]
			;(t1[1])[3] = 119
			state = 2
		elseif state == 2 then
			if (t1[1])[3] == 106 then
				state = 78
			else
				state = 3
			end
		elseif state == 3 then
			if (t1[1])[3] == 119 then
				state = 77
			else
				state = 4
			end
		elseif state == 4 then
			if (t1[1])[3] == 65 then
				state = 5
			else
				state = 2
			end
		elseif state == 5 then
			(t1[1])[4] = nil
			;(t1[1])[5] = upv1[1]
			;(t1[1])[6] = 105
			state = 6
		elseif state == 6 then
			if not ((t1[1])[6] > 52) then
				state = 8
			else
				state = 7
			end
		elseif state == 7 then
			(t1[1])[7] = upv1[105]
			;(t1[1])[4] = (t1[1])[1][(t1[1])[7]]
			state = 6
		elseif state == 8 then
			if (t1[1])[6] < 105 then
				state = 9
			else
				state = 6
			end
		elseif state == 9 then
			(t1[1])[7] = upv1[105]
			;(t1[1])[5] = (t1[1])[1][(t1[1])[7]]
			;(t1[1])[7] = upv4
			;(t1[1])[8] = (t1[1])[4]
			;(t1[1])[7] = (t1[1])[7]((t1[1])[8])

			if not (t1[1])[7] then
				state = 11
			else
				state = 10
			end
		elseif state == 10 then
			(t1[1])[7] = upv0
			;(t1[1])[8] = (t1[1])[4]
			;(t1[1])[9] = (t1[1])[5]
			;(t1[1])[7]((t1[1])[8], (t1[1])[9])
			state = 11
		elseif state == 11 then
			(t1[1])[4] = 96
			;(t1[1])[5] = 192
			;(t1[1])[6] = 17
			state = 12
		elseif state == 12 then
			if d_1 <= 0 then
				state = 15
			else
				state = 13
			end
		elseif state == 13 then
			if not (h_1 <= E_1) then
				state = 36
			else
				state = 14
			end
		elseif state == 14 then
			(t1[1])[7] = h_1
			state = 17
		elseif state == 15 then
			if not (h_1 >= E_1) then
				state = 36
			else
				state = 16
			end
		elseif state == 16 then
			(t1[1])[7] = h_1
			state = 17
		elseif state == 17 then
			if not ((t1[1])[7] > 96) then
				state = 19
			else
				state = 18
			end
		elseif state == 18 then
			(t1[1])[8] = upv0
			;(t1[1])[9] = (t1[1])[2]
			;(t1[1])[10] = upv1[106]
			;(t1[1])[10] = (t1[1])[1][(t1[1])[10]]
			;(t1[1])[8]((t1[1])[9], (t1[1])[10])
			state = 36
		elseif state == 19 then
			if (t1[1])[7] < 113 then
				state = 20
			else
				state = 12
			end
		elseif state == 20 then
			(t1[1])[8] = upv1[1]
			;(t1[1])[9] = upv1[1]
			;(t1[1])[11] = 375
			;(t1[1])[12] = 83
			state = 21
		elseif state == 21 then
			if d_2 <= 0 then
				state = 24
			else
				state = 22
			end
		elseif state == 22 then
			if not (h_2 <= E_2) then
				state = 12
			else
				state = 23
			end
		elseif state == 23 then
			(t1[1])[13] = h_2
			state = 26
		elseif state == 24 then
			if not (h_2 >= E_2) then
				state = 12
			else
				state = 25
			end
		elseif state == 25 then
			(t1[1])[13] = h_2
			state = 26
		elseif state == 26 then
			if not ((t1[1])[13] > 2) then
				state = 29
			else
				state = 27
			end
		elseif state == 27 then
			if (t1[1])[13] < 168 then
				state = 28
			else
				state = 29
			end
		elseif state == 28 then
			(t1[1])[14] = upv0
			;(t1[1])[15] = upv1[107]
			;(t1[1])[17] = (t1[1])[8]
			;(t1[1])[16] = (t1[1])[16]((t1[1])[17])
			;(t1[1])[14]((t1[1])[15], (t1[1])[16])
			;(t1[1])[14] = upv0
			;(t1[1])[15] = (t1[1])[8]
			;(t1[1])[16] = (t1[1])[9]
			;(t1[1])[14]((t1[1])[15], (t1[1])[16])
			state = 21
		elseif state == 29 then
			if (t1[1])[13] < 85 then
				state = 35
			else
				state = 30
			end
		elseif state == 30 then
			if (t1[1])[13] < 251 then
				state = 31
			else
				state = 33
			end
		elseif state == 31 then
			if not ((t1[1])[13] > 85) then
				state = 33
			else
				state = 32
			end
		elseif state == 32 then
			(t1[1])[14] = upv0
			;(t1[1])[15] = #(t1[1])[8]
			;(t1[1])[16] = #(t1[1])[9]
			;(t1[1])[14]((t1[1])[15], (t1[1])[16])
			state = 21
		elseif state == 33 then
			if not ((t1[1])[13] > 168) then
				state = 21
			else
				state = 34
			end
		elseif state == 34 then
			(t1[1])[14] = upv0
			;(t1[1])[15] = upv5
			;(t1[1])[16] = (t1[1])[1]
			;(t1[1])[15] = (t1[1])[15]((t1[1])[16])
			;(t1[1])[16] = (t1[1])[8]
			;(t1[1])[14]((t1[1])[15], (t1[1])[16])
			state = 12
		elseif state == 35 then
			(t1[1])[14] = upv1[108]
			;(t1[1])[8] = (t1[1])[1][(t1[1])[14]]
			;(t1[1])[14] = upv1[108]
			;(t1[1])[9] = (t1[1])[1][(t1[1])[14]]
			state = 21
		elseif state == 36 then
			(t1[1])[4] = nil
			;(t1[1])[5] = upv1[1]
			;(t1[1])[6] = 97
			;(t1[1])[7] = 216
			;(t1[1])[8] = 108
			state = 37
		elseif state == 37 then
			if d_1 <= 0 then
				state = 40
			else
				state = 38
			end
		elseif state == 38 then
			if not (h_1 <= E_1) then
				state = 46
			else
				state = 39
			end
		elseif state == 39 then
			(t1[1])[9] = h_1
			state = 42
		elseif state == 40 then
			if not (h_1 >= E_1) then
				state = 46
			else
				state = 41
			end
		elseif state == 41 then
			(t1[1])[9] = h_1
			state = 42
		elseif state == 42 then
			if (t1[1])[9] == 97 then
				state = 45
			else
				state = 43
			end
		elseif state == 43 then
			if (t1[1])[9] == 205 then
				state = 44
			else
				state = 37
			end
		elseif state == 44 then
			(t1[1])[5] = (t1[1])[1][(t1[1])[4]]
			state = 46
		elseif state == 45 then
			(t1[1])[4] = upv1[109]
			state = 37
		elseif state == 46 then
			(t1[1])[6] = (t1[1])[1][(t1[1])[4]]
			;(t1[1])[7] = upv1[1]
			;(t1[1])[8] = upv1[1]
			;(t1[1])[9] = 109
			state = 47
		elseif state == 47 then
			if (t1[1])[9] < 90 then
				state = 76
			else
				state = 48
			end
		elseif state == 48 then
			if (t1[1])[9] < 104 then
				state = 49
			else
				state = 51
			end
		elseif state == 49 then
			if not ((t1[1])[9] > 39) then
				state = 51
			else
				state = 50
			end
		elseif state == 50 then
			(t1[1])[10] = upv7
			;(t1[1])[11] = (t1[1])[7]
			;(t1[1])[12] = (t1[1])[8]
			;(t1[1])[10]((t1[1])[11], (t1[1])[12])
			;(t1[1])[9] = 113
			state = 47
		elseif state == 51 then
			if not ((t1[1])[9] > 109) then
				state = 70
			else
				state = 52
			end
		elseif state == 52 then
			(t1[1])[10] = upv1[47]
			;(t1[1])[11] = upv1[111]
			;(t1[1])[11] = (t1[1])[1][(t1[1])[11]]
			;(t1[1])[12] = (t1[1])[11]
			;(t1[1])[11] = (t1[1])[11].Connect

			v = table.pack(((nil --[[ constant not decoded ]])[57](table.pack(table.pack(table.pack(10, 0), table.pack(1, 2)), table.pack(nil, nil, nil, 46), 4, table.pack(2, 36, 3, 1, 1, 1), table.pack(127, 162, 127, 155, 142, 59), {}, table.pack(0, 500, 0, 1, 0, 0), {}, table.pack(0, 235, 0, 41, 0, 0), 0, {}), {})))
			;(nil --[[ constant not decoded ]])[49](v[1], t3[1])
			;(t1[1])[13] = v[1]

			if t3[6] then
				state = 53
			else
				state = 55
			end
		elseif state == 53 then
			if (t3[6])[10] then
				state = 55
			else
				state = 54
			end
		elseif state == 54 then
			(t3[6])[10] = { 10, t1[1] }
			state = 55
		elseif state == 55 then
			(t1[1])[11] = (t1[1])[11]((t1[1])[12], (t1[1])[13])
			;(t1[1])[12] = 1
			state = 56
		elseif state == 56 then
			if (t1[1])[12] == 1 then
				state = 69
			else
				state = 57
			end
		elseif state == 57 then
			(t1[1])[13] = upv9
			;(t1[1])[13]((t1[1])[14])
			;(t1[1])[13] = (t1[1])[11].Disconnect
			;(t1[1])[14] = 58
			;(t1[1])[15] = 231
			;(t1[1])[16] = 62
			state = 58
		elseif state == 58 then
			if d_1 <= 0 then
				state = 61
			else
				state = 59
			end
		elseif state == 59 then
			if not (h_1 <= E_1) then
				state = 68
			else
				state = 60
			end
		elseif state == 60 then
			(t1[1])[17] = h_1
			state = 63
		elseif state == 61 then
			if not (h_1 >= E_1) then
				state = 68
			else
				state = 62
			end
		elseif state == 62 then
			(t1[1])[17] = h_1
			state = 63
		elseif state == 63 then
			if not ((t1[1])[17] > 58) then
				state = 67
			else
				state = 64
			end
		elseif state == 64 then
			if (t1[1])[17] < 182 then
				state = 66
			else
				state = 65
			end
		elseif state == 65 then
			(t1[1])[18] = (t1[1])[13]
			;(t1[1])[19] = (t1[1])[11]
			;(t1[1])[18]((t1[1])[19])
			state = 68
		elseif state == 66 then
			(t1[1])[18] = upv10
			;(t1[1])[19] = (t1[1])[13]
			;(t1[1])[20] = upv1[1]
			;(t1[1])[18]((t1[1])[19], (t1[1])[20])
			state = 58
		elseif state == 67 then
			(t1[1])[18] = upv6
			;(t1[1])[20] = upv1[112]
			;(t1[1])[18]((t1[1])[19], (t1[1])[20])
			state = 58
		elseif state == 68 then
			(t1[1])[14] = upv8
			;(t1[1])[15] = upv1[113]
			;(t1[1])[15] = (t1[1])[11][(t1[1])[15]]
			;(t1[1])[14]((t1[1])[15])
			error("devirt: symbolic generic for (at 0:272)")
		elseif state == 69 then
			(t1[1])[12] = 108
			;(t1[1])[13] = upv8
			;(t1[1])[14] = (t1[1])[10]
			;(t1[1])[13]((t1[1])[14])
			state = 56
		elseif state == 70 then
			if (t1[1])[9] < 113 then
				state = 71
			else
				state = 73
			end
		elseif state == 71 then
			if not ((t1[1])[9] > 104) then
				state = 73
			else
				state = 72
			end
		elseif state == 72 then
			(t1[1])[9] = 104
			;(t1[1])[10] = upv7
			;(t1[1])[11] = (t1[1])[5]
			;(t1[1])[12] = (t1[1])[6]
			;(t1[1])[10]((t1[1])[11], (t1[1])[12])
			;(t1[1])[10] = upv9
			;(t1[1])[11] = (t1[1])[5] == (t1[1])[6]
			;(t1[1])[10]((t1[1])[11])
			;(t1[1])[10] = upv1[110]
			;(t1[1])[7] = (t1[1])[5][(t1[1])[10]]
			state = 47
		elseif state == 73 then
			if not ((t1[1])[9] > 90) then
				state = 47
			else
				state = 74
			end
		elseif state == 74 then
			if (t1[1])[9] < 109 then
				state = 75
			else
				state = 47
			end
		elseif state == 75 then
			(t1[1])[10] = upv1[110]
			;(t1[1])[8] = (t1[1])[5][(t1[1])[10]]
			;(t1[1])[10] = upv6
			;(t1[1])[11] = (t1[1])[7]
			;(t1[1])[12] = upv1[110]
			;(t1[1])[10]((t1[1])[11], (t1[1])[12])
			;(t1[1])[9] = 39
			state = 47
		elseif state == 76 then
			(t1[1])[9] = 90
			;(t1[1])[10] = upv6
			;(t1[1])[11] = (t1[1])[8]
			;(t1[1])[12] = upv1[110]
			;(t1[1])[10]((t1[1])[11], (t1[1])[12])
			state = 47
		elseif state == 77 then
			(t1[1])[4] = upv0
			;(t1[1])[5] = upv1[104]
			;(t1[1])[6] = upv3
			;(t1[1])[7] = (t1[1])[1]
			;(t1[1])[6] = (t1[1])[6]((t1[1])[7])
			;(t1[1])[4]((t1[1])[5], (t1[1])[6])
			;(t1[1])[3] = 106
			state = 2
		elseif state == 78 then
			(t1[1])[4] = upv0
			;(t1[1])[5] = upv1[103]
			;(t1[1])[6] = upv2
			;(t1[1])[7] = (t1[1])[1]
			;(t1[1])[6] = (t1[1])[6]((t1[1])[7])
			;(t1[1])[4]((t1[1])[5], (t1[1])[6])
			;(t1[1])[3] = 65
			state = 2
		end
	end
end

-- proto 49: vm sequence 23, 0 opcodes
local function proto_49()
	(t1[1])[1] = upv1[46]
	upv0 = (t1[1])[1]
	error("devirt: symbolic generic for (at 0:6)")
end

-- proto 20: vm sequence 24, 0 opcodes
local function proto_20()
	(t1[1])[1] = upv1[105]
	;(t1[1])[2] = upv2
	upv0[(t1[1])[1]] = (t1[1])[2]
	error("devirt: symbolic generic for (at 0:7)")
end

-- proto 21: vm sequence 25, 0 opcodes
local function proto_21()
	(t1[1])[1] = (t2[2])[1]
	;(t1[1])[2] = upv0[1]
	;(t1[1])[3] = upv0[1]
	;(t1[1])[4] = upv0[1]
	;(t1[1])[5] = upv0[1]
	;(t1[1])[6] = 63
	;(t1[1])[7] = 88
	;(t1[1])[8] = 25
	local exitTo9 = nil
	local v

	while true do
		if d_1 <= 0 then
			exitTo9 = 1
			break
		else
			if h_1 <= E_1 then
				(t1[1])[9] = h_1

				if (t1[1])[9] == 88 then
					(t1[1])[10] = upv3
					;(t1[1])[11] = (t1[1])[1]
					;(t1[1])[12] = upv0[132]

					v = table.pack(((nil --[[ constant not decoded ]])[56]((t1[1])[10]((nil --[[ constant not decoded ]])[26](t1[1], 12, 11)))))
					;(t1[1])[10] = (v[2])[1]
					;(t1[1])[11] = (v[2])[2]
					;(t1[1])[4] = (t1[1])[10]
					;(t1[1])[5] = (t1[1])[11]
				else
					(t1[1])[10] = upv1
					;(t1[1])[12] = upv0[132]
					;(t1[1])[10] = (t1[1])[10]((t1[1])[11], (t1[1])[12])
					;(t1[1])[2] = (t1[1])[10]
					;(t1[1])[10] = upv2
					;(t1[1])[11] = (t1[1])[1]
					;(t1[1])[12] = upv0[132]
					;(t1[1])[10] = (t1[1])[10]((t1[1])[11], (t1[1])[12])
					;(t1[1])[10] = (t1[1])[10]()
					;(t1[1])[3] = (t1[1])[10]
				end

				continue
			end

			break
		end
	end

	if exitTo9 == 1 then
		if not (h_1 >= E_1) then
			if not (t1[1])[4] then
				(t1[1])[6] = upv4
				;(t1[1])[6]()
			end
		else
			(t1[1])[9] = h_1
			local exitTo10 = nil

			while true do
				if (t1[1])[9] == 88 then
					(t1[1])[10] = upv3
					;(t1[1])[11] = (t1[1])[1]
					;(t1[1])[12] = upv0[132]

					local v2 = table.pack((nil --[[ constant not decoded ]])[56]((t1[1])[10]((nil --[[ constant not decoded ]])[26](t1[1], 12, 11))))
					;(t1[1])[10] = (v2[2])[1]
					;(t1[1])[11] = (v2[2])[2]
					;(t1[1])[4] = (t1[1])[10]
					;(t1[1])[5] = (t1[1])[11]
					local exitTo = nil

					while true do
						if d_1 <= 0 then
							exitTo = 1
							break
						else
							if h_1 <= E_1 then
								(t1[1])[9] = h_1

								if (t1[1])[9] == 88 then
									(t1[1])[10] = upv3
									;(t1[1])[11] = (t1[1])[1]
									;(t1[1])[12] = upv0[132]

									local v3 = table.pack((nil --[[ constant not decoded ]])[56]((t1[1])[10]((nil --[[ constant not decoded ]])[26](t1[1], 12, 11))))
									;(t1[1])[10] = (v3[2])[1]
									;(t1[1])[11] = (v3[2])[2]
									;(t1[1])[4] = (t1[1])[10]
									;(t1[1])[5] = (t1[1])[11]
								else
									(t1[1])[10] = upv1
									;(t1[1])[12] = upv0[132]
									;(t1[1])[10] = (t1[1])[10]((t1[1])[11], (t1[1])[12])
									;(t1[1])[2] = (t1[1])[10]
									;(t1[1])[10] = upv2
									;(t1[1])[11] = (t1[1])[1]
									;(t1[1])[12] = upv0[132]
									;(t1[1])[10] = (t1[1])[10]((t1[1])[11], (t1[1])[12])
									;(t1[1])[10] = (t1[1])[10]()
									;(t1[1])[3] = (t1[1])[10]
								end

								continue
							end

							break
						end
					end

					if exitTo == 1 then
						if not (h_1 >= E_1) then
							exitTo10 = 3
							break
						else
							(t1[1])[9] = h_1
						end
					else
						exitTo10 = 2
						break
					end
				else
					(t1[1])[10] = upv1
					;(t1[1])[12] = upv0[132]
					;(t1[1])[10] = (t1[1])[10]((t1[1])[11], (t1[1])[12])
					;(t1[1])[2] = (t1[1])[10]
					;(t1[1])[10] = upv2
					;(t1[1])[11] = (t1[1])[1]
					;(t1[1])[12] = upv0[132]
					;(t1[1])[10] = (t1[1])[10]((t1[1])[11], (t1[1])[12])
					;(t1[1])[10] = (t1[1])[10]()
					;(t1[1])[3] = (t1[1])[10]
					local exitTo2 = nil

					while true do
						if d_1 <= 0 then
							exitTo2 = 1
							break
						else
							if h_1 <= E_1 then
								(t1[1])[9] = h_1

								if (t1[1])[9] == 88 then
									(t1[1])[10] = upv3
									;(t1[1])[11] = (t1[1])[1]
									;(t1[1])[12] = upv0[132]

									local v2 = table.pack((nil --[[ constant not decoded ]])[56]((t1[1])[10]((nil --[[ constant not decoded ]])[26](t1[1], 12, 11))))
									;(t1[1])[10] = (v2[2])[1]
									;(t1[1])[11] = (v2[2])[2]
									;(t1[1])[4] = (t1[1])[10]
									;(t1[1])[5] = (t1[1])[11]
								else
									(t1[1])[10] = upv1
									;(t1[1])[12] = upv0[132]
									;(t1[1])[10] = (t1[1])[10]((t1[1])[11], (t1[1])[12])
									;(t1[1])[2] = (t1[1])[10]
									;(t1[1])[10] = upv2
									;(t1[1])[11] = (t1[1])[1]
									;(t1[1])[12] = upv0[132]
									;(t1[1])[10] = (t1[1])[10]((t1[1])[11], (t1[1])[12])
									;(t1[1])[10] = (t1[1])[10]()
									;(t1[1])[3] = (t1[1])[10]
								end

								continue
							end

							break
						end
					end

					if exitTo2 == 1 then
						if not (h_1 >= E_1) then
							exitTo10 = 1
							break
						else
							(t1[1])[9] = h_1
							continue
						end
					end

					break
				end
			end

			if exitTo10 == 1 then
				if not (t1[1])[4] then
					(t1[1])[6] = upv4
					;(t1[1])[6]()
				end
			elseif exitTo10 == 2 then
				if not (t1[1])[4] then
					(t1[1])[6] = upv4
					;(t1[1])[6]()
				end
			elseif exitTo10 == 3 then
				if not (t1[1])[4] then
					(t1[1])[6] = upv4
					;(t1[1])[6]()
				end
			elseif not (t1[1])[4] then
				(t1[1])[6] = upv4
				;(t1[1])[6]()
			end
		end
	elseif not (t1[1])[4] then
		(t1[1])[6] = upv4
		;(t1[1])[6]()
	end

	if not (t1[1])[5] then
		(t1[1])[6] = upv4
		;(t1[1])[6]()
	end
	;(t1[1])[6] = upv5
	;(t1[1])[7] = (t1[1])[1]
	;(t1[1])[8] = (t1[1])[4] + 1
	;(t1[1])[9] = (t1[1])[5] - 1
	;(t1[1])[6] = (t1[1])[6]((nil --[[ constant not decoded ]])[26](t1[1], 9, 7))
	;(t1[1])[7] = upv0[1]
	;(t1[1])[8] = upv0[1]
	;(t1[1])[9] = upv0[1]
	;(t1[1])[10] = 17

	while true do
		if (t1[1])[10] > 17 then
			if (t1[1])[10] < 78 then
				break
			end
		end

		if (t1[1])[10] < 107 then
			if (t1[1])[10] > 60 then
				if not (t1[1])[3] then
					(t1[1])[11] = upv4
					;(t1[1])[11]()
				end
				;(t1[1])[9] = (t1[1])[3] + 0
				;(t1[1])[10] = 111

				while (t1[1])[10] ~= 121 do
					if (t1[1])[10] == 2 then
						(t1[1])[10] = 121

						if not (t1[1])[8] then
							(t1[1])[11] = upv4
							;(t1[1])[11]()
						end
					elseif (t1[1])[10] == 111 then
						if not (t1[1])[6] then
							(t1[1])[11] = upv4
							;(t1[1])[11]()
						end
						;(t1[1])[10] = 2
					end
				end

				if not (t1[1])[7] then
					(t1[1])[11] = upv4
					;(t1[1])[11]()
				end
				;(t1[1])[11] = upv0[1]
				;(t1[1])[12] = upv0[1]
				;(t1[1])[13] = upv0[1]
				;(t1[1])[10] = 36

				while true do
					if (t1[1])[10] <= 51 then
						if (t1[1])[10] == 36 then
							(t1[1])[11] = (t1[1])[2] + 0
							;(t1[1])[10] = 51
						else
							(t1[1])[12] = (t1[1])[6] + 0
							;(t1[1])[10] = 118
						end

						continue
					end

					if (t1[1])[10] ~= 93 then
						(t1[1])[13] = (t1[1])[8] + 0
						;(t1[1])[10] = 93
						continue
					end

					break
				end
				;(t1[1])[14] = upv9
				;(t1[1])[15] = (t1[1])[2]
				;(t1[1])[16] = (t1[1])[3]
				;(t1[1])[14]((t1[1])[15], (t1[1])[16])
				;(t1[1])[14] = upv0[1]
				;(t1[1])[16] = 614
				;(t1[1])[17] = 126
				local exitTo3 = nil

				while true do
					if d_1 <= 0 then
						exitTo3 = 1
						break
					else
						if h_1 <= E_1 then
							(t1[1])[18] = h_1

							if (t1[1])[18] == 107 then
								(t1[1])[19] = upv9
								;(t1[1])[20] = (t1[1])[3]
								;(t1[1])[21] = (t1[1])[6]
								;(t1[1])[19]((t1[1])[20], (t1[1])[21])
								continue
							elseif (t1[1])[18] == 485 then
								(t1[1])[19] = upv9
								;(t1[1])[21] = (t1[1])[7]
								;(t1[1])[19]((t1[1])[20], (t1[1])[21])
								;(t1[1])[19] = upv9
								;(t1[1])[20] = (t1[1])[11]
								;(t1[1])[21] = (t1[1])[9]
								;(t1[1])[19]((t1[1])[20], (t1[1])[21])
								continue
							elseif (t1[1])[18] == 359 then
								(t1[1])[19] = upv9
								;(t1[1])[20] = (t1[1])[6]
								;(t1[1])[21] = (t1[1])[8]
								;(t1[1])[19]((t1[1])[20], (t1[1])[21])
								continue
							elseif (t1[1])[18] == 611 then
								exitTo3 = 2
								break
							else
								if (t1[1])[18] == 233 then
									(t1[1])[14] = (t1[1])[7] + 0
								end

								continue
							end
						end

						break
					end
				end

				if exitTo3 == 1 then
					if h_1 >= E_1 then
						(t1[1])[18] = h_1

						while true do
							if (t1[1])[18] == 107 then
								(t1[1])[19] = upv9
								;(t1[1])[20] = (t1[1])[3]
								;(t1[1])[21] = (t1[1])[6]
								;(t1[1])[19]((t1[1])[20], (t1[1])[21])
								local exitTo4 = nil

								while true do
									if d_1 <= 0 then
										exitTo4 = 1
										break
									else
										if h_1 <= E_1 then
											(t1[1])[18] = h_1

											if (t1[1])[18] == 107 then
												(t1[1])[19] = upv9
												;(t1[1])[20] = (t1[1])[3]
												;(t1[1])[21] = (t1[1])[6]
												;(t1[1])[19]((t1[1])[20], (t1[1])[21])
												continue
											elseif (t1[1])[18] == 485 then
												(t1[1])[19] = upv9
												;(t1[1])[21] = (t1[1])[7]
												;(t1[1])[19]((t1[1])[20], (t1[1])[21])
												;(t1[1])[19] = upv9
												;(t1[1])[20] = (t1[1])[11]
												;(t1[1])[21] = (t1[1])[9]
												;(t1[1])[19]((t1[1])[20], (t1[1])[21])
												continue
											elseif (t1[1])[18] == 359 then
												(t1[1])[19] = upv9
												;(t1[1])[20] = (t1[1])[6]
												;(t1[1])[21] = (t1[1])[8]
												;(t1[1])[19]((t1[1])[20], (t1[1])[21])
												continue
											elseif (t1[1])[18] == 611 then
												exitTo4 = 2
												break
											else
												if (t1[1])[18] == 233 then
													(t1[1])[14] = (t1[1])[7] + 0
												end

												continue
											end
										end

										break
									end
								end

								if exitTo4 == 1 then
									if h_1 >= E_1 then
										(t1[1])[18] = h_1
										continue
									end
								else
									if exitTo4 == 2 then
										(t1[1])[19] = upv9
										;(t1[1])[20] = (t1[1])[9]
										;(t1[1])[21] = (t1[1])[12]
										;(t1[1])[19]((t1[1])[20], (t1[1])[21])
									end

									break
								end

								break
							else
								if (t1[1])[18] == 485 then
									(t1[1])[19] = upv9
									;(t1[1])[21] = (t1[1])[7]
									;(t1[1])[19]((t1[1])[20], (t1[1])[21])
									;(t1[1])[19] = upv9
									;(t1[1])[20] = (t1[1])[11]
									;(t1[1])[21] = (t1[1])[9]
									;(t1[1])[19]((t1[1])[20], (t1[1])[21])
									local exitTo5 = nil

									while true do
										if d_1 <= 0 then
											exitTo5 = 1
											break
										else
											if h_1 <= E_1 then
												(t1[1])[18] = h_1

												if (t1[1])[18] == 107 then
													(t1[1])[19] = upv9
													;(t1[1])[20] = (t1[1])[3]
													;(t1[1])[21] = (t1[1])[6]
													;(t1[1])[19]((t1[1])[20], (t1[1])[21])
													continue
												elseif (t1[1])[18] == 485 then
													(t1[1])[19] = upv9
													;(t1[1])[21] = (t1[1])[7]
													;(t1[1])[19]((t1[1])[20], (t1[1])[21])
													;(t1[1])[19] = upv9
													;(t1[1])[20] = (t1[1])[11]
													;(t1[1])[21] = (t1[1])[9]
													;(t1[1])[19]((t1[1])[20], (t1[1])[21])
													continue
												elseif (t1[1])[18] == 359 then
													(t1[1])[19] = upv9
													;(t1[1])[20] = (t1[1])[6]
													;(t1[1])[21] = (t1[1])[8]
													;(t1[1])[19]((t1[1])[20], (t1[1])[21])
													continue
												elseif (t1[1])[18] == 611 then
													exitTo5 = 2
													break
												else
													if (t1[1])[18] == 233 then
														(t1[1])[14] = (t1[1])[7] + 0
													end

													continue
												end
											end

											break
										end
									end

									if exitTo5 == 1 then
										if h_1 >= E_1 then
											(t1[1])[18] = h_1
											continue
										end
									else
										if exitTo5 == 2 then
											(t1[1])[19] = upv9
											;(t1[1])[20] = (t1[1])[9]
											;(t1[1])[21] = (t1[1])[12]
											;(t1[1])[19]((t1[1])[20], (t1[1])[21])
										end

										break
									end
								elseif (t1[1])[18] == 359 then
									(t1[1])[19] = upv9
									;(t1[1])[20] = (t1[1])[6]
									;(t1[1])[21] = (t1[1])[8]
									;(t1[1])[19]((t1[1])[20], (t1[1])[21])
									local exitTo6 = nil

									while true do
										if d_1 <= 0 then
											exitTo6 = 1
											break
										else
											if h_1 <= E_1 then
												(t1[1])[18] = h_1

												if (t1[1])[18] == 107 then
													(t1[1])[19] = upv9
													;(t1[1])[20] = (t1[1])[3]
													;(t1[1])[21] = (t1[1])[6]
													;(t1[1])[19]((t1[1])[20], (t1[1])[21])
													continue
												elseif (t1[1])[18] == 485 then
													(t1[1])[19] = upv9
													;(t1[1])[21] = (t1[1])[7]
													;(t1[1])[19]((t1[1])[20], (t1[1])[21])
													;(t1[1])[19] = upv9
													;(t1[1])[20] = (t1[1])[11]
													;(t1[1])[21] = (t1[1])[9]
													;(t1[1])[19]((t1[1])[20], (t1[1])[21])
													continue
												elseif (t1[1])[18] == 359 then
													(t1[1])[19] = upv9
													;(t1[1])[20] = (t1[1])[6]
													;(t1[1])[21] = (t1[1])[8]
													;(t1[1])[19]((t1[1])[20], (t1[1])[21])
													continue
												elseif (t1[1])[18] == 611 then
													exitTo6 = 2
													break
												else
													if (t1[1])[18] == 233 then
														(t1[1])[14] = (t1[1])[7] + 0
													end

													continue
												end
											end

											break
										end
									end

									if exitTo6 == 1 then
										if h_1 >= E_1 then
											(t1[1])[18] = h_1
											continue
										end
									else
										if exitTo6 == 2 then
											(t1[1])[19] = upv9
											;(t1[1])[20] = (t1[1])[9]
											;(t1[1])[21] = (t1[1])[12]
											;(t1[1])[19]((t1[1])[20], (t1[1])[21])
										end

										break
									end
								elseif (t1[1])[18] == 611 then
									(t1[1])[19] = upv9
									;(t1[1])[20] = (t1[1])[9]
									;(t1[1])[21] = (t1[1])[12]
									;(t1[1])[19]((t1[1])[20], (t1[1])[21])
									break
								elseif (t1[1])[18] == 233 then
									(t1[1])[14] = (t1[1])[7] + 0
									local exitTo7 = nil

									while true do
										if d_1 <= 0 then
											exitTo7 = 1
											break
										else
											if h_1 <= E_1 then
												(t1[1])[18] = h_1

												if (t1[1])[18] == 107 then
													(t1[1])[19] = upv9
													;(t1[1])[20] = (t1[1])[3]
													;(t1[1])[21] = (t1[1])[6]
													;(t1[1])[19]((t1[1])[20], (t1[1])[21])
													continue
												elseif (t1[1])[18] == 485 then
													(t1[1])[19] = upv9
													;(t1[1])[21] = (t1[1])[7]
													;(t1[1])[19]((t1[1])[20], (t1[1])[21])
													;(t1[1])[19] = upv9
													;(t1[1])[20] = (t1[1])[11]
													;(t1[1])[21] = (t1[1])[9]
													;(t1[1])[19]((t1[1])[20], (t1[1])[21])
													continue
												elseif (t1[1])[18] == 359 then
													(t1[1])[19] = upv9
													;(t1[1])[20] = (t1[1])[6]
													;(t1[1])[21] = (t1[1])[8]
													;(t1[1])[19]((t1[1])[20], (t1[1])[21])
													continue
												elseif (t1[1])[18] == 611 then
													exitTo7 = 2
													break
												else
													if (t1[1])[18] == 233 then
														(t1[1])[14] = (t1[1])[7] + 0
													end

													continue
												end
											end

											break
										end
									end

									if exitTo7 == 1 then
										if h_1 >= E_1 then
											(t1[1])[18] = h_1
											continue
										end
									else
										if exitTo7 == 2 then
											(t1[1])[19] = upv9
											;(t1[1])[20] = (t1[1])[9]
											;(t1[1])[21] = (t1[1])[12]
											;(t1[1])[19]((t1[1])[20], (t1[1])[21])
										end

										break
									end
								else
									local exitTo8 = nil

									while true do
										if d_1 <= 0 then
											exitTo8 = 1
											break
										else
											if h_1 <= E_1 then
												(t1[1])[18] = h_1

												if (t1[1])[18] == 107 then
													(t1[1])[19] = upv9
													;(t1[1])[20] = (t1[1])[3]
													;(t1[1])[21] = (t1[1])[6]
													;(t1[1])[19]((t1[1])[20], (t1[1])[21])
													continue
												elseif (t1[1])[18] == 485 then
													(t1[1])[19] = upv9
													;(t1[1])[21] = (t1[1])[7]
													;(t1[1])[19]((t1[1])[20], (t1[1])[21])
													;(t1[1])[19] = upv9
													;(t1[1])[20] = (t1[1])[11]
													;(t1[1])[21] = (t1[1])[9]
													;(t1[1])[19]((t1[1])[20], (t1[1])[21])
													continue
												elseif (t1[1])[18] == 359 then
													(t1[1])[19] = upv9
													;(t1[1])[20] = (t1[1])[6]
													;(t1[1])[21] = (t1[1])[8]
													;(t1[1])[19]((t1[1])[20], (t1[1])[21])
													continue
												elseif (t1[1])[18] == 611 then
													exitTo8 = 2
													break
												else
													if (t1[1])[18] == 233 then
														(t1[1])[14] = (t1[1])[7] + 0
													end

													continue
												end
											end

											break
										end
									end

									if exitTo8 == 1 then
										if h_1 >= E_1 then
											(t1[1])[18] = h_1
											continue
										end
									else
										if exitTo8 == 2 then
											(t1[1])[19] = upv9
											;(t1[1])[20] = (t1[1])[9]
											;(t1[1])[21] = (t1[1])[12]
											;(t1[1])[19]((t1[1])[20], (t1[1])[21])
										end

										break
									end
								end

								break
							end
						end
					end
				elseif exitTo3 == 2 then
					(t1[1])[19] = upv9
					;(t1[1])[20] = (t1[1])[9]
					;(t1[1])[21] = (t1[1])[12]
					;(t1[1])[19]((t1[1])[20], (t1[1])[21])
				end
				;(t1[1])[15] = 5
				;(t1[1])[16] = 218
				;(t1[1])[17] = 57

				while true do
					if d_1 <= 0 then
						if not (h_1 >= E_1) then
							error("devirt: symbolic generic for (at 0:74)")
						end
						;(t1[1])[18] = h_1
					else
						if not (h_1 <= E_1) then
							error("devirt: symbolic generic for (at 0:74)")
						end
						;(t1[1])[18] = h_1
					end

					if (t1[1])[18] < 62 then
						(t1[1])[19] = upv9
						;(t1[1])[21] = (t1[1])[13]
						;(t1[1])[19]((t1[1])[20], (t1[1])[21])
						continue
					end

					if (t1[1])[18] < 119 then
						if (t1[1])[18] > 5 then
							(t1[1])[19] = upv9
							;(t1[1])[20] = (t1[1])[13]
							;(t1[1])[21] = (t1[1])[14]
							;(t1[1])[19]((t1[1])[20], (t1[1])[21])
							continue
						end
					end

					if not ((t1[1])[18] > 62) then
						continue
					end
					break
				end
				;(t1[1])[19] = (t1[1])[11]
				error("devirt: symbolic generic for (at 0:176)")
			end
		end

		if (t1[1])[10] < 60 then
			(t1[1])[10] = 60
			;(t1[1])[7] = upv0[1]
		elseif (t1[1])[10] > 78 then
			if not (t1[1])[2] then
				(t1[1])[11] = upv4
				;(t1[1])[11]()
			end
			;(t1[1])[10] = 78
		end
	end
	;(t1[1])[10] = 107
	;(t1[1])[11] = upv6
	;(t1[1])[12] = upv7
	;(t1[1])[13] = (t1[1])[1]
	;(t1[1])[14] = (t1[1])[4] + 1
	;(t1[1])[15] = (t1[1])[5] - 1
	error("devirt: numeric for with symbolic bounds (at 0:360)")
end

-- proto 22: vm sequence 26, 0 opcodes
local function proto_22()
	(t1[1])[1] = (t2[2])[1]
	upv0 = (t1[1])[1]
	error("devirt: symbolic generic for (at 0:4)")
end

-- proto 26: vm sequence 27, 0 opcodes
local function proto_26()
	(t1[1])[1] = (t2[2])[1]
	;(t1[1])[2] = (t1[1])[1][1]
	;(t1[1])[3] = (t1[1])[1][2]

	if (t1[1])[3] == "boolean" then
		(t1[1])[2] = not (t1[1])[2]
	elseif (t1[1])[3] == "string" then
		(t1[1])[4] = upv0
		;(t1[1])[5] = (t1[1])[2]
		;(t1[1])[6] = 1
		;(t1[1])[7] = 1
		;(t1[1])[4] = (t1[1])[4]((nil --[[ constant not decoded ]])[26](t1[1], 7, 5))
		;(t1[1])[4] = (t1[1])[4] ~= 0

		if not (t1[1])[4] then
			(t1[1])[5] = upv3
			;(t1[1])[6] = (t1[1])[2]
			;(t1[1])[7] = 2
			;(t1[1])[5] = (t1[1])[5]((t1[1])[6], (t1[1])[7])
			;(t1[1])[2] = (t1[1])[5]
		else
			(t1[1])[5] = upv0
			;(t1[1])[6] = (t1[1])[2]
			;(t1[1])[7] = 2
			;(t1[1])[8] = 2
			;(t1[1])[5] = (t1[1])[5]((nil --[[ constant not decoded ]])[26](t1[1], 8, 6))
			;(t1[1])[6] = 209 * (t1[1])[5]
			;(t1[1])[7] = upv1
			;(t1[1])[6] = (t1[1])[6] + (t1[1])[7]
			;(t1[1])[5] = (t1[1])[6] % 256
			;(t1[1])[6] = #(t1[1])[2]

			if not ((t1[1])[6] >= 600) then
				(t1[1])[7] = ""
				;(t1[1])[9] = (t1[1])[6]
				;(t1[1])[10] = 1

				while true do
					if d_1 <= 0 then
						if h_1 >= E_1 then
							(t1[1])[11] = h_1
							;(t1[1])[12] = upv0
							;(t1[1])[13] = (t1[1])[2]
							;(t1[1])[14] = (t1[1])[11]
							;(t1[1])[12] = (t1[1])[12]((t1[1])[13], (t1[1])[14])
							;(t1[1])[12] = (nil --[[ constant not decoded ]])[45]((t1[1])[12], (t1[1])[5])
							;(t1[1])[12] = upv2[(t1[1])[12]]
							;(t1[1])[7] = (t1[1])[7] .. (t1[1])[12]
							;(t1[1])[12] = 209 * (t1[1])[5]
							;(t1[1])[13] = upv1
							;(t1[1])[12] = (t1[1])[12] + (t1[1])[13]
							;(t1[1])[5] = (t1[1])[12] % 256
							continue
						end

						break
					else
						if h_1 <= E_1 then
							(t1[1])[11] = h_1
							;(t1[1])[12] = upv0
							;(t1[1])[13] = (t1[1])[2]
							;(t1[1])[14] = (t1[1])[11]
							;(t1[1])[12] = (t1[1])[12]((t1[1])[13], (t1[1])[14])
							;(t1[1])[12] = (nil --[[ constant not decoded ]])[45]((t1[1])[12], (t1[1])[5])
							;(t1[1])[12] = upv2[(t1[1])[12]]
							;(t1[1])[7] = (t1[1])[7] .. (t1[1])[12]
							;(t1[1])[12] = 209 * (t1[1])[5]
							;(t1[1])[13] = upv1
							;(t1[1])[12] = (t1[1])[12] + (t1[1])[13]
							;(t1[1])[5] = (t1[1])[12] % 256
							continue
						end

						break
					end
				end
				;(t1[1])[2] = (t1[1])[7]
			else
				(t1[1])[7] = {}
				;(t1[1])[9] = #(t1[1])[2]
				;(t1[1])[10] = 1

				while true do
					if d_1 <= 0 then
						if h_1 >= E_1 then
							(t1[1])[11] = h_1
							;(t1[1])[31] = {
								0,
								0,
								0,
								0,
								7,
								200,
								8,
								237,
								0,
								10,
								0,
								0,
								0,
								28,
								115,
								5,
								33,
								0,
								0,
								0,
								0,
								0,
								0,
								12,
								7,
								9,
								10,
								0,
								0,
								0,
								5,
								0,
								7,
								0,
								0,
								2,
								0,
								0,
								6,
								9,
								10,
								81,
								0,
								0,
								0,
								0,
								0,
								150,
								0,
								0,
								4,
								0,
								0,
								2,
								3,
								21,
								0,
								8,
								0,
								0,
								0,
								89,
								32,
								47,
								33,
								0,
								0,
								0,
								0,
								0,
								0,
								0,
								51,
								6,
								8,
								104,
								33,
								124,
								0,
								0,
								0,
								0,
								55,
								32,
								7,
								33,
								0,
								12,
								13,
								0,
								0,
								0,
								8,
								0,
								0,
								0,
								43,
								105,
								842,
								33,
								0,
								5,
								0,
								7,
								8,
								5,
								6,
								0,
								11,
								0,
								12,
								7,
								12,
								13,
								12,
								12,
								0,
								7,
								13,
								7,
								0,
								8,
								0,
								2,
								0,
								0,
								12,
								0,
								0,
								0,
								5,
								0,
								7,
								6,
								6,
								6,
								1070,
								0,
								0,
								0,
								8,
								0,
								7,
								4,
								4,
								0,
								0,
								222,
								0,
								0,
								2,
								0,
								0,
								0,
								0,
								614,
								4,
								891,
								33,
								41,
								0,
								0,
								7,
								12,
								13,
								12,
								12,
								0,
								89,
								0,
								0,
								24,
								0,
								31,
								0,
								4,
								629,
								33,
								0,
								0,
								0,
								31,
								32,
								447,
								33,
								89,
								0,
								0,
								21,
								0,
								24,
								0,
								0,
								10,
								0,
								245,
								0,
								7,
								7,
								9,
								0,
								1,
								9,
								1,
								10,
								1,
								8,
								11,
								196,
								112,
								15,
								11,
								205,
								4,
								8,
								0,
								0,
								0,
								6,
								713,
								33,
								0,
								8,
								0,
								74,
								24,
								244,
								0,
								0,
								60,
								8,
								221,
								9,
								0,
								851,
								24,
								21,
								790,
								351,
								24,
								17,
								168,
								25,
								0,
								0,
								248,
								0,
								0,
								4,
								5,
								6,
								0,
								0,
								8,
								13,
								0,
								4,
								0,
								6,
								0,
								0,
								31,
								0,
								50,
								55,
								3,
								33,
								133,
								0,
								12,
							}
							;(t1[1])[33] = {
								52,
								256,
								126,
								117,
								501,
								251,
								238,
								62,
								9,
								89,
								244,
								32,
								0,
								808,
								1002,
								58,
								26,
								50,
								173,
								2,
								248,
								195,
								94,
								12,
								12,
								89,
								6,
								43,
								24,
								161,
								3,
								6,
								6,
								0,
								19,
								89,
								248,
								180,
								121,
								89,
								89,
								89,
								22,
								22,
								0,
								1,
								50,
								32,
								149,
								228,
								0,
								247,
								0,
								89,
								6,
								854,
								123,
								0,
								125,
								32,
								0,
								60,
								60,
								224,
								26,
								101,
								0,
								2,
								248,
								0,
								0,
								32,
								65,
								65,
								942,
								6,
								26,
								28,
								256,
								32,
								0,
								0,
								314,
								314,
								699,
								26,
								28,
								6,
								0,
								14,
								15,
								252,
								89,
								168,
								0,
								32,
								952,
								952,
								54,
								26,
								147,
								0,
								6,
								6,
								6,
								4,
								5,
								132,
								0,
								46,
								12,
								7,
								5,
								1,
								13,
								5,
								244,
								12,
								89,
								13,
								23,
								0,
								139,
								0,
								248,
								66,
								0,
								13,
								14,
								0,
								12,
								110,
								1,
								7,
								5,
								2,
								6,
								49,
								260,
								0,
								7,
								168,
								89,
								4,
								32,
								30,
								170,
								11,
								3,
								248,
								2,
								248,
								28,
								0,
								0,
								87,
								87,
								753,
								26,
								123,
								57,
								171,
								13,
								5,
								1,
								13,
								5,
								37,
								35,
								138,
								101,
								959,
								234,
								0,
								0,
								882,
								91,
								26,
								87,
								1,
								0,
								0,
								3,
								447,
								26,
								179,
								38,
								0,
								0,
								0,
								233,
								152,
								224,
								89,
								121,
								778,
								179,
								12,
								108,
								89,
								92,
								8,
								89,
								9,
								6,
								10,
								11,
								23,
								120,
								226,
								2,
								129,
								69,
								11,
								11,
								108,
								32,
								0,
								27,
								363,
								26,
								195,
								92,
								197,
								26,
								87,
								999,
								152,
								0,
								59,
								241,
								62,
								2,
								193,
								24,
								157,
								24,
								136,
								24,
								791,
								24,
								62,
								16,
								126,
								57,
								362,
								47,
								44,
								62,
								1,
								62,
								46,
								0,
								13,
								13,
								162,
								0,
								5,
								89,
								142,
								32,
								0,
								0,
								431,
								431,
								412,
								26,
								0,
								39,
								319,
							}
							;(t1[1])[31][254] = 5
							;(t1[1])[33][19] = 87
							;(t1[1])[26] = nil
							;(t1[1])[27] = nil
							;(t1[1])[28] = nil
							;(t1[1])[29] = nil
							;(t1[1])[30] = nil
							;(t1[1])[31] = nil
							;(t1[1])[32] = nil
							;(t1[1])[33] = nil
							;(t1[1])[12] = (t1[1])[11] - 2
							;(t1[1])[13] = upv0
							;(t1[1])[14] = (t1[1])[2]
							;(t1[1])[15] = (t1[1])[11]
							;(t1[1])[13] = (t1[1])[13]((t1[1])[14], (t1[1])[15])
							;(t1[1])[13] = (nil --[[ constant not decoded ]])[45]((t1[1])[13], (t1[1])[8])
							;(t1[1])[13] = upv2[(t1[1])[13]]
							;(t1[1])[7][(t1[1])[12]] = (t1[1])[13]
							;(t1[1])[12] = 209 * (t1[1])[5]
							;(t1[1])[13] = upv1
							;(t1[1])[12] = (t1[1])[12] + (t1[1])[13]
							;(t1[1])[5] = (t1[1])[12] % 256
							;(t1[1])[33] = {
								52,
								256,
								126,
								117,
								501,
								251,
								238,
								62,
								9,
								89,
								244,
								32,
								0,
								808,
								1002,
								58,
								26,
								50,
								173,
								2,
								248,
								195,
								94,
								12,
								12,
								89,
								6,
								43,
								24,
								161,
								3,
								6,
								6,
								0,
								19,
								89,
								248,
								180,
								121,
								89,
								89,
								89,
								22,
								22,
								0,
								1,
								50,
								32,
								149,
								228,
								0,
								247,
								0,
								89,
								6,
								854,
								123,
								0,
								125,
								32,
								0,
								60,
								60,
								224,
								26,
								101,
								0,
								2,
								248,
								0,
								0,
								32,
								65,
								65,
								942,
								6,
								26,
								28,
								256,
								32,
								0,
								0,
								314,
								314,
								699,
								26,
								28,
								6,
								0,
								14,
								15,
								252,
								89,
								168,
								0,
								32,
								952,
								952,
								54,
								26,
								147,
								0,
								6,
								6,
								6,
								4,
								5,
								132,
								0,
								46,
								12,
								7,
								5,
								1,
								13,
								5,
								244,
								12,
								89,
								13,
								23,
								0,
								139,
								0,
								248,
								66,
								0,
								13,
								14,
								0,
								12,
								110,
								1,
								7,
								5,
								2,
								6,
								49,
								260,
								0,
								7,
								168,
								89,
								4,
								32,
								30,
								170,
								11,
								3,
								248,
								2,
								248,
								28,
								0,
								0,
								87,
								87,
								753,
								26,
								123,
								57,
								171,
								13,
								5,
								1,
								13,
								5,
								37,
								35,
								138,
								101,
								959,
								234,
								0,
								0,
								882,
								91,
								26,
								87,
								1,
								0,
								0,
								3,
								447,
								26,
								179,
								38,
								0,
								0,
								0,
								233,
								152,
								224,
								89,
								121,
								778,
								179,
								12,
								108,
								89,
								92,
								8,
								89,
								9,
								6,
								10,
								11,
								23,
								120,
								226,
								2,
								129,
								69,
								11,
								11,
								108,
								32,
								0,
								27,
								363,
								26,
								195,
								92,
								197,
								26,
								87,
								999,
								152,
								0,
								59,
								241,
								62,
								2,
								193,
								24,
								157,
								24,
								136,
								24,
								791,
								24,
								62,
								16,
								126,
								57,
								362,
								47,
								44,
								62,
								1,
								62,
								46,
								0,
								13,
								13,
								162,
								0,
								5,
								89,
								142,
								32,
								0,
								0,
								431,
								431,
								412,
								26,
								0,
								39,
								319,
							}
							;(t1[1])[31] = {
								0,
								0,
								0,
								0,
								7,
								200,
								8,
								237,
								0,
								10,
								0,
								0,
								0,
								28,
								115,
								5,
								33,
								0,
								0,
								0,
								0,
								0,
								0,
								12,
								7,
								9,
								10,
								0,
								0,
								0,
								5,
								0,
								7,
								0,
								0,
								2,
								0,
								0,
								6,
								9,
								10,
								81,
								0,
								0,
								0,
								0,
								0,
								150,
								0,
								0,
								4,
								0,
								0,
								2,
								3,
								21,
								0,
								8,
								0,
								0,
								0,
								89,
								32,
								47,
								33,
								0,
								0,
								0,
								0,
								0,
								0,
								0,
								51,
								6,
								8,
								104,
								33,
								124,
								0,
								0,
								0,
								0,
								55,
								32,
								7,
								33,
								0,
								12,
								13,
								0,
								0,
								0,
								8,
								0,
								0,
								0,
								43,
								105,
								842,
								33,
								0,
								5,
								0,
								7,
								8,
								5,
								6,
								0,
								11,
								0,
								12,
								7,
								12,
								13,
								12,
								12,
								0,
								7,
								13,
								7,
								0,
								8,
								0,
								2,
								0,
								0,
								12,
								0,
								0,
								0,
								5,
								0,
								7,
								6,
								6,
								6,
								1070,
								0,
								0,
								0,
								8,
								0,
								7,
								4,
								4,
								0,
								0,
								222,
								0,
								0,
								2,
								0,
								0,
								0,
								0,
								614,
								4,
								891,
								33,
								41,
								0,
								0,
								7,
								12,
								13,
								12,
								12,
								0,
								89,
								0,
								0,
								24,
								0,
								31,
								0,
								4,
								629,
								33,
								0,
								0,
								0,
								31,
								32,
								447,
								33,
								89,
								0,
								0,
								21,
								0,
								24,
								0,
								0,
								10,
								0,
								245,
								0,
								7,
								7,
								9,
								0,
								1,
								9,
								1,
								10,
								1,
								8,
								11,
								196,
								112,
								15,
								11,
								205,
								4,
								8,
								0,
								0,
								0,
								6,
								713,
								33,
								0,
								8,
								0,
								74,
								24,
								244,
								0,
								0,
								60,
								8,
								221,
								9,
								0,
								851,
								24,
								21,
								790,
								351,
								24,
								17,
								168,
								25,
								0,
								0,
								248,
								0,
								0,
								4,
								5,
								6,
								0,
								0,
								8,
								13,
								0,
								4,
								0,
								6,
								0,
								0,
								31,
								0,
								50,
								55,
								3,
								33,
								133,
								0,
								12,
							}
							;(t1[1])[31][39] = 0
							;(t1[1])[33][38] = 38
							continue
						end

						break
					else
						if h_1 <= E_1 then
							(t1[1])[11] = h_1
							;(t1[1])[31] = {
								0,
								0,
								0,
								0,
								7,
								200,
								8,
								237,
								0,
								10,
								0,
								0,
								0,
								28,
								115,
								5,
								33,
								0,
								0,
								0,
								0,
								0,
								0,
								12,
								7,
								9,
								10,
								0,
								0,
								0,
								5,
								0,
								7,
								0,
								0,
								2,
								0,
								0,
								6,
								9,
								10,
								81,
								0,
								0,
								0,
								0,
								0,
								150,
								0,
								0,
								4,
								0,
								0,
								2,
								3,
								21,
								0,
								8,
								0,
								0,
								0,
								89,
								32,
								47,
								33,
								0,
								0,
								0,
								0,
								0,
								0,
								0,
								51,
								6,
								8,
								104,
								33,
								124,
								0,
								0,
								0,
								0,
								55,
								32,
								7,
								33,
								0,
								12,
								13,
								0,
								0,
								0,
								8,
								0,
								0,
								0,
								43,
								105,
								842,
								33,
								0,
								5,
								0,
								7,
								8,
								5,
								6,
								0,
								11,
								0,
								12,
								7,
								12,
								13,
								12,
								12,
								0,
								7,
								13,
								7,
								0,
								8,
								0,
								2,
								0,
								0,
								12,
								0,
								0,
								0,
								5,
								0,
								7,
								6,
								6,
								6,
								1070,
								0,
								0,
								0,
								8,
								0,
								7,
								4,
								4,
								0,
								0,
								222,
								0,
								0,
								2,
								0,
								0,
								0,
								0,
								614,
								4,
								891,
								33,
								41,
								0,
								0,
								7,
								12,
								13,
								12,
								12,
								0,
								89,
								0,
								0,
								24,
								0,
								31,
								0,
								4,
								629,
								33,
								0,
								0,
								0,
								31,
								32,
								447,
								33,
								89,
								0,
								0,
								21,
								0,
								24,
								0,
								0,
								10,
								0,
								245,
								0,
								7,
								7,
								9,
								0,
								1,
								9,
								1,
								10,
								1,
								8,
								11,
								196,
								112,
								15,
								11,
								205,
								4,
								8,
								0,
								0,
								0,
								6,
								713,
								33,
								0,
								8,
								0,
								74,
								24,
								244,
								0,
								0,
								60,
								8,
								221,
								9,
								0,
								851,
								24,
								21,
								790,
								351,
								24,
								17,
								168,
								25,
								0,
								0,
								248,
								0,
								0,
								4,
								5,
								6,
								0,
								0,
								8,
								13,
								0,
								4,
								0,
								6,
								0,
								0,
								31,
								0,
								50,
								55,
								3,
								33,
								133,
								0,
								12,
							}
							;(t1[1])[33] = {
								52,
								256,
								126,
								117,
								501,
								251,
								238,
								62,
								9,
								89,
								244,
								32,
								0,
								808,
								1002,
								58,
								26,
								50,
								173,
								2,
								248,
								195,
								94,
								12,
								12,
								89,
								6,
								43,
								24,
								161,
								3,
								6,
								6,
								0,
								19,
								89,
								248,
								180,
								121,
								89,
								89,
								89,
								22,
								22,
								0,
								1,
								50,
								32,
								149,
								228,
								0,
								247,
								0,
								89,
								6,
								854,
								123,
								0,
								125,
								32,
								0,
								60,
								60,
								224,
								26,
								101,
								0,
								2,
								248,
								0,
								0,
								32,
								65,
								65,
								942,
								6,
								26,
								28,
								256,
								32,
								0,
								0,
								314,
								314,
								699,
								26,
								28,
								6,
								0,
								14,
								15,
								252,
								89,
								168,
								0,
								32,
								952,
								952,
								54,
								26,
								147,
								0,
								6,
								6,
								6,
								4,
								5,
								132,
								0,
								46,
								12,
								7,
								5,
								1,
								13,
								5,
								244,
								12,
								89,
								13,
								23,
								0,
								139,
								0,
								248,
								66,
								0,
								13,
								14,
								0,
								12,
								110,
								1,
								7,
								5,
								2,
								6,
								49,
								260,
								0,
								7,
								168,
								89,
								4,
								32,
								30,
								170,
								11,
								3,
								248,
								2,
								248,
								28,
								0,
								0,
								87,
								87,
								753,
								26,
								123,
								57,
								171,
								13,
								5,
								1,
								13,
								5,
								37,
								35,
								138,
								101,
								959,
								234,
								0,
								0,
								882,
								91,
								26,
								87,
								1,
								0,
								0,
								3,
								447,
								26,
								179,
								38,
								0,
								0,
								0,
								233,
								152,
								224,
								89,
								121,
								778,
								179,
								12,
								108,
								89,
								92,
								8,
								89,
								9,
								6,
								10,
								11,
								23,
								120,
								226,
								2,
								129,
								69,
								11,
								11,
								108,
								32,
								0,
								27,
								363,
								26,
								195,
								92,
								197,
								26,
								87,
								999,
								152,
								0,
								59,
								241,
								62,
								2,
								193,
								24,
								157,
								24,
								136,
								24,
								791,
								24,
								62,
								16,
								126,
								57,
								362,
								47,
								44,
								62,
								1,
								62,
								46,
								0,
								13,
								13,
								162,
								0,
								5,
								89,
								142,
								32,
								0,
								0,
								431,
								431,
								412,
								26,
								0,
								39,
								319,
							}
							;(t1[1])[31][254] = 5
							;(t1[1])[33][19] = 87
							;(t1[1])[26] = nil
							;(t1[1])[27] = nil
							;(t1[1])[28] = nil
							;(t1[1])[29] = nil
							;(t1[1])[30] = nil
							;(t1[1])[31] = nil
							;(t1[1])[32] = nil
							;(t1[1])[33] = nil
							;(t1[1])[12] = (t1[1])[11] - 2
							;(t1[1])[13] = upv0
							;(t1[1])[14] = (t1[1])[2]
							;(t1[1])[15] = (t1[1])[11]
							;(t1[1])[13] = (t1[1])[13]((t1[1])[14], (t1[1])[15])
							;(t1[1])[13] = (nil --[[ constant not decoded ]])[45]((t1[1])[13], (t1[1])[8])
							;(t1[1])[13] = upv2[(t1[1])[13]]
							;(t1[1])[7][(t1[1])[12]] = (t1[1])[13]
							;(t1[1])[12] = 209 * (t1[1])[5]
							;(t1[1])[13] = upv1
							;(t1[1])[12] = (t1[1])[12] + (t1[1])[13]
							;(t1[1])[5] = (t1[1])[12] % 256
							;(t1[1])[33] = {
								52,
								256,
								126,
								117,
								501,
								251,
								238,
								62,
								9,
								89,
								244,
								32,
								0,
								808,
								1002,
								58,
								26,
								50,
								173,
								2,
								248,
								195,
								94,
								12,
								12,
								89,
								6,
								43,
								24,
								161,
								3,
								6,
								6,
								0,
								19,
								89,
								248,
								180,
								121,
								89,
								89,
								89,
								22,
								22,
								0,
								1,
								50,
								32,
								149,
								228,
								0,
								247,
								0,
								89,
								6,
								854,
								123,
								0,
								125,
								32,
								0,
								60,
								60,
								224,
								26,
								101,
								0,
								2,
								248,
								0,
								0,
								32,
								65,
								65,
								942,
								6,
								26,
								28,
								256,
								32,
								0,
								0,
								314,
								314,
								699,
								26,
								28,
								6,
								0,
								14,
								15,
								252,
								89,
								168,
								0,
								32,
								952,
								952,
								54,
								26,
								147,
								0,
								6,
								6,
								6,
								4,
								5,
								132,
								0,
								46,
								12,
								7,
								5,
								1,
								13,
								5,
								244,
								12,
								89,
								13,
								23,
								0,
								139,
								0,
								248,
								66,
								0,
								13,
								14,
								0,
								12,
								110,
								1,
								7,
								5,
								2,
								6,
								49,
								260,
								0,
								7,
								168,
								89,
								4,
								32,
								30,
								170,
								11,
								3,
								248,
								2,
								248,
								28,
								0,
								0,
								87,
								87,
								753,
								26,
								123,
								57,
								171,
								13,
								5,
								1,
								13,
								5,
								37,
								35,
								138,
								101,
								959,
								234,
								0,
								0,
								882,
								91,
								26,
								87,
								1,
								0,
								0,
								3,
								447,
								26,
								179,
								38,
								0,
								0,
								0,
								233,
								152,
								224,
								89,
								121,
								778,
								179,
								12,
								108,
								89,
								92,
								8,
								89,
								9,
								6,
								10,
								11,
								23,
								120,
								226,
								2,
								129,
								69,
								11,
								11,
								108,
								32,
								0,
								27,
								363,
								26,
								195,
								92,
								197,
								26,
								87,
								999,
								152,
								0,
								59,
								241,
								62,
								2,
								193,
								24,
								157,
								24,
								136,
								24,
								791,
								24,
								62,
								16,
								126,
								57,
								362,
								47,
								44,
								62,
								1,
								62,
								46,
								0,
								13,
								13,
								162,
								0,
								5,
								89,
								142,
								32,
								0,
								0,
								431,
								431,
								412,
								26,
								0,
								39,
								319,
							}
							;(t1[1])[31] = {
								0,
								0,
								0,
								0,
								7,
								200,
								8,
								237,
								0,
								10,
								0,
								0,
								0,
								28,
								115,
								5,
								33,
								0,
								0,
								0,
								0,
								0,
								0,
								12,
								7,
								9,
								10,
								0,
								0,
								0,
								5,
								0,
								7,
								0,
								0,
								2,
								0,
								0,
								6,
								9,
								10,
								81,
								0,
								0,
								0,
								0,
								0,
								150,
								0,
								0,
								4,
								0,
								0,
								2,
								3,
								21,
								0,
								8,
								0,
								0,
								0,
								89,
								32,
								47,
								33,
								0,
								0,
								0,
								0,
								0,
								0,
								0,
								51,
								6,
								8,
								104,
								33,
								124,
								0,
								0,
								0,
								0,
								55,
								32,
								7,
								33,
								0,
								12,
								13,
								0,
								0,
								0,
								8,
								0,
								0,
								0,
								43,
								105,
								842,
								33,
								0,
								5,
								0,
								7,
								8,
								5,
								6,
								0,
								11,
								0,
								12,
								7,
								12,
								13,
								12,
								12,
								0,
								7,
								13,
								7,
								0,
								8,
								0,
								2,
								0,
								0,
								12,
								0,
								0,
								0,
								5,
								0,
								7,
								6,
								6,
								6,
								1070,
								0,
								0,
								0,
								8,
								0,
								7,
								4,
								4,
								0,
								0,
								222,
								0,
								0,
								2,
								0,
								0,
								0,
								0,
								614,
								4,
								891,
								33,
								41,
								0,
								0,
								7,
								12,
								13,
								12,
								12,
								0,
								89,
								0,
								0,
								24,
								0,
								31,
								0,
								4,
								629,
								33,
								0,
								0,
								0,
								31,
								32,
								447,
								33,
								89,
								0,
								0,
								21,
								0,
								24,
								0,
								0,
								10,
								0,
								245,
								0,
								7,
								7,
								9,
								0,
								1,
								9,
								1,
								10,
								1,
								8,
								11,
								196,
								112,
								15,
								11,
								205,
								4,
								8,
								0,
								0,
								0,
								6,
								713,
								33,
								0,
								8,
								0,
								74,
								24,
								244,
								0,
								0,
								60,
								8,
								221,
								9,
								0,
								851,
								24,
								21,
								790,
								351,
								24,
								17,
								168,
								25,
								0,
								0,
								248,
								0,
								0,
								4,
								5,
								6,
								0,
								0,
								8,
								13,
								0,
								4,
								0,
								6,
								0,
								0,
								31,
								0,
								50,
								55,
								3,
								33,
								133,
								0,
								12,
							}
							;(t1[1])[31][39] = 0
							;(t1[1])[33][38] = 38
							continue
						end

						break
					end
				end
				;(t1[1])[8] = #(t1[1])[7]

				while (t1[1])[8] > 1 do
					(t1[1])[32] = {
						0,
						0,
						0,
						0,
						0,
						246,
						19,
						103,
						6,
						0,
						8,
						0,
						33,
						32,
						32,
						33,
						0,
						0,
						0,
						5,
						0,
						0,
						0,
						13,
						9,
						9,
						10,
						0,
						234,
						0,
						0,
						2,
						0,
						5,
						0,
						7,
						0,
						0,
						0,
						0,
						0,
						201,
						0,
						0,
						0,
						0,
						0,
						2,
						0,
						0,
						201,
						0,
						1,
						1,
						1,
						3,
						0,
						2,
						0,
						0,
						33,
						33,
						32,
						33,
						0,
						0,
						0,
						7,
						0,
						27,
						33,
						0,
						33,
						32,
						27,
						33,
						118,
						71,
						0,
						0,
						33,
						27,
						27,
						32,
						33,
						0,
						0,
						11,
						0,
						2,
						11,
						0,
						9,
						0,
						33,
						0,
						32,
						33,
						33,
						0,
						0,
						0,
						2,
						0,
						0,
						0,
						933,
						0,
						9,
						0,
						2,
						12,
						933,
						0,
						12,
						104,
						0,
						10,
						10,
						13,
						0,
						18,
						0,
						2,
						0,
						0,
						0,
						2,
						11,
						12,
						12,
						0,
						0,
						6,
						104,
						0,
						4,
						0,
						0,
						0,
						0,
						0,
						0,
						0,
						4,
						4,
						0,
						10,
						0,
						0,
						0,
						0,
						0,
						33,
						27,
						27,
						33,
						33,
						38,
						44,
						0,
						0,
						12,
						933,
						0,
						12,
						104,
						0,
						8,
						0,
						0,
						0,
						0,
						0,
						33,
						31,
						33,
						0,
						0,
						0,
						33,
						0,
						31,
						33,
						26,
						211,
						0,
						23,
						0,
						17,
						143,
						24,
						0,
						0,
						8,
						3,
						0,
						10,
						146,
						9,
						0,
						7,
						7,
						9,
						7,
						10,
						10,
						39,
						203,
						9,
						42,
						48,
						52,
						10,
						11,
						0,
						0,
						33,
						32,
						33,
						0,
						0,
						10,
						0,
						174,
						215,
						14,
						0,
						7,
						107,
						63,
						234,
						0,
						0,
						24,
						24,
						1038,
						24,
						24,
						24,
						1038,
						23,
						0,
						0,
						0,
						3,
						0,
						0,
						0,
						0,
						0,
						4,
						13,
						13,
						2,
						0,
						0,
						2,
						0,
						0,
						0,
						0,
						33,
						31,
						32,
						33,
						64,
						173,
						0,
						366,
					}
					;(t1[1])[31] = {
						0,
						0,
						0,
						0,
						7,
						200,
						8,
						237,
						0,
						10,
						0,
						0,
						0,
						28,
						115,
						5,
						33,
						0,
						0,
						0,
						0,
						0,
						0,
						12,
						7,
						9,
						10,
						0,
						0,
						0,
						5,
						0,
						7,
						0,
						0,
						2,
						0,
						0,
						6,
						9,
						10,
						81,
						0,
						0,
						0,
						0,
						0,
						150,
						0,
						0,
						4,
						0,
						0,
						2,
						3,
						21,
						0,
						8,
						0,
						0,
						0,
						89,
						32,
						47,
						33,
						0,
						0,
						0,
						0,
						0,
						0,
						0,
						51,
						6,
						8,
						104,
						33,
						124,
						0,
						0,
						0,
						0,
						55,
						32,
						7,
						33,
						0,
						12,
						13,
						0,
						0,
						0,
						8,
						0,
						0,
						0,
						43,
						105,
						842,
						33,
						0,
						5,
						0,
						7,
						8,
						5,
						6,
						0,
						11,
						0,
						12,
						7,
						12,
						13,
						12,
						12,
						0,
						7,
						13,
						7,
						0,
						8,
						0,
						2,
						0,
						0,
						12,
						0,
						0,
						0,
						5,
						0,
						7,
						6,
						6,
						6,
						1070,
						0,
						0,
						0,
						8,
						0,
						7,
						4,
						4,
						0,
						0,
						222,
						0,
						0,
						2,
						0,
						0,
						0,
						0,
						614,
						4,
						891,
						33,
						41,
						0,
						0,
						7,
						12,
						13,
						12,
						12,
						0,
						89,
						0,
						0,
						24,
						0,
						31,
						0,
						4,
						629,
						33,
						0,
						0,
						0,
						31,
						32,
						447,
						33,
						89,
						0,
						0,
						21,
						0,
						24,
						0,
						0,
						10,
						0,
						245,
						0,
						7,
						7,
						9,
						0,
						1,
						9,
						1,
						10,
						1,
						8,
						11,
						196,
						112,
						15,
						11,
						205,
						4,
						8,
						0,
						0,
						0,
						6,
						713,
						33,
						0,
						8,
						0,
						74,
						24,
						244,
						0,
						0,
						60,
						8,
						221,
						9,
						0,
						851,
						24,
						21,
						790,
						351,
						24,
						17,
						168,
						25,
						0,
						0,
						248,
						0,
						0,
						4,
						5,
						6,
						0,
						0,
						8,
						13,
						0,
						4,
						0,
						6,
						0,
						0,
						31,
						0,
						50,
						55,
						3,
						33,
						133,
						0,
						12,
					}
					;(t1[1])[33] = {
						52,
						256,
						126,
						117,
						501,
						251,
						238,
						62,
						9,
						89,
						244,
						32,
						0,
						808,
						1002,
						58,
						26,
						50,
						173,
						2,
						248,
						195,
						94,
						12,
						12,
						89,
						6,
						43,
						24,
						161,
						3,
						6,
						6,
						0,
						19,
						89,
						248,
						180,
						121,
						89,
						89,
						89,
						22,
						22,
						0,
						1,
						50,
						32,
						149,
						228,
						0,
						247,
						0,
						89,
						6,
						854,
						123,
						0,
						125,
						32,
						0,
						60,
						60,
						224,
						26,
						101,
						0,
						2,
						248,
						0,
						0,
						32,
						65,
						65,
						942,
						6,
						26,
						28,
						256,
						32,
						0,
						0,
						314,
						314,
						699,
						26,
						28,
						6,
						0,
						14,
						15,
						252,
						89,
						168,
						0,
						32,
						952,
						952,
						54,
						26,
						147,
						0,
						6,
						6,
						6,
						4,
						5,
						132,
						0,
						46,
						12,
						7,
						5,
						1,
						13,
						5,
						244,
						12,
						89,
						13,
						23,
						0,
						139,
						0,
						248,
						66,
						0,
						13,
						14,
						0,
						12,
						110,
						1,
						7,
						5,
						2,
						6,
						49,
						260,
						0,
						7,
						168,
						89,
						4,
						32,
						30,
						170,
						11,
						3,
						248,
						2,
						248,
						28,
						0,
						0,
						87,
						87,
						753,
						26,
						123,
						57,
						171,
						13,
						5,
						1,
						13,
						5,
						37,
						35,
						138,
						101,
						959,
						234,
						0,
						0,
						882,
						91,
						26,
						87,
						1,
						0,
						0,
						3,
						447,
						26,
						179,
						38,
						0,
						0,
						0,
						233,
						152,
						224,
						89,
						121,
						778,
						179,
						12,
						108,
						89,
						92,
						8,
						89,
						9,
						6,
						10,
						11,
						23,
						120,
						226,
						2,
						129,
						69,
						11,
						11,
						108,
						32,
						0,
						27,
						363,
						26,
						195,
						92,
						197,
						26,
						87,
						999,
						152,
						0,
						59,
						241,
						62,
						2,
						193,
						24,
						157,
						24,
						136,
						24,
						791,
						24,
						62,
						16,
						126,
						57,
						362,
						47,
						44,
						62,
						1,
						62,
						46,
						0,
						13,
						13,
						162,
						0,
						5,
						89,
						142,
						32,
						0,
						0,
						431,
						431,
						412,
						26,
						0,
						39,
						319,
					}
					;(t1[1])[31][42] = 11
					;(t1[1])[32][42] = 8
					;(t1[1])[33][139] = 39
					;(t1[1])[9] = 1
					;(t1[1])[10] = 1
					;(t1[1])[81] = (t1[1])[201] - 1

					while true do
						(t1[1])[33] = {
							52,
							256,
							126,
							117,
							501,
							251,
							238,
							62,
							9,
							89,
							244,
							32,
							0,
							808,
							1002,
							58,
							26,
							50,
							173,
							2,
							248,
							195,
							94,
							12,
							12,
							89,
							6,
							43,
							24,
							161,
							3,
							6,
							6,
							0,
							19,
							89,
							248,
							180,
							121,
							89,
							89,
							89,
							22,
							22,
							0,
							1,
							50,
							32,
							149,
							228,
							0,
							247,
							0,
							89,
							6,
							854,
							123,
							0,
							125,
							32,
							0,
							60,
							60,
							224,
							26,
							101,
							0,
							2,
							248,
							0,
							0,
							32,
							65,
							65,
							942,
							6,
							26,
							28,
							256,
							32,
							0,
							0,
							314,
							314,
							699,
							26,
							28,
							6,
							0,
							14,
							15,
							252,
							89,
							168,
							0,
							32,
							952,
							952,
							54,
							26,
							147,
							0,
							6,
							6,
							6,
							4,
							5,
							132,
							0,
							46,
							12,
							7,
							5,
							1,
							13,
							5,
							244,
							12,
							89,
							13,
							23,
							0,
							139,
							0,
							248,
							66,
							0,
							13,
							14,
							0,
							12,
							110,
							1,
							7,
							5,
							2,
							6,
							49,
							260,
							0,
							7,
							168,
							89,
							4,
							32,
							30,
							170,
							11,
							3,
							248,
							2,
							248,
							28,
							0,
							0,
							87,
							87,
							753,
							26,
							123,
							57,
							171,
							13,
							5,
							1,
							13,
							5,
							37,
							35,
							138,
							101,
							959,
							234,
							0,
							0,
							882,
							91,
							26,
							87,
							1,
							0,
							0,
							3,
							447,
							26,
							179,
							38,
							0,
							0,
							0,
							233,
							152,
							224,
							89,
							121,
							778,
							179,
							12,
							108,
							89,
							92,
							8,
							89,
							9,
							6,
							10,
							11,
							23,
							120,
							226,
							2,
							129,
							69,
							11,
							11,
							108,
							32,
							0,
							27,
							363,
							26,
							195,
							92,
							197,
							26,
							87,
							999,
							152,
							0,
							59,
							241,
							62,
							2,
							193,
							24,
							157,
							24,
							136,
							24,
							791,
							24,
							62,
							16,
							126,
							57,
							362,
							47,
							44,
							62,
							1,
							62,
							46,
							0,
							13,
							13,
							162,
							0,
							5,
							89,
							142,
							32,
							0,
							0,
							431,
							431,
							412,
							26,
							0,
							39,
							319,
						}
						;(t1[1])[32] = {
							0,
							0,
							0,
							0,
							0,
							246,
							19,
							103,
							6,
							0,
							8,
							0,
							33,
							32,
							32,
							33,
							0,
							0,
							0,
							5,
							0,
							0,
							0,
							13,
							9,
							9,
							10,
							0,
							234,
							0,
							0,
							2,
							0,
							5,
							0,
							7,
							0,
							0,
							0,
							0,
							0,
							201,
							0,
							0,
							0,
							0,
							0,
							2,
							0,
							0,
							201,
							0,
							1,
							1,
							1,
							3,
							0,
							2,
							0,
							0,
							33,
							33,
							32,
							33,
							0,
							0,
							0,
							7,
							0,
							27,
							33,
							0,
							33,
							32,
							27,
							33,
							118,
							71,
							0,
							0,
							33,
							27,
							27,
							32,
							33,
							0,
							0,
							11,
							0,
							2,
							11,
							0,
							9,
							0,
							33,
							0,
							32,
							33,
							33,
							0,
							0,
							0,
							2,
							0,
							0,
							0,
							933,
							0,
							9,
							0,
							2,
							12,
							933,
							0,
							12,
							104,
							0,
							10,
							10,
							13,
							0,
							18,
							0,
							2,
							0,
							0,
							0,
							2,
							11,
							12,
							12,
							0,
							0,
							6,
							104,
							0,
							4,
							0,
							0,
							0,
							0,
							0,
							0,
							0,
							4,
							4,
							0,
							10,
							0,
							0,
							0,
							0,
							0,
							33,
							27,
							27,
							33,
							33,
							38,
							44,
							0,
							0,
							12,
							933,
							0,
							12,
							104,
							0,
							8,
							0,
							0,
							0,
							0,
							0,
							33,
							31,
							33,
							0,
							0,
							0,
							33,
							0,
							31,
							33,
							26,
							211,
							0,
							23,
							0,
							17,
							143,
							24,
							0,
							0,
							8,
							3,
							0,
							10,
							146,
							9,
							0,
							7,
							7,
							9,
							7,
							10,
							10,
							39,
							203,
							9,
							42,
							48,
							52,
							10,
							11,
							0,
							0,
							33,
							32,
							33,
							0,
							0,
							10,
							0,
							174,
							215,
							14,
							0,
							7,
							107,
							63,
							234,
							0,
							0,
							24,
							24,
							1038,
							24,
							24,
							24,
							1038,
							23,
							0,
							0,
							0,
							3,
							0,
							0,
							0,
							0,
							0,
							4,
							13,
							13,
							2,
							0,
							0,
							2,
							0,
							0,
							0,
							0,
							33,
							31,
							32,
							33,
							64,
							173,
							0,
							366,
						}
						;(t1[1])[32][199] = 9
						;(t1[1])[33][199] = 12
						;(t1[1])[33][23] = 147
						;(t1[1])[26] = nil
						;(t1[1])[27] = nil
						;(t1[1])[28] = nil
						;(t1[1])[29] = nil
						;(t1[1])[30] = nil
						;(t1[1])[31] = nil
						;(t1[1])[32] = nil
						;(t1[1])[33] = nil

						if (t1[1])[10] <= (t1[1])[11] then
							(t1[1])[12] = (t1[1])[7][(t1[1])[10]]
							;(t1[1])[13] = (t1[1])[10] + 1
							;(t1[1])[13] = (t1[1])[7][(t1[1])[13]]
							;(t1[1])[12] = (t1[1])[12] .. (t1[1])[13]
							;(t1[1])[7][(t1[1])[9]] = (t1[1])[12]
							;(t1[1])[9] = (t1[1])[9] + 1
							;(t1[1])[10] = (t1[1])[10] + 2
						else
							break
						end
					end

					if (t1[1])[10] == (t1[1])[8] then
						(t1[1])[12] = (t1[1])[7][(t1[1])[10]]
						;(t1[1])[7][(t1[1])[146]] = (t1[1])[108]
						;(t1[1])[9] = (t1[1])[9] + 1
					end
					;(t1[1])[8] = (t1[1])[9] - 1
				end
				;(t1[1])[2] = (t1[1])[7][1]
			end
		end
	elseif (t1[1])[3] == "number" then
		if (t1[1])[2] ~= 0 then
			(t1[1])[2] = -(t1[1])[2]
		end
	end
	;(t1[1])[4] = 3
	;(t1[1])[5] = #(t1[1])[1]
	;(t1[1])[6] = 3

	while true do
		if d_1 <= 0 then
			if h_1 >= E_1 then
				(t1[1])[7] = h_1
				;(t1[1])[8] = (t1[1])[1][(t1[1])[7]]
				;(t1[1])[9] = (t1[1])[7] + 1
				;(t1[1])[9] = (t1[1])[1][(t1[1])[9]]
				;(t1[1])[10] = (t1[1])[7] + 2
				;(t1[1])[10] = (t1[1])[1][(t1[1])[10]]
				;(t1[1])[11] = (t1[1])[8][(t1[1])[10]]
				;(t1[1])[11] = upv4[(t1[1])[10]]
				;(t1[1])[11] = (t1[1])[8][(t1[1])[11]]
				;(t1[1])[11][(t1[1])[9]] = (t1[1])[0]
				continue
			end

			break
		else
			if h_1 <= E_1 then
				(t1[1])[7] = h_1
				;(t1[1])[8] = (t1[1])[1][(t1[1])[7]]
				;(t1[1])[9] = (t1[1])[7] + 1
				;(t1[1])[9] = (t1[1])[1][(t1[1])[9]]
				;(t1[1])[10] = (t1[1])[7] + 2
				;(t1[1])[10] = (t1[1])[1][(t1[1])[10]]
				;(t1[1])[11] = (t1[1])[8][(t1[1])[10]]
				;(t1[1])[11] = upv4[(t1[1])[10]]
				;(t1[1])[11] = (t1[1])[8][(t1[1])[11]]
				;(t1[1])[11][(t1[1])[9]] = (t1[1])[0]
				continue
			end

			break
		end
	end

	error("devirt: symbolic generic for (at 0:46)")
end

-- proto 25: vm sequence 28, 0 opcodes
local function proto_25()
	(t1[1])[1] = (t2[2])[1]
	;(t1[1])[2] = (t2[2])[2]
	;(t1[1])[3] = upv0[1]
	;(t1[1])[4] = 25

	while (t1[1])[4] == 25 do
		(t1[1])[4] = 36
		;(t1[1])[3] = (t1[1])[5][(t1[1])[2]]
	end

	if not (t1[1])[3] then
		(t1[1])[5] = upv3
		;(t1[1])[5]()
		error("devirt: symbolic generic for (at 0:43)")
	end
	;(t1[1])[5] = upv1[(t1[1])[3]]
	;(t1[1])[6] = upv0[1]

	upv1[(t1[1])[3]] = (t1[1])[6]
	;(t1[1])[6] = 35

	while true do
		if (t1[1])[6] == 35 then
			(t1[1])[7] = upv2
			;(t1[1])[8] = (t1[1])[5]
			;(t1[1])[7]((t1[1])[8])
			;(t1[1])[6] = 38
			continue
		end

		if (t1[1])[6] ~= 38 then
			continue
		end
		break
	end
	;(t1[1])[7] = (t1[1])[1][(t1[1])[2]]
	error("devirt: symbolic generic for (at 0:34)")
end

-- proto 24: vm sequence 29, 0 opcodes
local function proto_24()
	repeat
		(t1[1])[1] = (t3[1]).task
		;(t1[1])[1] = (t1[1])[1].wait
		;(t1[1])[2] = 0.1
		;(t1[1])[1]((t1[1])[2])
		;(t1[1])[1] = (t3[1]).game
		;(t1[1])[2] = (t1[1])[1]
		;(t1[1])[1] = (t1[1])[1].IsLoaded
		;(t1[1])[1] = (t1[1])[1]((t1[1])[2])
	until (t1[1])[1]
	;(t1[1])[1] = (t3[1]).game
	;(t1[1])[2] = (t1[1])[1]
	;(t1[1])[1] = (t1[1])[1].GetService
	;(t1[1])[3] = "ReplicatedStorage"
	;(t1[1])[1] = (t1[1])[1]((t1[1])[2], (t1[1])[3])
	;(t1[1])[2] = (t1[1])[1].RemoteEvents
	;(t1[1])[2] = (t1[1])[2].GunFire
	;(t1[1])[3] = (t1[1])[1].RemoteEvents
	;(t1[1])[3] = (t1[1])[3].MeleeAttack
	;(t1[1])[4] = (t3[1]).game
	;(t1[1])[5] = (t1[1])[4]
	;(t1[1])[4] = (t1[1])[4].GetService
	;(t1[1])[6] = "UserInputService"
	;(t1[1])[4] = (t1[1])[4]((t1[1])[5], (t1[1])[6])
	;(t1[1])[5] = (t3[1]).game
	;(t1[1])[6] = (t1[1])[5]
	;(t1[1])[5] = (t1[1])[5].GetService
	;(t1[1])[7] = "RunService"
	;(t1[1])[5] = (t1[1])[5]((t1[1])[6], (t1[1])[7])
	;(t1[1])[6] = (t3[1]).game
	;(t1[1])[7] = (t1[1])[6]
	;(t1[1])[6] = (t1[1])[6].GetService
	;(t1[1])[8] = "TweenService"
	;(t1[1])[6] = (t1[1])[6]((t1[1])[7], (t1[1])[8])
	;(t1[1])[7] = (t3[1]).game
	;(t1[1])[8] = (t1[1])[7]
	;(t1[1])[7] = (t1[1])[7].GetService
	;(t1[1])[9] = "HttpService"
	;(t1[1])[7] = (t1[1])[7]((t1[1])[8], (t1[1])[9])
	;(t1[1])[8] = (t3[1]).game
	;(t1[1])[9] = (t1[1])[8]
	;(t1[1])[8] = (t1[1])[8].GetService
	;(t1[1])[10] = "VirtualInputManager"
	;(t1[1])[8] = (t1[1])[8]((t1[1])[9], (t1[1])[10])
	;(t1[1])[9] = (t3[1]).game
	;(t1[1])[9] = (t1[1])[9].Players
	;(t1[1])[9] = (t1[1])[9].LocalPlayer
	;(t1[1])[10] = nil

	local v = table.pack((nil --[[ constant not decoded ]])[57](table.pack(table.pack(table.pack(9, 1)), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (6), (87), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (173), (0), (0), (31), (nil), (nil), (nil), (nil), (nil), (0), (112), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (8), (20), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (206), (6670), (nil), (nil), (31), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (10), (104), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Character"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (22), (92), (68) }; t.n = 121; return t end)(), 31, (function() local t = { (97), (59), (9), (95), (77), (9), (81), (63), (0), (95), (124), (80), (29), (0), (0), (nil), (nil), (nil), (23), (87), (9), (63), (0), (11), (123), (5), (30), (84), (4), (65), (112), (3), (nil), (0), (3), (4), (0), (0), (91), (0), (0), (0), (nil), (nil), (nil), (nil), (23), (31), (31), (0), (29), (nil), (nil), (23), (112), (7), (0), (4), (65), (0), (0), (nil), (nil), (23), (20), (0), (30), (68), (0), (0), (nil), (21), (nil), (21), (nil), (13), (48), (0), (0), (31), (0), (0), (93), (nil), (23), (104), (106), (0), (56), (57), (169), (nil), (0), (0), (55), (9), (1), (0), (2), (2), (36), (nil), (65), (5), (65), (86), (nil), (nil), (11), (11), (10), (24), (0), (6), (0), (0), (0), (0), (nil), (nil), (nil), (23), (68), (87), (2) }; t.n = 125; return t end)(), (function() local t = { (127), (127), (185), (127), (127), (145), (143), (115), (81), (156), (127), (127), (93), (131), (34), (101), (101), (101), (92), (127), (145), (8), (81), (127), (114), (0), (124), (36), (185), (127), (127), (145), (8), (81), (39), (127), (173), (65), (48), (131), (34), (90), (101), (101), (101), (101), (14), (127), (127), (131), (93), (101), (101), (92), (127), (145), (22), (22), (78), (34), (131), (101), (101), (14), (127), (159), (127), (127), (34), (131), (151), (5), (141), (17), (101), (92), (127), (173), (65), (127), (131), (34), (101), (101), (92), (127), (127), (173), (143), (193), (11), (117), (84), (84), (127), (39), (127), (58), (155), (39), (127), (117), (80), (127), (32), (127), (117), (117), (1), (117), (48), (127), (168), (185), (65), (131), (90), (34), (101), (101), (101), (14), (127), (127), (127) }; t.n = 125; return t end)(), (function() local t = { (0), (26), (26), (26), (22), (26), (26), (26), (26), (26), (26), (27), (23), (23), (23), (23), (23), (23), (23), (23), (26), (26), (26), (26), (29), (29), (29), (29), (29), (29), (24), (21), (21), (21), (22), (22), (20), (20), (121), (21), (21), (21), (21), (21), (21), (21), (21), (21), (21), (24), (24), (24), (24), (24), (24), (24), (24), (24), (24), (26), (26), (26), (26), (26), (26), (24), (24), (21), (21), (21), (21), (21), (21), (21), (21), (21), (21), (22), (22), (21), (27), (27), (27), (27), (27), (27), (27), (23), (23), (23), (23), (23), (24), (24), (24), (26), (26), (1), (19), (20), (20), (25), (25), (25), (27), (27), (28), (28), (28), (28), (29), (29), (24), (33), (33), (21), (21), (21), (21), (21), (21), (21), (21), (23) }; t.n = 124; return t end)(), (function() local t = { (0), (0), (8), (0), (0), (182), (153), (24), (9), (9), (0), (0), (0), (30), (0), (29), (28), (30), (0), (0), (262), (0), (9), (0), (48), (22), (10), (232), (8), (0), (0), (nil), (0), (3), (123), (0), (3), (0), (350), (30), (0), (24), (24), (28), (30), (30), (146), (0), (0), (30), (0), (29), (30), (0), (0), (nil), (2), (0), (6), (0), (30), (28), (30), (2), (0), (6), (0), (0), (0), (20), (21), (21), (21), (nil), (20), (0), (0), (4), (0), (0), (30), (0), (28), (30), (0), (0), (0), (4), (38), (77), (nil), (5), (nil), (nil), (0), (11), (0), (1), (0), (79), (0), (8), (9), (0), (9), (0), (3), (9), (10), (10), (5), (0), (0), (4), (0), (30), (24), (0), (28), (24), (30), (12), (0), (0), (0) }; t.n = 125; return t end)(), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (58), (58), (124), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("HumanoidRootPart"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (88), (88), (88), (49), (nil), (nil), (nil), (nil), (nil), (113), (31), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (21), (2), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (384), (nil), (-7253), (nil), (80), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (12), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("huge"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Name"), (nil), (nil), (nil), (nil), ("Position"), ("Position"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (76), (76), (68) }; t.n = 121; return t end)(), (function() local t = { (0), (0), (0), (0), (0), (8), (11), (108), (0), (0), (0), (0), (0), (0), (28), (nil), (nil), (nil), (30), (0), (36), (11), (0), (0), (77), (213), (61), (223), (0), (0), (0), (2), (5), (0), (0), (0), (0), (3), (359), (0), (28), (0), (nil), (nil), (nil), (nil), (30), (0), (0), (0), (0), (nil), (nil), (30), (0), (7), (7), (6), (0), (28), (0), (nil), (nil), (30), (0), (101), (0), (0), (18), (0), (nil), (nil), (21), (18), (nil), (22), (0), (0), (4), (0), (0), (28), (nil), (nil), (30), (0), (0), (0), (5), (35), (179), (5), (6), (7), (0), (0), (0), (0), (nil), (0), (0), (9), (1), (0), (0), (0), (34), (11), (10), (10), (65), (0), (0), (0), (6), (0), (0), (28), (nil), (nil), (nil), (30), (0), (0), (0) }; t.n = 125; return t end)(), 0, (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("FindFirstChild"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("GetChildren"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (57), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("math"), (nil), ("pairs"), ("workspace") }; t.n = 94; return t end)()), {}))
	;(nil --[[ constant not decoded ]])[49](v[1], t3[1])
	;(t1[1])[11] = v[1]

	local v2 = table.pack((nil --[[ constant not decoded ]])[57](table.pack(table.pack(table.pack(9, 1)), (function() local t = { (nil), (nil), (nil), (nil), (5), (38), (nil), (nil), (nil), (nil), (nil), (9), (117), (nil), (nil), (nil), (nil), (nil), (5534), (nil), (nil), (24), (nil), (nil), ("Character"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (2), (1), (145), (72), (nil), (nil), (nil), (nil), (1), (120), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (78), (0), (31), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (92), (79), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (nil), (nil), (nil), (nil), (0), (99) }; t.n = 128; return t end)(), 32, (function() local t = { (49), (0), (0), (505), (505), (308), (24), (38), (80), (99), (0), (nil), (nil), (24), (117), (0), (0), (nil), (22), (nil), (22), (nil), (14), (24), (1), (1), (119), (39), (113), (40), (134), (3), (0), (nil), (0), (0), (7), (114), (130), (117), (nil), (nil), (12), (73), (8), (86), (11), (140), (65), (79), (0), (0), (0), (nil), (nil), (nil), (nil), (24), (72), (0), (0), (nil), (nil), (24), (120), (11), (95), (120), (72), (31), (3), (3), (2), (248), (nil), (0), (2), (98), (280), (24), (0), (9), (6), (202), (23), (7), (6), (0), (0), (0), (nil), (nil), (nil), (24), (31), (1), (2), (2), (70), (9), (245), (nil), (0), (10), (nil), (0), (27), (0), (0), (nil), (nil), (24), (79), (123), (0), (4), (39), (0), (8), (96), (nil), (39), (30), (67), (0), (0), (nil), (nil), (24), (99), (36), (3), (4), (39), (39), (39), (29) }; t.n = 137; return t end)(), (function() local t = { (127), (90), (131), (101), (101), (101), (92), (127), (127), (127), (131), (101), (101), (92), (127), (131), (90), (76), (5), (141), (17), (101), (92), (127), (155), (39), (127), (32), (127), (127), (127), (92), (84), (117), (84), (84), (145), (127), (127), (127), (117), (117), (1), (114), (56), (33), (135), (36), (127), (127), (90), (131), (34), (101), (101), (101), (101), (14), (127), (90), (131), (101), (101), (14), (127), (48), (127), (127), (127), (127), (92), (30), (145), (143), (115), (81), (39), (127), (16), (127), (168), (114), (0), (124), (36), (185), (30), (90), (131), (34), (101), (101), (101), (14), (127), (127), (92), (30), (127), (145), (143), (115), (81), (145), (8), (81), (127), (90), (131), (101), (101), (92), (127), (127), (22), (22), (78), (159), (127), (127), (117), (62), (127), (127), (131), (34), (101), (101), (92), (127), (134), (185), (185), (127), (32), (25), (127) }; t.n = 137; return t end)(), (function() local t = { (0), (47), (47), (47), (47), (47), (47), (47), (42), (43), (42), (42), (42), (42), (42), (37), (37), (37), (37), (37), (37), (37), (37), (37), (37), (38), (38), (45), (45), (45), (45), (41), (41), (41), (42), (42), (42), (42), (47), (42), (46), (46), (46), (46), (46), (46), (46), (46), (46), (37), (39), (39), (39), (39), (39), (39), (39), (39), (39), (45), (45), (45), (45), (45), (45), (47), (47), (45), (39), (41), (40), (40), (39), (39), (39), (39), (40), (40), (17), (37), (42), (54), (54), (54), (54), (54), (54), (41), (41), (41), (41), (41), (41), (41), (41), (47), (38), (38), (40), (43), (43), (43), (43), (44), (44), (44), (44), (37), (37), (37), (37), (37), (37), (45), (42), (42), (42), (42), (42), (38), (45), (45), (45), (45), (43), (43), (43), (43), (43), (43), (48), (49), (50), (50), (45), (45) }; t.n = 136; return t end)(), (function() local t = { (0), (25), (31), (25), (31), (31), (0), (0), (0), (0), (31), (31), (31), (0), (0), (21), (15), (nil), (22), (22), (nil), (21), (0), (0), (0), (68), (0), (9), (0), (0), (0), (0), (nil), (5), (nil), (nil), (nil), (0), (0), (0), (2), (10), (11), (16), (136), (11), (234), (15), (0), (0), (25), (31), (0), (31), (29), (25), (31), (126), (0), (25), (31), (25), (31), (189), (0), (5), (0), (0), (0), (0), (0), (3), (nil), (38), (126), (2), (69), (0), (85), (0), (0), (243), (239), (3), (53), (4), (3), (25), (31), (0), (25), (29), (31), (36), (0), (0), (0), (3), (0), (nil), (171), (249), (9), (nil), (0), (10), (0), (25), (31), (25), (31), (0), (0), (0), (2), (0), (6), (6), (0), (0), (9), (11), (0), (0), (31), (0), (29), (31), (0), (0), (11), (8), (10), (0), (10), (1), (0) }; t.n = 137; return t end)(), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (100), (40), (nil), (nil), (nil), (nil), (92), (nil), (-5212), (nil), (80), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("huge"), (nil), (nil), (nil), (nil), (nil), (nil), ("Position"), ("Position"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (73), (73), (73), (69), (nil), (nil), (nil), (nil), (43), (68), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("HumanoidRootPart"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (117), (117), (70), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Humanoid"), (nil), (nil), ("Head"), (nil), (nil), (nil), (nil), (23), (50), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Health"), (nil), (nil), (nil), (nil), (nil), (135), (10) }; t.n = 128; return t end)(), (function() local t = { (0), (0), (0), (234), (nil), (nil), (31), (0), (0), (0), (0), (nil), (nil), (31), (0), (0), (0), (22), (nil), (22), (15), (nil), (23), (0), (nil), (0), (0), (0), (0), (0), (0), (4), (5), (5), (6), (7), (7), (0), (0), (0), (11), (12), (11), (48), (11), (130), (198), (67), (0), (0), (0), (0), (29), (nil), (nil), (nil), (nil), (31), (0), (0), (0), (nil), (nil), (31), (0), (39), (0), (0), (0), (0), (4), (0), (1), (4), (83), (0), (0), (0), (151), (0), (0), (212), (182), (112), (114), (0), (0), (0), (0), (29), (nil), (nil), (nil), (31), (0), (0), (3), (0), (0), (8), (11), (200), (0), (8), (12), (0), (0), (0), (0), (nil), (nil), (31), (0), (0), (7), (6), (0), (9), (0), (0), (11), (nil), (0), (0), (0), (29), (nil), (nil), (31), (0), (0), (0), (0), (0), (0), (8), (0) }; t.n = 137; return t end)(), 0, (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (322), (nil), (nil), (97), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("math"), (nil), ("pairs"), ("workspace"), ("GetChildren"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("FindFirstChild"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("FindFirstChildOfClass"), (nil), (nil), (nil), ("FindFirstChild") }; t.n = 104; return t end)()), {}))
	;(nil --[[ constant not decoded ]])[49](v2[1], t3[1])
	;(t1[1])[12] = v2[1]

	local v3 = table.pack((nil --[[ constant not decoded ]])[57](table.pack(table.pack(table.pack(9, 1)), table.pack(nil, nil, nil, nil, 13, 13, 47, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, "Character", nil, nil, nil, nil, nil, 0, 13, 30, nil, nil, nil, nil, nil, nil, nil, 13, 13, 14, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 42), 23, table.pack(19, 33, 0, 21, nil, nil, nil, 15, 47, 0, 0, 255, 32, 59, 9, 53, 0, 40, 196, 1, 2, 56, 15, 0, 0, nil, nil, nil, 15, 30, 190, 17, 23, 21, 0, nil, nil, nil, 15, 14, 131, 58, 2, 2, 501, 0, 16, 72, 468, 13, nil, 5, 42, 2, 501, 0, 2, 1, 2, 214, 32), table.pack(127, 127, 131, 72, 101, 101, 101, 14, 127, 34, 131, 179, 32, 127, 127, 127, 65, 127, 147, 155, 185, 156, 127, 131, 34, 101, 101, 101, 14, 127, 39, 127, 127, 72, 131, 101, 101, 101, 14, 127, 8, 127, 155, 145, 8, 81, 127, 5, 141, 17, 101, 14, 127, 145, 8, 81, 39, 127, 127, 8, 127), table.pack(0, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 59, 59, 60, 98, 58, 59, 59, 59, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 59, 59, 59, 60, 60, 60, 60), table.pack(0, 0, 22, 0, 22, 21, 22, 2, 0, 0, 12, 314, 165, 0, 0, 0, 0, 0, 382, 0, 1, 2, 0, 22, 0, 20, 22, 22, 85, 0, 58, 0, 0, 0, 22, 21, 22, 22, 142, 0, 0, 0, 0, nil, 0, 2, 0, 138, 13, nil, 12, 3, 0, nil, 0, 2, 16, 0, 0, 0, 0), table.pack(nil, nil, nil, nil, 48, 48, 59, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 31, 31, 33, nil, nil, nil, nil, nil, nil, nil, 13, 12, 2, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 15), table.pack(0, 0, 0, 0, nil, nil, nil, 22, 0, 10, 0, 216, 0, 0, 0, 0, 2, 0, 91, nil, 0, 0, 0, 0, 20, nil, nil, nil, 22, 0, 195, 0, 0, 0, 0, nil, nil, nil, 22, 0, 13, 0, 330, 2, 141, 0, 0, 324, 13, 10, nil, 14, 0, 1, 4, 0, 0, 0, 0, 13, 0), 0, table.pack(nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, "FindFirstChildOfClass", nil, nil, nil, nil, nil, 45, nil, nil, nil, "FindFirstChildOfClass")), {}))
	;(nil --[[ constant not decoded ]])[49](v3[1], t3[1])
	;(t1[1])[13] = v3[1]

	local v4 = table.pack((nil --[[ constant not decoded ]])[57](table.pack(table.pack(table.pack(9, 1), table.pack(11, 1), table.pack(3, 1)), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (84), (0), (152), (nil), (nil), ("Character"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (116), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (5807), (nil), (nil), (52), (nil), (nil), (nil), (nil), (nil), (0), (59), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (8), (4), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (85), (21), (118), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (418), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (127), (0), (0), (0), (47), (nil), (nil), (nil), (nil), (195), (39), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (2), (nil), (nil), (nil), (nil), (nil), (nil), (table.pack(table.pack(table.pack(2, 2), table.pack(4, 0)), table.pack(), 10, table.pack(6, 1, 1, 126, 0, 9, 1, 425, 1, nil, 0, 0, 1, 8, 1, 8), table.pack(127, 195, 145, 8, 173, 127, 127, 60, 59, 8, 173, 88, 164, 17, 112, 127), table.pack(0, 90, 90, 90, 90, 90, 0, 2, 90, 90, 90, 90, 90, 90, 90), table.pack(0, 0, 80, 0, 4, 0, 0, 254, 0, 0, 6, 7, 0, nil, 7, 0), table.pack(nil, nil, nil, nil, nil, nil, nil, nil, nil, 1), table.pack(0, 0, 1, 3, 0, 0, 0, 300, 0, 5, 0, 0, 8, 7, 0, 0), 0, table.pack(nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 1))) }; t.n = 170; return t end)(), 31, (function() local t = { (101), (18), (281), (22), (10), (134), (39), (4), (26), (2), (52), (0), (0), (nil), (nil), (nil), (23), (152), (1), (2), (123), (35), (21), (27), (9), (110), (152), (nil), (62), (0), (0), (nil), (nil), (23), (116), (2), (nil), (0), (123), (8), (202), (9), (10), (215), (8), (26), (128), (0), (0), (nil), (97), (1), (0), (127), (nil), (nil), (nil), (0), (7), (2), (154), (86), (21), (nil), (21), (nil), (13), (52), (29), (0), (0), (nil), (nil), (23), (59), (160), (0), (nil), (0), (1), (101), (0), (nil), (0), (0), (10), (0), (nil), (0), (101), (118), (29), (0), (nil), (335), (23), (4), (1), (3), (4), (26), (47), (29), (0), (0), (nil), (nil), (nil), (23), (118), (9), (63), (0), (166), (91), (125), (9), (24), (0), (0), (nil), (22), (9), (59), (497), (0), (76), (168), (129), (9), (63), (0), (24), (68), (98), (0), (29), (0), (0), (nil), (nil), (nil), (nil), (nil), (23), (47), (0), (0), (nil), (nil), (23), (39), (0), (115), (61), (nil), (nil), (11), (11), (114), (29), (0), (383), (nil), (23), (155), (26), (75), (0), (0), (5), (76) }; t.n = 172; return t end)(), (function() local t = { (127), (127), (8), (127), (48), (127), (127), (22), (78), (127), (127), (90), (131), (101), (101), (101), (14), (127), (155), (185), (32), (127), (39), (127), (39), (127), (127), (8), (127), (131), (90), (101), (101), (14), (127), (145), (8), (81), (127), (195), (114), (0), (124), (36), (7), (32), (127), (84), (181), (117), (32), (127), (190), (143), (115), (8), (8), (9), (127), (39), (127), (127), (5), (141), (17), (101), (92), (127), (127), (131), (34), (101), (101), (14), (127), (127), (84), (117), (55), (83), (127), (84), (117), (173), (84), (127), (84), (117), (55), (127), (127), (72), (131), (101), (101), (92), (127), (59), (185), (185), (127), (127), (93), (131), (90), (101), (101), (101), (14), (127), (145), (8), (81), (127), (127), (127), (234), (127), (131), (90), (85), (32), (127), (127), (36), (168), (32), (127), (127), (145), (8), (81), (156), (127), (127), (90), (93), (34), (131), (101), (101), (101), (101), (101), (92), (127), (90), (131), (101), (101), (92), (127), (159), (127), (127), (117), (117), (1), (117), (127), (72), (131), (101), (101), (14), (127), (156), (127), (84), (116), (186), (127) }; t.n = 172; return t end)(), (function() local t = { (0), (68), (74), (74), (80), (80), (75), (74), (74), (74), (74), (74), (74), (74), (74), (74), (74), (74), (69), (70), (70), (70), (74), (74), (77), (77), (74), (74), (74), (77), (77), (77), (77), (77), (77), (70), (70), (70), (70), (75), (75), (75), (75), (75), (75), (76), (76), (68), (68), (68), (68), (68), (74), (74), (74), (74), (74), (74), (74), (71), (71), (71), (74), (74), (74), (74), (74), (74), (77), (71), (71), (71), (71), (71), (71), (79), (93), (93), (93), (68), (68), (73), (73), (73), (74), (74), (71), (71), (71), (71), (74), (80), (80), (80), (80), (80), (80), (68), (81), (82), (82), (68), (74), (74), (74), (74), (74), (74), (74), (74), (77), (77), (77), (77), (80), (74), (77), (77), (74), (74), (74), (74), (74), (71), (127), (74), (88), (88), (76), (77), (77), (77), (77), (77), (80), (68), (68), (68), (68), (68), (68), (68), (68), (68), (68), (68), (75), (75), (75), (75), (75), (75), (74), (74), (71), (79), (79), (79), (79), (79), (79), (79), (79), (79), (79), (79), (78), (78), (89), (90), (89) }; t.n = 171; return t end)(), (function() local t = { (0), (0), (0), (0), (3), (0), (0), (2), (5), (0), (0), (24), (30), (24), (30), (30), (155), (0), (0), (1), (2), (0), (62), (0), (166), (0), (0), (0), (0), (30), (24), (24), (30), (173), (0), (nil), (0), (2), (0), (1), (154), (127), (7), (78), (0), (8), (0), (nil), (1), (1), (1), (0), (6), (175), (19), (0), (0), (6), (0), (81), (0), (0), (21), (21), (nil), (20), (0), (0), (0), (30), (0), (28), (30), (104), (0), (0), (nil), (5), (5), (0), (0), (nil), (3), (4), (nil), (0), (nil), (3), (3), (0), (0), (0), (30), (29), (30), (0), (0), (0), (10), (179), (0), (0), (0), (30), (24), (24), (29), (30), (229), (0), (262), (0), (9), (0), (0), (0), (8), (0), (20), (14), (21), (21), (0), (0), (177), (0), (4), (0), (0), (182), (0), (9), (9), (0), (0), (24), (0), (0), (30), (24), (29), (30), (28), (30), (0), (0), (24), (30), (24), (30), (0), (0), (5), (0), (0), (142), (9), (10), (10), (0), (0), (30), (29), (30), (104), (0), (9), (0), (nil), (6), (0), (0) }; t.n = 172; return t end)(), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (77), (169), (27), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (335), (nil), (nil), (nil), (117), (69), (nil), (nil), (nil), ("HumanoidRootPart"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("FarmTree"), (nil), (nil), (nil), (nil), ("Tree"), ("BigTree"), ("RockTree"), (nil), (nil), (nil), (nil), (nil), (nil), (-6120), (nil), (11), (nil), (nil), (nil), (nil), (nil), (9), (124), (nil), (nil), (nil), (nil), ("wait"), (nil), (nil), (nil), (nil), ("huge"), (nil), (nil), (nil), (nil), ("wait"), (nil), (nil), (nil), (nil), (nil), (100), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (121), (121), (91), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (221), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (86), (86), (84), (84), (102), (nil), (nil), (nil), (nil), (40), (7), (nil), (nil), (nil), (nil), (nil), ("Position"), ("Position"), (nil), (nil), (nil), (nil), (nil), (nil), (76) }; t.n = 164; return t end)(), (function() local t = { (0), (0), (21), (0), (26), (0), (0), (5), (0), (0), (0), (0), (0), (nil), (nil), (nil), (30), (0), (nil), (0), (0), (0), (0), (0), (0), (0), (0), (21), (0), (0), (0), (234), (nil), (30), (0), (1), (4), (0), (0), (0), (88), (76), (21), (243), (0), (0), (0), (1), (0), (1), (0), (0), (3), (7), (52), (8), (9), (3), (0), (0), (0), (0), (nil), (21), (14), (nil), (22), (0), (0), (0), (28), (nil), (nil), (30), (0), (0), (5), (5), (0), (0), (0), (3), (3), (0), (5), (0), (3), (3), (0), (0), (0), (0), (0), (nil), (nil), (30), (0), (0), (0), (0), (0), (0), (0), (0), (0), (nil), (nil), (nil), (30), (0), (8), (11), (0), (0), (0), (0), (0), (0), (0), (0), (nil), (0), (0), (0), (278), (0), (0), (0), (0), (8), (11), (0), (0), (0), (0), (0), (0), (28), (0), (nil), (nil), (nil), (nil), (nil), (30), (0), (0), (0), (nil), (nil), (30), (0), (6), (0), (0), (10), (11), (10), (10), (0), (0), (0), (nil), (347), (30), (0), (0), (0), (5), (18), (0), (0) }; t.n = 172; return t end)(), 0, (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("FindFirstChild"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("getgenv"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (8), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("task"), (nil), (nil), (nil), (nil), ("math"), (nil), (nil), ("pairs"), (nil), ("task"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("pcall") }; t.n = 169; return t end)()), {}))
	;(nil --[[ constant not decoded ]])[49](v4[1], t3[1])
	;(t1[1])[14] = v4[1]

	local v5 = table.pack((nil --[[ constant not decoded ]])[57](table.pack(table.pack(table.pack(9, 1), table.pack(11, 1), table.pack(3, 1)), (function() local t = { (nil), (nil), (nil), (0), (0), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (1), (105), (nil), (nil), (nil), (nil), (1), (83), (nil), (nil), (nil), (0), (nil), (nil), (table.pack(table.pack(table.pack(2, 2), table.pack(3, 1)), table.pack(nil, nil, nil, nil, nil, nil, nil, nil, nil, 4, 6, nil, nil, nil, nil, nil, 1, 195, 12, 44, nil, nil, nil, nil, nil, nil, nil, nil, 1, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 14, 22), 32, table.pack(49, 1, 133, 126, 0, 50, 23, 0, 30, nil, nil, 24, 6, 0, 0, 30, nil, nil, nil, nil, 24, 44, 43, 0, 360, 22, 184, 22, nil, 10, 1, 80, 54, 106, 12, 143, 1, 1, 0, nil, nil, 24, 22, 7, nil, 6, 0, 31, 67, 38, 13), table.pack(127, 195, 145, 8, 173, 127, 127, 131, 72, 101, 101, 14, 127, 90, 131, 72, 101, 101, 101, 101, 92, 127, 127, 131, 151, 5, 141, 17, 101, 92, 127, 74, 114, 21, 53, 36, 112, 59, 131, 101, 101, 92, 127, 127, 8, 14, 88, 127, 11, 127, 127), table.pack(0, 108, 108, 108, 108, 108, 108, 108, 108, 108, 108, 108, 108, 108, 108, 108, 108, 108, 108, 108, 108, 108, 0, 108, 108, 108, 108, 108, 108, 108, 108, 108, 108, 108, 108, 108, 108, 108, 0, 0, 0, 0, 0, 108, 108, 108, 108, 108, 5, 0), table.pack(0, 0, 80, 0, 120, 0, 0, 31, 0, 30, 31, 96, 0, 25, 31, 0, 30, 25, 31, 31, 0, 0, 0, 21, 22, 22, 22, nil, 21, 0, 0, 223, 200, nil, 218, 3, 11, 0, 31, 31, 31, 0, 0, 0, 0, 129, 11, 0, 122, 0, 0), table.pack(nil, nil, nil, nil, nil, nil, nil, nil, nil, 5, 44, nil, nil, nil, nil, nil, 32, 32, 32, 51, nil, nil, nil, nil, nil, nil, nil, nil, 7, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 30, 50, nil, nil, nil, 2), table.pack(0, 0, 1, 3, 0, 0, 0, 0, 0, nil, nil, 31, 0, 0, 0, 0, nil, nil, nil, nil, 31, 0, 0, 0, 160, 434, 22, 21, nil, 23, 0, 0, 49, 11, 152, 250, 0, 0, 0, nil, nil, 31, 0, 0, 5, 10, 0, 0, 22, 0, 0), 0, table.pack(nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 3, nil, nil, nil, nil, nil, 1))), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (84), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Character"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (3), (69), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (table.pack(table.pack(table.pack(2, 2), table.pack(4, 0)), table.pack(nil, nil, nil, nil, nil, nil, nil, 15, 15, 27, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 1, nil, 29, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 14), 25, table.pack(28, 1, 0, nil, 30, 23, 0, nil, nil, nil, 17, 27, 19, 362, 1, 1, 126, 0, 1, 0, 0, 0, nil, nil, nil, 17, 29, 12, 5, 32, 1, 1, 0, 0, 483, 6, 156, 15, nil, 7, 14), table.pack(127, 164, 9, 8, 127, 72, 131, 101, 101, 101, 92, 127, 127, 184, 195, 145, 238, 76, 127, 34, 90, 131, 101, 101, 101, 14, 127, 127, 127, 127, 112, 59, 90, 131, 76, 5, 141, 17, 101, 14, 127), table.pack(0, 130, 130, 130, 130, 0, 0, 0, 0, 0, 0, 0, 130, 1, 130, 130, 130, 130, 130, 130, 130, 130, 130, 130, 130, 130, 130, 0, 0, 130, 130, 130, 130, 130, 130, 130, 130, 130, 130, 130), table.pack(0, 0, 4, 0, 0, 0, 24, 24, 23, 24, 0, 0, 0, 424, 0, 80, 0, 4, 0, 0, 18, 24, 22, 18, 24, 18, 0, 0, 0, 0, 5, 0, 8, 14, 317, 134, 15, nil, 14, 216, 0), table.pack(nil, nil, nil, 2, nil, nil, nil, 36, 36, 29, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 18, 18, 13, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 30), table.pack(0, 5, 1, 5, 0, 0, 0, nil, nil, nil, 24, 0, 0, 402, 0, 1, 3, 170, 0, 22, 0, 0, nil, 305, nil, 24, 0, 0, 0, 0, 0, 0, 0, 0, 15, 143, 15, 8, nil, 16, 0), 0, table.pack(nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 17))), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (8), (0), (84), (12), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (9), (0), (32), (29) }; t.n = 176; return t end)(), 21, (function() local t = { (156), (0), (0), (4), (4), (nil), (13), (126), (168), (24), (41), (115), (116), (0), (38), (137), (0), (0), (93), (93), (476), (13), (105), (47), (0), (nil), (nil), (13), (83), (nil), (135), (40), (0), (0), (4), (0), (nil), (125), (3), (41), (112), (0), (nil), (0), (76), (3), (141), (0), (0), (nil), (nil), (13), (65), (250), (nil), (0), (9), (101), (95), (3), (175), (nil), (3), (45), (32), (0), (0), (nil), (131), (0), (nil), (0), (76), (11), (10), (149), (0), (0), (nil), (1), (23), (2), (58), (146), (84), (2), (38), (198), (81), (134), (1), (2), (nil), (0), (81), (0), (0), (nil), (nil), (13), (69), (nil), (0), (135), (8), (0), (171), (76), (nil), (nil), (11), (73), (135), (166), (503), (157), (0), (nil), (0), (0), (0), (6), (0), (4), (135), (16), (0), (41), (nil), (141), (133), (155), (9), (59), (91), (0), (13), (0), (0), (5), (38), (0), (190), (221), (10), (149), (223), (nil), (10), (4), (3), (37), (93), (4), (135), (1), (76), (0), (0), (0), (nil), (354), (nil), (nil), (13), (12), (135), (108), (0), (0), (0), (19), (nil), (nil), (nil), (nil), (13), (29) }; t.n = 178; return t end)(), (function() local t = { (127), (131), (34), (101), (101), (101), (92), (127), (127), (127), (156), (127), (127), (168), (156), (127), (34), (131), (101), (101), (101), (14), (127), (127), (131), (101), (101), (92), (127), (117), (62), (127), (84), (116), (186), (84), (117), (127), (83), (127), (127), (84), (117), (55), (127), (83), (127), (90), (131), (101), (101), (92), (127), (145), (8), (81), (145), (127), (127), (195), (143), (115), (7), (156), (127), (131), (181), (117), (127), (84), (117), (55), (127), (117), (48), (127), (84), (181), (117), (39), (127), (39), (127), (155), (114), (0), (124), (36), (156), (127), (127), (145), (8), (81), (127), (34), (131), (101), (101), (14), (127), (8), (81), (156), (127), (55), (83), (127), (117), (117), (1), (127), (57), (127), (14), (127), (138), (117), (173), (84), (84), (145), (22), (22), (78), (127), (84), (181), (117), (156), (127), (156), (127), (127), (127), (159), (127), (84), (116), (186), (127), (84), (46), (104), (128), (36), (15), (117), (127), (114), (0), (124), (36), (185), (127), (59), (127), (34), (131), (90), (101), (101), (101), (101), (92), (127), (25), (127), (90), (34), (131), (72), (101), (101), (101), (101), (14), (127) }; t.n = 178; return t end)(), (function() local t = { (0), (104), (104), (104), (104), (104), (104), (104), (120), (99), (115), (115), (115), (117), (128), (128), (110), (110), (110), (110), (110), (110), (110), (98), (99), (99), (99), (99), (99), (120), (120), (120), (107), (108), (107), (110), (110), (110), (115), (115), (120), (135), (135), (135), (98), (104), (104), (98), (98), (98), (98), (98), (98), (118), (118), (118), (119), (119), (101), (105), (105), (105), (105), (106), (106), (98), (98), (98), (98), (101), (101), (101), (101), (121), (122), (122), (98), (98), (98), (98), (98), (101), (101), (99), (100), (100), (100), (100), (100), (100), (104), (100), (100), (100), (100), (101), (101), (101), (101), (101), (101), (119), (119), (120), (120), (110), (111), (111), (121), (121), (121), (121), (120), (120), (112), (115), (116), (116), (116), (117), (117), (117), (117), (117), (117), (110), (104), (104), (104), (104), (104), (98), (98), (104), (100), (117), (117), (129), (130), (129), (129), (115), (115), (115), (115), (115), (115), (115), (115), (123), (123), (123), (123), (124), (124), (98), (0), (115), (115), (115), (115), (115), (115), (115), (115), (115), (120), (120), (120), (120), (120), (120), (120), (120), (120), (120), (120) }; t.n = 177; return t end)(), (function() local t = { (0), (20), (0), (20), (18), (20), (0), (0), (0), (0), (3), (0), (0), (0), (4), (0), (0), (20), (18), (20), (20), (175), (0), (0), (20), (20), (20), (0), (0), (8), (10), (0), (nil), (5), (0), (nil), (4), (0), (0), (0), (0), (nil), (3), (3), (0), (0), (0), (14), (20), (14), (20), (0), (0), (nil), (0), (8), (nil), (0), (0), (1), (198), (239), (0), (3), (0), (nil), (1), (1), (0), (nil), (3), (3), (0), (10), (3), (0), (nil), (1), (1), (9), (0), (90), (0), (0), (103), (97), (1), (245), (2), (0), (0), (nil), (0), (2), (0), (0), (20), (18), (20), (192), (0), (0), (9), (8), (0), (4), (0), (0), (2), (9), (10), (0), (16), (0), (400), (0), (nil), (3), (4), (nil), (nil), (nil), (2), (0), (5), (0), (nil), (3), (3), (3), (0), (1), (0), (0), (0), (5), (0), (nil), (6), (0), (0), (nil), (3), (118), (66), (148), (29), (3), (0), (241), (201), (10), (88), (7), (0), (0), (0), (0), (20), (14), (20), (18), (14), (20), (0), (0), (1), (0), (14), (0), (20), (0), (19), (18), (14), (20), (116), (0) }; t.n = 178; return t end)(), (function() local t = { (nil), (nil), (nil), (nil), (nil), (91), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (84), (10), (nil), (nil), ("Health"), (nil), (nil), (nil), (nil), (nil), (nil), ("wait"), (nil), (nil), (nil), (nil), (nil), ("wait"), (nil), (nil), (nil), (nil), (nil), (nil), (66), (24), (nil), (nil), (nil), ("Humanoid"), (nil), (nil), (nil), (nil), (nil), (nil), ("Chicken"), (nil), (nil), (nil), (nil), (nil), ("AxeAuraChicken"), (nil), (nil), ("wait"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("AxeAuraZombie"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("HumanoidRootPart"), (nil), (nil), (nil), (nil), (71), (59), (nil), (nil), ("HumanoidRootPart"), (nil), (nil), (nil), (nil), (nil), (nil), ("Position"), ("Position"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("huge"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("AxeAuraChicken"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("AxeAuraZombie"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (54), (nil), (117), (116), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (113), (113), (113), (9) }; t.n = 176; return t end)(), (function() local t = { (0), (0), (18), (nil), (nil), (476), (20), (0), (0), (0), (0), (0), (0), (0), (0), (0), (18), (0), (nil), (nil), (nil), (20), (0), (0), (0), (nil), (nil), (20), (0), (10), (nil), (0), (4), (29), (0), (4), (4), (0), (0), (0), (0), (3), (3), (0), (0), (0), (0), (0), (0), (nil), (100), (20), (0), (7), (10), (0), (7), (0), (0), (0), (4), (80), (0), (0), (0), (1), (0), (1), (0), (3), (80), (0), (0), (10), (135), (0), (1), (0), (1), (0), (0), (0), (0), (nil), (8), (236), (198), (205), (0), (0), (0), (1), (4), (0), (0), (18), (0), (nil), (nil), (20), (0), (11), (0), (0), (0), (0), (81), (0), (10), (11), (10), (0), (249), (0), (290), (0), (3), (3), (155), (5), (6), (6), (6), (5), (0), (0), (3), (255), (3), (0), (0), (0), (0), (0), (0), (53), (0), (5), (22), (0), (0), (3), (27), (252), (83), (46), (163), (3), (0), (52), (208), (138), (148), (0), (0), (0), (0), (18), (0), (0), (nil), (nil), (nil), (nil), (20), (0), (7), (0), (0), (18), (0), (0), (nil), (nil), (nil), (nil), (20), (0) }; t.n = 178; return t end)(), 0, (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("pcall"), (nil), (nil), ("task"), (nil), (nil), (nil), (nil), (nil), ("task"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("FindFirstChildOfClass"), (nil), (nil), ("FindFirstChild"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("getgenv"), (nil), (nil), (nil), ("task"), (nil), (nil), (nil), (nil), (nil), (nil), ("getgenv"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("FindFirstChild"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("math"), (nil), (nil), ("pairs"), ("workspace"), ("GetChildren"), (nil), (nil), (nil), (nil), ("getgenv"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("pcall"), (nil), (nil), (nil), ("getgenv") }; t.n = 142; return t end)()), {}))
	;(nil --[[ constant not decoded ]])[49](v5[1], t3[1])
	;(t1[1])[15] = v5[1]

	local v6 = table.pack((nil --[[ constant not decoded ]])[57](table.pack(table.pack(table.pack(12, 1), table.pack(13, 1), table.pack(2, 1)), table.pack(nil, nil, nil, nil, nil, nil, nil, nil, 1, 3, 1, 0, 33, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 221, 4881, nil, nil, 33, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, table.pack(table.pack(table.pack(2, 2), table.pack(3, 1), table.pack(1, 1), table.pack(2, 1)), table.pack(nil, nil, nil, nil, nil, nil, nil, nil, 42, nil, nil, nil, nil, "Position", nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 3, 195, 42, nil, nil, nil, nil, nil, nil, 0, 0, 7, 3, 12), 28, table.pack(4, 349, 18, 19, 11, 18, 334, 18, nil, 10, 31, 47, 232, 6, nil, 0, 0, 1, 22, 343, 5, 32, 1, 191, 0, 0, nil, nil, nil, 20, 42, 24, 0, 0, 26, nil, nil, nil, nil, nil, 20, 12, 1, 1, 62, 4, 21, 0, 0, 454, 2, 1), table.pack(127, 8, 39, 127, 127, 5, 141, 17, 101, 92, 127, 127, 8, 155, 8, 88, 88, 112, 127, 8, 127, 127, 59, 16, 131, 90, 101, 101, 101, 14, 127, 127, 131, 34, 72, 101, 101, 101, 101, 101, 14, 127, 195, 230, 49, 195, 127, 90, 131, 162, 156, 127), table.pack(0, 151, 151, 151, 0, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 49, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151), table.pack(0, 0, 5, 0, 0, 18, 18, nil, 17, 0, 0, 0, 0, 250, 136, 8, 9, 9, 0, 0, 0, 0, 0, 116, 27, 21, 27, 21, 27, 47, 0, 0, 27, 0, 0, 25, 26, 25, 26, 27, 82, 0, 0, 80, 1, 2, 0, 11, 17, 18, 18, 0), table.pack(nil, nil, nil, nil, nil, nil, nil, nil, 12, nil, nil, nil, nil, nil, "Head", nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 45, 45, 32, nil, nil, nil, nil, nil, nil, 17, 15, 15, 14, 22), table.pack(0, 18, 0, 0, 0, 502, 18, 11, nil, 19, 0, 0, 5, nil, 234, 0, 90, 0, 0, 18, 0, 0, 0, 170, 0, 0, nil, nil, nil, 27, 0, 0, 0, 25, 0, nil, nil, nil, nil, nil, 27, 0, 0, 1, 0, 0, 0, 0, 0, 276, 0, 0), 0, table.pack(nil, nil, nil, nil, nil, nil, nil, 44)), nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 4, 0, 21), 24, (function() local t = { (0), (0), (nil), (42), (54), (0), (0), (22), (nil), (nil), (nil), (nil), (nil), (16), (33), (3), (0), (19), (37), (3), (43), (38), (0), (nil), (14), (nil), (14), (nil), (6), (55), (43), (15), (30), (1), (3), (43), (32), (58), (191), (0), (4), (19), (1), (0), (48), (210), (140), (nil), (37), (211), (nil), (3), (1), (57), (33), (33), (326), (0), (0), (0), (nil), (nil), (nil), (16), (21) }; t.n = 65; return t end)(), (function() local t = { (84), (181), (117), (32), (127), (34), (131), (93), (101), (101), (101), (101), (101), (14), (127), (195), (181), (156), (127), (83), (127), (127), (131), (151), (5), (141), (17), (101), (92), (127), (156), (127), (127), (195), (22), (32), (127), (127), (84), (116), (186), (127), (59), (84), (114), (56), (33), (135), (36), (143), (115), (186), (83), (127), (127), (127), (100), (127), (34), (131), (101), (101), (101), (14), (127) }; t.n = 65; return t end)(), table.pack(145, 145, 145, 145, 145, 146, 146, 146, 146, 146, 146, 146, 146, 146, 146, 148, 148, 149, 149, 147, 147, 149, 146, 146, 146, 146, 146, 146, 146, 146, 147, 147, 147, 146, 146, 147, 147, 149, 150, 151, 150, 150, 145, 155, 155, 155, 155, 155, 155, 155, 155, 155, 145, 145, 146, 146, 9, 145, 149, 149, 149, 149, 149, 149), (function() local t = { (nil), (1), (1), (1), (0), (0), (23), (0), (22), (22), (22), (21), (23), (92), (0), (1), (3), (3), (0), (0), (0), (0), (13), (14), (14), (14), (nil), (13), (0), (0), (2), (0), (0), (0), (1), (1), (0), (0), (nil), (5), (0), (0), (0), (nil), (102), (247), (3), (10), (177), (250), (234), (0), (0), (0), (0), (0), (387), (0), (0), (23), (21), (23), (23), (232), (0) }; t.n = 65; return t end)(), table.pack(nil, nil, "GunKillAll", nil, nil, nil, nil, nil, 36, 17, 16, 16, 56, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 87, nil, -5188, nil, 55, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, "wait", nil, nil, 0.1, nil, nil, nil, nil, nil, nil, nil, nil, nil, 39, 39, 38), (function() local t = { (1), (0), (1), (0), (0), (21), (0), (0), (nil), (nil), (nil), (nil), (nil), (23), (0), (0), (0), (0), (0), (0), (0), (0), (0), (nil), (nil), (14), (13), (nil), (15), (0), (0), (0), (0), (0), (1), (0), (0), (0), (255), (5), (0), (0), (0), (3), (230), (3), (57), (214), (127), (4), (231), (0), (0), (0), (0), (0), (79), (0), (21), (0), (nil), (nil), (nil), (23), (0) }; t.n = 65; return t end)(), 0, table.pack("getgenv", nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 34, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, "pcall", nil, nil, nil, nil, "task")), {}))
	;(nil --[[ constant not decoded ]])[49](v6[1], t3[1])
	;(t1[1])[16] = v6[1]
	;(t1[1])[17] = nil

	local v7 = table.pack((nil --[[ constant not decoded ]])[57](table.pack(table.pack(table.pack(17, 0), table.pack(15, 1)), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (86), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (12), (0), (3), (79), (nil), (nil), (nil), (nil), (84), (7), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (11), (44), (32), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (310) }; t.n = 84; return t end)(), 21, (function() local t = { (50), (0), (340), (0), (1), (0), (31), (0), (250), (6), (204), (48), (30), (nil), (17), (86), (1), (1), (60), (1), (189), (51), (81), (0), (nil), (nil), (13), (86), (135), (54), (16), (7), (0), (31), (53), (0), (19), (0), (nil), (nil), (nil), (nil), (13), (79), (0), (0), (nil), (nil), (13), (7), (32), (35), (28), (22), (11), (263), (11), (nil), (3), (1), (15), (0), (249), (181), (72), (nil), (208), (2), (1), (1), (1), (0), (0), (nil), (nil), (nil), (13), (32), (415), (11), (52), (0), (0), (11), (51), (19), (0), (19), (21), (176), (251), (231), (nil), (1), (30) }; t.n = 95; return t end)(), (function() local t = { (127), (84), (117), (164), (186), (117), (127), (84), (46), (104), (128), (36), (15), (117), (127), (127), (59), (39), (127), (143), (115), (127), (127), (131), (101), (101), (92), (127), (8), (127), (127), (127), (164), (32), (127), (131), (72), (34), (101), (101), (101), (101), (14), (127), (90), (131), (101), (101), (92), (127), (127), (127), (127), (127), (5), (141), (17), (101), (92), (127), (127), (84), (114), (56), (33), (135), (36), (195), (7), (142), (59), (131), (90), (101), (101), (101), (92), (127), (38), (39), (127), (131), (90), (44), (156), (127), (84), (46), (104), (128), (36), (15), (117), (39), (127) }; t.n = 95; return t end)(), (function() local t = { (0), (160), (160), (160), (160), (160), (160), (161), (161), (161), (161), (161), (161), (161), (161), (161), (161), (161), (161), (160), (160), (160), (160), (161), (161), (161), (161), (161), (160), (160), (161), (161), (160), (160), (160), (160), (160), (160), (160), (160), (160), (160), (160), (160), (161), (161), (161), (161), (161), (161), (160), (160), (160), (160), (160), (160), (160), (160), (160), (160), (161), (162), (162), (162), (162), (162), (162), (162), (162), (162), (162), (160), (160), (160), (160), (160), (160), (160), (126), (160), (160), (160), (160), (160), (160), (160), (161), (161), (161), (161), (161), (161), (161), (161) }; t.n = 94; return t end)(), (function() local t = { (0), (nil), (1), (0), (0), (0), (0), (nil), (1), (132), (188), (50), (239), (1), (0), (0), (0), (61), (0), (57), (4), (0), (0), (20), (20), (20), (0), (0), (0), (0), (0), (0), (0), (1), (0), (20), (0), (0), (18), (19), (20), (20), (93), (0), (14), (20), (14), (20), (0), (0), (0), (0), (0), (0), (11), (11), (nil), (10), (179), (0), (0), (nil), (0), (61), (1), (10), (84), (1), (0), (0), (0), (20), (14), (20), (14), (20), (0), (0), (507), (54), (0), (10), (4), (172), (11), (0), (nil), (1), (2), (189), (68), (92), (1), (61), (0) }; t.n = 95; return t end)(), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("AxeAuraZombie"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (87), (16), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (59), (59), (59), (52), (nil), (nil), (nil), (nil), (62), (32), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (23), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("spawn"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (84), (84), (51), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("AxeAuraChicken") }; t.n = 93; return t end)(), (function() local t = { (0), (1), (1), (2), (0), (0), (0), (1), (43), (240), (105), (151), (201), (1), (0), (0), (0), (0), (0), (11), (177), (0), (0), (0), (nil), (nil), (20), (0), (11), (0), (0), (0), (1), (0), (0), (0), (0), (18), (nil), (nil), (nil), (nil), (20), (0), (0), (0), (nil), (nil), (20), (0), (0), (0), (0), (0), (515), (11), (4), (nil), (210), (0), (0), (1), (55), (1), (17), (122), (97), (0), (0), (0), (0), (0), (0), (nil), (nil), (nil), (20), (0), (276), (0), (0), (0), (0), (nil), (0), (0), (1), (138), (65), (214), (186), (146), (1), (0), (0) }; t.n = 95; return t end)(), 0, (function() local t = { (nil), ("task"), (nil), (nil), (nil), (nil), (nil), ("getgenv"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (6), (nil), (nil), (nil), (nil), ("task"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("getgenv") }; t.n = 87; return t end)()), {}))
	;(nil --[[ constant not decoded ]])[49](v7[1], t3[1])
	;(t1[1])[18] = v7[1]

	if t3[6] then
		if not (t3[6])[17] then
			(t3[6])[17] = { 17, t1[1] }
		end
	end
	;(t1[1])[19] = nil
	;(t1[1])[20] = nil
	;(t1[1])[21] = 16
	;(t1[1])[22] = 16

	local v8 = table.pack((nil --[[ constant not decoded ]])[57](table.pack(table.pack(table.pack(9, 1), table.pack(19, 0), table.pack(5, 1), table.pack(4, 1), table.pack(21, 0)), (function() local t = { (nil), (nil), (nil), (297), (2040), (nil), (nil), (92), (nil), (nil), (nil), ("Heartbeat"), (nil), (table.pack(table.pack(table.pack(0, 2), table.pack(3, 1), table.pack(4, 1), table.pack(1, 2), table.pack(3, 2), table.pack(4, 2)), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (5), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Character"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (7), (57), (nil), (nil), (nil), (nil), (nil), (nil), (8), (7), (nil), (nil), (nil), (nil), (nil), (nil), (52), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (5), (5), (135), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (5), (91), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (84), (171), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (17), (nil), (nil), (nil), (nil), (nil), (5), (245), (nil), (nil), (nil), (nil), (117), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (195), (0), (4), (52), (nil), (nil), (nil), (nil), (0), (3), (220), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (17), (117), (1) }; t.n = 266; return t end)(), 27, (function() local t = { (34), (204), (11), (0), (0), (25), (490), (490), (166), (19), (177), (213), (nil), (270), (0), (176), (111), (5), (5), (135), (2), (72), (12), (nil), (371), (0), (17), (76), (11), (5), (218), (62), (51), (234), (1), (2), (98), (66), (5), (60), (0), (23), (126), (127), (109), (5), (17), (nil), (337), (0), (170), (3), (5), (5), (0), (145), (137), (374), (5), (5), (0), (47), (264), (5), (6), (218), (2), (nil), (0), (98), (0), (25), (nil), (415), (19), (57), (43), (1), (0), (0), (480), (295), (nil), (19), (128), (17), (486), (17), (253), (9), (217), (71), (5), (0), (nil), (313), (0), (268), (233), (232), (269), (0), (0), (nil), (nil), (nil), (19), (135), (4), (5), (28), (127), (392), (5), (176), (5), (255), (0), (nil), (373), (19), (91), (0), (212), (0), (203), (78), (150), (0), (nil), (nil), (nil), (nil), (4), (115), (38), (169), (366), (205), (0), (0), (nil), (nil), (19), (171), (nil), (223), (0), (255), (42), (0), (0), (414), (4), (19), (235), (0), (0), (287), (425), (19), (245), (0), (0), (nil), (nil), (19), (122), (162), (276), (101), (0), (0), (nil), (3), (275), (117), (5), (5), (0), (nil), (200), (240), (0), (374), (256), (0), (0), (25), (0), (406), (406), (406), (485), (19), (52), (0), (0), (nil), (nil), (nil), (19), (220), (70), (127), (17), (211), (3), (3), (3), (253), (271), (85), (127), (392), (5), (204), (186), (5), (183), (3), (3), (3), (161), (3), (6), (214), (65), (3), (3), (3), (32), (171), (220), (207), (0), (0), (nil), (205), (56), (0), (28), (100), (156), (198), (127), (135), (160), (19), (109), (107), (5), (38), (0), (51), (3), (540), (127), (127), (77), (0), (25), (0), (477), (296), (198), (19), (1), (260), (0), (nil), (nil), (nil), (nil), (108), (233), (243) }; t.n = 277; return t end)(), (function() local t = { (127), (32), (127), (131), (34), (72), (101), (101), (101), (14), (127), (127), (117), (117), (81), (32), (127), (195), (145), (143), (193), (11), (127), (117), (117), (81), (32), (127), (117), (99), (32), (127), (32), (127), (155), (185), (32), (127), (195), (145), (84), (127), (127), (117), (117), (1), (127), (117), (117), (81), (127), (59), (195), (145), (84), (127), (127), (213), (195), (145), (84), (127), (117), (164), (89), (127), (145), (8), (81), (127), (131), (72), (101), (101), (14), (127), (127), (59), (131), (34), (101), (101), (101), (14), (127), (5), (141), (17), (101), (92), (127), (195), (145), (84), (117), (117), (81), (127), (32), (127), (127), (34), (131), (101), (101), (101), (92), (127), (126), (1), (127), (117), (117), (1), (127), (47), (127), (131), (101), (101), (92), (127), (84), (117), (84), (127), (127), (127), (84), (117), (8), (8), (8), (126), (127), (32), (127), (8), (127), (90), (131), (101), (101), (92), (127), (117), (117), (81), (32), (127), (34), (131), (101), (101), (92), (127), (34), (131), (101), (101), (92), (127), (131), (90), (101), (101), (92), (127), (127), (127), (127), (84), (181), (117), (39), (127), (127), (122), (145), (84), (117), (117), (127), (84), (117), (127), (90), (131), (72), (34), (101), (101), (101), (101), (14), (127), (34), (131), (101), (101), (101), (92), (127), (127), (127), (39), (127), (164), (145), (186), (127), (8), (127), (63), (117), (47), (127), (127), (39), (127), (195), (145), (186), (114), (134), (108), (124), (36), (145), (186), (164), (127), (127), (127), (127), (34), (131), (20), (32), (127), (81), (32), (127), (127), (173), (117), (114), (56), (33), (135), (36), (47), (127), (142), (127), (127), (100), (117), (100), (127), (131), (72), (90), (101), (101), (101), (14), (127), (127), (84), (117), (8), (8), (8), (127), (127), (127) }; t.n = 277; return t end)(), (function() local t = { (0), (196), (196), (198), (198), (198), (198), (198), (198), (198), (198), (196), (195), (195), (195), (195), (195), (195), (195), (195), (195), (195), (195), (194), (194), (194), (194), (194), (199), (199), (199), (199), (188), (188), (184), (185), (185), (185), (194), (194), (194), (194), (197), (194), (194), (194), (194), (193), (193), (193), (193), (189), (197), (197), (197), (197), (197), (192), (193), (193), (193), (193), (199), (199), (199), (199), (185), (185), (185), (185), (192), (192), (192), (192), (192), (192), (194), (200), (197), (197), (197), (197), (197), (197), (197), (197), (197), (197), (197), (197), (197), (196), (196), (196), (196), (196), (196), (196), (186), (186), (198), (193), (193), (193), (193), (193), (193), (193), (198), (198), (198), (195), (195), (195), (195), (197), (197), (196), (196), (196), (196), (196), (191), (191), (192), (192), (197), (197), (197), (197), (197), (197), (197), (197), (197), (193), (193), (197), (197), (186), (186), (186), (186), (186), (186), (197), (197), (197), (197), (197), (197), (197), (197), (197), (197), (197), (193), (193), (193), (193), (193), (193), (191), (191), (191), (191), (191), (191), (191), (193), (193), (186), (186), (186), (186), (186), (196), (198), (198), (198), (198), (198), (198), (199), (199), (199), (197), (197), (197), (197), (197), (197), (197), (197), (197), (197), (187), (187), (187), (187), (187), (187), (187), (192), (197), (197), (197), (188), (188), (188), (188), (197), (197), (196), (196), (196), (196), (197), (199), (199), (187), (187), (187), (187), (187), (187), (187), (187), (187), (187), (188), (188), (186), (187), (188), (197), (197), (197), (197), (197), (198), (198), (198), (193), (104), (193), (193), (193), (193), (193), (193), (193), (193), (188), (188), (198), (199), (200), (200), (200), (196), (196), (196), (196), (196), (196), (196), (196), (196), (198), (198), (198), (198), (198), (198), (186) }; t.n = 276; return t end)(), (function() local t = { (0), (5), (0), (26), (0), (0), (25), (24), (26), (98), (0), (0), (7), (7), (5), (5), (0), (4), (39), (150), (94), (nil), (0), (7), (7), (5), (5), (0), (4), (nil), (5), (0), (3), (0), (0), (1), (2), (0), (4), (39), (nil), (0), (0), (3), (5), (4), (0), (27), (7), (5), (0), (0), (4), (39), (nil), (0), (0), (4), (4), (39), (nil), (0), (4), (0), (5), (0), (nil), (0), (2), (0), (26), (0), (25), (26), (94), (0), (0), (0), (26), (0), (24), (24), (26), (37), (0), (17), (17), (505), (16), (0), (0), (4), (39), (nil), (7), (7), (5), (0), (2), (0), (0), (0), (26), (26), (24), (26), (0), (0), (0), (4), (0), (3), (5), (4), (0), (4), (0), (26), (26), (26), (0), (0), (nil), (3), (nil), (0), (0), (0), (nil), (5), (0), (0), (0), (0), (0), (5), (0), (0), (0), (20), (26), (20), (26), (0), (0), (7), (7), (5), (5), (0), (0), (26), (24), (26), (0), (0), (0), (26), (24), (26), (0), (0), (26), (20), (20), (26), (0), (0), (0), (0), (0), (nil), (3), (3), (168), (0), (0), (146), (39), (nil), (7), (7), (0), (nil), (5), (0), (20), (26), (0), (0), (20), (24), (25), (26), (115), (0), (0), (26), (24), (26), (26), (0), (0), (0), (0), (85), (0), (0), (nil), (0), (0), (0), (0), (3), (5), (4), (0), (0), (256), (0), (1), (nil), (0), (40), (49), (198), (2), (11), (nil), (0), (0), (0), (0), (0), (0), (0), (16), (430), (183), (0), (5), (5), (0), (0), (248), (3), (148), (5), (5), (254), (72), (4), (0), (0), (0), (0), (245), (3), (5), (0), (26), (0), (20), (25), (20), (26), (44), (0), (0), (nil), (5), (0), (0), (0), (0), (0), (0) }; t.n = 277; return t end)(), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("KeyCode"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("KeyCode"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("KeyCode"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("HumanoidRootPart"), (nil), (nil), (nil), (nil), (48), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (127), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("KeyCode"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (40), (40), (171), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (92), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("new"), (0), (1), (0), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (172), (233), (nil), (nil), ("KeyCode"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (58), (169), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Fly"), (nil), (nil), (nil), (nil), (nil), (nil), ("KeyCode"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (221), (221), (234), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (219), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("new"), (0), (1), (0) }; t.n = 274; return t end)(), (function() local t = { (0), (0), (0), (0), (24), (0), (nil), (nil), (373), (26), (0), (0), (7), (7), (0), (0), (0), (0), (5), (7), (29), (240), (0), (7), (7), (0), (0), (0), (5), (5), (0), (0), (0), (0), (nil), (0), (0), (0), (0), (106), (7), (0), (0), (5), (5), (4), (0), (7), (7), (0), (0), (0), (0), (5), (7), (0), (0), (4), (0), (5), (7), (0), (5), (6), (5), (0), (1), (4), (0), (0), (0), (0), (nil), (nil), (26), (0), (0), (0), (0), (24), (nil), (nil), (4), (26), (0), (311), (17), (14), (nil), (18), (0), (0), (5), (7), (7), (7), (0), (0), (0), (0), (0), (24), (0), (nil), (nil), (nil), (26), (0), (5), (4), (0), (5), (5), (4), (0), (4), (0), (0), (nil), (nil), (26), (0), (3), (3), (4), (0), (0), (0), (5), (5), (146), (20), (62), (5), (0), (0), (0), (17), (0), (0), (0), (nil), (nil), (26), (0), (7), (7), (0), (0), (0), (24), (0), (nil), (511), (26), (0), (24), (0), (nil), (nil), (26), (0), (0), (0), (nil), (394), (26), (0), (0), (0), (0), (3), (0), (3), (0), (0), (0), (204), (5), (7), (7), (7), (0), (5), (5), (0), (0), (0), (0), (24), (nil), (nil), (nil), (nil), (26), (0), (24), (0), (nil), (nil), (nil), (26), (0), (0), (0), (0), (0), (3), (3), (0), (0), (150), (0), (5), (5), (4), (0), (0), (0), (0), (0), (3), (0), (152), (52), (239), (229), (121), (3), (0), (3), (0), (0), (0), (0), (14), (0), (17), (0), (0), (0), (0), (0), (0), (415), (184), (192), (5), (187), (207), (11), (4), (0), (3), (0), (0), (140), (5), (2), (0), (0), (0), (0), (nil), (nil), (nil), (26), (0), (0), (5), (5), (6), (7), (8), (0), (0), (0) }; t.n = 277; return t end)(), 0, (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Enum"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Enum"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Enum"), (nil), (nil), (nil), (nil), (nil), ("Enum"), (nil), (nil), (nil), (nil), (nil), ("FindFirstChild"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Enum"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("workspace"), (nil), ("Vector3"), (nil), (nil), (nil), ("Vector3"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("getgenv"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Enum"), (nil), (nil), (nil), ("Vector3"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Disconnect"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Destroy"), (nil), (nil), (nil), (nil), (nil), (nil), ("Destroy"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Vector3") }; t.n = 270; return t end)())), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (59), (43), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (127), (17), (68), (nil), (nil), (nil), (nil), (nil), (nil), (0), (4), (0), (15), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (3), (104), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (1000000), (nil), (nil), (nil), (nil), ("Character"), (nil), (nil), (nil), (nil), (nil), (nil), (17), (17), (49) }; t.n = 102; return t end)(), 27, (function() local t = { (24), (0), (0), (nil), (17), (nil), (17), (nil), (9), (92), (45), (5), (5), (0), (72), (nil), (nil), (nil), (nil), (4), (5), (0), (nil), (29), (49), (nil), (4), (0), (50), (nil), (nil), (nil), (82), (68), (0), (0), (0), (nil), (nil), (nil), (19), (43), (58), (2), (42), (2), (nil), (0), (96), (92), (15), (0), (0), (nil), (nil), (nil), (19), (68), (3), (0), (0), (25), (nil), (nil), (nil), (nil), (19), (15), (3), (0), (nil), (25), (0), (5), (1), (104), (0), (0), (nil), (nil), (19), (104), (4), (220), (231), (5), (181), (nil), (2), (2), (11), (270), (1), (2), (96), (10), (43), (25), (0), (nil), (nil), (nil), (19), (49), (0), (239), (22), (111), (nil), (199), (nil), (33) }; t.n = 112; return t end)(), (function() local t = { (127), (131), (90), (151), (5), (141), (17), (101), (14), (127), (127), (155), (145), (116), (127), (117), (8), (8), (8), (126), (17), (84), (117), (127), (127), (8), (7), (84), (127), (8), (8), (8), (127), (127), (131), (34), (90), (101), (101), (101), (14), (127), (127), (39), (127), (145), (8), (81), (127), (127), (127), (90), (131), (101), (101), (101), (14), (127), (59), (34), (131), (93), (101), (101), (101), (101), (14), (127), (7), (84), (117), (127), (81), (142), (59), (127), (131), (34), (101), (101), (92), (127), (126), (114), (21), (53), (36), (101), (17), (17), (127), (148), (155), (185), (32), (127), (127), (93), (131), (101), (101), (101), (92), (127), (84), (114), (56), (33), (135), (36), (8), (127) }; t.n = 112; return t end)(), (function() local t = { (0), (173), (173), (173), (173), (173), (173), (173), (173), (173), (174), (183), (183), (184), (184), (178), (178), (178), (178), (178), (178), (179), (179), (179), (173), (177), (177), (178), (178), (179), (179), (179), (179), (176), (175), (175), (175), (175), (175), (175), (175), (175), (175), (175), (175), (174), (174), (174), (174), (173), (178), (176), (176), (176), (176), (176), (176), (176), (175), (178), (178), (178), (178), (178), (178), (178), (178), (178), (176), (177), (177), (177), (183), (183), (183), (176), (176), (176), (176), (176), (176), (176), (179), (179), (179), (179), (179), (180), (181), (182), (182), (56), (173), (174), (174), (174), (175), (173), (173), (173), (173), (173), (173), (173), (176), (176), (176), (176), (176), (176), (176) }; t.n = 111; return t end)(), (function() local t = { (0), (16), (10), (17), (17), (17), (nil), (16), (90), (0), (0), (2), (nil), (7), (0), (5), (0), (0), (0), (0), (nil), (nil), (5), (0), (0), (0), (0), (nil), (0), (0), (0), (0), (0), (0), (26), (0), (20), (24), (20), (26), (33), (0), (0), (75), (0), (nil), (0), (2), (0), (0), (0), (20), (26), (20), (20), (26), (215), (0), (0), (0), (26), (0), (24), (26), (25), (26), (100), (0), (0), (nil), (4), (0), (5), (0), (0), (0), (26), (0), (24), (26), (0), (0), (0), (104), (nil), (90), (143), (4), (nil), (nil), (0), (173), (0), (1), (2), (0), (0), (0), (26), (25), (25), (26), (0), (0), (nil), (215), (146), (3), (35), (218), (0), (0) }; t.n = 112; return t end)(), (function() local t = { (nil), (nil), (nil), (472), (nil), (-2682), (nil), (50), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("new"), (1e9), (1e9), (1e9), (nil), (nil), (nil), ("new"), (nil), (nil), ("BodyGyro"), (nil), (nil), (nil), (1e9), (1e9), (1e9), (nil), (nil), (nil), (nil), (nil), (69), (59), (97), (nil), (nil), (nil), (nil), (nil), (nil), ("HumanoidRootPart"), (nil), (nil), (nil), (nil), (nil), (nil), (24), (21), (34), (nil), (nil), (nil), (nil), (nil), (nil), (33), (83), (83), (51), (nil), (nil), (nil), (nil), ("new"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (105), (76), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("P"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (4), (5), (25), (nil), (nil), (nil), (nil), (nil), (nil), ("new"), (nil), ("BodyVelocity") }; t.n = 111; return t end)(), (function() local t = { (0), (0), (0), (nil), (nil), (17), (10), (nil), (18), (0), (0), (nil), (5), (9), (0), (5), (6), (7), (8), (5), (3), (5), (5), (0), (0), (5), (0), (5), (0), (6), (7), (8), (0), (0), (0), (24), (0), (nil), (nil), (nil), (26), (0), (0), (0), (0), (1), (4), (0), (0), (0), (0), (0), (0), (nil), (nil), (nil), (26), (0), (0), (24), (0), (0), (nil), (nil), (nil), (nil), (26), (0), (0), (4), (4), (0), (0), (1), (0), (0), (0), (24), (nil), (nil), (26), (0), (5), (58), (4), (24), (122), (nil), (3), (4), (0), (396), (nil), (0), (0), (0), (0), (0), (0), (nil), (nil), (nil), (26), (0), (3), (39), (3), (215), (232), (226), (4), (0) }; t.n = 112; return t end)(), 0, (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (49), (nil), (nil), (nil), (nil), (nil), ("Connect"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("MaxForce"), ("Vector3"), (nil), (nil), (nil), (nil), (nil), ("Vector3"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("FindFirstChild"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Instance"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("MaxTorque"), (nil), (nil), (nil), ("Parent"), ("Parent"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Instance") }; t.n = 105; return t end)()), {}))
	;(nil --[[ constant not decoded ]])[49](v8[1], t3[1])
	;(t1[1])[24] = v8[1]

	if t3[6] then
		if (t3[6])[19] then
			if not (t3[6])[21] then
				(t3[6])[21] = { 21, t1[1] }
			end
		else
			(t3[6])[19] = { 19, t1[1] }

			if not (t3[6])[21] then
				(t3[6])[21] = { 21, t1[1] }
			end
		end
	end

	local v9 = table.pack((nil --[[ constant not decoded ]])[57](table.pack(table.pack(table.pack(20, 0), table.pack(5, 1), table.pack(9, 1), table.pack(22, 0)), table.pack(nil, nil, nil, nil, nil, nil, nil, nil, nil, "Stepped", nil, table.pack(table.pack(table.pack(2, 2), table.pack(3, 2)), table.pack(nil, nil, "Character", nil, nil, nil, nil, "Character", nil, nil, nil, nil, nil, nil, nil, nil, 50), 5, table.pack(7, 14, 1, 1, nil, 0, 12, 1, 12, 2, 322, 1, 11, 1, 1, 2, nil, 11), table.pack(127, 127, 155, 145, 8, 81, 127, 155, 32, 127, 158, 59, 32, 127, 164, 17, 101, 127), table.pack(0, 208, 207, 207, 207, 207, 207, 207, 207, 207, 58, 208, 208, 208, 209, 209, 210), table.pack(0, 0, 0, nil, 0, 1, 0, 0, 1, 0, 33, 0, 1, 0, 0, nil, 1, 0), table.pack(nil, nil, nil, nil, "Humanoid", nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, "JumpPower"), table.pack(0, 0, nil, 1, 3, 0, 0, nil, 0, 0, 268, 0, 0, 0, 2, 1, nil, 0), 0, table.pack(nil, nil, nil, "FindFirstChildOfClass", nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, "WalkSpeed"))), 4, table.pack(0, 9, 7, 0, 1, 1, 9, 3, 431, 1, 1, 0, 0, 1, 1), table.pack(164, 32, 127, 164, 145, 186, 127, 127, 118, 155, 145, 116, 81, 142, 59), table.pack(205, 205, 205, 205, 205, 205, 205, 205, 10, 206, 206, 207, 206, 206), table.pack(0, 1, 0, 0, nil, 0, 0, 0, 105, 1, nil, 3, 1, 0, 0), table.pack(), table.pack(1, 0, 0, 1, 1, 0, 0, 0, 353, nil, 1, 36, 0, 0, 0), 0, table.pack(nil, nil, nil, nil, "Disconnect", nil, nil, nil, nil, nil, "Connect")), {}))
	;(nil --[[ constant not decoded ]])[49](v9[1], t3[1])
	;(t1[1])[25] = v9[1]

	if t3[6] then
		if (t3[6])[20] then
			if not (t3[6])[22] then
				(t3[6])[22] = { 22, t1[1] }
			end
		else
			(t3[6])[20] = { 20, t1[1] }

			if not (t3[6])[22] then
				(t3[6])[22] = { 22, t1[1] }
			end
		end
	end

	local v10 = table.pack((nil --[[ constant not decoded ]])[57](table.pack(table.pack(table.pack(5, 1)), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (116), (nil), (0), (2), (nil), (nil), ("ESP_Highlight"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (116), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Heartbeat"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (table.pack(table.pack(table.pack(1, 1), table.pack(2, 1), table.pack(3, 1), table.pack(4, 0)), table.pack(nil, nil, "Parent", nil, nil, nil, nil, nil, 92, 39, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 2, nil, 15, nil, nil, nil, nil, nil, nil, nil, nil, 32, 35, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 2, nil, nil, nil, nil, "Health", nil, nil, nil, nil, 127, 1, 25), 22, (function() local t = { (12), (64), (1), (64), (50), (17), (0), (0), (nil), (nil), (14), (39), (6), (140), (49), (64), (14), (0), (0), (20), (100), (nil), (nil), (14), (15), (3), (199), (1), (63), (0), (0), (nil), (nil), (14), (35), (0), (0), (nil), (5), (61), (0), (0), (306), (12), (332), (12), (nil), (4), (2), (40), (51), (1), (nil), (1), (0), (0), (nil), (nil), (nil), (14), (25), (29), (54), (1), (1), (1), (1), (62) }; t.n = 68; return t end)(), (function() local t = { (127), (127), (175), (157), (127), (127), (131), (90), (101), (101), (92), (127), (127), (113), (127), (32), (127), (131), (90), (93), (101), (101), (101), (14), (127), (164), (145), (186), (218), (90), (131), (101), (101), (14), (127), (84), (181), (117), (127), (127), (131), (90), (151), (5), (141), (17), (101), (239), (127), (127), (127), (207), (123), (127), (90), (131), (101), (101), (101), (14), (127), (127), (127), (59), (195), (145), (186), (127) }; t.n = 68; return t end)(), (function() local t = { (0), (232), (232), (232), (232), (232), (0), (0), (0), (0), (0), (0), (0), (81), (232), (232), (232), (232), (232), (232), (232), (232), (232), (232), (232), (234), (234), (234), (234), (232), (232), (232), (232), (232), (232), (232), (232), (232), (232), (0), (232), (232), (232), (232), (232), (232), (232), (232), (232), (232), (232), (232), (232), (232), (234), (234), (234), (234), (234), (234), (234), (232), (234), (232), (233), (233), (233) }; t.n = 67; return t end)(), (function() local t = { (0), (0), (0), (1), (0), (0), (21), (15), (15), (21), (0), (0), (0), (309), (0), (1), (0), (21), (15), (0), (20), (15), (21), (9), (0), (0), (nil), (0), (0), (15), (21), (15), (21), (12), (0), (nil), (1), (1), (0), (0), (11), (5), (12), (12), (12), (nil), (11), (0), (0), (0), (0), (1), (1), (0), (15), (21), (15), (21), (21), (172), (0), (0), (0), (0), (44), (nil), (0), (0) }; t.n = 68; return t end)(), table.pack(nil, nil, nil, nil, nil, nil, nil, nil, 48, 13, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 52, 6, nil, nil, nil, nil, nil, nil, nil, nil, 4, 62, nil, nil, nil, nil, "ESP", nil, nil, nil, nil, nil, nil, nil, nil, 50, nil, nil, nil, nil, nil, 0, nil, nil, nil, 29, 27, 63), (function() local t = { (0), (0), (nil), (0), (0), (0), (0), (0), (nil), (nil), (21), (0), (0), (468), (0), (0), (0), (0), (0), (0), (nil), (347), (nil), (21), (0), (1), (1), (0), (0), (0), (0), (nil), (nil), (21), (0), (1), (0), (1), (0), (0), (0), (0), (161), (215), (12), (5), (nil), (13), (0), (0), (0), (nil), (63), (0), (0), (0), (nil), (nil), (nil), (21), (0), (0), (0), (0), (0), (1), (0), (0) }; t.n = 68; return t end)(), 0, (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Disconnect"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("getgenv"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (3), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Destroy") }; t.n = 66; return t end)())), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (16), (84), (16), (66), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (62), (nil), (nil), (nil), (nil), (nil), (32) }; t.n = 113; return t end)(), 26, (function() local t = { (67), (78), (0), (250), (212), (139), (nil), (218), (nil), (47), (0), (24), (0), (nil), (nil), (100), (100), (416), (18), (2), (nil), (0), (nil), (nil), (nil), (nil), (4), (4), (109), (0), (0), (nil), (nil), (18), (116), (56), (455), (0), (180), (102), (252), (nil), (25), (378), (3), (20), (3), (nil), (161), (nil), (4), (4), (353), (467), (1), (61), (3), (4), (1), (29), (110), (103), (1), (0), (5), (73), (89), (0), (2), (nil), (0), (56), (59), (5), (0), (0), (57), (46), (24), (0), (0), (0), (nil), (nil), (nil), (nil), (nil), (18), (66), (14), (0), (279), (231), (506), (16), (283), (8), (60), (3), (nil), (0), (37), (77), (0), (0), (nil), (nil), (18), (62), (10), (0), (0), (nil), (nil), (18), (98), (nil), (nil), (35) }; t.n = 119; return t end)(), (function() local t = { (127), (127), (84), (114), (56), (33), (135), (36), (8), (127), (131), (72), (90), (101), (101), (101), (101), (101), (92), (127), (101), (163), (117), (8), (8), (8), (126), (17), (127), (131), (34), (101), (101), (92), (127), (127), (58), (84), (114), (56), (33), (135), (36), (8), (7), (127), (59), (8), (143), (115), (126), (17), (101), (101), (17), (127), (59), (250), (59), (127), (127), (127), (17), (173), (120), (127), (127), (58), (145), (8), (81), (32), (127), (145), (189), (81), (127), (127), (93), (131), (34), (90), (101), (101), (101), (101), (101), (14), (127), (93), (131), (76), (5), (141), (17), (101), (14), (127), (145), (8), (81), (96), (127), (90), (131), (101), (101), (92), (127), (127), (90), (131), (101), (101), (14), (127), (117), (123), (127) }; t.n = 119; return t end)(), (function() local t = { (0), (219), (224), (224), (224), (224), (224), (224), (224), (224), (224), (224), (224), (224), (224), (224), (224), (224), (224), (224), (222), (223), (223), (223), (223), (223), (223), (223), (223), (218), (218), (218), (218), (218), (218), (218), (92), (221), (221), (221), (221), (221), (221), (221), (221), (221), (219), (224), (224), (224), (224), (224), (225), (226), (227), (227), (218), (231), (231), (218), (219), (228), (228), (230), (231), (231), (219), (1), (217), (217), (217), (218), (218), (231), (232), (231), (231), (219), (219), (219), (219), (219), (219), (219), (219), (219), (219), (219), (219), (219), (219), (219), (219), (219), (219), (219), (219), (219), (219), (219), (219), (219), (219), (228), (228), (228), (228), (228), (228), (224), (219), (219), (219), (219), (219), (219), (218), (218) }; t.n = 118; return t end)(), (function() local t = { (0), (0), (nil), (13), (158), (4), (248), (176), (0), (0), (25), (0), (19), (24), (19), (19), (24), (25), (0), (0), (3), (nil), (4), (219), (0), (0), (0), (359), (0), (25), (0), (23), (25), (0), (0), (0), (273), (nil), (97), (132), (3), (118), (237), (0), (0), (0), (0), (177), (193), (233), (0), (517), (3), (3), (331), (0), (0), (5), (0), (0), (0), (0), (nil), (4), (107), (0), (0), (1), (nil), (0), (2), (2), (0), (nil), (7), (5), (0), (0), (0), (25), (0), (19), (24), (25), (19), (23), (25), (234), (0), (0), (15), (317), (16), (16), (nil), (15), (126), (0), (nil), (0), (144), (3), (0), (19), (25), (19), (25), (0), (0), (0), (19), (25), (19), (25), (192), (0), (2), (3), (0) }; t.n = 119; return t end)(), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), ("fromRGB"), (nil), (255), (nil), (nil), (nil), (nil), (48), (75), (nil), (nil), (nil), (nil), (nil), ("Name"), (nil), ("fromRGB"), (255), (0), (0), (nil), (nil), (nil), (nil), (nil), (47), (60), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("new"), (nil), (nil), (nil), (nil), (nil), (255), (nil), (255), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Humanoid"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (24), (93), (22), (92), (2), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("ESP_Highlight"), (nil), (nil), (nil), (nil), (nil), (58), (62), (nil), (nil), (nil), (nil), (nil), (102), (61), (nil), (nil), ("Health"), (0) }; t.n = 118; return t end)(), (function() local t = { (0), (0), (4), (75), (4), (252), (235), (88), (5), (0), (0), (0), (0), (nil), (nil), (347), (nil), (nil), (25), (0), (nil), (4), (4), (5), (6), (7), (4), (3), (0), (0), (23), (nil), (nil), (25), (0), (0), (293), (3), (151), (3), (49), (177), (235), (4), (0), (0), (96), (6), (7), (125), (4), (3), (365), (nil), (3), (0), (0), (0), (0), (0), (0), (0), (3), (0), (nil), (0), (0), (0), (1), (4), (0), (0), (0), (5), (33), (0), (0), (0), (0), (0), (23), (0), (nil), (nil), (nil), (nil), (nil), (25), (0), (0), (0), (14), (395), (16), (14), (526), (17), (0), (1), (5), (0), (0), (0), (0), (0), (234), (nil), (25), (0), (0), (0), (0), (nil), (526), (25), (0), (3), (1), (0) }; t.n = 119; return t end)(), 0, (function() local t = { (nil), (nil), ("Color3"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Color3"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Instance"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Parent"), (nil), (nil), (nil), (nil), (nil), ("FindFirstChildOfClass"), (nil), (nil), (nil), (nil), ("Connect"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (101), (nil), (nil), (nil), ("FindFirstChild") }; t.n = 99; return t end)()), {}))
	;(nil --[[ constant not decoded ]])[49](v10[1], t3[1])
	;(t1[1])[26] = v10[1]

	local v11 = table.pack((nil --[[ constant not decoded ]])[57](table.pack({}, table.pack(nil, nil, nil, 14, 23, nil, nil, nil, nil, nil, 4, 0, 15, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 13979, nil, nil, 15, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 59, 0, 36), 24, table.pack(33, 0, 0, nil, nil, 16, 23, 23, 22, 0, nil, nil, nil, 16, 15, 0, 0, 2, 0, 4, 34, 0, 1, 0, 0, nil, 14, nil, 14, nil, 6, 35, 21, 15, 36, 15, 0, 32, 149, 0, 0, nil, nil, nil, 16, 36, 4, 4, 34, nil, nil, 46), table.pack(127, 131, 34, 101, 101, 14, 127, 127, 93, 131, 101, 101, 101, 14, 127, 84, 84, 145, 22, 22, 78, 168, 59, 131, 90, 76, 5, 141, 17, 101, 92, 127, 127, 127, 127, 127, 159, 127, 22, 90, 131, 101, 101, 101, 14, 127, 145, 186, 127, 117, 86, 127), table.pack(0, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 14, 240, 240, 240, 240, 240, 240, 240, 241, 241, 241, 241, 241), table.pack(0, 23, 0, 21, 23, 30, 0, 0, 0, 23, 23, 22, 23, 158, 0, nil, nil, nil, 2, 0, 1, 0, 0, 13, 7, nil, 14, 14, nil, 13, 0, 0, 0, 0, 0, 0, 1, 0, 171, 17, 23, 17, 23, 23, 5, 0, nil, 0, 0, 3, 4, 0), table.pack(nil, nil, nil, 26, 8, nil, nil, nil, nil, nil, 48, 48, 36, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 77, nil, -13611, nil, 34, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 23, 22, 35, nil, nil, nil, nil, nil, "Name", "ESP_Highlight"), table.pack(0, 0, 21, nil, nil, 23, 0, 0, 0, 0, nil, nil, nil, 23, 0, 1, 2, 2, 2, 1, 0, 0, 0, 0, 0, 14, nil, 14, 7, nil, 15, 0, 0, 0, 0, 0, 49, 0, 228, 0, 0, nil, nil, nil, 23, 0, 3, 0, 0, 4, 34, 0), 0, table.pack(nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, "pairs", "workspace", "GetDescendants", nil, nil, nil, nil, nil, nil, nil, 367, nil, nil, 21, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, "Destroy")), false))
	;(nil --[[ constant not decoded ]])[49](v11[1], t3[1])
	;(t1[1])[27] = v11[1]

	local v12 = table.pack((nil --[[ constant not decoded ]])[57](table.pack(table.pack(table.pack(9, 1), table.pack(26, 1), table.pack(27, 1)), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (76), (16), (37), (nil), (nil), (nil), (nil), (nil), (0), (20), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Character"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (19739), (nil), (nil), (nil), (nil), (21), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (5), (26), (nil), (nil), (nil), (nil), (nil), (1), (84), (1), (nil), (nil), (nil), (nil), (nil), (nil), (0), (nil), (nil), (nil), (nil), (1), (0), (94) }; t.n = 78; return t end)(), 26, (function() local t = { (4), (49), (36), (459), (20), (0), (0), (0), (nil), (nil), (nil), (18), (37), (0), (82), (0), (nil), (nil), (18), (20), (21), (0), (0), (nil), (81), (69), (6), (13), (52), (62), (180), (6), (150), (235), (5), (13), (68), (0), (0), (nil), (105), (16), (130), (241), (nil), (16), (nil), (8), (21), (1), (0), (1), (29), (0), (nil), (481), (18), (26), (0), (0), (0), (nil), (nil), (nil), (18), (1), (13), (25), (94), (nil), (13), (80), (24), (0), (0), (nil), (nil), (nil), (18), (94), (53), (1), (0), (0), (nil), (nil), (1), (4), (4), (151), (nil), (0), (66), (37), (0), (173), (241), (252), (2), (0), (4), (13) }; t.n = 102; return t end)(), (function() local t = { (127), (32), (127), (87), (127), (90), (131), (34), (101), (101), (101), (92), (127), (159), (127), (131), (101), (101), (92), (127), (127), (84), (181), (117), (127), (127), (155), (25), (127), (195), (114), (0), (124), (36), (186), (127), (127), (131), (34), (76), (114), (106), (105), (167), (141), (17), (101), (92), (127), (195), (55), (59), (127), (131), (101), (101), (92), (127), (34), (90), (131), (101), (101), (101), (14), (127), (32), (127), (127), (117), (62), (127), (93), (34), (131), (101), (101), (101), (92), (127), (127), (127), (168), (84), (117), (8), (186), (127), (145), (143), (115), (81), (127), (127), (84), (143), (193), (11), (145), (22), (22), (78) }; t.n = 102; return t end)(), (function() local t = { (0), (246), (246), (113), (246), (246), (246), (246), (246), (246), (246), (246), (246), (247), (247), (246), (246), (246), (246), (246), (246), (246), (246), (246), (246), (249), (249), (249), (249), (250), (250), (250), (250), (250), (250), (250), (246), (246), (246), (246), (246), (246), (246), (246), (246), (246), (246), (246), (246), (255), (255), (255), (249), (249), (249), (249), (249), (249), (246), (246), (246), (246), (246), (246), (246), (246), (249), (249), (247), (249), (249), (249), (247), (247), (247), (247), (247), (247), (247), (247), (249), (246), (247), (253), (253), (253), (253), (246), (248), (248), (248), (248), (248), (246), (247), (247), (247), (247), (247), (247), (247) }; t.n = 101; return t end)(), (function() local t = { (0), (1), (0), (336), (0), (19), (25), (0), (19), (23), (25), (0), (0), (1), (0), (25), (25), (25), (0), (0), (0), (nil), (1), (1), (0), (0), (0), (6), (0), (1), (7), (18), (3), (82), (0), (0), (0), (15), (0), (nil), (184), (250), (16), (222), (16), (nil), (15), (0), (0), (2), (1), (0), (0), (25), (25), (25), (0), (0), (0), (19), (25), (23), (19), (25), (152), (0), (4), (0), (0), (4), (5), (0), (0), (0), (25), (23), (24), (25), (0), (0), (0), (0), (0), (nil), (1), (0), (0), (0), (nil), (81), (190), (4), (0), (0), (nil), (129), (137), (nil), (nil), (2), (0), (1) }; t.n = 102; return t end)(), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (40), (40), (94), (nil), (nil), (nil), (nil), (nil), (23), (5), (nil), (nil), (nil), (nil), (nil), ("ESP"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (74), (nil), (nil), (nil), (nil), (-19557), (nil), (21), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (30), (nil), (nil), (nil), (nil), (nil), (nil), (95), (95), (82), (nil), (nil), (nil), (nil), (nil), ("Health"), (nil), (nil), (nil), (nil), (nil), (84), (83), (69), (nil), (nil), (nil), (nil), (nil), (nil), ("wait"), (1), (nil), (nil), (nil), (nil), ("Humanoid") }; t.n = 91; return t end)(), (function() local t = { (0), (0), (0), (176), (0), (0), (0), (23), (nil), (nil), (nil), (25), (0), (88), (0), (0), (nil), (nil), (25), (0), (0), (1), (0), (1), (0), (0), (nil), (3), (0), (0), (98), (84), (45), (233), (0), (0), (0), (0), (13), (16), (21), (nil), (4), (224), (16), (13), (nil), (17), (0), (0), (0), (0), (0), (0), (nil), (nil), (25), (0), (23), (0), (0), (nil), (nil), (nil), (25), (0), (0), (0), (0), (5), (nil), (0), (0), (23), (0), (nil), (nil), (nil), (25), (0), (0), (0), (0), (1), (1), (2), (0), (0), (3), (6), (241), (0), (0), (0), (1), (2), (164), (43), (2), (2), (1), (0) }; t.n = 102; return t end)(), 0, (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("getgenv"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (255), (nil), (nil), (nil), (nil), (nil), (22), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("task"), (nil), (nil), (nil), (nil), ("FindFirstChildOfClass"), (nil), (nil), (nil), (nil), (nil), ("pairs"), (nil), (nil), ("workspace"), ("GetChildren") }; t.n = 99; return t end)()), {}))
	;(nil --[[ constant not decoded ]])[49](v12[1], t3[1])
	;(t1[1])[28] = v12[1]
	;(t1[1])[29] = (t1[1])[25]
	;(t1[1])[29]()
	;(t1[1])[30] = (t3[1]).game
	;(t1[1])[31] = (t1[1])[30]
	;(t1[1])[30] = (t1[1])[30].HttpGet
	;(t1[1])[32] = "https://github.com/Footagesus/WindUI/releases/latest/download/main.lua"
	error("devirt: numeric for with symbolic bounds (at 0:352)")
end

-- proto 35: vm sequence 30, 0 opcodes
local function proto_35()
	(t1[1])[1] = (t2[2])[1]
	;(t1[1])[2] = upv0.Character

	if (t1[1])[2] then
		(t1[1])[4] = (t1[1])[2]
		;(t1[1])[3] = (t1[1])[2].FindFirstChild
		;(t1[1])[5] = "HumanoidRootPart"
		;(t1[1])[3] = (t1[1])[3]((t1[1])[4], (t1[1])[5])

		if (t1[1])[3] then
			(t1[1])[4] = nil
			;(t1[1])[5] = (t1[1])[5].huge
			;(t1[1])[6] = (t3[1]).pairs
			;(t1[1])[7] = (t3[1]).workspace
			;(t1[1])[8] = (t1[1])[7]
			;(t1[1])[7] = (t1[1])[7].GetChildren
			error("devirt: numeric for with symbolic bounds (at 0:57)")
		end
		;(t1[1])[4] = nil
		error("devirt: symbolic generic for (at 0:79)")
	end
	;(t1[1])[3] = nil
	error("devirt: symbolic generic for (at 0:38)")
end

-- proto 38: vm sequence 31, 0 opcodes
local function proto_38()
	(t1[1])[1] = upv0.Character

	if (t1[1])[1] then
		(t1[1])[3] = (t1[1])[1]
		;(t1[1])[2] = (t1[1])[1].FindFirstChild
		;(t1[1])[2] = (t1[1])[2]((t1[1])[3], (t1[1])[4])

		if (t1[1])[2] then
			(t1[1])[3] = nil
			;(t1[1])[4] = nil
			;(t1[1])[5] = (t3[1]).math
			;(t1[1])[5] = (t1[1])[5].huge
			;(t1[1])[6] = (t3[1]).pairs
			;(t1[1])[7] = (t3[1]).workspace
			;(t1[1])[8] = (t1[1])[7]
			;(t1[1])[7] = (t1[1])[7].GetChildren
			error("devirt: numeric for with symbolic bounds (at 0:115)")
		end
		;(t1[1])[3] = nil
		;(t1[1])[4] = nil
		error("devirt: symbolic generic for (at 0:72)")
	end
	;(t1[1])[2] = nil
	;(t1[1])[3] = nil
	error("devirt: symbolic generic for (at 0:98)")
end

-- proto t543: vm sequence 32, 0 opcodes
local function proto_t543()
	(t1[1])[1] = upv0.Character
	;(t1[1])[2] = (t1[1])[1]
	error("devirt: while loop limit (at 0:22)")
end

-- proto 34: vm sequence 33, 0 opcodes
local function proto_34()
	while true do
		(t1[1])[1] = (t3[1]).getgenv
		;(t1[1])[1] = (t1[1])[1]()
		;(t1[1])[1] = (t1[1])[1].FarmTree

		if not (t1[1])[1] then
			error("devirt: symbolic generic for (at 0:98)")
		else
			(t1[1])[1] = upv0.Character
			;(t1[1])[2] = (t1[1])[1]

			if (t1[1])[2] then
				(t1[1])[3] = (t1[1])[1]
				;(t1[1])[2] = (t1[1])[1].FindFirstChild
				;(t1[1])[4] = "HumanoidRootPart"
				;(t1[1])[2] = (t1[1])[2]((t1[1])[3], (t1[1])[4])
			end

			if (t1[1])[2] then
				break
			end
			;(t1[1])[3] = (t3[1]).task
			;(t1[1])[3] = (t1[1])[3].wait
			;(t1[1])[3]()
		end
	end
	;(t1[1])[3] = (t3[1]).math
	;(t1[1])[3] = (t1[1])[3].huge
	;(t1[1])[4] = nil
	;(t1[1])[5] = (t3[1]).pairs
	;(t1[1])[6] = (nil --[[ constant not decoded ]])[3](3)
	;(t1[1])[8] = "BigTree"
	;(t1[1])[9] = "RockTree"
	;(nil --[[ constant not decoded ]])[31](t1[1], 7, 9, 1, (t1[1])[6])

	local v = table.pack((nil --[[ constant not decoded ]])[56]((t1[1])[5]((nil --[[ constant not decoded ]])[26](t1[1], 6, 6))))
	;(t1[1])[5] = (v[2])[1]
	;(t1[1])[6] = (v[2])[2]
	;(t1[1])[7] = (v[2])[3]
	;(nil --[[ constant not decoded ]])[18](function(...) end)((t1[1])[5], (t1[1])[6], (t1[1])[7])
	local v2

	while true do
		v2 = table.pack((h_1()))

		if v2[1] then
			(t1[1])[6] = v2[2]
			;(t1[1])[7] = v2[3]
			;(t1[1])[8] = upv1
			;(t1[1])[8] = (t1[1])[8]((t1[1])[9])
			if not (t1[1])[8] then
				continue
			end
			;(t1[1])[10] = (t1[1])[8]
			;(t1[1])[9] = (t1[1])[8][nil --[[ constant not decoded ]]]
			;(t1[1])[11] = nil --[[ constant not decoded ]]
			;(t1[1])[9] = (t1[1])[9]((t1[1])[10], (t1[1])[11])
			error("devirt: while loop limit (at 0:133)")
		else
			break
		end
	end

	local v3

	if (t1[1])[4] then
		(t1[1])[5] = (t3[1]).pcall

		v3 = table.pack(((nil --[[ constant not decoded ]])[57](table.pack(table.pack(table.pack(2, 2), table.pack(4, 0)), table.pack(), 10, table.pack(6, 1, 1, 126, 0, 9, 1, 425, 1, nil, 0, 0, 1, 8, 1, 8), table.pack(127, 195, 145, 8, 173, 127, 127, 60, 59, 8, 173, 88, 164, 17, 112, 127), table.pack(0, 90, 90, 90, 90, 90, 0, 2, 90, 90, 90, 90, 90, 90, 90), table.pack(0, 0, 80, 0, 4, 0, 0, 254, 0, 0, 6, 7, 0, nil, 7, 0), table.pack(nil, nil, nil, nil, nil, nil, nil, nil, nil, 1), table.pack(0, 0, 1, 3, 0, 0, 0, 300, 0, 5, 0, 0, 8, 7, 0, 0), 0, table.pack(nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 1)), {})))
		;(nil --[[ constant not decoded ]])[49](v3[1], t3[1])
		;(t1[1])[6] = v3[1]

		if t3[6] then
			if not (t3[6])[4] then
				(t3[6])[4] = { 4, t1[1] }
			end
		end
		;(t1[1])[5]((t1[1])[6])
	end
	;(t1[1])[5] = (t3[1]).task
	;(t1[1])[5] = (t1[1])[5].wait
	;(t1[1])[5]()
	error("devirt: symbolic generic for (at 0:80)")
end

-- proto t207: vm sequence 34, 0 opcodes
local function proto_t207()
	(t1[1])[1] = (t3[1]).getgenv
	;(t1[1])[1] = (t1[1])[1]()
	;(t1[1])[1] = (t1[1])[1].AxeAuraZombie

	if (t1[1])[1] then
		(t1[1])[20] = {
			156,
			0,
			0,
			4,
			4,
			nil,
			13,
			126,
			168,
			24,
			41,
			115,
			116,
			0,
			38,
			137,
			0,
			0,
			93,
			93,
			476,
			13,
			105,
			47,
			0,
			nil,
			nil,
			13,
			83,
			nil,
			135,
			40,
			0,
			0,
			4,
			0,
			nil,
			125,
			3,
			41,
			112,
			0,
			nil,
			0,
			76,
			3,
			141,
			0,
			0,
			nil,
			nil,
			13,
			65,
			250,
			nil,
			0,
			9,
			101,
			95,
			3,
			175,
			nil,
			3,
			45,
			32,
			0,
			0,
			nil,
			131,
			0,
			nil,
			0,
			76,
			11,
			10,
			149,
			0,
			0,
			nil,
			1,
			23,
			2,
			58,
			146,
			84,
			2,
			38,
			198,
			81,
			134,
			1,
			2,
			nil,
			0,
			81,
			0,
			0,
			nil,
			nil,
			13,
			69,
			nil,
			0,
			135,
			8,
			0,
			171,
			76,
			nil,
			nil,
			11,
			73,
			135,
			166,
			503,
			157,
			0,
			nil,
			0,
			0,
			0,
			6,
			0,
			4,
			135,
			16,
			0,
			41,
			nil,
			141,
			133,
			155,
			9,
			59,
			91,
			0,
			13,
			0,
			0,
			5,
			38,
			0,
			190,
			221,
			10,
			149,
			223,
			nil,
			10,
			4,
			3,
			37,
			93,
			4,
			135,
			1,
			76,
			0,
			0,
			0,
			nil,
			354,
			nil,
			nil,
			13,
			12,
			135,
			108,
			0,
			0,
			0,
			19,
			nil,
			nil,
			nil,
			nil,
			13,
			29,
		}
		;(t1[1])[20][84] = 1
		;(t1[1])[20][10] = 83
		;(t1[1])[13] = nil
		;(t1[1])[14] = nil
		;(t1[1])[15] = nil
		;(t1[1])[16] = nil
		;(t1[1])[17] = nil
		;(t1[1])[18] = nil
		;(t1[1])[19] = nil
		;(t1[1])[20] = nil
		;(t1[1])[146] = upv0.Character
		error("devirt: while loop limit (at 0:89)")
	end
	;(t1[1])[14] = {
		127,
		131,
		34,
		101,
		101,
		101,
		92,
		127,
		127,
		127,
		156,
		127,
		127,
		168,
		156,
		127,
		34,
		131,
		101,
		101,
		101,
		14,
		127,
		127,
		131,
		101,
		101,
		92,
		127,
		117,
		62,
		127,
		84,
		116,
		186,
		84,
		117,
		127,
		83,
		127,
		127,
		84,
		117,
		55,
		127,
		83,
		127,
		90,
		131,
		101,
		101,
		92,
		127,
		145,
		8,
		81,
		145,
		127,
		127,
		195,
		143,
		115,
		7,
		156,
		127,
		131,
		181,
		117,
		127,
		84,
		117,
		55,
		127,
		117,
		48,
		127,
		84,
		181,
		117,
		39,
		127,
		39,
		127,
		155,
		114,
		0,
		124,
		36,
		156,
		127,
		127,
		145,
		8,
		81,
		127,
		34,
		131,
		101,
		101,
		14,
		127,
		8,
		81,
		156,
		127,
		55,
		83,
		127,
		117,
		117,
		1,
		127,
		57,
		127,
		14,
		127,
		138,
		117,
		173,
		84,
		84,
		145,
		22,
		22,
		78,
		127,
		84,
		181,
		117,
		156,
		127,
		156,
		127,
		127,
		127,
		159,
		127,
		84,
		116,
		186,
		127,
		84,
		46,
		104,
		128,
		36,
		15,
		117,
		127,
		114,
		0,
		124,
		36,
		185,
		127,
		59,
		127,
		34,
		131,
		90,
		101,
		101,
		101,
		101,
		92,
		127,
		25,
		127,
		90,
		34,
		131,
		72,
		101,
		101,
		101,
		101,
		14,
		127,
	}
	;(t1[1])[20] = {
		156,
		0,
		0,
		4,
		4,
		nil,
		13,
		126,
		168,
		24,
		41,
		115,
		116,
		0,
		38,
		137,
		0,
		0,
		93,
		93,
		476,
		13,
		105,
		47,
		0,
		nil,
		nil,
		13,
		83,
		nil,
		135,
		40,
		0,
		0,
		4,
		0,
		nil,
		125,
		3,
		41,
		112,
		0,
		nil,
		0,
		76,
		3,
		141,
		0,
		0,
		nil,
		nil,
		13,
		65,
		250,
		nil,
		0,
		9,
		101,
		95,
		3,
		175,
		nil,
		3,
		45,
		32,
		0,
		0,
		nil,
		131,
		0,
		nil,
		0,
		76,
		11,
		10,
		149,
		0,
		0,
		nil,
		1,
		23,
		2,
		58,
		146,
		84,
		2,
		38,
		198,
		81,
		134,
		1,
		2,
		nil,
		0,
		81,
		0,
		0,
		nil,
		nil,
		13,
		69,
		nil,
		0,
		135,
		8,
		0,
		171,
		76,
		nil,
		nil,
		11,
		73,
		135,
		166,
		503,
		157,
		0,
		nil,
		0,
		0,
		0,
		6,
		0,
		4,
		135,
		16,
		0,
		41,
		nil,
		141,
		133,
		155,
		9,
		59,
		91,
		0,
		13,
		0,
		0,
		5,
		38,
		0,
		190,
		221,
		10,
		149,
		223,
		nil,
		10,
		4,
		3,
		37,
		93,
		4,
		135,
		1,
		76,
		0,
		0,
		0,
		nil,
		354,
		nil,
		nil,
		13,
		12,
		135,
		108,
		0,
		0,
		0,
		19,
		nil,
		nil,
		nil,
		nil,
		13,
		29,
	}
	;(t1[1])[14][66] = 84
	;(t1[1])[20][24] = nil --[[ constant not decoded ]]
	;(t1[1])[13] = nil
	;(t1[1])[14] = nil
	;(t1[1])[15] = nil
	;(t1[1])[16] = nil
	;(t1[1])[17] = nil
	;(t1[1])[18] = nil
	;(t1[1])[19] = nil
	;(t1[1])[20] = nil
	;(t1[1])[nil] = {
		156,
		0,
		0,
		4,
		4,
		nil,
		13,
		126,
		168,
		24,
		41,
		115,
		116,
		0,
		38,
		137,
		0,
		0,
		93,
		93,
		476,
		13,
		105,
		47,
		0,
		nil,
		nil,
		13,
		83,
		nil,
		135,
		40,
		0,
		0,
		4,
		0,
		nil,
		125,
		3,
		41,
		112,
		0,
		nil,
		0,
		76,
		3,
		141,
		0,
		0,
		nil,
		nil,
		13,
		65,
		250,
		nil,
		0,
		9,
		101,
		95,
		3,
		175,
		nil,
		3,
		45,
		32,
		0,
		0,
		nil,
		131,
		0,
		nil,
		0,
		76,
		11,
		10,
		149,
		0,
		0,
		nil,
		1,
		23,
		2,
		58,
		146,
		84,
		2,
		38,
		198,
		81,
		134,
		1,
		2,
		nil,
		0,
		81,
		0,
		0,
		nil,
		nil,
		13,
		69,
		nil,
		0,
		135,
		8,
		0,
		171,
		76,
		nil,
		nil,
		11,
		73,
		135,
		166,
		503,
		157,
		0,
		nil,
		0,
		0,
		0,
		6,
		0,
		4,
		135,
		16,
		0,
		41,
		nil,
		141,
		133,
		155,
		9,
		59,
		91,
		0,
		13,
		0,
		0,
		5,
		38,
		0,
		190,
		221,
		10,
		149,
		223,
		nil,
		10,
		4,
		3,
		37,
		93,
		4,
		135,
		1,
		76,
		0,
		0,
		0,
		nil,
		354,
		nil,
		nil,
		13,
		12,
		135,
		108,
		0,
		0,
		0,
		19,
		nil,
		nil,
		nil,
		nil,
		13,
		29,
	}
	;(t1[1])[1] = (t1[1])[1]()
	;(t1[1])[1] = (t1[1])[1].AxeAuraChicken
	error("devirt: while loop limit (at 0:132)")
end

-- proto 37: vm sequence 35, 0 opcodes
local function proto_37()
	(t1[1])[1] = (t3[1]).getgenv
	;(t1[1])[1] = (t1[1])[1]()
	;(t1[1])[1] = (t1[1])[1].GunKillAll

	if not (t1[1])[1] then
		error("devirt: symbolic generic for (at 0:43)")
	end
	;(t1[1])[1] = upv0

	local v = table.pack((nil --[[ constant not decoded ]])[56]((t1[1])[1]()))
	;(t1[1])[1] = (v[2])[1]
	;(t1[1])[2] = (v[2])[2]

	if not (t1[1])[1] then
		(t1[1])[3] = (t3[1]).task
		;(t1[1])[3]((t1[1])[4])
		error("devirt: symbolic generic for (at 0:53)")
	end

	error("devirt: while loop limit (at 0:31)")
end

-- proto 41: vm sequence 36, 0 opcodes
local function proto_41()
	(t1[1])[1] = upv0

	if not (t1[1])[1] then
		(t1[1])[1] = (t3[1]).getgenv
		;(nil --[[?NilIndex]])()
		;(t1[1])[1] = (t1[1])[1].AxeAuraZombie

		if not (t1[1])[1] then
			(t1[1])[1] = (t3[1]).getgenv
			;(nil --[[?NilIndex]])()
			;(t1[1])[1] = (t1[1])[1].AxeAuraChicken

			if not (t1[1])[1] then
				error("devirt: symbolic generic for (at 0:17)")
			end
		end
		;(t1[1])[1] = (t3[1]).task
		;(t1[1])[2] = upv1
		;(t1[1])[1] = (t1[1])[1]((t1[1])[2])
		upv0 = (t1[1])[1]
		error("devirt: symbolic generic for (at 0:71)")
	end
	;(t1[1])[10] = {
		50,
		0,
		340,
		0,
		1,
		0,
		31,
		0,
		250,
		6,
		204,
		48,
		30,
		nil,
		17,
		86,
		1,
		1,
		60,
		1,
		189,
		51,
		81,
		0,
		nil,
		nil,
		13,
		86,
		135,
		54,
		16,
		7,
		0,
		31,
		53,
		0,
		19,
		0,
		nil,
		nil,
		nil,
		nil,
		13,
		79,
		0,
		0,
		nil,
		nil,
		13,
		7,
		32,
		35,
		28,
		22,
		11,
		263,
		11,
		nil,
		3,
		1,
		15,
		0,
		249,
		181,
		72,
		nil,
		208,
		2,
		1,
		1,
		1,
		0,
		0,
		nil,
		nil,
		nil,
		13,
		32,
		415,
		11,
		52,
		0,
		0,
		11,
		51,
		19,
		0,
		19,
		21,
		176,
		251,
		231,
		nil,
		1,
		30,
	}
	;(t1[1])[4] = {
		127,
		84,
		117,
		164,
		186,
		117,
		127,
		84,
		46,
		104,
		128,
		36,
		15,
		117,
		127,
		127,
		59,
		39,
		127,
		143,
		115,
		127,
		127,
		131,
		101,
		101,
		92,
		127,
		8,
		127,
		127,
		127,
		164,
		32,
		127,
		131,
		72,
		34,
		101,
		101,
		101,
		101,
		14,
		127,
		90,
		131,
		101,
		101,
		92,
		127,
		127,
		127,
		127,
		127,
		5,
		141,
		17,
		101,
		92,
		127,
		127,
		84,
		114,
		56,
		33,
		135,
		36,
		195,
		7,
		142,
		59,
		131,
		90,
		101,
		101,
		101,
		92,
		127,
		38,
		39,
		127,
		131,
		90,
		44,
		156,
		127,
		84,
		46,
		104,
		128,
		36,
		15,
		117,
		39,
		127,
	}
	;(t1[1])[11] = 310 ~= nil --[[ constant not decoded ]]
	error("devirt: while loop limit (at 0:85)")
end

-- proto 43: vm sequence 37, 0 opcodes
local function proto_43()
	(t1[1])[1] = upv0.Character
	;(t1[1])[2] = (t1[1])[1]

	if (t1[1])[2] then
		(t1[1])[3] = (t1[1])[1]
		;(t1[1])[2] = (t1[1])[1].FindFirstChild
		;(t1[1])[4] = "HumanoidRootPart"
		;(t1[1])[2] = (t1[1])[2]((t1[1])[3], (t1[1])[4])
	end

	local v

	if (t1[1])[2] then
		(t1[1])[3] = (t3[1]).Instance
		;(t1[1])[4] = "BodyVelocity"
		;(t1[1])[3] = (t1[1])[3]((t1[1])[4])
		;(t1[1])[4] = (t3[1]).Instance
		;(t1[1])[4] = (t1[1])[4].new
		;(t1[1])[5] = "BodyGyro"
		;(t1[1])[4] = (t1[1])[4]((t1[1])[5])
		;(t1[1])[5] = (t3[1]).Vector3
		;(t1[1])[5] = (t1[1])[5].new
		;(t1[1])[6] = 1e9
		;(t1[1])[7] = 1e9
		;(t1[1])[8] = 1e9
		;(t1[1])[5] = (t1[1])[5]((nil --[[ constant not decoded ]])[26](t1[1], 8, 6))
		;(t1[1])[3].MaxForce = (t1[1])[5]
		;(t1[1])[5] = (t3[1]).Vector3
		;(t1[1])[5] = (t1[1])[5].new
		;(t1[1])[6] = 1e9
		;(t1[1])[7] = 1e9
		;(t1[1])[8] = 1e9
		;(t1[1])[5] = (t1[1])[5]((nil --[[ constant not decoded ]])[26](t1[1], 8, 6))
		;(t1[1])[4].P = 1000000
		;(t1[1])[3].Parent = (t1[1])[2]
		;(t1[1])[4].Parent = (t1[1])[2]
		;(t1[1])[5] = upv2.Heartbeat
		;(t1[1])[6] = (t1[1])[5]
		;(t1[1])[5] = (t1[1])[5].Connect

		v = table.pack(((nil --[[ constant not decoded ]])[57](table.pack(table.pack(table.pack(0, 2), table.pack(3, 1), table.pack(4, 1), table.pack(1, 2), table.pack(3, 2), table.pack(4, 2)), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (5), (1), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Character"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (7), (57), (nil), (nil), (nil), (nil), (nil), (nil), (8), (7), (nil), (nil), (nil), (nil), (nil), (nil), (52), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (5), (5), (135), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (5), (91), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (84), (171), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (17), (nil), (nil), (nil), (nil), (nil), (5), (245), (nil), (nil), (nil), (nil), (117), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (195), (0), (4), (52), (nil), (nil), (nil), (nil), (0), (3), (220), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (17), (117), (1) }; t.n = 266; return t end)(), 27, (function() local t = { (34), (204), (11), (0), (0), (25), (490), (490), (166), (19), (177), (213), (nil), (270), (0), (176), (111), (5), (5), (135), (2), (72), (12), (nil), (371), (0), (17), (76), (11), (5), (218), (62), (51), (234), (1), (2), (98), (66), (5), (60), (0), (23), (126), (127), (109), (5), (17), (nil), (337), (0), (170), (3), (5), (5), (0), (145), (137), (374), (5), (5), (0), (47), (264), (5), (6), (218), (2), (nil), (0), (98), (0), (25), (nil), (415), (19), (57), (43), (1), (0), (0), (480), (295), (nil), (19), (128), (17), (486), (17), (253), (9), (217), (71), (5), (0), (nil), (313), (0), (268), (233), (232), (269), (0), (0), (nil), (nil), (nil), (19), (135), (4), (5), (28), (127), (392), (5), (176), (5), (255), (0), (nil), (373), (19), (91), (0), (212), (0), (203), (78), (150), (0), (nil), (nil), (nil), (nil), (4), (115), (38), (169), (366), (205), (0), (0), (nil), (nil), (19), (171), (nil), (223), (0), (255), (42), (0), (0), (414), (4), (19), (235), (0), (0), (287), (425), (19), (245), (0), (0), (nil), (nil), (19), (122), (162), (276), (101), (0), (0), (nil), (3), (275), (117), (5), (5), (0), (nil), (200), (240), (0), (374), (256), (0), (0), (25), (0), (406), (406), (406), (485), (19), (52), (0), (0), (nil), (nil), (nil), (19), (220), (70), (127), (17), (211), (3), (3), (3), (253), (271), (85), (127), (392), (5), (204), (186), (5), (183), (3), (3), (3), (161), (3), (6), (214), (65), (3), (3), (3), (32), (171), (220), (207), (0), (0), (nil), (205), (56), (0), (28), (100), (156), (198), (127), (135), (160), (19), (109), (107), (5), (38), (0), (51), (3), (540), (127), (127), (77), (0), (25), (0), (477), (296), (198), (19), (1), (260), (0), (nil), (nil), (nil), (nil), (108), (233), (243) }; t.n = 277; return t end)(), (function() local t = { (127), (32), (127), (131), (34), (72), (101), (101), (101), (14), (127), (127), (117), (117), (81), (32), (127), (195), (145), (143), (193), (11), (127), (117), (117), (81), (32), (127), (117), (99), (32), (127), (32), (127), (155), (185), (32), (127), (195), (145), (84), (127), (127), (117), (117), (1), (127), (117), (117), (81), (127), (59), (195), (145), (84), (127), (127), (213), (195), (145), (84), (127), (117), (164), (89), (127), (145), (8), (81), (127), (131), (72), (101), (101), (14), (127), (127), (59), (131), (34), (101), (101), (101), (14), (127), (5), (141), (17), (101), (92), (127), (195), (145), (84), (117), (117), (81), (127), (32), (127), (127), (34), (131), (101), (101), (101), (92), (127), (126), (1), (127), (117), (117), (1), (127), (47), (127), (131), (101), (101), (92), (127), (84), (117), (84), (127), (127), (127), (84), (117), (8), (8), (8), (126), (127), (32), (127), (8), (127), (90), (131), (101), (101), (92), (127), (117), (117), (81), (32), (127), (34), (131), (101), (101), (92), (127), (34), (131), (101), (101), (92), (127), (131), (90), (101), (101), (92), (127), (127), (127), (127), (84), (181), (117), (39), (127), (127), (122), (145), (84), (117), (117), (127), (84), (117), (127), (90), (131), (72), (34), (101), (101), (101), (101), (14), (127), (34), (131), (101), (101), (101), (92), (127), (127), (127), (39), (127), (164), (145), (186), (127), (8), (127), (63), (117), (47), (127), (127), (39), (127), (195), (145), (186), (114), (134), (108), (124), (36), (145), (186), (164), (127), (127), (127), (127), (34), (131), (20), (32), (127), (81), (32), (127), (127), (173), (117), (114), (56), (33), (135), (36), (47), (127), (142), (127), (127), (100), (117), (100), (127), (131), (72), (90), (101), (101), (101), (14), (127), (127), (84), (117), (8), (8), (8), (127), (127), (127) }; t.n = 277; return t end)(), (function() local t = { (0), (196), (196), (198), (198), (198), (198), (198), (198), (198), (198), (196), (195), (195), (195), (195), (195), (195), (195), (195), (195), (195), (195), (194), (194), (194), (194), (194), (199), (199), (199), (199), (188), (188), (184), (185), (185), (185), (194), (194), (194), (194), (197), (194), (194), (194), (194), (193), (193), (193), (193), (189), (197), (197), (197), (197), (197), (192), (193), (193), (193), (193), (199), (199), (199), (199), (185), (185), (185), (185), (192), (192), (192), (192), (192), (192), (194), (200), (197), (197), (197), (197), (197), (197), (197), (197), (197), (197), (197), (197), (197), (196), (196), (196), (196), (196), (196), (196), (186), (186), (198), (193), (193), (193), (193), (193), (193), (193), (198), (198), (198), (195), (195), (195), (195), (197), (197), (196), (196), (196), (196), (196), (191), (191), (192), (192), (197), (197), (197), (197), (197), (197), (197), (197), (197), (193), (193), (197), (197), (186), (186), (186), (186), (186), (186), (197), (197), (197), (197), (197), (197), (197), (197), (197), (197), (197), (193), (193), (193), (193), (193), (193), (191), (191), (191), (191), (191), (191), (191), (193), (193), (186), (186), (186), (186), (186), (196), (198), (198), (198), (198), (198), (198), (199), (199), (199), (197), (197), (197), (197), (197), (197), (197), (197), (197), (197), (187), (187), (187), (187), (187), (187), (187), (192), (197), (197), (197), (188), (188), (188), (188), (197), (197), (196), (196), (196), (196), (197), (199), (199), (187), (187), (187), (187), (187), (187), (187), (187), (187), (187), (188), (188), (186), (187), (188), (197), (197), (197), (197), (197), (198), (198), (198), (193), (104), (193), (193), (193), (193), (193), (193), (193), (193), (188), (188), (198), (199), (200), (200), (200), (196), (196), (196), (196), (196), (196), (196), (196), (196), (198), (198), (198), (198), (198), (198), (186) }; t.n = 276; return t end)(), (function() local t = { (0), (5), (0), (26), (0), (0), (25), (24), (26), (98), (0), (0), (7), (7), (5), (5), (0), (4), (39), (150), (94), (nil), (0), (7), (7), (5), (5), (0), (4), (nil), (5), (0), (3), (0), (0), (1), (2), (0), (4), (39), (nil), (0), (0), (3), (5), (4), (0), (27), (7), (5), (0), (0), (4), (39), (nil), (0), (0), (4), (4), (39), (nil), (0), (4), (0), (5), (0), (nil), (0), (2), (0), (26), (0), (25), (26), (94), (0), (0), (0), (26), (0), (24), (24), (26), (37), (0), (17), (17), (505), (16), (0), (0), (4), (39), (nil), (7), (7), (5), (0), (2), (0), (0), (0), (26), (26), (24), (26), (0), (0), (0), (4), (0), (3), (5), (4), (0), (4), (0), (26), (26), (26), (0), (0), (nil), (3), (nil), (0), (0), (0), (nil), (5), (0), (0), (0), (0), (0), (5), (0), (0), (0), (20), (26), (20), (26), (0), (0), (7), (7), (5), (5), (0), (0), (26), (24), (26), (0), (0), (0), (26), (24), (26), (0), (0), (26), (20), (20), (26), (0), (0), (0), (0), (0), (nil), (3), (3), (168), (0), (0), (146), (39), (nil), (7), (7), (0), (nil), (5), (0), (20), (26), (0), (0), (20), (24), (25), (26), (115), (0), (0), (26), (24), (26), (26), (0), (0), (0), (0), (85), (0), (0), (nil), (0), (0), (0), (0), (3), (5), (4), (0), (0), (256), (0), (1), (nil), (0), (40), (49), (198), (2), (11), (nil), (0), (0), (0), (0), (0), (0), (0), (16), (430), (183), (0), (5), (5), (0), (0), (248), (3), (148), (5), (5), (254), (72), (4), (0), (0), (0), (0), (245), (3), (5), (0), (26), (0), (20), (25), (20), (26), (44), (0), (0), (nil), (5), (0), (0), (0), (0), (0), (0) }; t.n = 277; return t end)(), (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("KeyCode"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("KeyCode"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("KeyCode"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("HumanoidRootPart"), (nil), (nil), (nil), (nil), (48), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (127), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("KeyCode"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (40), (40), (171), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (92), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("new"), (0), (1), (0), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (172), (233), (nil), (nil), ("KeyCode"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (58), (169), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Fly"), (nil), (nil), (nil), (nil), (nil), (nil), ("KeyCode"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (221), (221), (234), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (219), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("new"), (0), (1), (0) }; t.n = 274; return t end)(), (function() local t = { (0), (0), (0), (0), (24), (0), (nil), (nil), (373), (26), (0), (0), (7), (7), (0), (0), (0), (0), (5), (7), (29), (240), (0), (7), (7), (0), (0), (0), (5), (5), (0), (0), (0), (0), (nil), (0), (0), (0), (0), (106), (7), (0), (0), (5), (5), (4), (0), (7), (7), (0), (0), (0), (0), (5), (7), (0), (0), (4), (0), (5), (7), (0), (5), (6), (5), (0), (1), (4), (0), (0), (0), (0), (nil), (nil), (26), (0), (0), (0), (0), (24), (nil), (nil), (4), (26), (0), (311), (17), (14), (nil), (18), (0), (0), (5), (7), (7), (7), (0), (0), (0), (0), (0), (24), (0), (nil), (nil), (nil), (26), (0), (5), (4), (0), (5), (5), (4), (0), (4), (0), (0), (nil), (nil), (26), (0), (3), (3), (4), (0), (0), (0), (5), (5), (146), (20), (62), (5), (0), (0), (0), (17), (0), (0), (0), (nil), (nil), (26), (0), (7), (7), (0), (0), (0), (24), (0), (nil), (511), (26), (0), (24), (0), (nil), (nil), (26), (0), (0), (0), (nil), (394), (26), (0), (0), (0), (0), (3), (0), (3), (0), (0), (0), (204), (5), (7), (7), (7), (0), (5), (5), (0), (0), (0), (0), (24), (nil), (nil), (nil), (nil), (26), (0), (24), (0), (nil), (nil), (nil), (26), (0), (0), (0), (0), (0), (3), (3), (0), (0), (150), (0), (5), (5), (4), (0), (0), (0), (0), (0), (3), (0), (152), (52), (239), (229), (121), (3), (0), (3), (0), (0), (0), (0), (14), (0), (17), (0), (0), (0), (0), (0), (0), (415), (184), (192), (5), (187), (207), (11), (4), (0), (3), (0), (0), (140), (5), (2), (0), (0), (0), (0), (nil), (nil), (nil), (26), (0), (0), (5), (5), (6), (7), (8), (0), (0), (0) }; t.n = 277; return t end)(), 0, (function() local t = { (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Enum"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (0), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Enum"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Enum"), (nil), (nil), (nil), (nil), (nil), ("Enum"), (nil), (nil), (nil), (nil), (nil), ("FindFirstChild"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Enum"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("workspace"), (nil), ("Vector3"), (nil), (nil), (nil), ("Vector3"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("getgenv"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Enum"), (nil), (nil), (nil), ("Vector3"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Disconnect"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Destroy"), (nil), (nil), (nil), (nil), (nil), (nil), ("Destroy"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("Vector3") }; t.n = 270; return t end)()), {})))
		;(nil --[[ constant not decoded ]])[49](v[1], t3[1])
		;(t1[1])[7] = v[1]
		;(t1[1])[5] = (t1[1])[5]((t1[1])[6], (t1[1])[7])
		upv1 = (t1[1])[5]
		error("devirt: symbolic generic for (at 0:75)")
	end

	error("devirt: symbolic generic for (at 0:59)")
end

-- proto 27: vm sequence 38, 0 opcodes
local function proto_27()
	(t1[1])[1] = upv0

	if (t1[1])[1] then
		(t1[1])[1] = upv0
		;(t1[1])[2] = (t1[1])[1]
		;(t1[1])[1] = (t1[1])[1].Disconnect
		;(t1[1])[1]((t1[1])[2])
	end
	;(t1[1])[1] = upv1.Stepped
	;(t1[1])[2] = (t1[1])[1]
	;(t1[1])[1] = (t1[1])[1].Connect

	local v = table.pack((nil --[[ constant not decoded ]])[57](table.pack(table.pack(table.pack(2, 2), table.pack(3, 2)), table.pack(nil, nil, "Character", nil, nil, nil, nil, "Character", nil, nil, nil, nil, nil, nil, nil, nil, 50), 5, table.pack(7, 14, 1, 1, nil, 0, 12, 1, 12, 2, 322, 1, 11, 1, 1, 2, nil, 11), table.pack(127, 127, 155, 145, 8, 81, 127, 155, 32, 127, 158, 59, 32, 127, 164, 17, 101, 127), table.pack(0, 208, 207, 207, 207, 207, 207, 207, 207, 207, 58, 208, 208, 208, 209, 209, 210), table.pack(0, 0, 0, nil, 0, 1, 0, 0, 1, 0, 33, 0, 1, 0, 0, nil, 1, 0), table.pack(nil, nil, nil, nil, "Humanoid", nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, "JumpPower"), table.pack(0, 0, nil, 1, 3, 0, 0, nil, 0, 0, 268, 0, 0, 0, 2, 1, nil, 0), 0, table.pack(nil, nil, nil, "FindFirstChildOfClass", nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, "WalkSpeed")), {}))
	;(nil --[[ constant not decoded ]])[49](v[1], t3[1])
	;(t1[1])[3] = v[1]
	;(t1[1])[1] = (t1[1])[1]((t1[1])[2], (t1[1])[3])
	upv0 = (t1[1])[1]
	error("devirt: symbolic generic for (at 0:15)")
end

-- proto t376: vm sequence 39, 0 opcodes
local function proto_t376()
	(t1[1])[1] = (t2[2])[1]
	;(t1[1])[3] = (t1[1])[1]
	;(t1[1])[2] = (t1[1])[1].FindFirstChildOfClass
	;(t1[1])[4] = "Humanoid"
	;(t1[1])[2] = (t1[1])[2]((t1[1])[3], (t1[1])[4])

	if not (t1[1])[2] then
		error("devirt: symbolic generic for (at 0:57)")
	end
	;(t1[1])[25] = {
		67,
		78,
		0,
		250,
		212,
		139,
		nil,
		218,
		nil,
		47,
		0,
		24,
		0,
		nil,
		nil,
		100,
		100,
		416,
		18,
		2,
		nil,
		0,
		nil,
		nil,
		nil,
		nil,
		4,
		4,
		109,
		0,
		0,
		nil,
		nil,
		18,
		116,
		56,
		455,
		0,
		180,
		102,
		252,
		nil,
		25,
		378,
		3,
		20,
		3,
		nil,
		161,
		nil,
		4,
		4,
		353,
		467,
		1,
		61,
		3,
		4,
		1,
		29,
		110,
		103,
		1,
		0,
		5,
		73,
		89,
		0,
		2,
		nil,
		0,
		56,
		59,
		5,
		0,
		0,
		57,
		46,
		24,
		0,
		0,
		0,
		nil,
		nil,
		nil,
		nil,
		nil,
		18,
		66,
		14,
		0,
		279,
		231,
		506,
		16,
		283,
		8,
		60,
		3,
		nil,
		0,
		37,
		77,
		0,
		0,
		nil,
		nil,
		18,
		62,
		10,
		0,
		0,
		nil,
		nil,
		18,
		98,
		nil,
		nil,
		35,
	}
	;(t1[1])[23] = {
		0,
		0,
		4,
		75,
		4,
		252,
		235,
		88,
		5,
		0,
		0,
		0,
		0,
		nil,
		nil,
		347,
		nil,
		nil,
		25,
		0,
		nil,
		4,
		4,
		5,
		6,
		7,
		4,
		3,
		0,
		0,
		23,
		nil,
		nil,
		25,
		0,
		0,
		293,
		3,
		151,
		3,
		49,
		177,
		235,
		4,
		0,
		0,
		96,
		6,
		7,
		125,
		4,
		3,
		365,
		nil,
		3,
		0,
		0,
		0,
		0,
		0,
		0,
		0,
		3,
		0,
		nil,
		0,
		0,
		0,
		1,
		4,
		0,
		0,
		0,
		5,
		33,
		0,
		0,
		0,
		0,
		0,
		23,
		0,
		nil,
		nil,
		nil,
		nil,
		nil,
		25,
		0,
		0,
		0,
		14,
		395,
		16,
		14,
		526,
		17,
		0,
		1,
		5,
		0,
		0,
		0,
		0,
		0,
		234,
		nil,
		25,
		0,
		0,
		0,
		0,
		nil,
		526,
		25,
		0,
		3,
		1,
		0,
	}
	;(t1[1])[23][47] = 0
	;(t1[1])[25][60] = 116
	;(t1[1])[18] = nil
	;(t1[1])[19] = nil
	;(t1[1])[20] = nil
	;(t1[1])[21] = nil
	;(t1[1])[22] = nil
	;(t1[1])[23] = nil
	;(t1[1])[24] = nil
	;(t1[1])[25] = nil
	;(t1[1])[3] = (t1[1])[2].Health
	error("devirt: while loop limit (at 0:118)")
end

-- proto 48: vm sequence 40, 0 opcodes
local function proto_48()
	(t1[1])[1] = (t3[1]).pairs
	;(t1[1])[2] = (t3[1]).workspace
	;(t1[1])[3] = (t1[1])[2]
	;(t1[1])[2] = (t1[1])[2].GetDescendants
	error("devirt: numeric for with symbolic bounds (at 0:19)")
end

-- proto 47: vm sequence 41, 0 opcodes
local function proto_47()
	(t1[1])[1] = (t3[1]).getgenv
	;(t1[1])[1] = (t1[1])[1]()
	;(t1[1])[1] = (t1[1])[1].ESP

	if not (t1[1])[1] then
		(t1[1])[1] = upv2
		;(t1[1])[1]()
		error("devirt: symbolic generic for (at 0:52)")
	end
	;(t1[1])[1] = (t3[1]).pairs
	;(t1[1])[3] = (t1[1])[2]
	;(t1[1])[2] = (t1[1])[2].GetChildren
	error("devirt: numeric for with symbolic bounds (at 0:100)")
end

-- proto 50: vm sequence 42, 0 opcodes
local function proto_50()
	(t1[1])[1] = upv0.Character

	if (t1[1])[1] then
		(t1[1])[1] = upv0.Character
		;(t1[1])[2] = (t1[1])[1]
		;(t1[1])[1] = (t1[1])[1].FindFirstChildOfClass
		;(t1[1])[3] = "Humanoid"
		;(t1[1])[1] = (t1[1])[1]((t1[1])[2], (t1[1])[3])
	end

	if (t1[1])[1] then
		(t1[1])[2] = upv1
		;(t1[1])[1].WalkSpeed = (t1[1])[2]
		;(t1[1])[1].JumpPower = 50
	end

	error("devirt: symbolic generic for (at 0:12)")
end

-- proto 28: vm sequence 43, 0 opcodes
local function proto_28()
	(t1[1])[1] = upv0

	if not (t1[1])[1] then
		(t1[1])[1] = upv1
		;(t1[1])[2] = (t1[1])[1]
		;(t1[1])[1] = (t1[1])[1].Destroy
		;(t1[1])[1]((t1[1])[2])
		;(t1[1])[1] = upv2
		;(t1[1])[2] = (t1[1])[1]
		;(t1[1])[1] = (t1[1])[1].Destroy
		;(t1[1])[1]((t1[1])[2])
		error("devirt: symbolic generic for (at 0:31)")
	end

	while true do
		(t1[1])[19] = {
			0,
			0,
			0,
			nil,
			nil,
			21,
			0,
			19,
			0,
			0,
			0,
			nil,
			nil,
			nil,
			nil,
			21,
			0,
			0,
			0,
			10,
			168,
			224,
			185,
			213,
			12,
			5,
			nil,
			13,
			0,
			0,
			0,
			0,
			171,
			120,
			0,
			0,
			1,
			0,
			1,
			1,
			0,
			0,
			1,
			0,
			0,
			0,
		}
		;(t1[1])[20] = {
			0,
			21,
			0,
			20,
			21,
			24,
			0,
			0,
			0,
			21,
			15,
			19,
			15,
			20,
			21,
			144,
			0,
			5,
			11,
			12,
			22,
			180,
			133,
			12,
			12,
			nil,
			11,
			0,
			0,
			0,
			0,
			nil,
			179,
			372,
			0,
			1,
			nil,
			0,
			0,
			nil,
			0,
			0,
			0,
			1,
			0,
			0,
		}
		;(t1[1])[21] = {
			42,
			0,
			20,
			nil,
			nil,
			14,
			35,
			0,
			20,
			0,
			0,
			nil,
			nil,
			nil,
			nil,
			14,
			45,
			0,
			0,
			68,
			35,
			177,
			51,
			12,
			171,
			12,
			nil,
			4,
			31,
			1,
			1,
			0,
			1,
			83,
			7,
			1,
			1,
			1,
			2,
			1,
			29,
			35,
			0,
			41,
			34,
			17,
		}
		;(t1[1])[15] = {
			127,
			131,
			93,
			101,
			101,
			14,
			127,
			34,
			93,
			131,
			90,
			101,
			101,
			101,
			101,
			14,
			127,
			90,
			131,
			6,
			111,
			49,
			36,
			5,
			141,
			17,
			101,
			92,
			127,
			186,
			59,
			172,
			194,
			28,
			127,
			195,
			145,
			186,
			164,
			145,
			127,
			127,
			164,
			32,
			127,
			127,
		}
		;(t1[1])[19][33] = 0
		;(t1[1])[15][33] = 59
		;(t1[1])[20][33] = 0
		;(t1[1])[21][35] = 45
		;(t1[1])[14] = nil
		;(t1[1])[15] = nil
		;(t1[1])[16] = nil
		;(t1[1])[17] = nil
		;(t1[1])[18] = nil
		;(t1[1])[19] = nil
		;(t1[1])[20] = nil
		;(t1[1])[21] = nil
		;(t1[1])[5] = {
			127,
			131,
			93,
			101,
			101,
			14,
			127,
			34,
			93,
			131,
			90,
			101,
			101,
			101,
			101,
			14,
			127,
			90,
			131,
			6,
			111,
			49,
			36,
			5,
			141,
			17,
			101,
			92,
			127,
			186,
			59,
			172,
			194,
			28,
			127,
			195,
			145,
			186,
			164,
			145,
			127,
			127,
			164,
			32,
			127,
			127,
		}
		;(t1[1])[11] = {
			42,
			0,
			20,
			nil,
			nil,
			14,
			35,
			0,
			20,
			0,
			0,
			nil,
			nil,
			nil,
			nil,
			14,
			45,
			0,
			0,
			68,
			35,
			177,
			51,
			12,
			171,
			12,
			nil,
			4,
			31,
			1,
			1,
			0,
			1,
			83,
			7,
			1,
			1,
			1,
			2,
			1,
			29,
			35,
			0,
			41,
			34,
			17,
		}
		;(t1[1])[12] = nil --[[ constant not decoded ]] + (t1[1])[12]
		;(t1[1])[12] = (t1[1])[12] + nil --[[ constant not decoded ]]
		;(t1[1])[5][32] = (t1[1])[12]
		;(t1[1])[11][46] = 31
		;(t1[1])[4] = nil
		;(t1[1])[5] = nil
		;(t1[1])[6] = nil
		;(t1[1])[7] = nil
		;(t1[1])[8] = nil
		;(t1[1])[9] = nil
		;(t1[1])[10] = nil
		;(t1[1])[11] = nil
		;(t1[1])[12] = nil
		;(t1[1])[13] = nil
		;(t1[1])[179] = t1[1]
	end
end

-- proto 31: vm sequence 44, 0 opcodes
local function proto_31()
	(t1[1])[1] = (t3[1]).setclipboard
	;(t1[1])[2] = "https://discord.gg/9HeEetE7rt"
	;(t1[1])[1]((t1[1])[2])
	;(t1[1])[1] = (t3[1]).pcall

	local v = table.pack((nil --[[ constant not decoded ]])[57](table.pack(table.pack(table.pack(0, 2)), table.pack(nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, 192, 29059, nil, nil, 33, nil, nil, nil, nil, 6, 6, 62, nil, nil, nil, nil, "http://127.0.0.1:6463/rpc?v=1", "POST", nil, "application/json", "https://discord.com", nil, nil, nil, nil, nil, nil, "INVITE_BROWSER", nil, nil, nil, nil, nil, nil, 17, 0, 5, 195, 0, 9, nil, nil, nil, "9HeEetE7rt"), 27, (function() local t = { (15), (6), (0), (232), (74), (3), (51), (1), (1), (33), (6), (nil), (0), (1), (223), (61), (62), (0), (15), (nil), (17), (nil), (17), (nil), (9), (33), (25), (0), (nil), (nil), (nil), (19), (62), (0), (0), (nil), (nil), (0), (nil), (nil), (3), (3), (3), (0), (234), (nil), (211), (0), (16), (0), (0), (0), (25), (nil), (nil), (nil), (nil), (nil), (nil), (19), (9), (9), (nil), (125), (253), (6), (219), (6), (10) }; t.n = 69; return t end)(), (function() local t = { (127), (17), (81), (114), (21), (53), (36), (186), (59), (127), (145), (8), (81), (127), (42), (127), (127), (131), (93), (151), (5), (141), (17), (101), (92), (127), (93), (131), (101), (101), (101), (92), (127), (84), (88), (101), (101), (88), (101), (101), (17), (195), (145), (88), (6), (118), (3), (88), (127), (34), (90), (131), (93), (101), (101), (101), (101), (101), (101), (14), (127), (127), (101), (114), (21), (53), (36), (195), (127) }; t.n = 69; return t end)(), (function() local t = { (0), (307), (304), (304), (304), (304), (304), (297), (307), (297), (307), (307), (307), (307), (106), (0), (306), (297), (297), (297), (297), (297), (297), (297), (297), (297), (306), (306), (306), (306), (306), (306), (306), (297), (297), (298), (299), (300), (301), (302), (300), (304), (304), (304), (305), (305), (305), (306), (306), (297), (297), (297), (297), (297), (297), (297), (297), (297), (297), (297), (297), (297), (306), (306), (306), (306), (306), (307) }; t.n = 68; return t end)(), (function() local t = { (0), (nil), (3), (225), (nil), (252), (200), (0), (0), (0), (nil), (0), (6), (0), (388), (0), (0), (16), (0), (17), (17), (17), (nil), (16), (0), (0), (0), (26), (26), (25), (26), (0), (0), (nil), (2), (2), (2), (3), (3), (3), (nil), (0), (nil), (5), (5), (198), (13), (6), (0), (0), (20), (26), (0), (25), (24), (25), (20), (24), (26), (27), (0), (0), (6), (12), (nil), (87), (226), (0), (0) }; t.n = 69; return t end)(), table.pack(nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, nil, false, nil, nil, nil, nil, nil, nil, nil, 403, nil, -29652, nil, 10, nil, nil, nil, nil, 2, 63, 17, nil, nil, nil, nil, "Url", "Method", nil, "Content-Type", "Origin", nil, nil, nil, nil, nil, "cmd", nil, nil, nil, nil, nil, nil, nil, 20, 44, 44, 42, 42, 62, nil, nil, nil, "code"), (function() local t = { (0), (5), (0), (243), (2), (61), (254), (0), (0), (0), (6), (8), (0), (0), (19), (0), (0), (0), (0), (nil), (nil), (17), (15), (nil), (18), (0), (0), (0), (nil), (nil), (nil), (26), (0), (1), (0), (nil), (nil), (0), (nil), (nil), (2), (0), (3), (0), (96), (170), (nil), (0), (0), (24), (0), (0), (0), (nil), (nil), (nil), (nil), (nil), (nil), (26), (0), (0), (nil), (20), (5), (31), (24), (0), (0) }; t.n = 69; return t end)(), 0, (function() local t = { (nil), ("nonce"), (nil), (nil), ("Body"), (nil), (nil), (nil), (nil), (nil), ("GenerateGUID"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (36), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("request"), (nil), (nil), (nil), (nil), (nil), (nil), ("Headers"), (nil), ("JSONEncode"), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), (nil), ("args") }; t.n = 65; return t end)()), {}))
	;(nil --[[ constant not decoded ]])[49](v[1], t3[1])
	;(t1[1])[2] = v[1]
	;(t1[1])[1]((t1[1])[2])
	error("devirt: symbolic generic for (at 0:10)")
end

-- proto 29: vm sequence 45, 0 opcodes
local function proto_29()
	error("devirt: symbolic generic for (at 0:2)")
end

-- proto 30: vm sequence 46, 0 opcodes
local function proto_30()
	(t1[1])[1] = upv0
	;(t1[1])[1]()
	error("devirt: symbolic generic for (at 0:5)")
end

-- proto 32: vm sequence 47, 0 opcodes
local function proto_32()
	(t1[1])[1] = (t3[1]).request
	;(t1[1])[2] = {}
	;(t1[1])[2].Url = "http://127.0.0.1:6463/rpc?v=1"
	;(t1[1])[2].Method = "POST"
	;(t1[1])[3] = {}
	;(t1[1])[3]["Content-Type"] = "application/json"
	;(t1[1])[3].Origin = "https://discord.com"
	;(t1[1])[2].Headers = (t1[1])[3]
	;(t1[1])[3] = upv0
	;(t1[1])[4] = (t1[1])[3]
	;(t1[1])[3] = (t1[1])[3].JSONEncode
	;(t1[1])[5] = {}
	;(t1[1])[6] = {}
	;(t1[1])[6].code = "9HeEetE7rt"
	;(t1[1])[6] = upv0
	;(t1[1])[7] = (t1[1])[6]
	;(t1[1])[6] = (t1[1])[6].GenerateGUID
	;(t1[1])[8] = false
	;(t1[1])[6] = (t1[1])[6]((t1[1])[7], (t1[1])[8])
	;(t1[1])[5].nonce = (t1[1])[6]
	;(t1[1])[3] = (t1[1])[3]((t1[1])[4], (t1[1])[5])
	;(t1[1])[1]((t1[1])[2])
	error("devirt: symbolic generic for (at 0:9)")
end

-- proto 33: vm sequence 48, 0 opcodes
local function proto_33()
	(t1[1])[1] = (t2[2])[1]
	;(t1[1])[2] = (t3[1]).getgenv
	;(t1[1])[2] = (t1[1])[2]()
	;(t1[1])[2].FarmTree = (t1[1])[1]

	if (t1[1])[1] then
		(t1[1])[2] = (t3[1]).task
		;(t1[1])[2] = (t1[1])[2].spawn
		;(t1[1])[3] = upv0
		;(t1[1])[2]((t1[1])[3])
		error("devirt: symbolic generic for (at 0:18)")
	end

	error("devirt: symbolic generic for (at 0:30)")
end

-- proto 36: vm sequence 49, 0 opcodes
local function proto_36()
	(t1[1])[1] = (t2[2])[1]
	;(t1[1])[2] = (t3[1]).getgenv
	;(t1[1])[2] = (t1[1])[2]()
	;(t1[1])[2].GunKillAll = (t1[1])[1]

	if (t1[1])[1] then
		(t1[1])[2] = (t3[1]).task
		;(t1[1])[2] = (t1[1])[2].spawn
		;(t1[1])[3] = upv0
		;(t1[1])[2]((t1[1])[3])
		error("devirt: symbolic generic for (at 0:4)")
	end

	error("devirt: symbolic generic for (at 0:32)")
end

-- proto 39: vm sequence 50, 0 opcodes
local function proto_39()
	(t1[1])[1] = (t2[2])[1]
	;(t1[1])[2] = (t3[1]).getgenv
	;(t1[1])[2] = (t1[1])[2]()
	;(t1[1])[2].AxeAuraTarget = (t1[1])[1]
	;(t1[1])[2] = (t3[1]).getgenv
	;(t1[1])[2] = (t1[1])[2]()

	if (t1[1])[2] then
		(t1[1])[2] = (t3[1]).getgenv
		;(t1[1])[2] = (t1[1])[2]()
		;(t1[1])[3] = (t1[1])[1] == "Zombie"
		;(t1[1])[2] = (t3[1]).getgenv
		;(t1[1])[2] = (t1[1])[2]()
		;(t1[1])[3] = (t1[1])[1] == "Chicken"
		;(t1[1])[2].AxeAuraChicken = (t1[1])[3]
		;(t1[1])[23] = {
			70,
			2,
			0,
			nil,
			nil,
			16,
			46,
			33,
			0,
			0,
			nil,
			nil,
			16,
			33,
			37,
			134,
			0,
			22,
			nil,
			nil,
			nil,
			16,
			49,
			1,
			0,
			0,
			251,
			243,
			49,
			nil,
			224,
			71,
			14,
			0,
			0,
			0,
			58,
			72,
			49,
			0,
			0,
			nil,
			nil,
			nil,
			16,
			7,
			179,
			0,
			71,
			0,
			0,
			nil,
			14,
			nil,
			14,
			nil,
			6,
			59,
			23,
			33,
			0,
			0,
			nil,
			nil,
			16,
			23,
			0,
			3,
			3,
			1,
			7,
			1,
			0,
			0,
			3,
			33,
			27,
			3,
			150,
			0,
			66,
		}
		;(t1[1])[23][47] = 2
		;(t1[1])[23][2] = 46
		;(t1[1])[16] = nil
		;(t1[1])[17] = nil
		;(t1[1])[18] = nil
		;(t1[1])[19] = nil
		;(t1[1])[20] = nil
		;(t1[1])[21] = nil
		;(t1[1])[22] = nil
		;(t1[1])[23] = nil
		;(t1[1])[179] = upv0
		;(t1[1])[2]()
	end

	error("devirt: symbolic generic for (at 0:72)")
end

-- proto 40: vm sequence 51, 0 opcodes
local function proto_40()
	(t1[1])[1] = (t2[2])[1]
	;(t1[1])[2] = (t3[1]).getgenv
	;(t1[1])[2] = (t1[1])[2]()
	;(t1[1])[2].AxeAuraActive = (t1[1])[1]
	;(t1[1])[2] = (t3[1]).getgenv
	;(nil --[[?NilIndex]])()
	;(t1[1])[3] = (t1[1])[1]

	if (t1[1])[3] then
		(t1[1])[3] = (t3[1]).getgenv
		;(t1[1])[3] = (t1[1])[3]()
		;(t1[1])[3] = (t1[1])[3].AxeAuraTarget
		;(t1[1])[3] = (t1[1])[3] == "Zombie"
	end
	;(t1[1])[2].AxeAuraZombie = (t1[1])[3]
	;(t1[1])[2] = (t3[1]).getgenv
	;(t1[1])[2] = (t1[1])[2]()
	;(t1[1])[3] = (t1[1])[1]

	if (t1[1])[3] then
		(t1[1])[3] = (t3[1]).getgenv
		;(nil --[[?NilIndex]])()
		;(t1[1])[3] = (t1[1])[3].AxeAuraTarget
		;(t1[1])[3] = (t1[1])[3] == "Chicken"
	end
	;(t1[1])[2].AxeAuraChicken = (t1[1])[3]
	;(t1[1])[2] = upv0
	;(t1[1])[2]()
	error("devirt: symbolic generic for (at 0:19)")
end

-- proto 42: vm sequence 52, 0 opcodes
local function proto_42()
	(t1[1])[1] = (t2[2])[1]
	;(t1[1])[2] = (t3[1]).getgenv
	;(t1[1])[2] = (t1[1])[2]()
	;(t1[1])[2].Fly = (t1[1])[1]

	if (t1[1])[1] then
		(t1[1])[2] = upv0
		;(t1[1])[2]()
	end

	error("devirt: symbolic generic for (at 0:17)")
end

-- proto 51: vm sequence 53, 0 opcodes
local function proto_51()
	(t1[1])[1] = upv0.Character
	;(t1[1])[2] = (t1[1])[1]

	if (t1[1])[2] then
		(t1[1])[3] = (t1[1])[1]
		;(t1[1])[2] = (t1[1])[1].FindFirstChild
		;(t1[1])[4] = "HumanoidRootPart"
		;(t1[1])[2] = (t1[1])[2]((t1[1])[3], (t1[1])[4])
	end

	if (t1[1])[2] then
		(t1[1])[3] = (t3[1]).getgenv
		;(t1[1])[3] = (t1[1])[3]()
		;(t1[1])[3] = (t1[1])[3].Fly

		if (t1[1])[3] then
			(t1[1])[26] = {
				34,
				204,
				11,
				0,
				0,
				25,
				490,
				490,
				166,
				19,
				177,
				213,
				nil,
				270,
				0,
				176,
				111,
				5,
				5,
				135,
				2,
				72,
				12,
				nil,
				371,
				0,
				17,
				76,
				11,
				5,
				218,
				62,
				51,
				234,
				1,
				2,
				98,
				66,
				5,
				60,
				0,
				23,
				126,
				127,
				109,
				5,
				17,
				nil,
				337,
				0,
				170,
				3,
				5,
				5,
				0,
				145,
				137,
				374,
				5,
				5,
				0,
				47,
				264,
				5,
				6,
				218,
				2,
				nil,
				0,
				98,
				0,
				25,
				nil,
				415,
				19,
				57,
				43,
				1,
				0,
				0,
				480,
				295,
				nil,
				19,
				128,
				17,
				486,
				17,
				253,
				9,
				217,
				71,
				5,
				0,
				nil,
				313,
				0,
				268,
				233,
				232,
				269,
				0,
				0,
				nil,
				nil,
				nil,
				19,
				135,
				4,
				5,
				28,
				127,
				392,
				5,
				176,
				5,
				255,
				0,
				nil,
				373,
				19,
				91,
				0,
				212,
				0,
				203,
				78,
				150,
				0,
				nil,
				nil,
				nil,
				nil,
				4,
				115,
				38,
				169,
				366,
				205,
				0,
				0,
				nil,
				nil,
				19,
				171,
				nil,
				223,
				0,
				255,
				42,
				0,
				0,
				414,
				4,
				19,
				235,
				0,
				0,
				287,
				425,
				19,
				245,
				0,
				0,
				nil,
				nil,
				19,
				122,
				162,
				276,
				101,
				0,
				0,
				nil,
				3,
				275,
				117,
				5,
				5,
				0,
				nil,
				200,
				240,
				0,
				374,
				256,
				0,
				0,
				25,
				0,
				406,
				406,
				406,
				485,
				19,
				52,
				0,
				0,
				nil,
				nil,
				nil,
				19,
				220,
				70,
				127,
				17,
				211,
				3,
				3,
				3,
				253,
				271,
				85,
				127,
				392,
				5,
				204,
				186,
				5,
				183,
				3,
				3,
				3,
				161,
				3,
				6,
				214,
				65,
				3,
				3,
				3,
				32,
				171,
				220,
				207,
				0,
				0,
				nil,
				205,
				56,
				0,
				28,
				100,
				156,
				198,
				127,
				135,
				160,
				19,
				109,
				107,
				5,
				38,
				0,
				51,
				3,
				540,
				127,
				127,
				77,
				0,
				25,
				0,
				477,
				296,
				198,
				19,
				1,
				260,
				0,
				nil,
				nil,
				nil,
				nil,
				108,
				233,
				243,
			}
			;(t1[1])[20] = {
				127,
				32,
				127,
				131,
				34,
				72,
				101,
				101,
				101,
				14,
				127,
				127,
				117,
				117,
				81,
				32,
				127,
				195,
				145,
				143,
				193,
				11,
				127,
				117,
				117,
				81,
				32,
				127,
				117,
				99,
				32,
				127,
				32,
				127,
				155,
				185,
				32,
				127,
				195,
				145,
				84,
				127,
				127,
				117,
				117,
				1,
				127,
				117,
				117,
				81,
				127,
				59,
				195,
				145,
				84,
				127,
				127,
				213,
				195,
				145,
				84,
				127,
				117,
				164,
				89,
				127,
				145,
				8,
				81,
				127,
				131,
				72,
				101,
				101,
				14,
				127,
				127,
				59,
				131,
				34,
				101,
				101,
				101,
				14,
				127,
				5,
				141,
				17,
				101,
				92,
				127,
				195,
				145,
				84,
				117,
				117,
				81,
				127,
				32,
				127,
				127,
				34,
				131,
				101,
				101,
				101,
				92,
				127,
				126,
				1,
				127,
				117,
				117,
				1,
				127,
				47,
				127,
				131,
				101,
				101,
				92,
				127,
				84,
				117,
				84,
				127,
				127,
				127,
				84,
				117,
				8,
				8,
				8,
				126,
				127,
				32,
				127,
				8,
				127,
				90,
				131,
				101,
				101,
				92,
				127,
				117,
				117,
				81,
				32,
				127,
				34,
				131,
				101,
				101,
				92,
				127,
				34,
				131,
				101,
				101,
				92,
				127,
				131,
				90,
				101,
				101,
				92,
				127,
				127,
				127,
				127,
				84,
				181,
				117,
				39,
				127,
				127,
				122,
				145,
				84,
				117,
				117,
				127,
				84,
				117,
				127,
				90,
				131,
				72,
				34,
				101,
				101,
				101,
				101,
				14,
				127,
				34,
				131,
				101,
				101,
				101,
				92,
				127,
				127,
				127,
				39,
				127,
				164,
				145,
				186,
				127,
				8,
				127,
				63,
				117,
				47,
				127,
				127,
				39,
				127,
				195,
				145,
				186,
				114,
				134,
				108,
				124,
				36,
				145,
				186,
				164,
				127,
				127,
				127,
				127,
				34,
				131,
				20,
				32,
				127,
				81,
				32,
				127,
				127,
				173,
				117,
				114,
				56,
				33,
				135,
				36,
				47,
				127,
				142,
				127,
				127,
				100,
				117,
				100,
				127,
				131,
				72,
				90,
				101,
				101,
				101,
				14,
				127,
				127,
				84,
				117,
				8,
				8,
				8,
				127,
				127,
				127,
			}
			;(t1[1])[20][58] = 117
			;(t1[1])[26][169] = nil --[[ constant not decoded ]]
			;(t1[1])[19] = nil
			;(t1[1])[20] = nil
			;(t1[1])[21] = nil
			;(t1[1])[22] = nil
			;(t1[1])[23] = nil
			;(t1[1])[24] = nil
			;(t1[1])[25] = nil
			;(t1[1])[26] = nil
			;(t1[1])[3] = (t3[1]).workspace
			;(t1[1])[3] = (t1[1])[3][nil --[[ constant not decoded ]]]
			;(t1[1])[4] = (t3[1]).Vector3
			;(t1[1])[26] = {
				34,
				204,
				11,
				0,
				0,
				25,
				490,
				490,
				166,
				19,
				177,
				213,
				nil,
				270,
				0,
				176,
				111,
				5,
				5,
				135,
				2,
				72,
				12,
				nil,
				371,
				0,
				17,
				76,
				11,
				5,
				218,
				62,
				51,
				234,
				1,
				2,
				98,
				66,
				5,
				60,
				0,
				23,
				126,
				127,
				109,
				5,
				17,
				nil,
				337,
				0,
				170,
				3,
				5,
				5,
				0,
				145,
				137,
				374,
				5,
				5,
				0,
				47,
				264,
				5,
				6,
				218,
				2,
				nil,
				0,
				98,
				0,
				25,
				nil,
				415,
				19,
				57,
				43,
				1,
				0,
				0,
				480,
				295,
				nil,
				19,
				128,
				17,
				486,
				17,
				253,
				9,
				217,
				71,
				5,
				0,
				nil,
				313,
				0,
				268,
				233,
				232,
				269,
				0,
				0,
				nil,
				nil,
				nil,
				19,
				135,
				4,
				5,
				28,
				127,
				392,
				5,
				176,
				5,
				255,
				0,
				nil,
				373,
				19,
				91,
				0,
				212,
				0,
				203,
				78,
				150,
				0,
				nil,
				nil,
				nil,
				nil,
				4,
				115,
				38,
				169,
				366,
				205,
				0,
				0,
				nil,
				nil,
				19,
				171,
				nil,
				223,
				0,
				255,
				42,
				0,
				0,
				414,
				4,
				19,
				235,
				0,
				0,
				287,
				425,
				19,
				245,
				0,
				0,
				nil,
				nil,
				19,
				122,
				162,
				276,
				101,
				0,
				0,
				nil,
				3,
				275,
				117,
				5,
				5,
				0,
				nil,
				200,
				240,
				0,
				374,
				256,
				0,
				0,
				25,
				0,
				406,
				406,
				406,
				485,
				19,
				52,
				0,
				0,
				nil,
				nil,
				nil,
				19,
				220,
				70,
				127,
				17,
				211,
				3,
				3,
				3,
				253,
				271,
				85,
				127,
				392,
				5,
				204,
				186,
				5,
				183,
				3,
				3,
				3,
				161,
				3,
				6,
				214,
				65,
				3,
				3,
				3,
				32,
				171,
				220,
				207,
				0,
				0,
				nil,
				205,
				56,
				0,
				28,
				100,
				156,
				198,
				127,
				135,
				160,
				19,
				109,
				107,
				5,
				38,
				0,
				51,
				3,
				540,
				127,
				127,
				77,
				0,
				25,
				0,
				477,
				296,
				198,
				19,
				1,
				260,
				0,
				nil,
				nil,
				nil,
				nil,
				108,
				233,
				243,
			}

			error("devirt: while loop limit (at 0:72)")
		end
	end
	;(t1[1])[3] = upv1
	;(t1[1])[4] = (t1[1])[3]
	;(t1[1])[3] = (t1[1])[3].Destroy
	;(t1[1])[3]((t1[1])[4])
	;(t1[1])[4] = (t1[1])[3]
	;(t1[1])[3] = (t1[1])[3].Destroy
	;(t1[1])[3]((t1[1])[4])
	;(t1[1])[3] = upv3

	if (t1[1])[3] then
		(t1[1])[3] = upv3
		;(t1[1])[4] = (t1[1])[3]
		;(t1[1])[3] = (t1[1])[3].Disconnect
		;(t1[1])[3]((t1[1])[4])
		upv3 = (t1[1])[0]
	end

	error("devirt: symbolic generic for (at 0:52)")
end

-- proto 44: vm sequence 54, 0 opcodes
local function proto_44()
	(t1[1])[1] = (t2[2])[1]

	upv0 = (t1[1])[1]
	;(t1[1])[2] = upv1
	;(t1[1])[2]()
	error("devirt: symbolic generic for (at 0:9)")
end

-- proto 45: vm sequence 55, 0 opcodes
local function proto_45()
	(t1[1])[1] = (t2[2])[1]
	upv0 = (t1[1])[1]
	error("devirt: symbolic generic for (at 0:5)")
end

-- proto 46: vm sequence 56, 0 opcodes
local function proto_46()
	(t1[1])[1] = (t2[2])[1]
	;(t1[1])[2] = (t3[1]).getgenv
	;(t1[1])[2] = (t1[1])[2]()
	;(t1[1])[2].ESP = (t1[1])[1]

	if not (t1[1])[1] then
		(t1[1])[2] = upv1
		;(nil)()
	else
		(t1[1])[2] = (t3[1]).task
		;(t1[1])[2] = (t1[1])[2].spawn
		;(t1[1])[3] = upv0
		;(t1[1])[2]((t1[1])[3])
	end

	error("devirt: symbolic generic for (at 0:56)")
end

-- proto 54: vm sequence 57, 0 opcodes
local function proto_54()
	(t1[1])[1] = (t2[2])[1]
	;(t1[1])[2] = (t1[1])[1]

	if (t1[1])[2] then
		(t1[1])[2] = (t3[1]).Color3
		;(t1[1])[2] = (t1[1])[2].fromRGB
		;(t1[1])[3] = 245
		;(t1[1])[5] = 245
		;(t1[1])[2] = (t1[1])[2]((nil --[[ constant not decoded ]])[26](t1[1], 5, 3))
	end

	if not (t1[1])[2] then
		(t1[1])[2] = (t3[1]).Color3
		;(t1[1])[2] = (t1[1])[2].fromRGB
		;(t1[1])[3] = 255
		;(t1[1])[4] = 255
		;(t1[1])[2] = (t1[1])[2]((nil --[[ constant not decoded ]])[26](t1[1], 5, 3))
	end
	;(t1[1])[3] = upv0
	;(t1[1])[4] = (t1[1])[3]
	;(t1[1])[3] = (t1[1])[3].Create
	;(t1[1])[5] = upv1
	;(t1[1])[6] = (t3[1]).TweenInfo
	;(t1[1])[6] = (t1[1])[6].new
	;(t1[1])[8] = (t3[1]).Enum
	;(t1[1])[8] = (t1[1])[8].EasingStyle
	;(t1[1])[8] = (t1[1])[8].Sine
	;(t1[1])[6] = (t1[1])[6]((t1[1])[7], (t1[1])[8])
	;(t1[1])[7] = {}
	;(t1[1])[7].BackgroundColor3 = (t1[1])[2]
	;(t1[1])[3] = (t1[1])[3]((nil --[[ constant not decoded ]])[26](t1[1], 7, 4))
	;(t1[1])[4] = (t1[1])[3]
	;(t1[1])[3] = (t1[1])[3].Play
	;(t1[1])[3]((t1[1])[4])
	error("devirt: symbolic generic for (at 0:4)")
end

-- proto 52: vm sequence 58, 0 opcodes
local function proto_52()
	(t1[1])[1] = upv0
	;(t1[1])[1] = not (t1[1])[1]

	upv0 = (t1[1])[1]
	;(t1[1])[1] = upv0

	if (t1[1])[1] then
		(t1[1])[1] = "Close GUI"
	end

	if not (t1[1])[1] then
		(t1[1])[1] = "Open GUI"
	end

	upv1.Text = (t1[1])[1]

	upv2 = true
	;(t1[1])[1] = upv3
	;(t1[1])[2] = (t1[1])[1]
	;(t1[1])[1] = (t1[1])[1].Toggle
	;(t1[1])[1]((t1[1])[2])
	error("devirt: symbolic generic for (at 0:22)")
end

-- proto 53: vm sequence 59, 0 opcodes
local function proto_53()
	(t1[1])[1] = upv0
	;(t1[1])[2] = true
	;(t1[1])[1]((t1[1])[2])
	error("devirt: symbolic generic for (at 0:5)")
end

-- proto 55: vm sequence 60, 0 opcodes
local function proto_55()
	(t1[1])[1] = upv0
	;(t1[1])[2] = false
	;(t1[1])[1]((t1[1])[2])
	error("devirt: symbolic generic for (at 0:5)")
end

return proto_1(...)
