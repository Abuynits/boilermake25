from parsing_utils.rest_utils import *
import parsing_utils.bs_utils as bs_utils
import os
import json
import time
import numpy as np
import pdb
SAVE_FOLLOWER=False
SAVE_ORG=True


data_name = 'example_res.json'
resume_file = Path(__file__).parent / 'data' / f'{data_name}'

if not os.path.exists(resume_file):
    print(f"error: file {resume_file} DNE")
    exit(1)


with open(resume_file) as f:
      data = json.load(f)
# gh_username = data['contact']['github'].split('/')[-1]
gh_username = 'SpideR1sh1'

# user_bio_info = get_user_bio(gh_username)
# if not user_bio_info:
#     print(f"error: user {gh_username} not found!")

user_orgs = get_user_orgs(gh_username)
# user_orgs = ['MEHDesignClass', 'apc-mhs', 'Hack-the-Future', 'HelloWorldHackathon', 'TheDataScienceLabs']

user_followers = bs_utils.extract_user_followers(gh_username)
# user_followers = ['amogh-orolabs-dev', 'youngjun-yoo16', 'sagarreddypatil', 'qi116', 'harmya', 'laureanray', 'theopn', 'jinensetpal', 'Jaimss', 'JLH973', 'vsingh25', 'ScriptedButton', 'parmesean-pixel', 'RohanVSuri', 'DannyOppenheimer', 'AndrewLester', '0x7B5', 'pauloca', 'ErikBoesen']

all_user_repos = []
file_paths = []
for repo in bs_utils.extract_repo_from_gh_user(gh_username):
    commits = bs_utils.filter_commits_by_user_in_repo(gh_username, repo, gh_username) 
    if len(commits) == 0:
        continue
    all_user_repos.append((gh_username, repo, commits))
    file_paths.append([f'{gh_username}/{repo}','usr', len(commits)])
    print(f"Adding {gh_username}/{repo} with {len(commits)}")
added_other_users = 0

if SAVE_FOLLOWER:
    for other_user in set(user_followers):
        other_repos = bs_utils.extract_repo_from_gh_user(other_user)
        for other_repo in set(other_repos):
            print(f"checking: {other_user}/{other_repo}")
            commits = bs_utils.filter_commits_by_user_in_repo(other_user, other_repo, gh_username)
            if len(commits) == 0:
                continue
            all_user_repos.append((other_user, other_repo, commits))
            file_paths.append([f'{other_user}/{other_repo}','usr', len(commits)])
            print(f"Adding {other_user}/{other_repo} with {len(commits)}")
            added_other_users += 1

if SAVE_ORG:
    added_orgs= 0
    for org in set(user_orgs):
        other_repos = bs_utils.extract_repo_from_gh_org(org)
        for other_repo in set(other_repos):
            # print(f"checking: {org}/{other_repo}")
            commits = bs_utils.filter_commits_by_user_in_repo(org, other_repo, gh_username)
            if len(commits) == 0:
                continue
            added_orgs += 1
            all_user_repos.append((org, other_repo, commits))
            file_paths.append([f'{org}/{other_repo}','org', len(commits)])
            print(f"Adding {org}/{other_repo} with {len(commits)}")
    print(f"Found total of {len(all_user_repos)}, {added_orgs} repos from orgs, {added_other_users} from other userrs")
    save = np.array(file_paths)
    np.save(Path(__file__).parent / 'data' / 'user_repo', save)