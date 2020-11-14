import toml
import tkinter as tk
from tkinter import ttk
from game import games
from utils import *

class PreferencesPane(ttk.Frame):
  def __init__(self, master, state, **kw):
    super().__init__(master=master, **kw)

    self.state = state
    self.var_game = tk.StringVar("")

    l = ttk.Label(self, text="Default Game")
    l.grid(row=0, column=0, padx=10, pady=10)


    code = self.state.config['game']['default_game']
    g = first(games, lambda x : x.code == code)

    if g is None:
      g = games[0]

    l = ttk.OptionMenu(self,self.var_game,g.name, *[g.name for g in games])
    l.grid(row=0, column=1, padx=10, pady=10)

    self.var_game.trace('w', self.update_game)

  def update_game(self, *args):
    n = self.var_game.get()
    g = first(games, lambda x : x.name == n)
    if g is not None:
      print(f"Changing game to {g.name}")
      self.state.config['game']['default_game'] = g.code
      toml.dump(self.state.config, open("config.toml", "w"))

  def refresh(self, event):
    pass