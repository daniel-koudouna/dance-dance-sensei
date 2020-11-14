import os
import tkinter as tk
from tkinter import ttk

import ttkwidgets

class UploadPane(ttk.Frame):
  def __init__(self, master, state, **kw) -> None:
    super().__init__(master=master, **kw)
    self.state = state

    r = 0

    ## Upload button
    b = ttk.Label(self, text="Your sequences")
    b.grid(row=r,column=0,padx=10,pady=10, columnspan=3, sticky="news")

    b = ttk.Label(self, text="Log")
    b.grid(row=r,column=3,padx=10,pady=10, columnspan=3, sticky="news")

    r += 1

    ## Upload menu
    self.tree = ttkwidgets.CheckboxTreeview(self)
    self.tree.grid(row=r,column=0,padx=10, pady=10, columnspan=3, sticky="news")

    rootpath = f"{self.state.mode.sequences}/personal"
    for dirpath, dirnames, files in os.walk(rootpath):
      parent = "" if dirpath == rootpath else dirpath[dirpath.index(rootpath):].replace("\\","/")
      for d in dirnames:
        self.tree.insert(parent, "end", f"{dirpath}/{d}", text=d)
      for f in files:
        iid = self.tree.insert(parent, "end", f"{dirpath}/{f}", text=f)
        if not f.replace(".txt","").replace("_","").isdigit():
          self.tree.change_state(iid, 'checked')

    self.text = tk.Text(self)
    self.text.grid(row=r, column=3, padx=10, pady=10, columnspan=3, sticky="news")

    r += 1

    b = ttk.Button(self, text="Upload changes", command=self.upload)
    b.grid(row=r, column=3, padx=10, pady=10, columnspan=1, sticky="news")

  def upload(self):
    l = self.tree.get_checked()
    print(l)
    if len(l) == 0:
      self.text.insert(tk.END, "No sequences selected for upload.\n")
    else:
      self.state.network.upload(l)

  def refresh(self, event):
    if event is not None and event[0] == 'upload':
      self.text.insert(tk.END, f"{event[1]}\n")