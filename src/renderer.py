from os import listdir
from os.path import isfile, join
import pygame

class Renderer(object):
  def __init__(self, path : str):
    self.rows = []
    self.padding = 10
    self.width = 50
    self.images = {}
    self.lookahead_frames = 90
    self.screen_width = 0
    self.screen_height = 0
    images = [(f, f"{path}/{f}") for f in listdir(path) if isfile(join(path, f))]
    images.extend([(f, f"img/common/{f}") for f in listdir("img/common") if isfile(join("img/common", f))])
    for key, im in images:
      print(key)
      self.images[key.split(".")[0]] = pygame.image.load(im)



  def draw_im(self, im, pos, scale=1.0):
    i = self.images[im]
    sf = i.get_width() / (1.0*self.width)
    newh = i.get_height() / sf
    off = (1-scale)/2.0
    x,y = pos
    newpos = (x + off*self.width, y + off*newh)
    self.screen.blit(pygame.transform.scale(self.images[im], ((int)(self.width*scale), (int)(newh*scale))), newpos)

  def pressed(self, button):
    if self.state.buttons[button]:
      return button
    else:
      return button + "_empty"

  def render_row(self, row, sequence):
    pass
    rowtype = row.rowtype
    if row.button not in self.state.buttons:
      return
    if rowtype == 'BUTTON':
      self.draw_im(self.pressed(row.button), (row.x, self.padding))
      if sequence is None:
        return
      for renderable in sequence.objects:
        renderable.render(row)

    elif rowtype == 'DIRECTION':
      self.draw_im(str(self.state.buttons[row.button]), (row.x, self.padding))
      if sequence is None:
        return
      for renderable in sequence.objects:
        renderable.render(row)

  def render(self, state, screen):
    if len(self.rows) == 0:
      return
    self.screen = screen
    self.state = state
    w, h = screen.get_size()
    self.width = (int)(((w - self.padding) / (1.0*len(self.rows)) ) - self.padding)

    self.screen_width = w
    self.screen_height = h

    seq = self.state.parsed_sequence

    for i, row in enumerate(self.rows):
      row.x = (self.width + self.padding)*i + self.padding
      self.render_row(row, seq)

    ##for i, row in enumerate(self.rows):
    ##  self.render_row(row, state, screen, (self.width + self.padding)*i + self.padding, icons_to_render)
    
    if self.state.is_recording:
      self.draw_im('record', ((w - self.width)/2,(h - self.width)/2))


  def add_direction_row(self, button_name):
    self.rows.append(RenderRow(self, "DIRECTION", button_name))

  def add_button_row(self, button_name):
    self.rows.append(RenderRow(self, "BUTTON", button_name))

class RenderRow(object):
  def __init__(self, renderer : Renderer, rowtype, button):
    self.renderer = renderer
    self.rowtype = rowtype
    self.button = button
    self.x = 0