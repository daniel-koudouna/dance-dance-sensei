import hashlib
import os
import toml
import requests

from utils import *


class Network(object):
  def __init__(self, state):
    super().__init__()
    self.state = state
    self.url = state.config['network']['url']
    self.token = state.config['network']['token']
    self.user = None

    if self.token is not None:
      try:
        r = requests.get(f"{self.url}/user/{self.token}")
        res = r.json()
        if res is None:
          ## Wrong token
          pass
        else:
          self.user = res['user']
          print("Retrieved user from network")
          print(self.user)
      except requests.ConnectionError as errc:
        print("Connection error")
        pass


  def login(self, username : str, password : str):
    r= requests.post(self.url + "/login", json={"username":username, "password":password})
    res = r.json()
    if res is None:
      return False
    else:
      print(res)
      self.user = res
      self.state.config['network']['token'] = res['token']
      toml.dump(self.state.config, open("config.toml", "w"))
      return True


  def download(self):
    if self.user is None:
      return
    
    ## TODO for all modes!
    mode = self.state.mode

    print(self.state.config['network']['following'])

    for u in self.state.config['network']['following']:
      rootpath = f"{mode.sequences}/{u}"

      on_local = local_files(rootpath, mode.code)
      on_server = remote_files(self.url, u, mode.code, "sequence")
      if on_server is not None:
        sync_to_local(on_local, on_server)
    
    self.state.window.reload_context_menu()

  def upload(self):
    if self.user is None:
      return

    ## TODO for all modes!
    mode = self.state.mode
    rootpath = f"{mode.sequences}/personal"

    on_local = local_files(rootpath, mode.code)
    on_server = remote_files(self.url, self.user['username'], mode.code, "sequence")
    sync_to_remote(on_local, on_server, f"{self.url}/{self.user['token']}/sequences")
