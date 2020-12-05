import os
import pygame
import threading
import tkinter as tk
import tkinter.messagebox as mb
from game import games
from option_window import OptionWindow
import webbrowser


def to_label(filename):
  s = filename.split(".")[0]
  return s.replace("_"," ").replace("_", " ")


class GameWindow(tk.Tk):
  def __init__(self, state, *args, **kwargs):
    tk.Tk.__init__(self, *args, **kwargs)
    self.state = state
    self.state.window = self
    self.options = None
    self.x = None
    self.y = None
    self.options_window : OptionWindow = None
    self.overrideredirect(True)

    config = state.config
    width = state.config['display']['width']
    height = state.config['display']['height']

    self.geometry(f"{width}x{height}+100+100")  # Whatever size
    self.attributes('-topmost', 1)
    self.wm_attributes('-alpha',0.7)
    self['bg'] = '#000'

    self.reload_context_menu()

    os.environ['SDL_WINDOWID'] = str(self.winfo_id())
    os.environ['SDL_VIDEODRIVER'] = 'windib'

  def recursive_menu(self, folder, root):
    submenu = tk.Menu(self, tearoff=0)
    subdir = root if folder == "" else f"{root}/{folder}"
    for seq in os.listdir(subdir):
      subseq = seq if folder == "" else f"{folder}/{seq}"
      abspath = f"{subdir}/{seq}"
      if os.path.isfile(abspath):
        submenu.add_command(label=to_label(seq),
          command=lambda subseq=subseq: self.state.reload_sequence(subseq))
      elif os.path.isdir(abspath):
        subsubmenu = self.recursive_menu(subseq, root)
        submenu.add_cascade(label=to_label(seq), menu=subsubmenu)

    return submenu

  def reload_context_menu(self):
    self.popup_menu = tk.Menu(self, tearoff=0)

    ## Add menu to change mode
    modemenu = tk.Menu(self, tearoff=0)
    for m in games:
      modemenu.add_command(label=m.name,
                           command=lambda m=m: self.state.reload_mode(m))
    self.popup_menu.add_cascade(label=f"Current mode: {self.state.mode.name}", menu=modemenu)

    self.popup_menu.add_command(label="Reload",
                                command=lambda : self.state.reload_last_sequence())

    ## Add menu to change sequence
    submenu = self.recursive_menu("", self.state.mode.sequences)
    self.popup_menu.add_cascade(label="Sequences", menu=submenu)

    self.popup_menu.add_command(label="Options", command=self.show_options)

    self.var_metronome = tk.BooleanVar()
    self.var_metronome.trace('w', self.toggle_metronome)
    self.popup_menu.add_checkbutton(label="Metronome", onvalue=True, offvalue=False, variable=self.var_metronome)

    self.popup_menu.add_command(label="Quit",
                                command=self.stop)

  def toggle_metronome(self, *args):
    self.state.use_metronome = self.var_metronome.get()

  def show_options(self):
    self.options = tk.Toplevel(self)
    self.options.title("Dance Dance Sensei - Options")
    self.options.geometry("+500+100")
    self.options.iconbitmap('logo.ico')
    self.options_window = OptionWindow(self.options, self.state)
    self.refresh((None, None))

  def refresh(self, event):
    if self.options_window is not None:
      self.options_window.refresh(event)

  def stop(self):
    self.state.is_running = False

  def prompt_update(self, current, latest):
    res = mb.askyesno("New version available", f"There is a new version available.\n" + \
    f"Your version: {current}\nLatest version: {latest}.\nWould you like to update?\n" + \
    "At the moment, clicking 'Yes' will attempt to download the newest zip archive from your browser.")
    if res:
      webbrowser.open_new_tab(f"{self.state.network.url}/download/latest")
    

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
