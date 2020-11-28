from abc import ABC, abstractmethod 
import pygame

from renderer import Renderer, RenderRow


class Renderable(ABC):
  @abstractmethod
  def render(self, row : RenderRow):
    pass


class ChargeInput(Renderable):
  def __init__(self, frame : int, hold_key: str, duration: int, release_key: str):
    self.frame = frame
    self.hold_key = hold_key
    self.duration = duration
    self.release_key = release_key
  
  def __repr__(self) -> str:
    return type(self).__name__ + f"[{self.hold_key}{self.release_key}] ~ {self.frame}:{self.duration}"

  def render(self, row : RenderRow):
    if row.rowtype != 'DIRECTION':
      return

    g = row.renderer

    i = g.state.idx
    l = g.lookahead_frames
    pos_start = (self.frame - i)/(1.0*l)
    pos_end = (self.frame + self.duration - i)/(1.0*l)

    if pos_end < -0.05 or pos_start > 1.2:
      return

    y_start = g.padding + g.screen_height*max(0,pos_start)
    y_end = g.padding + g.screen_height*max(0,pos_end)

    g.draw_im("motion_start", (row.x, y_start))
    g.draw_im("motion_end", (row.x, y_end))

    for step in range(1, self.duration):
      pos = (self.frame + step - i)/(1.0*l)
      y_step = g.padding + g.screen_height*max(0,pos)
      g.draw_im("motion_mid", (row.x, y_step))

    for ii in range(self.duration):
      if ii % 7 != 0 and ii != self.duration - 1:
        continue
      p_step = (self.frame + (ii/(self.duration-1))*self.duration - i)/(1.0*l)
      p_step_last = (self.frame + self.duration - i)/(1.0*l)

      y_step = g.padding + g.screen_height*max(0,p_step)
      k = "dot"
      if ii == self.duration - 1:
        k = self.release_key
      if ii == 0:
        k = self.hold_key

      should_draw = (ii == self.duration -1) or \
                    (ii == 0 and p_step_last > 0.01) or \
                    p_step > 0.01


      if should_draw:
        g.draw_im(k, (row.x, y_step), 0.7)

class MotionInput(Renderable):
  def __init__(self, frame : int, motion : str, duration: int):
    self.frame = frame
    self.motion = motion
    self.duration = duration

  def __repr__(self) -> str:
    return type(self).__name__ + f"[{self.motion}] ~ {self.frame}:{self.duration}"
  
  def render(self, row : RenderRow):
    if row.rowtype != 'DIRECTION':
      return

    g = row.renderer

    i = g.state.idx
    l = g.lookahead_frames
    pos_start = (self.frame - i)/(1.0*l)
    pos_end = (self.frame + self.duration - i)/(1.0*l)

    if pos_end < -0.05 or pos_start > 1.2:
      return

    y_start = g.padding + g.screen_height*max(0,pos_start)
    y_end = g.padding + g.screen_height*max(0,pos_end)

    g.draw_im("motion_start", (row.x, y_start))
    g.draw_im("motion_end", (row.x, y_end))

    for step in range(1,self.duration):
      pos = (self.frame + step - i)/(1.0*l)
      y_step = g.padding + g.screen_height*max(0,pos)
      g.draw_im("motion_mid", (row.x, y_step))

    for ii, m in enumerate(self.motion):
      p_step = (self.frame + (ii/(len(self.motion)-1))*self.duration - i)/(1.0*l)
      ii_next = ii if ii == len(self.motion) - 1 else ii+1
      p_step_next = (self.frame + (ii_next/(len(self.motion)-1))*self.duration - i)/(1.0*l)

      y_step = g.padding + g.screen_height*max(0, p_step)
      if ii == len(self.motion) - 1 or p_step_next > 0.01:
        g.draw_im(m, (row.x, y_step), 0.7)


class DirectionInput(Renderable):
  def __init__(self, frame : int, key : str, duration : int):
    self.frame = frame
    self.key = key
    self.duration = duration

  def __repr__(self) -> str:
    return type(self).__name__ + f"[{self.key}] ~ {self.frame}:{self.duration}"

  def render(self, row : RenderRow):
    if row.rowtype != 'DIRECTION':
      return

    g = row.renderer

    i = g.state.idx
    l = g.lookahead_frames
    pos_start = (self.frame - i)/(1.0*l)
    pos_end = (self.frame + self.duration - i)/(1.0*l)

    if pos_end < -0.0 or pos_start > 1.2:
      return

    y_start = g.padding + g.screen_height*max(0,pos_start)
    y_end = g.padding + g.screen_height*max(0,pos_end)

    for step in range(1,self.duration):
      pos = (self.frame + step - i)/(1.0*l)
      y_step = g.padding + g.screen_height*max(0,pos)
      g.draw_im(self.key, (row.x, y_step))

    g.draw_im(self.key, (row.x, y_start))

class ButtonInput(Renderable):
  def __init__(self, frame : int, key : str, duration : int):
    self.frame = frame
    self.key = key
    self.duration = duration

  def __repr__(self) -> str:
    return type(self).__name__ + f"[{self.key}] ~ {self.frame}:{self.duration}"

  def render(self, row : RenderRow):
    if row.rowtype != 'BUTTON' or row.button != self.key:
      return

    g = row.renderer

    i = g.state.idx
    l = g.lookahead_frames
    pos_start = (self.frame - i)/(1.0*l)
    pos_end = (self.frame + self.duration - i)/(1.0*l)

    if pos_end < -0.05 or pos_start > 1.2:
      return


    y_start = g.padding + g.screen_height*max(0, pos_start)
    y_end = g.padding + g.screen_height*max(0, pos_end)

    for step in range(1,self.duration):
      pos = max(0, (self.frame + step - i)/(1.0*l))
      y_step = g.padding + g.screen_height*pos
      g.draw_im(self.key + "_", (row.x, y_step))

    g.draw_im(self.key + "_end", (row.x, y_end))
    g.draw_im(self.key, (row.x, y_start))