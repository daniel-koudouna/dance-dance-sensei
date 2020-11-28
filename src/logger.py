from datetime import datetime


FILENAME = "log.txt"

class Log:
  def debug(s):
    print(s)
    today = datetime.now()
    fname = today.strftime("%Y_%m_%d_%H_%M_%S")
    open(FILENAME, "a+").write(f"[{fname}]\t{s}\n")