import toml
import tkinter as tk
from tkinter import ttk

class NetworkPane(ttk.Frame):
  def __init__(self, master, state, **kw) -> None:
    super().__init__(master=master, **kw)
    self.state = state

    ## Account management
    self.var_username = tk.StringVar()
    self.var_password = tk.StringVar()
    self.re_init()


  def re_init(self):
    if self.state.network.user is not None:
      l = ttk.Label(self, text=f"Welcome back, {self.state.network.user['username']}")
      l.grid(row=0, column = 0, padx=10, pady=10, columnspan=2)
    else:
      l = ttk.Label(self, text="Username :")
      l.grid(row=0,column=0,padx=10,pady=10)
      l = ttk.Entry(self, textvariable=self.var_username)
      l.grid(row=0,column=1,padx=10,pady=10)
      l = ttk.Label(self, text="Password :")
      l.grid(row=1,column=0,padx=10,pady=10)
      l = ttk.Entry(self, show="*", textvariable=self.var_password)
      l.grid(row=1,column=1,padx=10,pady=10)
      l = ttk.Button(self, text="Login", command=self.login)
      l.grid(row=2,column=0,padx=10,pady=10)
      l = ttk.Button(self, text="Register", command=self.register)
      l.grid(row=2,column=1,padx=10,pady=10)


    ## Application update
    l = ttk.Button(self, text="Check for updates", command=self.try_update)
    l.grid(row=0, column=2, padx=10, pady=10)

  def user_callback(self, res):
    if res is not None:
      print(res)
      self.state.network.user = res['user']
      self.state.config['network']['token'] = res['user']['token']
      toml.dump(self.state.config, open("config.toml", "w"))

      for child in self.winfo_children():
        child.destroy()
      self.re_init()

  def register(self):
    u = self.var_username.get()
    p = self.var_password.get()
    self.state.network.register(u, p, self.user_callback)

  def login(self):
    u = self.var_username.get()
    p = self.var_password.get()
    self.state.network.login(u, p, self.user_callback)

  def try_update(self):
    pass

  def refresh(self, event):
    pass