import tkinter as tk
from tkinter import ttk

DEFAULT_TEXT="Add"
WAITING_TEXT="..."

def mapping_string(tup):
  _key, btntype, val, device = tup
  return f"{btntype} {val}"

class ControllerPane(ttk.Frame):
  def __init__(self, master, state, **kw):
    super().__init__(master=master, **kw)

    self.state = state
    self.var_inputs = {}
    self.var_btntext = {}

    idx = 0
    self.recalc_mappings()
    for btn in self.state.mode.buttons:
      l = ttk.Label(self, text=f"{btn}")
      l.grid(row=idx, column=0, padx=10, pady=10)

      l = ttk.Button(self, 
                     textvariable=self.var_btntext[btn],
                     command=lambda btn=btn: self.new_btn(btn))
      l.grid(row=idx, column=1, padx=10, pady=10)

      l = ttk.Entry(self, 
                    state="readonly", 
                    width=60,
                    textvariable=self.var_inputs[btn])
      l.grid(row=idx, column=2, padx=10, pady=10)

      l = ttk.Button(self, 
                     text="Clear",
                     command= lambda btn=btn: self.clear_btn(btn))
      l.grid(row=idx, column=3, padx=10, pady=10)

      idx += 1

  def new_btn(self, btn):
    self.var_btntext[btn].set(WAITING_TEXT)
    self.state.register_new_button(btn)

  def clear_btn(self, btn):
    self.state.clear_button(btn)
    self.recalc_mappings()

  def recalc_mappings(self):
    for btn in self.state.mode.buttons:
      rep_list = [f for f in self.state.mappings if f[0] == btn]
      rep = [mapping_string(h) for h in rep_list]
      rep = ",".join(rep)
      if btn in self.var_inputs:
        self.var_inputs[btn].set(rep)
      else:
        self.var_inputs[btn] = tk.StringVar(self, rep)

      if btn not in self.var_btntext:
        self.var_btntext[btn] = tk.StringVar(self, DEFAULT_TEXT)
      self.var_btntext[btn].set(DEFAULT_TEXT)


  def refresh(self, event):
    self.recalc_mappings()