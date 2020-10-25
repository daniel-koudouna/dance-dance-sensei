from os import listdir
from os.path import isfile, join
import pygame

class Renderer(object):
  def __init__(self, path):
    self.rows = []
    self.padding = 10
    self.width = 50
    self.images = {}
    self.lookahead_frames = 90
    images = [(f, f"{path}/{f}") for f in listdir(path) if isfile(join(path, f))]
    images.append(("_record", "img/record.png"))
    images.append(("_play", "img/play.png"))
    for key, im in images:
      print(f"Loading {im}")
      self.images[key.split(".")[0]] = pygame.image.load(im)



  def draw_im(self, screen, im, pos):
    screen.blit(pygame.transform.scale(self.images[im], (self.width, self.width)), pos)

  def pressed(self, state, button):
    if state.buttons[button]:
      return button
    else:
      return button + "_empty"

  def render_row(self, row, state, screen, x, icons_to_render):
    rowtype = row['type']
    if row['button'] not in state.buttons:
      return
    if rowtype == 'BUTTON':
      self.draw_im(screen, self.pressed(state, row['button']), (x, self.padding))
      for y,btns in icons_to_render:
        for btn in btns:
          if btn == row['button']:
            self.draw_im(screen, row['button'], (x, y))
    elif rowtype == 'DIRECTION':
      self.draw_im(screen, str(state.buttons[row['button']]), (x, self.padding))
      for y,btns in icons_to_render:
        for btn in btns:
          if btn.isdigit():
            self.draw_im(screen, btn, (x,y))

  def render(self, state, screen):
    if len(self.rows) == 0:
      return
    w, h = screen.get_size()
    self.width = (int)(((w - self.padding) / (1.0*len(self.rows)) ) - self.padding)

    icons_to_render = []

    for i in range(self.lookahead_frames):
      n = i + state.idx
      if n >= 0 and n < len(state.sequence):
        action = state.sequence[n]
        if action['type'] == 'button':
          btns = action['buttons']
          y = (int)(i * h/ (1.0*self.lookahead_frames)) + 10
          icons_to_render.append( (y, btns))

    for i, row in enumerate(self.rows):
      self.render_row(row, state, screen, (self.width + self.padding)*i + self.padding, icons_to_render)
    
    if state.is_recording:
      self.draw_im(screen, '_record', ((w - self.width)/2,(h - self.width)/2))


  def add_direction_row(self, button_name):
    self.rows.append({"type": "DIRECTION", "button": button_name})

  def add_button_row(self, button_name):
    self.rows.append({"type": "BUTTON", "button": button_name})