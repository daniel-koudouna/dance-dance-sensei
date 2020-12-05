import os
import pygame
import shutil
import threading
import toml
import traceback


from game_window import GameWindow
from game_state import GameState
from game import games
from logger import Log

from utils import *


def main():
  Log.debug("=== Running Dance Dance Sensei ===")
  if not os.path.isfile("config.toml"):
    Log.debug("Config not found, copying default config")
    shutil.copyfile("default_config.toml", "config.toml")

  config = toml.load("config.toml")

  if 'game' not in config:
    config['game'] = {}
    config['game']['default_game'] = games[0].code
    toml.dump(config, open("config.toml", "w"))

  if os.path.exists('sequence'):
    print("Sliently moving")
    print(os.path.expanduser("~\.dds"))


  ## Find game from config
  game_id = config['game']['default_game']
  game = first(games, lambda x : x.code == game_id)

  state = GameState(game, config)
  window = GameWindow(state)

  pygame.init()

  ## Get window size
  width = config['display']['width'] 
  height = config['display']['height'] 
  screen = pygame.display.set_mode((width,height))

  clock = pygame.time.Clock()

  soundclock = pygame.time.Clock()

  pygame.mixer.init()
  beep = pygame.mixer.Sound(file="sound/beep.wav")
  beep.set_volume(0.75)


  def pygamethread():
    try:
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
    except Exception as e:
      Log.debug(traceback.format_exc())

    pygame.quit()
    state.is_running = False
    window.quit()

  def soundthread():
    last_played = 0
    try:
      while state.is_running:
        last_played += 1

        if state.is_playing and state.use_metronome and last_played > 30:
          last_played = 0
          beep.stop()
          beep.play(0)

        soundclock.tick(240)
    except Exception as e:
      Log.debug(traceback.format_exc())


  threading.Thread(None, pygamethread).start()
  threading.Thread(None, soundthread).start()

  window.mainloop()


if __name__ == "__main__":
  try:
    main()
  except Exception as e:
    Log.debug(traceback.format_exc())