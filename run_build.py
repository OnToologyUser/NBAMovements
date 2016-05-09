from pygithub3 import Github

username = "albaizq"
password = "albita1993"

gh = Github(login=username, password = password)

get_user = gh.users.get()

user_repos = gh.repos.list().all()

for repo in user_repos:
    print repo.language
