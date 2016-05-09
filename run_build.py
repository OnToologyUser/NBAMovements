from github import Github

g = Github("albaizq", "albita1993")

for repo in g.get_user().get_repos():
    print repo.name
