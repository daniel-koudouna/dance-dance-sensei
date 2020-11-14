import hashlib
import json
import os
import threading
import toml
import requests

from utils import *
from typing import Callable, List, Any

def async_post(url, payload, cb : Callable[[dict], Any]):
  def callback():
    try:
      response = requests.post(url, json=payload)
      data = response.json()
      status = response.status_code
      if status != 200:
        print(f"Fetching URL {url} got status code {status}")
        print(data)
      cb(data)
    except requests.ConnectionError as errc:
      print("Connection error")
      print(errc)

  threading.Thread(target=callback, args=()).start()

def async_get(url, cb : Callable[[dict], Any]):
  def callback():
    try:
      response = requests.get(url)
      data = response.json()
      status = response.status_code
      if status != 200:
        print(f"Fetching URL {url} got status code {status}")
        print(data)
      cb(data)
    except requests.ConnectionError as errc:
      print("Connection error")
      print(errc)

  threading.Thread(target=callback, args=()).start()
  
def sync_get(url):
  try:
    response = requests.get(url)
    data = response.json()
    status = response.status_code
    if status != 200:
      print(f"Fetching URL {url} got status code {status}")
      print(data)
    return (data, status)
  except requests.ConnectionError as errc:
    print("Connection error")
    print(errc)
    return (None, 400)
  except json.decoder.JSONDecodeError as errj:
    print("No JSON returned from the server")
    print(errj)
    return (None, 400)


class Network(object):
  def __init__(self, state):
    super().__init__()
    self.state = state
    self.url = state.config['network']['url']
    self.token = None
    if 'token' in state.config['network']:
      self.token = state.config['network']['token']
    self.user = None

    if self.token is not None:
      def cb(res):
        self.user = res['user']

      async_get(f"{self.url}/user/{self.token}", cb)


  def login(self, username : str, password : str, callback : Callable[[dict], Any]):
    async_post(f"{self.url}/login", {"username":username, "password":password}, callback)

  def register(self, username : str, password : str, callback : Callable[[dict], Any]):
    async_post(f"{self.url}/register", {"username":username, "password":password}, callback)


  def remote_files(self, baseurl, user, code, seq_path, tag):
    result = []
    res, status = sync_get(f"{baseurl}/sequences/{user}")

    if res is None:
      ## Something went wrong
      self.state.refresh((tag, f"Could not get data for {user} from remote!"))
      return None

    self.state.refresh((tag, f"Got data for {user} from remote!"))
    result = [s for s in res['sequences'] if s['game'] == code]
    for r in result:
      folder = r['folder']
      if not folder.endswith('/'):
        folder = folder + '/'
      if not folder.startswith('/'):
        folder = '/' + folder

      filename = r['name']

      r['path'] = f"{seq_path}/{code}/{user}{folder}{filename}"

    return result

  def download(self):
    ##if self.user is None:
    ##  return
    
    ## TODO for all modes!
    mode = self.state.mode

    print(self.state.config['network']['following'])

    for u in self.state.config['network']['following']:
      rootpath = f"{mode.sequences}/{u}"

      on_local = local_files(rootpath, mode.code)
      on_server = self.remote_files(self.url, u, mode.code, "sequence", "download")
      if on_server is not None:
        self.sync_to_local(on_local, on_server)
    
    self.state.window.reload_context_menu()

  def sync_to_local(self, local, remote):
    hash_matches = []
    not_in_local = []
    old_in_local = []
    if len(remote) == 0:
      self.state.refresh(("download", f"\tThere were no sequences for the current mode."))

    for r in remote:
      found = False
      for l in local:
        if r['data_hash'] == l['data_hash']:
          found = True
          hash_matches.append((l, r))
          break
      if not found:
        not_in_local.append(r)  

    for l in local:
      found = False
      for r in remote:
        if r['data_hash'] == l['data_hash']:
          found = True

      if not found:
        old_in_local.append(l)

    for l, r in hash_matches:
      dirname, _fname = os.path.split(r['path'])
      os.makedirs(dirname, exist_ok=True)
      if l['path'] == r['path']:
        self.state.refresh(("download", f"\tLocal sequence {l['name']} is up to date."))
      else:
        self.state.refresh(("download", f"\tRenaming local sequence {l['name']} to {r['path']}."))
        os.rename(l['path'], r['path'])

    for s in old_in_local:
      self.state.refresh(("download", f"\tDeleting local sequence with name {s['name']}"))
      os.remove(s['path'])

    for s in not_in_local:
      self.state.refresh(("download", f"\tCreating new sequence with name {s['name']}"))
      dirname, _fname = os.path.split(s['path'])
      os.makedirs(dirname, exist_ok=True)
      open(s['path'],"w").write(s['data'])

    ##TODO remote empty directories

  def upload(self, filter):
    if self.user is None:
      return

    ## TODO for all modes!
    mode = self.state.mode
    rootpath = f"{mode.sequences}/personal"

    on_local = local_files(rootpath, mode.code)
    on_server = self.remote_files(self.url, self.user['username'], mode.code, "sequence", "upload")
    self.sync_to_remote(on_local, on_server, f"{self.url}/{self.user['token']}/sequences", filter)



  def sync_to_remote(self, local, remote, endpoint, filter):
    for_deletion = []
    for s in remote:
      in_local = False
      for l in local:
        if l['data_hash'] == s['data_hash']:
          in_local = True
      if not in_local:
        for_deletion.append(s)

    for seq in local:
      if filter == None or seq['path'] in filter:
        self.state.refresh(("upload", f"Posting sequence with name {seq['name']}"))
        try:
          r = requests.post(endpoint, json=seq)
          if r.status_code == 200:
            self.state.refresh(("upload", f"Uploaded sequence {seq['name']} successfully."))
          else:
            self.state.refresh(("upload", f"Uploaded sequence {seq['name']} with return code {r.status_code}."))
        except requests.ConnectionError as errc:
          self.state.refresh(("upload", f"Communication error occured.\n {errc}\n"))

    for seq in for_deletion:
      self.state.refresh(("upload", f"Deleting sequence with name: {seq['name']}"))
      try:
        r = requests.delete(endpoint + f"/{seq['id']}")
        if r.status_code == 200:
          self.state.refresh(("upload", f"Deleted sequence {seq['name']} successfully.\n"))
        else:
          self.state.refresh(("upload", f"Deleted sequence {seq['name']} with return code {r.status_code}.\n"))
      except requests.ConnectionError as errc:
        self.state.refresh(("upload", f"Communication error occured.\n {errc}\n"))