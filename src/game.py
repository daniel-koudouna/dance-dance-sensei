from typing import List, Tuple

class Game(object):
  def __init__(self, **kwargs):
    self.name = kwargs["name"]
    self.code = kwargs["code"]
    self.visuals = f"img/{self.code}"
    self.sequences = f"sequence/{self.code}"
    self.mappings = f"mappings/{self.code}.csv"
    self.motions = kwargs["motions"]
    self.charge_motions = kwargs["charge_motions"]
    self.renderer = kwargs["renderer"]
    self.buttons = kwargs["buttons"]
    self.action_buttons = [b for b in kwargs['buttons']]
    self.buttons.insert(0, "Movement")
    self.buttons.insert(1, "Up")
    self.buttons.insert(2, "Down")
    self.buttons.insert(3, "Left")
    self.buttons.insert(4, "Right")
    self.buttons.append("Play")
    self.buttons.append("Record")



def guilty_gear_renderer(r):
  r.add_direction_row("Movement")
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

def guilty_gear_plusr_motions():
  return augment([
    ("214", "214"),
    ("236", "236"), 
    ("623", "623"), 
    ("6236", "623"),
    ("41236", "41236"),
  ])

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
                       buttons=["P", "K", "S", "H", "D"],
                       motions=guilty_gear_motions(),
                       charge_motions=guilty_gear_charge(),
                       renderer=guilty_gear_renderer)
                      
guilty_gear_strive = Game(name="Guilty Gear Strive",
                          code="ggst",
                          buttons=["P", "K", "S", "H", "D"],
                          motions=guilty_gear_motions(),
                          charge_motions=guilty_gear_charge(),
                          renderer=guilty_gear_renderer)

guilty_gear_plusr = Game(name="Guilty Gear AC+R", 
                       code="plusr",
                       buttons=["P", "K", "S", "H", "D"],
                       motions=guilty_gear_plusr_motions(),
                       charge_motions=guilty_gear_charge(),
                       renderer=guilty_gear_renderer)

def uni_renderer(r):
  r.add_direction_row("Movement")
  r.add_button_row("A")
  r.add_button_row("B")
  r.add_button_row("C")
  r.add_button_row("D")

def uni_motions():
  return augment([
    ("214", "214"),
    ("236", "236"), 
    ("623", "623"), 
    ("3236", "623"),
    ("41236", "41236"),
    ## 360
    ("632147", "62486"),
    ("6321478", "62486"),
    ("63214789", "62486"),
    ("632147896", "62486"),
    ("321478963", "62486"),
    ("214789632", "62486"),
    ("147896321", "62486"),
    ("478963214", "62486"),
    ("789632147", "62486"),
    ("896321478", "62486"),
    ("963214789", "62486"),
    ## 720
    ("62486247", "62486247"),
  ])

uni = Game(name="Under Night In-Birth",
           code="uni",
           buttons=["A","B","C","D"],
           motions=uni_motions(),
           charge_motions=guilty_gear_charge(),
           renderer=uni_renderer)

def sg_motions():
  return augment([
    ("214", "214"),
    ("236", "236"), 
    ("623", "623"), 
    ("63214789", "63214789")
  ])

def sg_renderer(r):
  r.add_direction_row("Movement")
  r.add_button_row("LP")
  r.add_button_row("LK")
  r.add_button_row("MP")
  r.add_button_row("MK")
  r.add_button_row("HP")
  r.add_button_row("HK")

def kof_renderer(r):
  r.add_direction_row("Movement")
  r.add_button_row("LP")
  r.add_button_row("LK")
  r.add_button_row("HP")
  r.add_button_row("HK")

skullgirls = Game(name="Skullgirls",
           code="skullgirls",
           buttons=["LP","MP","HP","LK", "MK", "HK"],
           motions=sg_motions(),
           charge_motions=guilty_gear_charge(),
           renderer=sg_renderer)

kof_13 = Game(name="King of Fighters XIII",
              code="kof13",
              buttons=["LP", "HP", "LK", "HK"],
              motions=sg_motions,
              charge_motions=guilty_gear_charge(),
              renderer=kof_renderer)

kof_2kum = Game(name="King of Fighters 2003 UM",
              code="kof2kum",
              buttons=["LP", "HP", "LK", "HK"],
              motions=sg_motions,
              charge_motions=guilty_gear_charge(),
              renderer=kof_renderer)

hisoutensoku = Game(name="Touhou 12.3 Hisoutensoku",
              code = "hisoutensoku",
              buttons=["A","B","C","D"],
              motions=sg_motions(),
              charge_motions=guilty_gear_charge(),
              renderer=uni_renderer)

blazblue_cf = Game(name="BlazBlue Centralfiction",
                   code="bbcf",
                   buttons=["A","B","C","D"],
                   motions=uni_motions(),
                   charge_motions=guilty_gear_charge(),
                   renderer=uni_renderer)

games = [guilty_gear_xrd,
         guilty_gear_plusr,
         guilty_gear_strive,
         blazblue_cf,
         uni,
         kof_13,
         kof_2kum,
         skullgirls,
         hisoutensoku]