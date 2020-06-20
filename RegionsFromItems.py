import re


def RegionsFromItems():
    num = RPR_CountSelectedMediaItems(0)
    if num == 0:
        return
    for i in range(num):
        item = RPR_GetSelectedMediaItem(0, i)
        take = RPR_GetActiveTake(item)
        if take:
            name = RPR_GetTakeName(take)
            if '.' in name:
                name = re.sub(r'\.[0-9a-zA-z]{0,5}$', '', name)
            start = RPR_GetMediaItemInfo_Value(item, "D_POSITION")
            end = RPR_GetMediaItemInfo_Value(item, "D_LENGTH") + start
            RPR_AddProjectMarker(0, True, start, end, name, -1)


RegionsFromItems()
