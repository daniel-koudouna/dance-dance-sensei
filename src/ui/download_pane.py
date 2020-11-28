import toml
import tkinter as tk
from tkinter import ttk

class DownloadPane(ttk.Frame):
  def __init__(self, master, state, **kw):
    super().__init__(master=master, **kw)

    self.state = state
    self.var_follower = tk.StringVar("")

    r = 0

    l = ttk.Label(self, text="Follower list")
    l.grid(row=r, column=0, padx=10, pady=10, columnspan=2, sticky="news")

    l = ttk.Label(self, text="Log")
    l.grid(row=r, column=2, padx=10, pady=10, columnspan=3, sticky="news")

    r += 1

    lb = tk.Listbox(self, selectmode=tk.SINGLE)
    lb.grid(row=r, column=0, padx=10, pady=10, columnspan=2, sticky="news")
    if 'following' in self.state.config['network']:
      for u in self.state.config['network']['following']:
        lb.insert("end", u)

    self.text = tk.Text(self)
    self.text.grid(row=r, column=2, padx=10, pady=10, columnspan=3, sticky="news")

    r += 1

    e = ttk.Entry(self, textvariable=self.var_follower)
    e.grid(row=r, column=0, padx=10, pady=10, columnspan=2, sticky="news")

    b = ttk.Button(self, text="Download updates", command=self.state.network.download)
    b.grid(row=r, column=2, padx=10, pady=10, columnspan=1, sticky="news")

    r += 1

    b = ttk.Button(self, text="Add", command = lambda lb=lb: self.add_follower(lb))
    b.grid(row=r, column=0, padx=10, pady=10)

    b = ttk.Button(self, text = "Delete", command = lambda lb=lb: self.remove_follower(lb))
    b.grid(row=r, column=1, padx=10, pady=10)


    r += 1


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

  def refresh(self, event):
    if event is not None and event[0] == 'download':
      self.text.insert(tk.END, f"{event[1]}\n")