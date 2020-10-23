import re
import os
from glob import glob
import tkinter as tk
from tkinter import ttk


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()
        center_x = int(self.master.winfo_screenwidth()/2)
        center_y = int(self.master.winfo_screenheight()/2)
        self.master.geometry('+{}+{}'.format(center_x-200, center_y-200))
        self.master.resizable(0, 0)
        self.master.wm_attributes('-topmost',1)

    def create_widgets(self):
        self.edit_frame = ttk.LabelFrame(self, text='Text editor')
        self.edit_frame.pack(ipadx=10, ipady=10)
        self.edit = tk.Text(self.edit_frame, width=50)
        self.edit.pack()

        self.btn_frame = ttk.Frame(self)
        self.btn_frame.pack(ipadx=10, ipady=10)
        self.clear_btn = ttk.Button(self.btn_frame, text='Clear')
        self.clear_btn.pack(side='left')
        self.insert_tracks_btn = ttk.Button(
            self.btn_frame, text='Insert tracks')
        self.insert_tracks_btn.pack(side='left')
        self.insert_regions_btn = ttk.Button(
            self.btn_frame, text='Insert regions')
        self.insert_regions_btn.pack(side='left')

        self.insert_tracks_btn.bind('<Button-1>', self.insert_tracks)
        self.clear_btn.bind('<Button-1>', self.clear)

    def parse_list(self):
        ctx = self.edit.get(1.0, 'end').strip()
        if ctx:
            data = ctx.split('\n')
            return data
        else:
            return []

    def insert_tracks(self, event):
        RPR_Undo_BeginBlock()
        data = self.parse_list()
        for name in data:
            idx = RPR_GetNumTracks()
            RPR_InsertTrackAtIndex(idx, False)
            tr = RPR_GetTrack(0, idx)
            RPR_GetSetMediaTrackInfo_String(tr, 'P_NAME', name, True)
        RPR_Undo_EndBlock('Insert tracks', 0)

    def insert_regions(self, event):
        data = self.parse_list()
        for name in data:
            pass

    def clear(self, event):
        self.edit.delete(0.1, 'end')


if __name__ == "__main__":
    root = tk.Tk(baseName=os.getcwd())
    root.title('Insert_from_list')
    app = Application(master=root)
    app.mainloop()
