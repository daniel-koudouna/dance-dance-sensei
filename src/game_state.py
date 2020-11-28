from datetime import datetime
import csv
import os
from typing import List
import pygame
import time
import threading

from game import Game
from logger import Log
from renderer import Renderer
from network import Network
from sequence import Sequence

from input_manager import InputManager

class GameState(object):
  def __init__(self, mode, config):
    self.is_running = True
    self.window = None
    self.input_manager = InputManager()
    self.reload_mode(mode)
    self.config = config
    self.network = Network(self)
    self.register_mode = None

  def render(self, screen):
    self.idx += 1
    self.renderer.render(self, screen)

  def reload_mode(self, mode : Game):
    self.last_reloaded = 0
    self.idx = 0
    self.mode = mode
    self.last_sequence = None
    self.parsed_sequence = None
    self.is_recording = False
    self.previous_buttons = {}
    self.buttons = {}
    self.renderer = Renderer(mode.visuals)
    os.makedirs(mode.sequences, exist_ok=True)

    mode.renderer(self.renderer)
    if self.window is not None:
      self.window.reload_context_menu()
    
    self.reload_gamepad(self.mode.mappings)

  def reload_last_sequence(self):
    self.reload_sequence(self.last_sequence)



  def register_new_button(self, btn):
    self.register_mode = btn

  def clear_button(self, btn):
    print(f"CLEARING BUTTON {btn}")
    mapping_file = open(self.mode.mappings)
    lines = [[s.strip() for s in l] for l in csv.reader(mapping_file) if len(l) == 4]
    lines = [l for l in lines if l[0] != btn]
    mapping_file.close()
    mapping_file = open(self.mode.mappings, "w")
    csv.writer(mapping_file).writerows(lines)
    mapping_file.close()
    self.reload_mode(self.mode)


  def set_sequence(self, seq):
    self.parsed_sequence = seq
    self.last_reloaded = 0
    self.is_playing = True
    self.idx = -60


  def reload_sequence(self, filename):
    seq_file = f"{self.mode.sequences}/{filename}"
    self.last_sequence = filename 
    lines = open(seq_file).readlines()
    self.set_sequence(Sequence(lines, self.mappings, self.mode))

  def refresh(self, event):
    if self.window is not None:
      self.window.refresh(event)


  def reload_gamepad(self, filename):
    if not os.path.isfile(filename):
      os.makedirs("mappings", exist_ok=True)
      f = open(filename, "w+")
      f.write("\n")
      f.close()
    mapping_file = open(filename)
    lines = [[s.strip() for s in l] for l in csv.reader(mapping_file) if len(l) == 4]
    self.mappings = lines
    self.input_manager.set_mappings(self.mode, lines)
    self.refresh(("mappings", None))

  def update(self):
    self.handle_input()
    self.last_reloaded += 1
    if self.is_recording:
      res = ""
      found_something = False
      for k,v in self.buttons.items():
        if type(v) is bool and v == True:
          res = res + k
          found_something = True
        elif type(v) is int and v != 5:
          res = str(v) + res
          found_something = True
      if found_something:
        self.recorded_sequence.append(res)
      else:
        self.recorded_sequence.append("5")

    if 'Play' in self.buttons and self.buttons['Play'] and self.last_reloaded > 100 and self.last_sequence is not None and not self.is_recording:
      self.reload_last_sequence()
    if 'Record' in self.buttons and self.buttons['Record']:
      if self.is_recording and not self.previous_buttons['Record']:
        self.stop_recording()
      elif self.last_reloaded > 50:
        self.start_recording()

  def start_recording(self):
    self.is_recording = True
    self.last_reloaded = 0
    print("Recording!")
    self.recorded_sequence = []

  def stop_recording(self):
    self.last_reloaded = 0
    self.is_recording = False
    print("Stopped recording!")
    print(self.recorded_sequence)
    today = datetime.now()
    fname = today.strftime("%Y_%m_%d_%H_%M_%S")
    filename = f"{self.mode.sequences}/personal/{fname}_{len(self.recorded_sequence)}.txt"
    lines = [l + "\n" for l in self.recorded_sequence]

    if len(lines) < 100:
      return

    actual_btns = [l for l in self.recorded_sequence if l != '5' and l != 'Record']

    if len(actual_btns) < 30:
      return

    os.makedirs(f"{self.mode.sequences}/personal", exist_ok=True)
    open(filename, "w").writelines(lines)
    self.window.reload_context_menu()

  def handle_event(self, event):
    if event.type == pygame.QUIT:
      self.is_running = False

  def handle_input(self):
    if self.register_mode is None:
      self.previous_buttons = self.buttons
      self.buttons = self.input_manager.poll()
    else:
      if self.register_mode == "Movement":
        next_btn = self.input_manager.poll_full_motion(self.register_mode)
      else:
        next_btn = self.input_manager.poll_full(self.register_mode)

      if next_btn is not None:
        self.register_mode = None
        if next_btn[0] is not "INVALID":
          Log.debug(f"Writing new key binding {next_btn}")
          f = open(self.mode.mappings, "a")
          csv.writer(f).writerow(next_btn)
          f.close()
        else:
          Log.debug(f"Key binding invalid: {next_btn[1]}")

        self.reload_gamepad(self.mode.mappings)

