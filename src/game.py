from typing import List, Tuple

class Game(object):
  def __init__(self, **kwargs):
    self.name = kwargs["name"]
    self.code = kwargs["code"]
    self.visuals = f"img/{self.code}"
    self.sequences = f"sequence/{self.code}"
    self.mappings = f"mappings/{self.code}"
    self.motions = kwargs["motions"]
    self.charge_motions = kwargs["charge_motions"]
    self.renderer = kwargs["renderer"]


def guilty_gear_renderer(r):
  r.add_direction_row("M")
  r.add_button_row("P")
  r.add_button_row("K")
  r.add_button_row("S")
  r.add_button_row("H")
  r.add_button_row("D")

def flip(motion : str) -> str:
  result = list(motion)
  for i in range(len(result)):
    if result[i] == '1':
      result[i] = '3'
    elif result[i] == '3':
      result[i] = '1'
    elif result[i] == '4':
      result[i] = '6'
    elif result[i] == '6':
      result[i] = '4'
    elif result[i] == '7':
      result[i] = '9'
    elif result[i] == '9':
      result[i] = '7'
  
  return "".join(result)

def augment(arr : List[Tuple[str, str]]) -> List[Tuple[str, str]]:
  res = []
  res.extend(arr)
  res.extend([(flip(motion), flip(name)) for motion, name in arr])
  return res

def guilty_gear_motions():
  return augment([
    ("214", "214"),
    ("236", "236"), 
    ("623", "623"), 
    ("6236", "623"),
    ("41236", "41236"),
    ("4136", "41236")
  ])

def guilty_gear_charge():
  return [
    ("46", "46"),
    ("16", "46"), 

    ("64", "64"),
    ("34", "64"), 

    ("28", "28"),
    ("18", "28"),
    ("38", "28")
  ]

guilty_gear_xrd = Game(name="Guilty Gear Xrd", 
                       code="xrd",
                       motions=guilty_gear_motions(),
                       charge_motions=guilty_gear_charge(),
                       renderer=guilty_gear_renderer)


def pony_renderer(r):
  r.add_direction_row("M")
  r.add_button_row("A")
  r.add_button_row("B")
  r.add_button_row("C")
  r.add_button_row("D")

thems_fighting_herds = Game(name="Them's Fighting Herds", 
                       code="tfh",
                       motions=[],
                       charge_motions=[],
                       renderer=pony_renderer)


games = [guilty_gear_xrd,
         thems_fighting_herds]