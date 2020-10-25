import hashlib
import os
import toml
import requests


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


  def login(self, username, password):
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

    def to_server_path(root, path):
      return path[len(root):].replace("\\","/")

    print(self.state.config['network']['following'])

    for u in self.state.config['network']['following']:
      rootpath = f"{mode.sequences}/{u}"

      ## TODO REFACTOR THIS
      on_local = []
      for dirpath, dirnames, files in os.walk(rootpath):
        for f in files:
          res = {}
          res['name'] = f
          res['folder'] = to_server_path(rootpath, dirpath)
          res['data'] = open(f"{dirpath}/{f}", "r").read()
          res['game'] = mode.code
          m = hashlib.md5()
          m.update(res['data'].encode("utf-8"))
          res['data_hash'] = m.hexdigest()
          on_local.append(res)

      on_server = []
      ## TODO THIS IS DIFFERENT
      r = requests.get(f"{self.url}/sequences/{u}")
      res = r.json()
      if res is None:
        ## Something went wrong
        pass
      else:
        on_server = res['sequences']

      for new_file in on_server:
        folder = new_file['folder']
        if not folder.endswith('/'):
          folder = folder + '/'
        if not folder.startswith('/'):
          folder = '/' + folder
        
        full_folder = f"{mode.sequences}/{u}{folder}"
        os.makedirs(full_folder, exist_ok=True)
        filename = f"{full_folder}{new_file['name']}"
        open(filename,"w").write(new_file['data'])

  def upload(self):
    if self.user is None:
      return

    ## TODO for all modes!
    mode = self.state.mode
    rootpath = f"{mode.sequences}/personal"

    def to_server_path(root, path):
      return path[len(root):].replace("\\","/")

    on_local = []
    for dirpath, dirnames, files in os.walk(rootpath):
      for f in files:
        res = {}
        res['name'] = f
        res['folder'] = to_server_path(rootpath, dirpath)
        res['data'] = open(f"{dirpath}/{f}", "r").read()
        res['game'] = mode.code
        m = hashlib.md5()
        m.update(res['data'].encode("utf-8"))
        res['data_hash'] = m.hexdigest()
        on_local.append(res)

    on_server = []
    r = requests.get(f"{self.url}/sequences/{self.user['username']}")
    res = r.json()
    if res is None:
      ## Something went wrong
      return
    else:
      on_server = res['sequences']


    for seq in on_local:
      r= requests.post(f"{self.url}/{self.user['token']}/sequences", json=seq)
      if r.status_code != 200:
        print(r)
        print(r.status_code)
        res = r.json()
        print(res)

    for_deletion = []
    for s in on_server:
      in_local = False
      for l in on_local:
        if l['data_hash'] == s['data_hash']:
          in_local = True
      if not in_local:
        for_deletion.append(s)

    ##TODO NEED FOR ALL GAMES
    print(for_deletion)