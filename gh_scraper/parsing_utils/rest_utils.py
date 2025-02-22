from path import Path
import os
import json
import time
import pdb
import requests
import requests
from bs4 import BeautifulSoup

def get_request_data(url):
    response = requests.get(url)

    if response.status_code == 200:
        repositories_data = response.json()
        return repositories_data
    else:
        return None

def get_user_bio(username):
    url = f"https://api.github.com/users/{username}"
    return get_request_data(url)

def get_user_repos(username):
    url = f"https://api.github.com/users/{username}/repos"
    repos = get_request_data(url)
    return [repo["name"] for repo in repos] if repos else []

def get_user_orgs(username):
    url = f"https://api.github.com/users/{username}/orgs"
    orgs = get_request_data(url)
    return [org["login"] for org in orgs] if orgs else []

def get_user_contributions(username):
    url = f"https://api.github.com/users/{username}/contributions"
    return get_request_data(url)
    
def get_user_followers(username):
    url = f"https://api.github.com/users/{username}/followers"
    result = get_request_data(url)
    return [follower['login'] for follower in result] if result else []

def in_commiters(owner, repo, gh_username):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    res = get_request_data(url)
    if res is None:
        print('res is None')
        return False
    commits  = [a for a in res if a['committer']['login'] == gh_username]
    return False if len(commits) == 0 else True
 

def get_pinned(gh_username):
    url = f"https://github.com/{gh_username}"

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    pinned_repos = soup.find_all("span", class_="repo")
    return  pinned_repos