import re
import os
import csv
from functools import wraps
import tkinter as tk
from tkinter import ttk, simpledialog, filedialog, messagebox


# =============== INFO ================== #
# Date   : 2020-01-27
# Author : Pear
# Email  : 1101588023@qq.com / cccomposer510@gmail.com
# Bug    :
#     1.Python standard library cannot get Mark/Region name,
# Use "Mark_1, Mark_2" instead of Mark name,
# Also used instead of region name.
#     2.The change of the region name will
# be refreshed when the script is closed.
#     3.Cannot use reaper shortcut when script is enabled.
#     4.I really love Google Translate. :)
# =============== INFO ================== #


# =============== REPAER API ================== #


def log(msg, end='\n'):
    RPR_ShowConsoleMsg(f'{msg}{end}')


def clear_log():
    RPR_ClearConsole()


def get_tracks():
    tracks = []
    count = RPR_CountTracks(0)  # all tracks count
    for idx in range(count):
        tr = RPR_GetTrack(0, idx)
        state = RPR_GetTrackState(tr, 2)
        tracks.append(state)
    return tracks


def get_selected_tracks():
    tracks = []
    tracks = get_tracks()
    for i in tracks:
        if i[-1] == 2:
            selected_tracks.append(i)
    return tracks


def set_track_name(tr, name):
    RPR_Undo_BeginBlock()
    RPR_GetSetMediaTrackInfo_String(tr, 'P_NAME', name, True)
    RPR_Undo_EndBlock(f'Set track name: {name}', 0)


def get_regions():
    regions = []
    (rerval, proj,
     marks_num, regions_num) = RPR_CountProjectMarkers(0, 0, 0)
    name_count = 0 # ...
    for i in range(rerval):  # reval  = all marks count
        (retval, idx, isrgnOut, posOut, rgnendOut, nameOut,
         markrgnindexnumberOut) = RPR_EnumProjectMarkers(i, 0, 0, 0, f'region_{name_count+1}', 0)
        if isrgnOut:
            region_info = (markrgnindexnumberOut, isrgnOut, posOut, rgnendOut)
            regions.append([region_info, nameOut])
            name_count += 1
    return regions


def get_selected_regions():
    pass


def set_region_name(region_info, name):
    RPR_Undo_BeginBlock()
    markrgnindexnumber, isrgn, pos, rgnend = region_info
    RPR_SetProjectMarker(markrgnindexnumber, isrgn, pos, rgnend, name)
    RPR_Undo_EndBlock(f'Set region name: {name}', 0)


def get_marks():
    marks = []
    (rerval, proj,
     marks_num, regions_num) = RPR_CountProjectMarkers(0, 0, 0)
    name_count = 0 # ...
    for i in range(rerval):  # reval  = all marks count
        (retval, idx, isrgnOut, posOut, rgnendOut, nameOut,
         markrgnindexnumberOut) = RPR_EnumProjectMarkers(i, 0, 0, 0, f'mark_{name_count+1}', 0)
        if isrgnOut:
            continue
        mark_info = (markrgnindexnumberOut, isrgnOut, posOut, rgnendOut)
        marks.append([mark_info, nameOut])
        name_count += 1
    return marks


def get_selected_marks():
    pass


def set_marks_name(mark_info, name):
    RPR_Undo_BeginBlock()
    markrgnindexnumber, isrgn, pos, rgnend = mark_info
    RPR_SetProjectMarker(markrgnindexnumber, isrgn, pos, rgnend, name)
    RPR_Undo_EndBlock(f'Set region name: {name}', 0)


def get_media_items():
    items = []
    count = RPR_CountMediaItems(0)
    for idx in range(count):
        item = RPR_GetMediaItem(0, idx)
        take = RPR_GetMediaItemTake(item, 0)
        take_name = RPR_GetTakeName(take)
        items.append([take, take_name])
    return items


def set_take_name(idx, name):
    RPR_Undo_BeginBlock()
    item = RPR_GetMediaItem(0, idx)
    take = RPR_GetMediaItemTake(item, 0)
    RPR_GetSetMediaItemTakeInfo_String(take, 'P_NAME', name, True)
    RPR_Undo_EndBlock(f'Set take name: {name}', 0)


# =============== UI ================== #


class Application(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(expand=True, fill='both', padx=5, pady=5)
        self.diff = False
        self.create_widgets()
        self.refresh()

    def create_widgets(self):
        # Head widgets
        self.head_fram = ttk.Frame(self)
        self.head_fram.pack(pady=5, anchor='nw')

        ttk.Label(self.head_fram, text='Mode: ').pack(side='left', anchor='w')

        self.cbx_var = tk.StringVar()
        self.cbx_mode = ttk.Combobox(self.head_fram)
        self.cbx_mode['textvariable'] = self.cbx_var
        self.cbx_mode['state'] = 'readonly'
        self.cbx_mode['values'] = (
            'Tracks', 'Selected Tracks', 'Regions', 'Selected Regions',
            'Media Items', 'Selected Media Items', 'Marks', 'Selected Marks'
        )
        self.cbx_mode.current(0)
        self.cbx_mode.bind('<<ComboboxSelected>>', self.cbx_selected)
        self.cbx_mode.pack(side='left')

        self.btn_refresh = ttk.Button(self.head_fram)
        self.btn_refresh['text'] = 'Refresh'
        self.btn_refresh['command'] = self.refresh
        self.btn_refresh.pack(side='left')

        self.btn_insert_name = ttk.Button(self.head_fram)
        self.btn_insert_name['text'] = 'Insert Name'
        self.btn_insert_name['command'] = self.insert_name
        self.btn_insert_name.pack(side='left')

        self.btn_rename = ttk.Button(self.head_fram)
        self.btn_rename['text'] = 'Rename'
        self.btn_rename['command'] = self.rename
        self.btn_rename.pack(side='left')

        self.btn_export = ttk.Button(self.head_fram)
        self.btn_export['text'] = 'Export'
        self.btn_export['command'] = self.export
        self.btn_export.pack(side='left')

        self.btn_import = ttk.Button(self.head_fram)
        self.btn_import['text'] = 'Import'
        self.btn_import['command'] = self.import_
        self.btn_import.pack(side='left')

        # Tree view
        self.tree = ttk.Treeview(self)
        self.tree['columns'] = ('ID', 'NAME', 'NEW_NAME')
        self.tree['selectmode'] = 'browse'
        self.tree['show'] = 'headings'
        self.tree.column('ID', width=20)
        self.tree.heading('ID', text='ID')
        self.tree.heading('NAME', text='NAME')
        self.tree.heading('NEW_NAME', text='NEW NAME')
        self.tree.pack(expand=True, fill='both')

    def is_empty(self):
        items = self.tree.get_children()
        if not items:
            return True
        else:
            return False

    def clear_tree(self):
        items = self.tree.get_children()
        for i in items:
            self.tree.delete(i)

    def cbx_selected(self, event):
        self.refresh()

    def refresh(self):
        print('Refresh!')
        self.clear_tree()

        if self.cbx_var.get() == 'Tracks':
            self.refresh_tracks()
        elif self.cbx_var.get() == 'Regions':
            self.refresh_regions()
        elif self.cbx_var.get() == 'Media Items':
            self.refresh_media_items()
        elif self.cbx_var.get() == 'Marks':
            self.refresh_marks()

        self.diff = False

    def refresh_tracks(self):
        self.tracks = get_tracks()
        for index, tr in enumerate(self.tracks):
            self.tree.insert('', 'end',  value=(index, tr[0]))

    def refresh_regions(self):
        self.regions = get_regions()
        for index, region in enumerate(self.regions):
            self.tree.insert('', 'end', value=(index, region[1]))

    def refresh_media_items(self):
        self.media_items = get_media_items()
        for index, item in enumerate(self.media_items):
            self.tree.insert('', 'end',  value=(index, item[1]))

    def refresh_marks(self):
        self.marks = get_marks()
        for index, mark in enumerate(self.marks):
            self.tree.insert('', 'end', value=(index, mark[1]))

    def insert_name(self):
        print('Insert Name!')
        text = simpledialog.askstring('Input', 'input something...')
        if not text or not str(text).strip():
            return
        lis = str(text).strip().split('\n')
        self.insert_name_list(lis)

    def insert_name_list(self, lis):
        self.refresh()
        for index, i in enumerate(self.tree.get_children()):
            v = self.tree.item(i).get('values')
            if index == len(lis):
                break
            v.append(lis[index])
            self.tree.item(i, value=v)
        self.diff = True

    def rename(self):
        print('Rename!')
        if not self.diff:
            return

        if self.cbx_var.get() == 'Tracks':
            self.rename_tracks()
        elif self.cbx_var.get() == 'Regions':
            self.rename_regions()
        elif self.cbx_var.get() == 'Media Items':
            self.rename_media_items()
        elif self.cbx_var.get() == 'Marks':
            self.rename_marks()

        self.refresh()

    def rename_tracks(self):
        for i in self.tree.get_children():
            v = self.tree.item(i).get('values')
            if len(v) == 3 and str(v[2]).strip():
                idx = v[0]
                new_name = v[2]
                tr = self.tracks[idx][1]
                set_track_name(tr, new_name)

    def rename_regions(self):
        for i in self.tree.get_children():
            v = self.tree.item(i).get('values')
            if len(v) == 3 and str(v[2]).strip():
                idx = v[0]
                idx = self.regions[idx][0]
                new_name = v[2]
                set_region_name(idx, new_name)

    def rename_media_items(self):
        for i in self.tree.get_children():
            v = self.tree.item(i).get('values')
            if len(v) == 3 and str(v[2]).strip():
                idx = v[0]
                new_name = v[2]
                set_take_name(idx, new_name)

    def rename_marks(self):
        for i in self.tree.get_children():
            v = self.tree.item(i).get('values')
            if len(v) == 3 and str(v[2]).strip():
                idx = v[0]
                idx = self.marks[idx][0]
                new_name = v[2]
                set_marks_name(idx, new_name)

    def export(self):
        print('Export!')
        if self.is_empty():
            print('Nothing to export.')
            messagebox.showinfo('Info', 'Nothing to export.')
            return

        file_name = filedialog.asksaveasfilename(
            title='Export csv',
            filetypes=[('CSV', '*.csv'), ('All Files', '*.*')]
        )
        if file_name:
            try:
                headers = self.tree['columns']
                rows = []
                for i in self.tree.get_children():
                    item_data = {}
                    values = self.tree.item(i).get('values')
                    item_data[headers[0]] = values[0]
                    item_data[headers[1]] = values[1]
                    if len(values) == 3 and str(values[2]).strip():
                        item_data[headers[2]] = values[2]
                    rows.append(item_data)
                with open(file_name, 'w', newline='')as f:
                    f_csv = csv.DictWriter(f, headers)
                    f_csv.writeheader()
                    f_csv.writerows(rows)
            except Exception as e:
                messagebox.showerror('Error', e)
            finally:
                pass
        else:
            pass

    def import_(self):
        print('Import!')
        file_name = filedialog.askopenfilename(
            title='Import csv',
            filetypes=[('CSV', '*.csv'), ('All Files', '*.*')]
        )
        if file_name:
            try:
                with open(file_name)as f:
                    f_csv = csv.DictReader(f)
                    lis = []
                    for row in f_csv:
                        lis.append(row['NEW_NAME'])
                    self.insert_name_list(lis)
            except Exception as e:
                messagebox.showerror('Error', e)
            finally:
                pass
        else:
            pass


if __name__ == "__main__":
    root = tk.Tk(baseName=os.getcwd())
    root.title('RenamePlus')
    center_x = int(root.winfo_screenwidth()/2)
    center_y = int(root.winfo_screenheight()/2)
    root.geometry(f'+{center_x-200}+{center_y-200}')
    # root.resizable(0, 0)
    root.wm_attributes('-topmost', 1)
    app = Application(master=root)
    app.mainloop()
