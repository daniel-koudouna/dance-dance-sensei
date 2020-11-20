from collections import Counter

from renderable import *
from utils import *

class Sequence(object):
  def pop_button_stack(self, b : str, n : int):
    if b in self.button_stack:
      start = self.button_stack[b]
      del self.button_stack[b]
      self.objects.append(ButtonInput(start, b, n - start))

  def handle_empty(self, n):
    keys = list(self.button_stack.keys())
    self.last_motion = None
    for k in keys:
      self.pop_button_stack(k, n)
    if len(self.motion_stack) > 0 and self.motion_stack[-1][1] != "5":
      self.motion_stack.append((n, "5"))

  def collapse_motion(self, n):
    if len(self.motion_stack) == 1:
      return

    ## If we hit a non-digit, attempt to end the motion
    while len(self.motion_stack) > 1:
      ## check motion
      for inputs, motion in self.motion_converters:
        if len(self.motion_stack) != len(inputs):
          continue

        print(self.motion_stack)

        mo = self.motion_stack[:len(inputs)]
        mm = ''.join([m[0] for (y,m) in mo])
        if mm == inputs:
          for i in range(len(inputs)):
            self.motion_stack.pop(0)

          frame_start = mo[0][0]
          frame_end = n
          print("Found motion from " + str(frame_start) + " to " + str(frame_end))
          duration = frame_end - frame_start
          frame_next_start = mo[1][0]
          if duration <= self.max_motion_length:
            self.objects.append(MotionInput(frame_start, motion, frame_end - frame_start))
            self.last_motion = mm[-1]
          elif frame_end - frame_next_start <= self.max_motion_length:
            print("motion too long due to held key, splitting!!")
            new_start = frame_next_start - 1
            self.objects.append(DirectionInput(frame_start, mo[0][1], new_start - frame_start))
            self.objects.append(MotionInput(new_start, motion, frame_end - new_start))
            self.last_motion = mm[-1]
          else:
            print("motion too long, fully splitting!!")
            for ff, bb in mo:
              ## TODO more than 1 frame!
              self.objects.append(DirectionInput(ff, bb, 1))


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
      else:
        if b not in self.button_stack:
          self.button_stack[b] = n
          self.collapse_motion(n)
    keys = list(self.button_stack.keys())
    for k in keys:
      if k not in btns:
        self.pop_button_stack(k, n)


  def __init__(self, raw_inputs, motions, charge_motions):
    self.objects = []

    self.motion_stack = []
    self.button_stack = {}
    self.max_motion_length = 20
    self.min_hold_motion_length = 30
    self.last_motion = None

    self.motion_converters = list(sorted(motions, key=lambda x: x[0]))
    self.charge_motions = charge_motions

    for n in range(len(raw_inputs)):
      action = raw_inputs[n]
      if action['type'] == 'empty':
        self.handle_empty(n)
      if action['type'] == 'button':
        btns = action['buttons']
        self.handle_button(btns, n)

    for ff,bb in self.motion_stack:
      if bb != "5":
        self.objects.append(DirectionInput(ff, bb, 1))

