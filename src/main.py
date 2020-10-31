import pygame
import threading
import toml

from game_window import GameWindow
from game_state import GameState
from game import games

from utils import *

def main():
  config = toml.load("config.toml")


  ## Find input method from config
  pygame.joystick.init()
  joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

  input_method = None

  if config['input']['method'] == 'joystick':
    joy_num = config['input']['default_joystick']
    joystick = joysticks[0]
    input_method = joystick
  else:
    print("NON JOYSTICK NOT SUPPORTED YET")
    exit(0)

  ## Find game from config
  game_id = config['game']['default_mode']
  game = first(games, lambda x : x.code == game_id)

  state = GameState(game, input_method, config)
  window = GameWindow(state)

  pygame.init()

  ## Get window size
  width = config['display']['width'] 
  height = config['display']['height'] 
  screen = pygame.display.set_mode((width,height))

  clock = pygame.time.Clock()

  def pygamethread():
    while state.is_running:

      for event in pygame.event.get():
        state.handle_event(event)
        window.handle_event(event)

      ## Drawing
      screen.fill(pygame.Color('black'))

      state.update()
      state.render(screen)

      ## End drawing
      pygame.display.update()
      clock.tick(60)


    pygame.quit()
    state.is_running = False
    window.quit()

  threading.Thread(None, pygamethread).start()

  window.mainloop()


if __name__ == "__main__":
  main()
