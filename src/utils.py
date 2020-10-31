import requests
import hashlib
import os

def first(lst, fn):
  for l in lst:
    if fn(l):
      return l
  return None

def to_server_path(root, path):
  return path[len(root):].replace("\\","/")

def remote_files(baseurl, user, code, seq_path):
  result = []
  r = requests.get(f"{baseurl}/sequences/{user}")
  res = r.json()
  if res is None:
    ## Something went wrong
    return None

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

def local_files(directory, code):
  result = []
  for dirpath, dirnames, files in os.walk(directory):
    for f in files:
      res = {}
      res['name'] = f
      res['folder'] = to_server_path(directory, dirpath)
      res['path'] = f"{dirpath}/{f}"
      res['data'] = open(res['path'], "r").read()
      res['game'] = code
      m = hashlib.md5()
      m.update(res['data'].encode("utf-8"))
      res['data_hash'] = m.hexdigest()

      existing_element = first(result, lambda r: r['data_hash'] == res['data_hash'])
      if existing_element is None:
        result.append(res)
  
  return result


def sync_to_local(local, remote):
  hash_matches = []
  not_in_local = []
  old_in_local = []
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
    print(f"Renaming local sequence with name {l['name']}")
    dirname, _fname = os.path.split(r['path'])
    os.makedirs(dirname, exist_ok=True)
    os.rename(l['path'], r['path'])

  for s in old_in_local:
    print(f"Deleting local sequence with name {s['name']}")
    os.remove(s['path'])
  
  for s in not_in_local:
    print(f"Creating new sequence with name {s['name']}")
    dirname, _fname = os.path.split(s['path'])
    os.makedirs(dirname, exist_ok=True)
    open(s['path'],"w").write(s['data'])
  
  ##TODO remote empty directories

def sync_to_remote(local, remote, endpoint):
  for_deletion = []
  for s in remote:
    in_local = False
    for l in local:
      if l['data_hash'] == s['data_hash']:
        in_local = True
    if not in_local:
      for_deletion.append(s)

  for seq in local:
    print(f"Posting sequence with name {seq['name']}")
    r= requests.post(endpoint, json=seq)
    if r.status_code != 200:
      print(r)
      print(r.status_code)
      res = r.json()
      print(res)

  for seq in for_deletion:
    print(f"Deleting sequence with name: {seq['name']}")
    r = requests.delete(endpoint + f"/{seq['id']}")
    if r.status_code != 200:
      print(r)
      print(r.status_code)
      res = r.json()
      print(res)