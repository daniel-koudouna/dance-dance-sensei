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
