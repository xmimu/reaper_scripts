function RegionsFromItems()
    local num = reaper.CountSelectedMediaItems(0)
    if num == 0 then return end
    for i = 0, num - 1 do
        local item = reaper.GetSelectedMediaItem(0, i)
        local take = reaper.GetActiveTake(item)
        if take then
            local name = reaper.GetTakeName(take)
            local r = string.match(name, "(.+)%.%w+$")
            if r then name = r end
            local start_p = reaper.GetMediaItemInfo_Value(item, "D_POSITION")
            local end_p = reaper.GetMediaItemInfo_Value(item, "D_LENGTH") + start_p
            reaper.AddProjectMarker(0, true, start_p, end_p, name, -1)
        end
    end
end

RegionsFromItems()
