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
  
  def render(self, row : RenderRow):
    if row.rowtype != 'DIRECTION':
      return

    i = row.renderer.state.idx
    l = row.renderer.lookahead_frames
    pos_start = (self.frame - i)/(1.0*l)
    pos_end = (self.frame + self.duration - i)/(1.0*l)

    if pos_end < -0.2 or pos_start > 1.2:
      return

    y_start = row.renderer.screen_height*pos_start
    y_end = row.renderer.screen_height*pos_end

    row.renderer.draw_im("motion_start", (row.x, y_start))
    row.renderer.draw_im("motion_end", (row.x, y_end))

    for step in range(self.duration):
      pos = (self.frame + step - i)/(1.0*l)
      y_step = row.renderer.screen_height*pos
      row.renderer.draw_im("motion_mid", (row.x, y_step))

    for ii in range(self.duration):
      if ii % 7 != 0 and ii != self.duration - 1:
        continue
      p_step = (self.frame + (ii/(self.duration-1))*self.duration - i)/(1.0*l)
      y_step = row.renderer.screen_height*p_step
      k = self.release_key if ii == self.duration - 1 else self.hold_key
      row.renderer.draw_im(k, (row.x, y_step), 0.7)

    ##row.renderer.draw_im(self.hold_key, (row.x, y_start))
    ##for step in range(self.duration):
    ##  if step % 7 != 0:
    ##    continue
    ##  pos = (self.frame + step - i)/(1.0*l)
    ##  y_step = row.renderer.screen_height*pos
    ##  row.renderer.draw_im(self.hold_key, (row.x, y_step))
    ##row.renderer.draw_im(self.release_key, (row.x, y_end))
    ##row.renderer.draw_im("0004", (row.x, y_start))

class MotionInput(Renderable):
  def __init__(self, frame : int, motion : str, duration: int):
    self.frame = frame
    self.motion = motion
    self.duration = duration
  
  def render(self, row : RenderRow):
    if row.rowtype != 'DIRECTION':
      return

    i = row.renderer.state.idx
    l = row.renderer.lookahead_frames
    pos_start = (self.frame - i)/(1.0*l)
    pos_end = (self.frame + self.duration - i)/(1.0*l)

    if pos_end < -0.2 or pos_start > 1.2:
      return

    y_start = row.renderer.screen_height*pos_start
    y_end = row.renderer.screen_height*pos_end

    row.renderer.draw_im("motion_start", (row.x, y_start))
    row.renderer.draw_im("motion_end", (row.x, y_end))

    for step in range(self.duration):
      pos = (self.frame + step - i)/(1.0*l)
      y_step = row.renderer.screen_height*pos
      row.renderer.draw_im("motion_mid", (row.x, y_step))

    for ii, m in enumerate(self.motion):
      p_step = (self.frame + (ii/(len(self.motion)-1))*self.duration - i)/(1.0*l)
      y_step = row.renderer.screen_height*p_step
      row.renderer.draw_im(m, (row.x, y_step), 0.7)


class DirectionInput(Renderable):
  def __init__(self, frame : int, key : str, duration : int):
    self.frame = frame
    self.key = key
    self.duration = duration

  def render(self, row : RenderRow):
    if row.rowtype != 'DIRECTION':
      return

    i = row.renderer.state.idx
    l = row.renderer.lookahead_frames
    pos = (self.frame - i)/(1.0*l)

    if pos < -0.2 or pos > 1.2:
      return

    y = row.renderer.screen_height*pos
    row.renderer.draw_im(self.key, (row.x, y))
    ## TODO draw for more than one frame

class ButtonInput(Renderable):
  def __init__(self, frame : int, key : str, duration : int):
    self.frame = frame
    self.key = key
    self.duration = duration

  def render(self, row : RenderRow):
    if row.rowtype != 'BUTTON' or row.button != self.key:
      return

    i = row.renderer.state.idx
    l = row.renderer.lookahead_frames
    pos = (self.frame - i)/(1.0*l)

    if pos < -0.2 or pos > 1.2:
      return

    y = row.renderer.screen_height*pos
    row.renderer.draw_im(self.key, (row.x, y))
    ## TODO draw for more than one frame