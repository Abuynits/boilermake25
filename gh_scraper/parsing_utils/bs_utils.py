import requests
from bs4 import BeautifulSoup

def filter_commits_by_user_in_repo(owner, repo, user):
    # url = f"https://github.com/PurdueRCAC/DatasetDocs/commits?author=JonathanOppenheimer"
    url = f"https://github.com/{owner}/{repo}/commits?author={user}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    # <h4 class="markdown-title Title-module__heading--upUxW CommitRow-module__ListItemTitle_0--g9uVv"><span class="Text__StyledText-sc-17v1xeu-0 hWqAbU TitleHeader-module__inline--rL27T Title-module__anchor--SyQM6 Title-module__markdown--KiFgL"><a data-pjax="true" title="edit output file directory" class="color-fg-default" href="/PurdueRCAC/DatasetDocs/commit/12022e4c5e5e518dcdc8f20648e34fda2fe886a2" tabindex="-1">edit output file directory</a></span></h4>
    followers = soup.find_all("span", class_="Text__StyledText-sc-17v1xeu-0 hWqAbU TitleHeader-module__inline--rL27T Title-module__anchor--SyQM6 Title-module__markdown--KiFgL")
    user_commits = [follower.text.strip() for follower in followers]
    return user_commits

def extract_user_followers(user):
    url = f"https://github.com/{user}?tab=followers"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    followers = soup.find_all("span", class_="Link--secondary pl-1")
    follower_usernames = [follower.text.strip() for follower in followers]
    return follower_usernames

def extract_repo_from_gh_user(user):
    url = f"https://github.com/{user}?tab=repositories"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    # <a href="/JonathanOppenheimer/github-stats" itemprop="name codeRepository">github-stats</a>
    repos = soup.find_all("a", itemprop="name codeRepository")
    user_repos = [repos[i].__dict__['attrs']['href'] for i in range(len(repos))]
    repos = [repo.split('/')[-1] for repo in user_repos]
    return repos
def extract_repo_from_gh_org(org):
    url = f"https://github.com/orgs/{org}/repositories"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    repos = soup.find_all("span", class_="Text__StyledText-sc-17v1xeu-0 hWqAbU")

    repos = [repo.text.strip() for repo in repos]
    return repos
def extract_desc_from_repo(user, repo):
    # https://github.com/jinensetpal/boilerbot
    url = f"https://github.com/{user}/{repo}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    desc = soup.find_all("p", class_="f4 my-3")
    return None if len(desc) == 0 else desc[0].text.strip()

def extract_files_from_gh(user, repo):
    def extract_files_from_dir(user,repo, path):
        # https://github.com/CoMMALab/mpinets/tree/main/mpinets
        url = f"https://github.com/{user}/{repo}/tree/main/{path}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        desc = soup.find_all("a", class_="Link--primary")
        files = [f'{path}/{d.text}' for d in desc if d.get('aria-label') is not None and 'Directory' not in d.get('aria-label')]
        dirs = [d.text for d in desc if d.get('aria-label') is not None and 'Directory' in d.get('aria-label')]
        for dir in dirs:
            files += extract_files_from_dir(user, repo, f"{path}/{dir}")
        return files
    # https://github.com/jinensetpal/boilerbot
    # <a title="ssvqe.py" aria-label="ssvqe.py, (File)" class="Link--primary" href="/SpideR1sh1/Variational-Quantum-Eigensolver/blob/main/ssvqe.py">ssvqe.py</a>
    # <a title="docker" aria-label="docker, (Directory)" class="Link--primary" href="/CoMMALab/mpinets/tree/main/docker">docker</a>
    # <a title="neural_cc" aria-label="neural_cc, (Directory)" class="Link--primary" href="/CoMMALab/mpinets/tree/main/mpinets/neural_cc">neural_cc</a>
    url = f"https://github.com/{user}/{repo}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    desc = soup.find_all("a", class_="Link--primary")
    files = [d.text for d in desc if d.get('aria-label') is not None and 'Directory' not in d.get('aria-label')]
    dirs = [d.text for d in desc if d.get('aria-label') is not None and 'Directory' in d.get('aria-label')]
    for tgt_dir in dirs:
        files += extract_files_from_dir(user,repo, tgt_dir)
    return files 
