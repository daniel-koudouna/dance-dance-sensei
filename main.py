import pygame
from game_window import GameWindow
from game_state import GameState

def main():
  state = GameState("xrd")
  window = GameWindow(state)

  state.renderer.add_direction_row("M")
  state.renderer.add_button_row("P")
  state.renderer.add_button_row("K")
  state.renderer.add_button_row("S")
  state.renderer.add_button_row("H")
  state.renderer.add_button_row("D")

  pygame.init()

  ## TODO select using config
  screen = pygame.display.set_mode((360,800))

  clock = pygame.time.Clock()
  pygame.joystick.init()

  joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
  print(joysticks)

  ## TODO select using config
  joystick = joysticks[0]
  state.reload_gamepad(joystick, "mappings.csv")

  ## TODO measure using config
  sz = 30
  padding = 10
  width = sz + padding

  while state.is_running:
    ##print(btn_state)

    for event in pygame.event.get():
      state.handle_event(event)
      window.handle_event(event)

    window.update()
    ## Drawing
    screen.fill(pygame.Color('black'))

    state.update()
    state.render(screen)

    ## End drawing
    pygame.display.update()
    clock.tick(60)


  pygame.quit()
  state.is_running = False


if __name__ == "__main__":
  main()
