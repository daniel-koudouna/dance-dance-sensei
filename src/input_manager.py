import pygame
import win32api

from typing import List, Tuple, Dict, Callable

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
        btns[key] = hat_to_dir(d.get_hat(val_i))
      elif method == 'PosAxis' and val_i <= d.get_numaxes():
        btns[key] = btns[key] or d.get_axis(val_i) > 0.5
      elif method == 'NegAxis' and val_i <= d.get_numaxes():
        btns[key] = btns[key] or d.get_axis(val_i) < -0.5
      elif method == 'Keyboard':
        btns[key] = btns[key] or is_pressed(val)

    return btns
