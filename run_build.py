from github import Github
import os

username = os.environ['github_username']
password = os.environ['github_password']
g = Github(username, password)

for repo in g.get_user().get_repos():
    print repo.name
