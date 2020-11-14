import pygame
import win32api

from typing import List, Tuple, Dict, Callable

def raw_to_hat(x,y):
  x_hat = 0
  y_hat = 0
  if x < -0.5:
    x_hat = -1
  if x > 0.5:
    x_hat = 1

  ## Y is an inverted axis
  if y < -0.5:
    y_hat = 1
  if y > 0.5:
    y_hat = -1

  return (x_hat, y_hat)

def hat_to_dir(hat):
  if hat == (-1,-1):
    return 1
  elif hat == (0,-1):
    return 2
  elif hat == (1,-1):
    return 3 
  elif hat == (-1,0):
    return 4
  elif hat == (1,0):
    return 6
  elif hat == (-1,1):
    return 7
  elif hat == (0,1):
    return 8
  elif hat == (1,1):
    return 9
  else:
    return 5

def is_pressed(c):
  key = ord(c)
  return win32api.GetKeyState(key) & (1 << 7) != 0

def safe_int(v):
  try:
    return int(v)
  except (ValueError, TypeError):
    return -1

class InputManager(object):
  def __init__(self):
    pygame.joystick.init()
    self.mappings : List[Tuple[str, str, str, str]] = []
    self.complete_mappings : bool = False
    self.devices = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    for d in self.devices:
      d.init()

  def set_mappings(self, game, mappings : List[Tuple[str, str, str, str]]):
    self.mappings = mappings


  def poll_full_motion(self):
    for dev in range(len(self.devices)):
      d = self.devices[dev]
      for i in range(d.get_numhats()):
        if d.get_hat(i) != (0,0):
          return ("Movement", "Hat", i, dev)

      for i in range(d.get_numaxes()):
        if (d.get_axis(i) > 0.5 or d.get_axis(i) < -0.5):
          for j in range(d.get_numaxes()):
            if i != j and (d.get_axis(j) > 0.5 or d.get_axis(j) < -0.5):
              return ("Movement", "DualAxis", str(i) + str(j), dev)

    return None

  def poll_full(self, btn):
    for dev in range(len(self.devices)):
      d = self.devices[dev]
      for i in range(d.get_numbuttons()):
        if d.get_button(i) == 1:
          return (btn, "Button", i, dev)
      for i in range(d.get_numaxes()):
        if d.get_axis(i) > 0.5:
          return (btn, "PosAxis", i, dev)
        if d.get_axis(i) < -0.5:
          return (btn, "NegAxis", i, dev)
    
    for i in range(65, 91):
      if is_pressed(chr(i)):
        return (btn, "Keyboard", chr(i), 0)

    return None

  def poll(self) -> Dict[str, bool]:
    btns = {}
    for key, method, val, device in self.mappings:
      if key not in btns:
        btns[key] = False

      val_i = safe_int(val)
      device_i = safe_int(device)
      d = self.devices[device_i]

      if method == 'Button' and val_i <= d.get_numbuttons():
        btns[key] = btns[key] or d.get_button(val_i) == 1
      elif method == 'Hat' and val_i <= d.get_numhats():
        r = hat_to_dir(d.get_hat(val_i))
        if btns[key] == False or r != 5:
          btns[key] = r
      elif method == 'PosAxis' and val_i <= d.get_numaxes():
        btns[key] = btns[key] or d.get_axis(val_i) > 0.5
      elif method == 'NegAxis' and val_i <= d.get_numaxes():
        btns[key] = btns[key] or d.get_axis(val_i) < -0.5
      elif method == 'DualAxis':
        ax_1 = safe_int(val[0])
        ax_2 = safe_int(val[1])
        if ax_1 >= 0 and ax_2 >= 0 and ax_1 <= d.get_numaxes() and ax_2 <= d.get_numaxes():
          v_x = d.get_axis(ax_1)
          v_y = d.get_axis(ax_2)
          r = hat_to_dir(raw_to_hat(v_x, v_y))
          if btns[key] == False or r != 5:
            btns[key] = r
      elif method == 'Keyboard':
        btns[key] = btns[key] or is_pressed(val)

    ## Consolidate movement keys, they take priority over pad
    key_x = 0
    if 'Left' in btns and btns['Left']:
      key_x = -1
    if 'Right' in btns and btns['Right']:
      key_x = 1

    key_y = 0
    if 'Down' in btns and btns['Down']:
      key_y = -1
    if 'Up' in btns and btns['Up']:
      key_y = 1

    key_dir = hat_to_dir((key_x, key_y))
    if key_dir != 5:
      btns['Movement'] = key_dir

    return btns
