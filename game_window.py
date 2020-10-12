import os
import pygame
import tkinter as tk

def to_label(filename):
  s = filename.split(".")[0]
  return s.replace("_"," ").replace("_", " ")


class GameWindow(tk.Tk):
  def __init__(self, state, *args, **kwargs):
    tk.Tk.__init__(self, *args, **kwargs)
    self.state = state
    self.state.window = self
    self.x = None
    self.y = None
    self.overrideredirect(True)
    self.geometry("360x800")  # Whatever size
    self.attributes('-topmost', 1)
    self.wm_attributes('-alpha',0.7)
    self['bg'] = '#000'

    self.reload_context_menu()

    os.environ['SDL_WINDOWID'] = str(self.winfo_id())
    os.environ['SDL_VIDEODRIVER'] = 'windib'

  def reload_context_menu(self):
    self.popup_menu = tk.Menu(self, tearoff=0)
    self.popup_menu.add_command(label="Reload",
                                command=lambda : self.state.reload_last_sequence())
    submenu = tk.Menu(self, tearoff=0)
    seqs = os.listdir(f"sequence/{self.state.mode}")
    for s in seqs:
      submenu.add_command(label=to_label(s),
                          command=lambda s=s: self.state.reload_sequence(s))
    self.popup_menu.add_cascade(label="Sequences", menu=submenu)

    self.popup_menu.add_command(label="Quit",
                                command=self.stop)

  def stop(self):
    self.state.is_running = False

  def handle_event(self, event):
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
      self.start_move(event)
    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
      self.stop_move(event)
    if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
      self.show_popup(event)
    if event.type == pygame.MOUSEMOTION:
      self.do_move(event)

  def show_popup(self, event):
    try:
      x = self.winfo_x() + event.pos[0]
      y = self.winfo_y() + event.pos[1]
      self.popup_menu.tk_popup(x, y, 0)
    finally:
      self.popup_menu.grab_release()

  def start_move(self, event):
    self.x = event.pos[0]
    self.y = event.pos[1]

  def stop_move(self, event):
    self.x = None
    self.y = None

  def do_move(self, event):
    if self.x != None and self.y != None:
      deltax = event.pos[0] - self.x
      deltay = event.pos[1] - self.y
      x = self.winfo_x() + deltax
      y = self.winfo_y() + deltay
      self.geometry(f"+{x}+{y}")
