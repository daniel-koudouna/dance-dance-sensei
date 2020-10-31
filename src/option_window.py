import os
from pyupdater.client import Client
import requests 
import tkinter as tk
from tkinter import ttk
from ttkwidgets import CheckboxTreeview
import toml

from game import games

class OptionWindow(ttk.Notebook):

  def login(self):
    u = self.var_username.get()
    p = self.var_password.get()
    success = self.state.network.login(u, p)
    if success:
      self.destroy()

  def print_status_info(info):
    total = info.get(u'total')
    downloaded = info.get(u'downloaded')
    status = info.get(u'status')
    print(downloaded, total, status)

  def __init__(self, parent, state):
    super().__init__(parent)
    self.state = state
    self.mode = state.mode

    tab1 = ttk.Frame(self)
    downloadTab = ttk.Frame(self)
    uploadTab = ttk.Frame(self)
    accountTab = ttk.Frame(self)
    updateTab = ttk.Frame(self)

    self.add(tab1, text="Preferences")
    self.add(accountTab, text="Account")
    self.add(uploadTab, text="Upload")
    self.add(downloadTab, text="Download")
    self.add(updateTab, text="Update")
    self.pack(expand = 1, fill ="both") 

    ## Account management
    self.var_username = tk.StringVar()
    self.var_password = tk.StringVar()

    if self.state.network.user is not None:
      ttk.Label(accountTab, text=f"Welcome back, {self.state.network.user['username']}").grid(row=0, column = 0, padx=10, pady=10)
    else:
      ttk.Label(accountTab, text="Username :").grid(row=0,column=0,padx=10,pady=10)
      ttk.Entry(accountTab, textvariable=self.var_username).grid(row=0,column=1,padx=10,pady=10)
      ttk.Label(accountTab, text="Password :").grid(row=1,column=0,padx=10,pady=10)
      ttk.Entry(accountTab, show="*", textvariable=self.var_password).grid(row=1,column=1,padx=10,pady=10)
      ttk.Button(accountTab, text="Login/Register", command=self.login).grid(row=2,column=0,padx=10,pady=10)

    gamechoices = [m.name for m in games]

    self.var_game = tk.StringVar()

    ttk.Combobox(uploadTab, textvariable=self.var_game, state='readonly',
    values=gamechoices).grid(row=0, column=1, padx=10, pady=10)
    ttk.Label(uploadTab, text="Game: ").grid(row=0, column=0, padx=10, pady=10)


    ## Upload button
    ttk.Button(uploadTab, text="Sync", command=self.state.network.upload).grid(row=2,column=0,padx=10,pady=10)

    ## Upload menu
    t = CheckboxTreeview(uploadTab)
    t.grid(row=1,column=0,padx=10, pady=10, columnspan=3)

    print(self.state.mode.code)

    rootpath = f"{self.state.mode.sequences}/personal"


    for dirpath, dirnames, files in os.walk(rootpath):
      parent = "" if dirpath == rootpath else dirpath[dirpath.index(rootpath):].replace("\\","/")
      for d in dirnames:
        t.insert(parent, "end", f"{dirpath}/{d}", text=d)
      for f in files:
        t.insert(parent, "end", f"{dirpath}/{f}", text=f)

    ts = CheckboxTreeview(uploadTab)
    ts.grid(row=1,column=4,padx=10, pady=10, columnspan=3)

    ## Download menu
    ttk.Combobox(downloadTab, textvariable=self.var_game, state='readonly',
    values=gamechoices).grid(row=0, column=1, padx=10, pady=10)
    ttk.Label(downloadTab, text="Game: ").grid(row=0, column=0, padx=10, pady=10)

    lb = tk.Listbox(downloadTab, selectmode=tk.SINGLE)
    lb.grid(row=1, column=0, padx=10, pady=10)
    for u in self.state.config['network']['following']:
      lb.insert("end", u)

    b = ttk.Button(downloadTab, text = "Delete", command = lambda lb=lb: self.remove_follower(lb))
    b.grid(row=2, column=0, padx=10, pady=10)

    self.var_follower = tk.StringVar("")
    e = ttk.Entry(downloadTab, textvariable=self.var_follower)
    e.grid(row=1, column=1, padx=10, pady=10)

    b = ttk.Button(downloadTab, text="Add", command = lambda : self.add_follower(lb))
    b.grid(row=2, column=1, padx=10, pady=10)

    b = ttk.Button(downloadTab, text="Sync", command=self.state.network.download)
    b.grid(row=2, column=2, padx=10, pady=10)

    ## Application update
    b = ttk.Button(updateTab, text="Check for updates", command=self.try_update)
    b.grid(row=0, column=0, padx=10, pady=10)
 
  def try_update(self):
    pass


 
  def add_follower(self, lb):
    follower = self.var_follower.get()
    if follower == "":
      return
    lb.insert("end", follower)
    if 'following' not in self.state.config['network']:
      self.state.config['network']['following'] = []
    self.state.config['network']['following'].append(follower)
    toml.dump(self.state.config, open("config.toml", "w"))
    self.var_follower.set("")

  def remove_follower(self, lb):
    follower = lb.get(tk.ANCHOR)
    lb.delete(tk.ANCHOR)
    self.state.config['network']['following'].remove(follower)
    toml.dump(self.state.config, open("config.toml", "w"))


  def refresh(self):
    self.var_game.set(self.state.mode.name)