#@
-- This wrapper allows the program to run headless on any OS (in theory)
-- It can be run using a standard lua interpreter, although LuaJIT is preferable

if not arg[1] then error("Please provide account name") end

local inputFolder = "/tmp/"
local outputFolder = "/tmp/"

local characterName = arg[1]
local json = require('dkjson')

-- Callbacks
local callbackTable = {}
local mainObject
function runCallback(name, ...)
	if callbackTable[name] then
		return callbackTable[name](...)
	elseif mainObject and mainObject[name] then
		return mainObject[name](mainObject, ...)
	end
end

function SetCallback(name, func)
	callbackTable[name] = func
end

function GetCallback(name)
	return callbackTable[name]
end

function SetMainObject(obj)
	mainObject = obj
end

-- Image Handles
local imageHandleClass = {}
imageHandleClass.__index = imageHandleClass
function NewImageHandle()
	return setmetatable({}, imageHandleClass)
end

function imageHandleClass:Load(fileName, ...)
	self.valid = true
end

function imageHandleClass:Unload()
	self.valid = false
end

function imageHandleClass:IsValid()
	return self.valid
end

function imageHandleClass:SetLoadingPriority(pri) end

function imageHandleClass:ImageSize()
	return 1, 1
end

-- Rendering
function RenderInit() end

function GetScreenSize()
	return 1920, 1080
end

function SetClearColor(r, g, b, a) end

function SetDrawLayer(layer, subLayer) end

function SetViewport(x, y, width, height) end

function SetDrawColor(r, g, b, a) end

function DrawImage(imgHandle, left, top, width, height, tcLeft, tcTop, tcRight, tcBottom) end

function DrawImageQuad(imageHandle, x1, y1, x2, y2, x3, y3, x4, y4, s1, t1, s2, t2, s3, t3, s4, t4) end

function DrawString(left, top, align, height, font, text) end

function DrawStringWidth(height, font, text)
	return 1
end

function DrawStringCursorIndex(height, font, text, cursorX, cursorY)
	return 0
end

function StripEscapes(text)
	return text:gsub("%^%d", ""):gsub("%^x%x%x%x%x%x%x", "")
end

function GetAsyncCount()
	return 0
end


_fhandle = {}

setmetatable(_fhandle, {__index = _fhandle;})

function _fhandle:new(tbl)
    return setmetatable({tbl=tbl, cur_idx=1}, getmetatable(self))
end

function _fhandle:NextFile()
    local next_idx = self.cur_idx + 1
    self.cur_idx = next_idx
    return self.tbl[next_idx]
end

function _fhandle:GetFileName()
    local filename, popen = self.tbl[self.cur_idx], io.popen
    if filename then
        local pfile = popen("basename "..filename)
        for line in pfile:lines() do
            return line
        end
    end
    return nil
end

function _fhandle:GetFileModifiedTime()
    local filename, popen = self.tbl[self.cur_idx], io.popen
    if filename then
        local pfile = popen("stat -c '%Y' "..filename)
        for line in pfile:lines() do
            return tonumber(line)
        end
    end
    return 0
end

function executeCommand(command)
    local tmpfile = '/tmp/lua_execute_tmp_file'
    local exit = os.execute(command .. ' > ' .. tmpfile .. ' 2> ' .. tmpfile .. '.err')

    local stdout_file = io.open(tmpfile)
    local stdout = stdout_file:read("*all")

    local stderr_file = io.open(tmpfile .. '.err')
    local stderr = stderr_file:read("*all")

    stdout_file:close()
    stderr_file:close()

    return exit, stdout, stderr
end

-- Search Handles
function NewFileSearch(directory) 
    local i, t, popen = 0, {}, io.popen
    local exit, stdout, stderr = executeCommand("find "..directory)
	
    if exit ~= 0 then
		-- print(stderr)
        return nil
    end

    for filename in stdout:gmatch("[^\r\n]+") do
        i = i + 1
        t[i] = filename
    end
	-- print(stdout)
    return _fhandle:new(t)
end

-- General Functions
function SetWindowTitle(title) end

function GetCursorPos()
	return 0, 0
end

function SetCursorPos(x, y) end

function ShowCursor(doShow) end

function IsKeyDown(keyName) end

function Copy(text) end

function Paste() end

function Deflate(data)
	ConPrintf("DEFLATE: %s", data)
	-- TODO: Might need this
	return ""
end

function Inflate(data)
	ConPrintf("INFLATE: %s", data)
	-- TODO: And this
	return ""
end

function GetTime()
	return 0
end

function GetScriptPath()
	return os.getenv('POB_SCRIPTPATH')
end

function GetRuntimePath()
	return os.getenv('POB_SCRIPTPATH')
end

function GetUserPath()
	return ""
end

function MakeDir(path) end

function RemoveDir(path) end

function SetWorkDir(path) end

function GetWorkDir()
	return ""
end

function LaunchSubScript(scriptText, funcList, subList, ...) end

function AbortSubScript(ssID) end

function IsSubScriptRunning(ssID) end

function LoadModule(fileName, ...)
	if not fileName:match("%.lua") then
		fileName = fileName .. ".lua"
	end
	local func, err = loadfile(fileName)
	if func then
		return func(...)
	else
		error("LoadModule() error loading '" .. fileName .. "': " .. err)
	end
end

function PLoadModule(fileName, ...)
	if not fileName:match("%.lua") then
		fileName = fileName .. ".lua"
	end
	local func, err = loadfile(fileName)
	if func then
		return PCall(func, ...)
	else
		error("PLoadModule() error loading '" .. fileName .. "': " .. err)
	end
end

function PCall(func, ...)
	local ret = { pcall(func, ...) }
	if ret[1] then
		table.remove(ret, 1)
		return nil, unpack(ret)
	else
		return ret[2]
	end
end

function ConPrintf(fmt, ...)
	-- Optional
	print(string.format(fmt, ...))
end

function ConPrintTable(tbl, noRecurse) end

function ConExecute(cmd) end

function ConClear() end

function SpawnProcess(cmdName, args) end

function OpenURL(url) end

function SetProfiling(isEnabled) end

function Restart() end

function Exit() end

local l_require = require
function require(name)
	-- Hack to stop it looking for lcurl, which we don't really need
	if name == "lcurl.safe" then
		return
	end
	return l_require(name)
end

dofile("Launch.lua")

-- Prevents loading of ModCache
-- Allows running mod parsing related tests without pushing ModCache
-- The CI env var will be true when run from github workflows but should be false for other tools using the headless wrapper
mainObject.continuousIntegrationMode = os.getenv("CI")

runCallback("OnInit")
runCallback("OnFrame") -- Need at least one frame for everything to initialise

if mainObject.promptMsg then
	-- Something went wrong during startup
	print(mainObject.promptMsg)
	io.read("*l")
	return
end

-- The build module; once a build is loaded, you can find all the good stuff in here
build = mainObject.main.modes["BUILD"]

-- Here's some helpful helper functions to help you get started
function newBuild()
	mainObject.main:SetMode("BUILD", false, "Help, I'm stuck in Path of Building!")
	runCallback("OnFrame")
end

function loadBuildFromXML(xmlText, name)
	mainObject.main:SetMode("BUILD", false, name or "", xmlText)
	runCallback("OnFrame")
end

function loadBuildFromJSON(getItemsJSON, getPassiveSkillsJSON)
	mainObject.main:SetMode("BUILD", false, "")
	runCallback("OnFrame")
	local charData = build.importTab:ImportItemsAndSkills(getItemsJSON)
	build.importTab:ImportPassiveTreeAndJewels(getPassiveSkillsJSON, charData)
	-- You now have a build without a correct main skill selected, or any configuration options set
	-- Good luck!
end

function run()
	local itemsFile = inputFolder .. characterName .. ".items.json"
	local treeFile =  inputFolder .. characterName .. ".tree.json"

	local f, err = io.open(itemsFile, 'r')
	print(err)
	
	local items = f:read("*a")
	f:close()
	
	local f, err = io.open(treeFile, 'r')
	print(err)
	local tree = f:read("*a")
	f:close()

	loadBuildFromJSON(items, tree)
	runCallback("OnFrame")

	local output = {}
	
	for k, v in pairs(build.calcsTab.mainOutput) do
		if k == "Life" or k == "EnergyShield" or k == "CombinedDPS" then
			output[k] = v
			ConPrintf('%s:%s', k, v)
		end
	end

	local outputStr = json.encode(output)
	
	local f, _ = io.open(outputFolder .. characterName .. '.output.json', 'w+')
	f:write(outputStr)
	f:close()

end

run()
