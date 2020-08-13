#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author:pear
@license: Apache Licence 
@file: xm_notes.py
@time: 2020/8/13 15:32
@contact: 1101588023@qq.com
@software: PyCharm

# code is far away from bugs with the god animal protecting
    I love animals. They taste delicious.
"""

import os
import hashlib
import tkinter as tk
from tkinter import ttk


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.locked = True
        # self.notes = get_notes()
        # self.sig = get_sig(self.notes)
        self.pack(expand='yes', fill='both', padx=10, pady=10)
        self.create_widgets()

    def create_widgets(self):
        self.head_frame = ttk.Frame(self)
        self.btn_lock = ttk.Button(self.head_frame, text='unlock', command=self.lock_switch)
        self.btn_lock.pack(side='top')
        self.head_frame.pack(anchor='center')
        self.edit_frame = ttk.LabelFrame(self, text='Project notes')
        self.text = tk.Text(self.edit_frame)
        # self.text.insert('end', self.notes)
        self.text['state'] = 'disabled'
        self.text.pack(expand='yes', fill='both')
        self.edit_frame.pack(side='top', expand='yes', fill='both')

    def lock_switch(self):
        self.locked = not self.locked
        if not self.locked:
            self.btn_lock['text'] = 'lock'
            self.text['state'] = 'normal'
        else:
            self.btn_lock['text'] = 'unlock'
            self.text['state'] = 'disabled'

    # def check(self):
    #     contents = self.text.get('1.0', 'end')
    #     if self.sig != get_sig(contents):
    #         set_notes(contents)
    #         self.sig = contents


# def get_sig(contents):
#     m = hashlib.md5(contents.encode())
#     return m.digest()
#
#
# def get_notes():
#     _, _, notes, _ = RPR_GetSetProjectNotes(0, False, 'project notes', 1000)
#     return notes
#
#
# def set_notes(string):
#     RPR_GetSetProjectNotes(0, True, string)


root = tk.Tk(baseName=os.getcwd())
root.title('XM_Notes')
screen_x, screen_y = root.maxsize()
root.geometry("{}x{}+{}+{}".format(400, 600, screen_x // 2 - 200, screen_y // 2 - 300))
root.minsize(300, 400)
app = Application(master=root)
app.mainloop()
