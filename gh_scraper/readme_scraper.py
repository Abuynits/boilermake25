import numpy as np
from path import Path
import parsing_utils.bs_utils as bs_utils
import json
import os
from urllib.request import urlopen
gh_username = 'Abuynits'
data = np.load(Path(__file__).parent / 'data' / 'user_repo.npy')
readme_files = ['readme.md', 'README.md', "README.MD", "Readme.md", "ReadMe.md", "ReadMe.MD"]
for (gh_path, owner_type, commit_count) in data:
    gh_path = str(gh_path)
    owner_type = str(owner_type)
    commit_count = int(commit_count)
    print(f"Checking {gh_path} with {commit_count} commits")
    output=None
    # try to wget readme:
    for readme_file in readme_files:
        # https://raw.githubusercontent.com/jinensetpal/boilerbot/refs/heads/main/README.md
        url = f"https://raw.githubusercontent.com/{gh_path}/refs/heads/main/{readme_file}"
        try:
            output = urlopen(url).read().decode('utf-8')
            break
        except Exception as e:
            continue
    if not os.path.exists(Path(__file__).parent / 'data' / gh_username):
        os.mkdir(Path(__file__).parent / 'data' / gh_username)

    repo_name = gh_path.split('/')[-1]
    repo_owner = gh_path.split('/')[0]
    
    description = bs_utils.extract_desc_from_repo(repo_owner, repo_name)
    prev_commits = bs_utils.filter_commits_by_user_in_repo(repo_owner, repo_name, gh_username)
    data = {
        'description': description,
        'readme': output,
        'prev_commits': prev_commits,
        'title': repo_name,
        'owner': repo_owner,
        'commits': commit_count
    }
    json_path = Path(__file__).parent / 'data' / gh_username / f'{repo_name}.json'
    with open(json_path, 'w') as f:
        json.dump(data, f)