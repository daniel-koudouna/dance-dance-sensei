class Game(object):
  def __init__(self, **kwargs):
    self.name = kwargs["name"]
    self.code = kwargs["code"]
    self.visuals = f"img/{self.code}"
    self.sequences = f"sequence/{self.code}"
    self.mappings = f"mappings/{self.code}"
    self.renderer = kwargs["renderer"]


def guilty_gear_renderer(r):
  r.add_direction_row("M")
  r.add_button_row("P")
  r.add_button_row("K")
  r.add_button_row("S")
  r.add_button_row("H")
  r.add_button_row("D")


guilty_gear_xrd = Game(name="Guilty Gear Xrd", 
                       code="xrd",
                       renderer=guilty_gear_renderer)


def pony_renderer(r):
  r.add_direction_row("M")
  r.add_button_row("A")
  r.add_button_row("B")
  r.add_button_row("C")
  r.add_button_row("D")

thems_fighting_herds = Game(name="Them's Fighting Herds", 
                       code="tfh",
                       renderer=pony_renderer)


games = [guilty_gear_xrd,
         thems_fighting_herds]