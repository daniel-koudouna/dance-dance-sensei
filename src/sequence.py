from collections import Counter

from typing import List

from renderable import *
from utils import *

MOTION_FRAME_WINDOW = 2


class Sequence(object):
  DEFAULT_BPM = 60

  def buttons_from_line(btns : List[str], line : str):
    res = []
    digit = [str(char) for char in line if str(char).isdigit()]
    if len(digit) > 0:
      res.extend(digit)

    lineres = line
    for b in btns:
      idx = lineres.find(b)
      if idx >= 0:
        lineres = lineres.replace(b, "")
        res.append(b)

    return res

  def read_bpm(lines):
    for l in lines:
      line = l.strip()
      if not line.startswith("# bpm: "):
        continue
      try:
        bpm = int(line.split(":")[1].strip())
        return bpm
      except ValueError:
        continue
    return Sequence.DEFAULT_BPM

  def sequence_from_raw(mappings, lines):
    btns = list(set([s[0] for s in mappings]))
    btns.sort(key=lambda x : -len(x))
    res = []

    for l in lines:
      line = l.strip()
      if line.startswith("#"):
        continue
      if line == '5':
        res.append(None)
      else:
        res.append(Sequence.buttons_from_line(btns, line))

    return res

  def pop_button_stack(self, b : str, n : int):
    if b in self.button_stack:
      start = self.button_stack[b]
      del self.button_stack[b]
      self.objects.append(ButtonInput(start, b, n - start))
    if len(self.button_stack) == 0:
      self.last_button_up = n

  def handle_empty(self, n):
    keys = list(self.button_stack.keys())
    self.last_motion = None
    for k in keys:
      self.pop_button_stack(k, n)
    if len(self.motion_stack) > 0 and self.motion_stack[-1][1] != "5":
      self.motion_stack.append((n, "5"))

  def maybe_collapse_motion(self, n):
    if len(self.motion_stack) == 1:
      return


  def collapse_motion(self, n):
    if len(self.motion_stack) == 1:
      return

    ## If we hit a non-digit, attempt to end the motion
    while len(self.motion_stack) > 1:
      ## check motion
      print(self.motion_stack)

      for inputs, motion, max_duration in self.motion_converters:
        if len(self.motion_stack) < len(inputs):
          continue

        mo = self.motion_stack[:len(inputs)]
        frame_end = mo[-1][0]
        mm = ''.join([m[0] for (y,m) in mo])
        if mm == inputs:
          for i in range(len(inputs)):
            self.motion_stack.pop(0)

          frame_start = mo[0][0]
          print("Found motion from " + str(frame_start) + " to " + str(frame_end))
          duration = frame_end - frame_start
          frame_next_start = mo[1][0]
          if duration <= max_duration:
            self.objects.append(MotionInput(frame_start, motion, frame_end - frame_start))
            self.last_motion = mm[-1]
          elif frame_end - frame_next_start <= max_duration:
            print("motion too long due to held key, splitting!!")
            new_start = frame_next_start - 1
            self.objects.append(DirectionInput(frame_start, mo[0][1], new_start - frame_start))
            self.objects.append(MotionInput(new_start, motion, frame_end - new_start))
            self.last_motion = mm[-1]
          else:
            print("motion too long, fully splitting!!")
            print(f"Last button up was at {self.last_button_up}")
            if mo[0][1] != "5":
              duration = mo[1][0] - mo[0][0]
              self.objects.append(DirectionInput(mo[0][0], mo[0][1], duration))

            print(mo)
            w = mo[1:]
            w.reverse()
            for ff, bb in w:
              self.motion_stack.insert(0, (ff,bb))


      if len(self.motion_stack) >= 2:
        firstf, firstb = self.motion_stack[0]
        nextf, nextb = self.motion_stack[1]
        lastf, lastb =  self.motion_stack[-1]
        charge = firstb + lastb
        duration = nextf - firstf

        foundC = first(self.charge_motions, lambda x : x[0] == charge)
        if foundC is not None and duration > self.min_hold_motion_length:
          normalized_motion = foundC[1]
          print("Found charge from " + str(firstf) + " to " + str(lastf))
          self.objects.append(ChargeInput(firstf, normalized_motion[0], duration, normalized_motion[1]))
          self.motion_stack = []
          self.last_motion = charge[-1]
          continue

      ## Pop if not found, repeat
      ## TODO clean this to have a button input more than 1 frame!!
      if len(self.motion_stack) <= 1:
        continue
      ff, bb = self.motion_stack.pop(0)
      if bb != "5":
        fnext, _bnext = self.motion_stack[0]
        self.objects.append(DirectionInput(ff, bb, fnext - ff))


  def handle_button(self, btns, n):
    for b in btns:
      if b.isdigit():
        if len(self.motion_stack) == 0 or self.motion_stack[-1][1] != b:
          if self.last_motion == None or self.last_motion != b:
            self.motion_stack.append((n, b))
            self.last_motion = None
      elif b in self.action_buttons:
        if b not in self.button_stack:
          self.button_stack[b] = n
          self.motion_window_counter = 1
    keys = list(self.button_stack.keys())
    for k in keys:
      if k not in btns:
        self.pop_button_stack(k, n)


  def duration(self):
    if len(self.objects) < 1:
      return 0
    l = self.objects[-1]
    return l.frame + l.duration

  def first_frame(self):
    abtns = [o for o in self.objects if type(o) is ButtonInput and o.key in self.action_buttons]

    if len(abtns) < 1:
      return 0

    print(abtns[0])
    return abtns[0].frame


  def __init__(self, raw_lines, mappings, mode):
    self.objects = []
    self.lines = raw_lines
    self.motion_stack = []
    self.button_stack = {}
    self.max_motion_length = 25
    self.min_hold_motion_length = 34
    self.last_button_up = 0
    self.last_motion = None
    self.motion_window_counter = 0
    self.action_buttons = mode.action_buttons
    self.bpm = Sequence.DEFAULT_BPM

    self.has_22 = True

    self.motion_converters = [(raw, inputs, 25) for (raw,inputs) in mode.motions]
    if self.has_22:
      self.motion_converters.append(("252","22", 10))

    self.motion_converters = list(sorted(self.motion_converters, key=lambda x: x[0]))

    self.charge_motions = mode.charge_motions

    raw_inputs = Sequence.sequence_from_raw(mappings, raw_lines)
    self.bpm = Sequence.read_bpm(raw_lines)

    for n in range(len(raw_inputs)):
      action = raw_inputs[n]
      if action == None:
        self.handle_empty(n)
      else:
        self.handle_button(action, n)

      if self.motion_window_counter > 0:
        self.motion_window_counter += 1
        if self.motion_window_counter > MOTION_FRAME_WINDOW + 1:
          self.motion_window_counter = 0
          self.collapse_motion(n)

    for ff,bb in self.motion_stack:
      if bb != "5":
        self.objects.append(DirectionInput(ff, bb, 1))

