from pygithub3 import Github

username = raw_input("Please enter a Github username: ")
password = raw_input("Please enter the account password: ")

gh = Github(login=username, password = password)

get_user = gh.users.get()

user_repos = gh.repos.list().all()

for repo in user_repos:
    print repo.language
