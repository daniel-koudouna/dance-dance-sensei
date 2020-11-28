import tkinter as tk
from tkinter import ttk
import toml

from game import games
import ui

class OptionWindow(ttk.Notebook):

  def __init__(self, parent, state):
    super().__init__(parent)
    self.state = state

    self.preferences_pane = ui.PreferencesPane(self, state)
    self.network_pane = ui.NetworkPane(self, state)
    self.upload_pane = ui.UploadPane(self, state)
    self.controller_pane = ui.ControllerPane(self, state)
    self.download_pane = ui.DownloadPane(self, state)
    self.editor_pane = ui.EditorPane(self, state)

    self.add(self.preferences_pane, text="Preferences")
    self.add(self.network_pane, text="Account")
    self.add(self.upload_pane, text="Upload")
    self.add(self.download_pane, text="Download")
    self.add(self.controller_pane, text="Controls")
    self.add(self.editor_pane, text="Editor")
    self.pack(expand = 1, fill ="both") 

  def refresh(self, event):
    self.controller_pane.refresh(event)
    self.download_pane.refresh(event)
    self.upload_pane.refresh(event)
    self.network_pane.refresh(event)
    self.preferences_pane.refresh(event)