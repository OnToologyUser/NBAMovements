from github import Github
import os

username = albaizq  
password = albita1993
g = Github(username, password)

for repo in g.get_user().get_repos():
    print repo.name
