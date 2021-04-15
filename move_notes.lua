local Element = {}
function Element:new(x, y, w, h, r, g, b, a, lbl, fnt, fnt_sz, norm_val)
    local elm = {}
    elm.def_xywh = {x, y, w, h, fnt_sz} -- its default coord,used for Zoom etc
    elm.x, elm.y, elm.w, elm.h = x, y, w, h
    elm.r, elm.g, elm.b, elm.a = r, g, b, a
    elm.lbl, elm.fnt, elm.fnt_sz = lbl, fnt, fnt_sz
    elm.norm_val = norm_val
    ------
    setmetatable(elm, self)
    self.__index = self
    return elm
end
--------------------------------------------------------------
--- Function for Child Classes(args = Child,Parent Class) ----
--------------------------------------------------------------
function extended(Child, Parent) setmetatable(Child, {__index = Parent}) end
--------------------------------------------------------------
---   Element Class Methods(Main Methods)   ------------------
--------------------------------------------------------------
function Element:update_xywh()
    if not Z_w or not Z_h then return end -- return if zoom not defined
    if Z_w > 0.5 and Z_w < 3 then
        self.x, self.w = math.ceil(self.def_xywh[1] * Z_w),
                         math.ceil(self.def_xywh[3] * Z_w) -- upd x,w
    end
    if Z_h > 0.5 and Z_h < 3 then
        self.y, self.h = math.ceil(self.def_xywh[2] * Z_h),
                         math.ceil(self.def_xywh[4] * Z_h) -- upd y,h
    end
    if Z_w > 0.5 or Z_h > 0.5 then -- fix it!--
        self.fnt_sz = math.max(9, self.def_xywh[5] * (Z_w + Z_h) / 2)
        self.fnt_sz = math.min(22, self.fnt_sz)
    end
end
--------
function Element:pointIN(p_x, p_y)
    return p_x >= self.x and p_x <= self.x + self.w and p_y >= self.y and p_y <=
               self.y + self.h
end
--------
function Element:mouseIN()
    return gfx.mouse_cap & 1 == 0 and self:pointIN(gfx.mouse_x, gfx.mouse_y)
end
--------
function Element:mouseDown()
    return gfx.mouse_cap & 1 == 1 and self:pointIN(mouse_ox, mouse_oy)
end
--------
function Element:mouseClick()
    return gfx.mouse_cap & 1 == 0 and last_mouse_cap & 1 == 1 and
               self:pointIN(gfx.mouse_x, gfx.mouse_y) and
               self:pointIN(mouse_ox, mouse_oy)
end
--------
function Element:draw_frame()
    local x, y, w, h = self.x, self.y, self.w, self.h
    gfx.rect(x, y, w, h, 0) -- frame1
    gfx.roundrect(x, y, w - 1, h - 1, 3, true) -- frame2
end
--------------------------------------------------------------------------------
---   Create Element Child Classes(Button,Slider,Knob)   -----------------------
--------------------------------------------------------------------------------
local Button = {};
local Knob = {};
local Slider = {};
extended(Button, Element)
extended(Knob, Element)
extended(Slider, Element)
---Create Slider Child Classes(V_Slider,H_Slider)----
local H_Slider = {};
local V_Slider = {};
extended(H_Slider, Slider)
extended(V_Slider, Slider)

--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
---   Button Class Methods   ---------------------------------------------------
--------------------------------------------------------------------------------
function Button:draw_lbl()
    local x, y, w, h = self.x, self.y, self.w, self.h
    local fnt, fnt_sz = self.fnt, self.fnt_sz
    -- Draw btn lbl(text)--
    gfx.set(0.7, 1, 0, 1) -- set label color
    gfx.setfont(1, fnt, fnt_sz); -- set label fnt
    local lbl_w, lbl_h = gfx.measurestr(self.lbl)
    gfx.x = x + (w - lbl_w) / 2;
    gfx.y = y + (h - lbl_h) / 2
    gfx.drawstr(self.lbl)
end
---------------------
function Button:draw()
    self:update_xywh() -- Update xywh(if wind changed)
    local x, y, w, h = self.x, self.y, self.w, self.h
    local r, g, b, a = self.r, self.g, self.b, self.a
    ---Get L_mouse state--
    -- in element--
    if self:mouseIN() then a = a + 0.1 end
    -- in elm L_down--
    if self:mouseDown() then a = a + 0.2 end
    -- in elm L_up(released and was previously pressed)--
    if self:mouseClick() then self.onClick() end
    -- Draw btn(body,frame)--
    gfx.set(r, g, b, a) -- set btn color
    gfx.rect(x, y, w, h, true) -- body
    self:draw_frame()
    ------------------------
    self:draw_lbl()
end

function Log(msg) reaper.ShowConsoleMsg(tostring(msg) .. '\n') end
function Clear() reaper.ClearConsole() end

function MovePPQPos(take, ppqpos, num)
    num = num / 1000
    time = reaper.MIDI_GetProjTimeFromPPQPos(take, ppqpos)
    new_time = time + num
    new_ppqpos = reaper.MIDI_GetPPQPosFromProjTime(take, new_time)
    return new_ppqpos
end

function MoveSelNotes(num)
    hw = reaper.MIDIEditor_GetActive()
    tk = reaper.MIDIEditor_GetTake(hw)
    _, notecnt, _, _ = reaper.MIDI_CountEvts(tk)
    for i = 0, notecnt - 1 do
        retval, selected, muted, startppqpos, endppqpos, chan, pitch, vel =
            reaper.MIDI_GetNote(tk, i)
        if selected == true then
            new_start = MovePPQPos(tk, startppqpos, num)
            new_end = MovePPQPos(tk, endppqpos, num)
            reaper.MIDI_SetNote(tk, i, selected, muted, new_start, new_end,
                                chan, pitch, vel, 1)
        end
    end
end

----------------------------------------------------------------------------------------------------
---   START   --------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------
local btn1 = Button:new(10, 10, 70, 70, 0.2, 0.2, 1, 0.5, "-50ms", "Arial", 15,
                        -50) -- title 是按钮显示的文字，最后一个参数是移动的值，单位毫秒
local btn2 = Button:new(90, 10, 70, 70, 0.2, 0.2, 1, 0.5, "50ms", "Arial", 15,
                        50)
local btn3 = Button:new(170, 10, 70, 70, 0.2, 0.2, 1, 0.5, "title", "Arial", 15,
                        0)
local btn4 = Button:new(10, 90, 70, 70, 0.2, 0.2, 1, 0.5, "title", "Arial", 15,
                        0)
local btn5 = Button:new(90, 90, 70, 70, 0.2, 0.2, 1, 0.5, "title", "Arial", 15,
                        0)
local btn6 = Button:new(170, 90, 70, 70, 0.2, 0.2, 1, 0.5, "title", "Arial", 15,
                        0)
local btn7 = Button:new(10, 170, 70, 70, 0.2, 0.2, 1, 0.5, "title", "Arial", 15,
                        0)
local btn8 = Button:new(90, 170, 70, 70, 0.2, 0.2, 1, 0.5, "title", "Arial", 15,
                        0)
local btn9 = Button:new(170, 170, 70, 70, 0.2, 0.2, 1, 0.5, "title", "Arial",
                        15, 0)

local Button_TB = {btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9}

-- Add "on click function" for each button
for i = 1, #Button_TB do
    local curr_btn = Button_TB[i]
    curr_btn.onClick = function()
        local step = curr_btn.norm_val
        if step ~= 0 then MoveSelNotes(step) end
    end
    curr_btn.onClickKey = function()
        --
    end
end

----------------------------------------------------------------------------------------------------
---   Main DRAW function   -------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------
function DRAW() for key, btn in pairs(Button_TB) do btn:draw() end end

--------------------------------------------------------------------------------
--   INIT   --------------------------------------------------------------------
--------------------------------------------------------------------------------
function Init()
    -- Some gfx Wnd Default Values--------------
    local R, G, B = 20, 20, 20 -- 0..255 form
    Wnd_bgd = R + G * 256 + B * 65536 -- red+green*256+blue*65536
    Wnd_Title, Wnd_W, Wnd_H, Wnd_Dock, Wnd_X, Wnd_Y = "Move Selected Notes",
                                                      250, 250, 0, 100, 320
    -- Init window------------------------------
    gfx.clear = Wnd_bgd
    gfx.init(Wnd_Title, Wnd_W, Wnd_H, Wnd_Dock, Wnd_X, Wnd_Y)
    -- Mouse--------------
    last_mouse_cap = 0
    last_x, last_y = 0, 0
end
----------------------------------------
--   Mainloop   ------------------------
----------------------------------------
function mainloop()
    Z_w, Z_h = gfx.w / Wnd_W, gfx.h / Wnd_H
    if gfx.mouse_cap & 1 == 1 and last_mouse_cap & 1 == 0 then
        mouse_ox, mouse_oy = gfx.mouse_x, gfx.mouse_y
    end
    Ctrl = gfx.mouse_cap & 4 == 4
    Shift = gfx.mouse_cap & 8 == 8
    -----------------------
    -- DRAW,MAIN functions--
    DRAW() -- Main()
    -----------------------
    -----------------------
    last_mouse_cap = gfx.mouse_cap
    last_x, last_y = gfx.mouse_x, gfx.mouse_y

    hotkey = gfx.getchar()
    if hotkey == 27 then -- ESC
        gfx.quit()
    end

    if hotkey ~= -1 then reaper.defer(mainloop) end -- defer
    -----------
    gfx.update()
    -----------
end

function exitnow()
    --
end
reaper.atexit(exitnow)
Init()
mainloop()

-- step = -500 -- 移动500毫秒
-- MoveSelNotes(step)
