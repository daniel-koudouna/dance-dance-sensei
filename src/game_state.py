from datetime import datetime
import csv
import os
import pygame
import time
import threading

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

  def render(self, screen):
    self.idx += 1
    self.renderer.render(self, screen)

  def reload_mode(self, mode):
    self.last_reloaded = 0
    self.idx = 0
    self.mode = mode
    self.last_sequence = None
    self.sequence = []
    self.parsed_sequence = None
    self.is_recording = False
    self.buttons = {}
    self.renderer = Renderer(mode.visuals)
    mode.renderer(self.renderer)
    if self.window is not None:
      self.window.reload_context_menu()
    
    mappings = os.listdir(self.mode.mappings)
    self.reload_gamepad(mappings[0])

  def reload_last_sequence(self):
    self.reload_sequence(self.last_sequence)




  def reload_sequence(self, filename):
    seq_file = f"{self.mode.sequences}/{filename}"
    self.last_sequence = filename 
    self.last_reloaded = 0
    self.is_playing = True
    self.idx = -60
    self.sequence = []
    lines = open(seq_file).readlines()
    for line in lines:
      l = line.strip()
      if l == "5":
        self.sequence.append({"type": "empty"})
      else:
        self.sequence.append({"type": "button", "buttons": [str(char) for char in l if (char != ' ')] })
    self.parsed_sequence = Sequence(self.sequence, self.mode.motions, self.mode.charge_motions)


  def reload_gamepad(self, filename):
    mapping_file = open(f"{self.mode.mappings}/{filename}")
    lines = [[s.strip() for s in l] for l in csv.reader(mapping_file) if len(l) == 4]
    self.input_manager.set_mappings(self.mode, lines)

  def update(self):
    self.handle_input()
    self.last_reloaded += 1
    if self.is_recording:
      res = ""
      found_something = False
      for k,v in self.buttons.items():
        if len(k) == 1:
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
      if self.is_recording and self.last_reloaded > 100:
        self.stop_recording()
      elif self.last_reloaded > 100:
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

    os.makedirs(f"{self.mode.sequences}/personal", exist_ok=True)
    open(filename, "w").writelines(lines)
    self.window.reload_context_menu()

  def handle_event(self, event):
    print(event)
    if event.type == pygame.QUIT:
      self.is_running = False

  def handle_input(self):
    self.buttons = self.input_manager.poll()