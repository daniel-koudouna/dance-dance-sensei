import time
import winsound


def average_bpm(times):
  """ For the list of times(seconds since epoch) return
      the average beats per minute.
  """
  spaces = []
  previous = times[0]
  for t in times[1:]:
      spaces.append(t - previous)
      previous = t
  avg_space = sum(spaces) / len(spaces)
  return 60.0 / avg_space

class AudioManager:

  def __init__(self, soundfile, hitfile, initial_bpm, first_frame):
    self.soundfile = soundfile
    self.hitfile = hitfile
    self.space_between_beats = 0.5
    self.last_press = time.time()
    """ The time since epoch of the last press.
    """
    self.bpm = initial_bpm
    self.bpm_average = initial_bpm
    """ The average bpm from the last 4 presses.
    """

    self.start_time = time.time()

    self.times = []

    self.delay_time = first_frame / 60.0

    print(f"Delay time is {self.delay_time}")

    self._last_update = time.time()
    self._elapsed_time = 0.0
    self._last_closeness = 1.0

    self.on_beat = 0
    """ The time since the epoch when the last beat happened.
    """

    self.beat_num = 0
    """ accumlative counter of beats.
    """

    self.finished_beat = 0
    """ True for one tick, when 0.1 seconds has passed since the beat.
    """

    self.first_beat = 0
    """ True if we are the first beat on a bar (out of 4).
    """

    self.started_beat = 0
    """ This is true only on the tick
    """


  def press(self):
    """ For when someone is trying to update the timer.
    """
    press_time = time.time()
    self.space_between_beats = press_time - self.last_press
    self.last_press = press_time
    self.times.append(press_time)
    self.bpm = 60.0 / self.space_between_beats

    if len(self.times) > 4:
        self.bpm_average = average_bpm(self.times[-4:])
        self.times = self.times[-4:]
    else:
        self.bpm_average = self.bpm


  def update(self, should_play, should_hit):
    the_time = time.time()
    delta_time = the_time - self._last_update

    self.delay_time -= delta_time

    self._last_update = the_time

    if self.delay_time > 0:
      ## print(self.delay_time)
      return


    self._elapsed_time += delta_time

    # if _elapsed_time 'close' to bpm show light.
    space_between_beats = 60.0 / self.bpm_average
    since_last_beat = the_time - self.on_beat

    self.finished_beat = self.on_beat and (since_last_beat > 0.1)
    if self.finished_beat:
      self.on_beat = 0

    closeness = self._elapsed_time % space_between_beats
    if closeness < self._last_closeness:
      self.on_beat = the_time
      self.finished_beat = 0
      self.dirty = 1
      self.beat_num += 1
      self.started_beat = 1
      self.first_beat = not (self.beat_num % 4)
    else:
      self.started_beat = 0

    self._last_closeness = closeness

    if self.started_beat == 1 and should_play:
      winsound.PlaySound(self.soundfile, winsound.SND_ASYNC)

    if should_hit:
      winsound.PlaySound(self.hitfile, winsound.SND_ASYNC)
