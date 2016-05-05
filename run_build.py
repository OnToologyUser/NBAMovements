import os
from github import Github

def init_g():
  global g
  username = os.environ['github_username']
  password = os.environ['github_password']
  g = Github(username, password)
  print g
  
if __name__ == "__main__":
  init_g()
