from os import listdir
from os.path import isfile, join
import threading
from typing import List
import pygame
from profilehooks import profile

class Renderer(object):
  def __init__(self, path : str):
    self.rows = []
    self.padding = 10
    self.width = 50
    self.images = {}
    self.scales = {}
    self.lookahead_frames = 90
    self.screen_width = 0
    self.screen_height = 0
    self.path = path
    self.ready = False


  def start(self):
    images = [(f, f"{self.path}/{f}") for f in listdir(self.path) if isfile(join(self.path, f))]
    images.extend([(f, f"img/common/{f}") for f in listdir("img/common") if isfile(join("img/common", f))])

    for key, im in images:
      k = key.split(".")[0]
      self.images[k] = pygame.image.load(im).convert_alpha()
      self.scales[k] = {}
    
    pygame.font.init()
    self.font = pygame.font.Font('Roboto-Regular.ttf', 20)


  def draw_im_free(self, im, pos, sz, align='center', opacity=1.0):
    i = self.images[im]
    w = i.get_width()
    h = i.get_height()
    sf = 1
    r_img = w/h
    r_container = sz[0]/sz[1]
    if r_img > r_container:
      sf = w/(1.0*sz[0])
    else:
      sf = h/(1.0*sz[1])
    new_w = w/sf
    new_h = h/sf
    s = pygame.transform.scale(i, ((int)(new_w), (int)(new_h)))
    off_x = 0
    off_y = 0
    if align == 'center':
      off_x = (sz[0] - new_w)/2
      off_y = (sz[1] - new_h)/2

    if opacity < 1.0:
      s.set_alpha((int)(255*opacity))

    newpos = (pos[0] + off_x, pos[1] + off_y)
    self.screen.blit(s, newpos)

  def draw_im(self, im, pos, scale=1.0):
    i = self.images[im]
    sf = i.get_width() / (1.0*self.width)
    newh = i.get_height() / sf
    off = (1-scale)/2.0
    x,y = pos
    newpos = (x + off*self.width, y + off*newh)

    if scale not in self.scales[im]:
      self.scales[im][scale] = pygame.transform.scale(self.images[im], ((int)(self.width*scale), (int)(newh*scale)))

    theimage = self.scales[im][scale]
    self.screen.blit(theimage, newpos)

  def pressed(self, button):
    if button in self.state.buttons and self.state.buttons[button]:
      return button
    else:
      return button + "_empty"

  def render_row(self, row, sequence):
    rowtype = row.rowtype
    if rowtype == 'BUTTON':
      if sequence is None:
        self.draw_im(self.pressed(row.button), (row.x, self.padding))
        return
      for renderable in sequence.objects:
        renderable.render(row)
        self.draw_im(self.pressed(row.button), (row.x, self.padding))

    elif rowtype == 'DIRECTION':
      direction_draw = "5"
      if row.button in self.state.buttons:
        direction_draw = str(self.state.buttons[row.button])
      self.draw_im(direction_draw, (row.x, self.padding))
      if sequence is None:
        return
      for renderable in sequence.objects:
        renderable.render(row)

  @profile
  def render(self, state, screen):
    if len(self.rows) == 0:
      return

    if not self.ready:
      self.start()
      self.ready = True

    self.screen = screen
    self.state = state
    w, h = screen.get_size()
    self.width = (int)(((w - self.padding) / (1.0*len(self.rows)) ) - self.padding)

    self.screen_width = w
    self.screen_height = h

    seq = self.state.parsed_sequence

    ## Render logo
    logo_pad = 10
    logo_size = 100
    l_x = self.screen_width - logo_size - logo_pad
    l_y = self.screen_height - logo_size - logo_pad
    self.draw_im_free('logo', (l_x, l_y), (logo_size, logo_size), opacity=0.5)

    for i, row in enumerate(self.rows):
      row.x = (self.width + self.padding)*i + self.padding
      self.render_row(row, seq)

    ## Move this into game state
    registered = set([t[0] for t in state.mappings])
    not_registered = set([b for b in state.mode.buttons if b not in registered])

    not_registered.discard('Play')
    not_registered.discard('Record')
    if 'Movement' in registered:
      not_registered.discard('Up')
      not_registered.discard('Down')
      not_registered.discard('Left')
      not_registered.discard('Right')

    if 'Up' in registered or 'Down' in registered or 'Left' in registered or 'Right' in registered:
      not_registered.discard('Movement')

    if len(not_registered) > 0:
      text = self.font.render('Some buttons are not set', True, (255, 255, 255))
      text2 = self.font.render('Right-click -> Options -> Controls', True, (255,255,255))
      screen.blit(text, (10, 100))
      screen.blit(text2, (10, 150))



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