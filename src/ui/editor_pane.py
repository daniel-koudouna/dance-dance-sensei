import os
import toml
import ttkwidgets
import tkinter as tk
from tkinter import ttk
from renderable import ButtonInput

from sequence import Sequence

class EditorPane(ttk.Frame):
  def __init__(self, master, state, **kw):
    super().__init__(master=master, **kw)

    self.state = state
    self.selected_file = tk.StringVar("")
    self.selected_file.trace('w', self.reload)
    self.sequence = []
    self.sub_sequences = []
    self.var_filename = tk.StringVar("")
    self.var_bpm = tk.IntVar(value=50)

    r = 0

    self.tree = ttk.Treeview(self)
    self.tree.grid(row=r,column=0,padx=10, pady=10, rowspan=3, columnspan=3, sticky="news")

    self.tree.bind("<<TreeviewSelect>>", self.maybe_update)

    canvas = tk.Canvas(self)
    canvas.grid(row=r, column=3, padx=10, pady=10, rowspan=5, columnspan=9, sticky="news")

    scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
    scrollbar.grid(row=r, column=15, padx=0, pady=10, rowspan=5, sticky="nsw")
    self.subframe = ttk.Frame(canvas)

    self.subframe.bind(
      "<Configure>",
      lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=self.subframe, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)



    r += 3

    ll = ttk.Label(self, text="Enter filename for exporting:")
    ll.grid(row=r, column=0, padx=10, pady=10, sticky="w")

    r += 1

    ll = ttk.Entry(self, textvariable=self.var_filename)
    ll.grid(row=r, column=0, padx=10, pady=10, columnspan=3, sticky="ew")
     
    r +=1

    ll = ttk.Label(self, text="Enter BPM:")
    ll.grid(row=r, column=0, padx=10, pady=10, sticky="w")

    r +=1

    ll = ttk.Entry(self, textvariable=self.var_bpm)
    ll.grid(row=r, column=0, padx=10, pady=10, columnspan=3, sticky="ew")
    

    self.reset()

  def reset(self):
    self.tree.delete(*self.tree.get_children())

    found_file = False
    thepath = None

    rootpath = f"{self.state.mode.sequences}/personal"
    for dirpath, dirnames, files in os.walk(rootpath):
      parent = "" if dirpath == rootpath else dirpath[dirpath.index(rootpath):].replace("\\","/")
      for d in dirnames:
        self.tree.insert(parent, "end", f"{dirpath}/{d}", text=d)
      for f in files:
        iid = self.tree.insert(parent, "end", f"{dirpath}/{f}", text=f)
        if not found_file:
          found_file = True
          thepath = iid

    
    if found_file:
      self.tree.selection_set(thepath)

  def export(self, lines):
    fname = self.var_filename.get()
    if len(fname) > 0:
      filename = f"{self.state.mode.sequences}/personal/{fname}.txt"
      os.makedirs(f"{self.state.mode.sequences}/personal", exist_ok=True)
      if not os.path.exists(filename):
        handle = open(filename, "w")
        lines_to_write = ["# bpm: " + str(self.var_bpm.get()) + "\n"]
        lines_to_write.extend(lines)
        handle.writelines(lines_to_write)
        self.var_filename.set("")
        self.reset() 

  def maybe_update(self, event):
    print(self.tree.selection())
    self.selected_file.set(self.tree.selection()[0])

  def play_seq(self, seq):
    bpm = self.var_bpm.get()
    seq.bpm = bpm
    self.state.set_sequence(seq)

  def fit_bpm(self, seq):
    frames = [o.frame for o in seq.objects if isinstance(o,ButtonInput)]
    start = frames[0]
    frames = [f - start for f in frames]
    diffs = []
    for i in range(len(frames) - 1):
      d = frames[i + 1] - frames[i]
      if d > 2:
        diffs.append(d)
    print(diffs)
    self.var_bpm.set(10)

  def reload(self, *args):
    lines = open(self.selected_file.get()).readlines()
    sub_seqs = []
    curr = []
    for l in lines:
      if l == 'Play\n':
        sub_seqs.append(curr)
        curr = []
      else:
        curr.append(l)
    sub_seqs.append(curr)

    sub_seqs = [li for li in sub_seqs if len(li) > 10]
    self.parsed_sequence = Sequence(lines, self.state.mappings, self.state.mode)
    self.sub_sequences = [Sequence(li, self.state.mappings, self.state.mode) for li in sub_seqs]
    self.sub_sequences = [s for s in self.sub_sequences if s.duration() > 0]

    print(f"Found {len(self.sub_sequences)} sequences")

    print(self.parsed_sequence.objects)
    for child in self.subframe.winfo_children():
      child.destroy()

    for i, ss in enumerate(self.sub_sequences):
      ll = ttk.Label(self.subframe, text=f"Attempt #{i+1}, {ss.duration()} frames" )
      ll.grid(row=i, column=0, padx=5, pady=10, sticky="w")

      ll = ttk.Button(self.subframe, text="Play", command= lambda seq=ss: self.play_seq(seq))
      ll.grid(row=i, column=1, padx=5, pady=10, sticky="w")

      ll = ttk.Button(self.subframe, text="Fit BPM", command= lambda seq=ss: self.fit_bpm(seq))
      ll.grid(row=i, column=2, padx=5, pady=10, sticky="w")

      ll = ttk.Button(self.subframe, text="Export", command= lambda seq=ss: self.export(seq.lines))
      ll.grid(row=i, column=3, padx=5, pady=10, sticky="w")
