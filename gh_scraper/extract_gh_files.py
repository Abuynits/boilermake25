import numpy as np
from path import Path
from .parsing_utils import bs_utils
import json
import os
from openai import OpenAI
import openai
import time
from urllib.request import urlopen
from repo_llm_context import repo_url_to_context, repo_url_to_commits
data_name = 'example_res.json'

api_key = os.environ.get("OPENAI_API_KEY")
openai.api_key = api_key
client = OpenAI()
gh_username = "SpideR1sh1"
resume_file = Path(__file__).parent / 'data' / f'{data_name}'
with open(resume_file, 'r') as file:
    resume_data = json.load(file)

if not os.path.exists(resume_file):
    print(f"error: file {resume_file} DNE")
    exit(1)

def prompt_gpt(prompt, sys_prompt):

    # Replace with your OpenAI API key
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Adjust based on the available model
        messages=[
            {"role": "system", "content": f"{sys_prompt}"},
            {"role": "user", "content": f"{prompt}"}
        ]
    )

    content = response.choices[0].message.content
    return content

user_path = Path(__file__).parent / 'data' / gh_username
full_prompt = ""


full_prompt += "\n\nCandidate Resume Projects:\n"
if 'projects' in resume_data:
    for i, proj in enumerate(resume_data['projects']):
        full_prompt += f"Project {i} [{proj['name']}]:\n"
        desc = '\n\t- '.join(proj['description'])
        full_prompt += f"Descrition: {desc}\n"
else:
    full_prompt += "None\n"

full_prompt += "\n\nCandidate Resume Experiences:\n"

if 'experience' in resume_data:
    for i, exp in enumerate(resume_data['experience']):
        ['responsibilities']
        full_prompt += f"Experience {i} [{exp['title']}]:\n"
        desc = '\n\t- '.join(exp['responsibilities'])
        full_prompt += f"Descrition: {desc}\n"
else:
    full_prompt += "None\n"

    

full_prompt += "\n\nCandidate Github Projects:\n"
all_repo_data = []
for i, repo_path in enumerate(os.listdir(user_path)):
    with open(user_path / repo_path, 'r') as json_file:
        repo_data = json.load(json_file)
        all_repo_data.append(repo_data)
        prompt_data = f"Project {i} [{repo_data['title']}] owned by {repo_data['owner']} with {repo_data['commits']} commits\n"
        if repo_data['description'] is not None:
            prompt_data += f"Description: {repo_data['description']}\n" 
        if repo_data['readme'] is not None:
            prompt_data += f"Readme: {repo_data['readme']}\n"
        if repo_data['prev_commits'] is not None:
            str_commits = "\n -".join(repo_data['prev_commits'])
            prompt_data += f"Prev Commits: {str_commits}\n" 
        full_prompt += f'\n{prompt_data}'
print(full_prompt)
sys_prompt =  """You are tasked with screening a candidate for a large company. 
You are provided with:
1. list of github repos they have contributed to (along with their readme, description, and previous commit messages if available)
2. list of projects the candidate has claimed to work on, their experiences.
3. list of the candidates experiences

For each project, provided the most likely github repo in the list that matches with the candidate project. Its ok to say none, as the code could be private.
Make sure that the matching repo isn't for a candaites experience.

Format your output as follows. Just answer the question (your response should start with 'resume project #1: github project # (or 'None')'):
resume project #0: github project # (or 'None')
resume project #1: github project # (or 'None')
...
"""
# resp = prompt_gpt(full_prompt, sys_prompt)
proj_gh_match = "resume project #0: github project #8\nresume project #1: github project #13\nresume project #2: github project #3"
proj_gh_match = proj_gh_match.split("\n")
proj_gh_match = [resp for resp in proj_gh_match if len(resp) > 1]

repo_scores = []

# breakpoint()
for i, resp in enumerate(proj_gh_match):
    proj_id = int(resp.split(":")[0].split("#")[-1].strip())
    gh_id = resp.split(":")[-1]
    if 'none' in gh_id.lower():
        print("no proj found")
        repo_scores.append((proj_id, 'None', 'YELLOW'))
        gh_id = -1
    else:
        gh_id = int(gh_id.split("#")[-1].strip())
        repo_scores.append((resume_data['projects'][i], all_repo_data[gh_id], 'tbd'))
    print(proj_id, ' -> ', gh_id)
    
sys_prompt_2 = """
You are given:
A project
The project's description from the candidate's resume
The git log of the candidate's contributions

*Task*:
Rate the repository's legitimacy on a scale of 1-5, where:
    1 = High likelihood of plagiarism or embellishment
    5 = Original work
Err on the side of skepticism—only assign a 4 or 5 if there is clear, consistent, and meaningful development from the candidate.

*Red Flags to Watch For*:
- Large initial commits followed by minimal contributions (suggesting bulk copy-pasting)
- Code copied from well-known sources (e.g., GitHub repositories, Stack Overflow, or open-source projects)
- Minimal meaningful code contributions (e.g., mostly modifying comments, formatting, or renaming variables)
- Inconsistent coding style (indicating possible multiple authors)
- Commits with drastic jumps in complexity (suggesting pasted code rather than iterative development)
- Sudden, short bursts of activity followed by long inactivity (suggesting last-minute additions rather than steady progress)
- Missing implementation details for complex claims in the resume

*Response Format*:
Repo #0: [rating] 
Resoning:
Repo #1: [rating]
Reasoning:
...
"""
# resp = prompt_gpt(prompt, sys_prompt_2)
all_resps = {}
# now need to iteratore through repos
for i, resp in enumerate(proj_gh_match):

    prompt = ""
    breakpoint()
    proj_data, repo_data, status = repo_scores[i]
    if status == 'tmp':
        continue
    url = f"https://github.com/{repo_data['owner']}/{repo_data['title']}.git"
    # resp = repo_url_to_context(url)
    eval = repo_url_to_commits(url, gh_username)
    prompt += f"**Repo #{i}**:\n"
    prompt += f"**Description**: {proj_data['description']}\n"
    prompt += f"**Git Log**: {eval}\n"
    # model_rating = prompt_gpt(prompt, sys_prompt_2)
    model_rating = None
    all_resps[i] = model_rating

print(all_resps)

all_resps = ['Repo #0: 2  \nReasoning: While the code appears to involve a specific implementation aimed at quantum computing, the git log shows a single commit with a substantial amount of code. This large initial commit suggests the possibility of bulk copy-pasting or pasting significant portions of existing work rather than iterative development. Furthermore, there is no evidence of development history, including ongoing discussions or smaller commits that would indicate regular progress over time. The absence of intermediate commits raises concerns about the originality of the work. Additionally, the README file is minimal, which does not provide sufficient documentation or context for the project. These factors together indicate a high likelihood of embellishment.', 'Repo #1: 5  \nReasoning: The repository represents a minimal implementation of Git, suggesting strong conceptual understanding and significant individual effort. The git log indicates meaningful, incremental contributions across multiple files, suggesting a thoughtful, developmental approach rather than bulk copy-pasting. The project structure and thorough documentation demonstrate organization and intention behind the implementation. The project acknowledges a tutorial, but it does not detract from the originality, as the candidate seems to have created an implementation that reflects their own work and understanding. The complexity and depth of the implementation align well with the claims made in the resume, indicating that this is original work.', 'Repo #2: 5 \nReasoning: The repository demonstrates a clear and consistent approach to developing a Redis-like in-memory database using Go. The commit history indicates a structured and iterative development process, with meaningful contributions such as the implementation of crucial features like PUB/SUB functionality, RESP parsing, and data persistence using an Append Only File (AOF) mechanism. The README file is comprehensive, detailing the project structure, features, installation steps, and usage examples. The code itself reflects original work, with a consistent coding style across various modules, no signs of bulk commits, or copied code from well-known sources. The functionality aligns well with the claims in the project description, showcasing a solid understanding of concurrent programming and the project objectives.']
# now need to iteratore through repos
for i, resp in enumerate(proj_gh_match):

    prompt = ""
    breakpoint()
    proj_data, repo_data, status = repo_scores[i]
    if status == 'tmp':
        continue
    url = f"https://github.com/{repo_data['owner']}/{repo_data['title']}.git"
    # resp = repo_url_to_context(url)
    eval = repo_url_to_commits(url, gh_username)
    prompt += f"**Repo #{i}**:\n"
    prompt += f"**Description**: {proj_data['description']}\n"
    prompt += f"**Git Log**: {eval}\n"
    # model_rating = prompt_gpt(prompt, sys_prompt_2)
    # all_resps.append(model_rating)

print(all_resps)

all_resps = ['Repo #0: 2  \nReasoning: While the code appears to involve a specific implementation aimed at quantum computing, the git log shows a single commit with a substantial amount of code. This large initial commit suggests the possibility of bulk copy-pasting or pasting significant portions of existing work rather than iterative development. Furthermore, there is no evidence of development history, including ongoing discussions or smaller commits that would indicate regular progress over time. The absence of intermediate commits raises concerns about the originality of the work. Additionally, the README file is minimal, which does not provide sufficient documentation or context for the project. These factors together indicate a high likelihood of embellishment.', 'Repo #1: 5  \nReasoning: The repository represents a minimal implementation of Git, suggesting strong conceptual understanding and significant individual effort. The git log indicates meaningful, incremental contributions across multiple files, suggesting a thoughtful, developmental approach rather than bulk copy-pasting. The project structure and thorough documentation demonstrate organization and intention behind the implementation. The project acknowledges a tutorial, but it does not detract from the originality, as the candidate seems to have created an implementation that reflects their own work and understanding. The complexity and depth of the implementation align well with the claims made in the resume, indicating that this is original work.', 'Repo #2: 5 \nReasoning: The repository demonstrates a clear and consistent approach to developing a Redis-like in-memory database using Go. The commit history indicates a structured and iterative development process, with meaningful contributions such as the implementation of crucial features like PUB/SUB functionality, RESP parsing, and data persistence using an Append Only File (AOF) mechanism. The README file is comprehensive, detailing the project structure, features, installation steps, and usage examples. The code itself reflects original work, with a consistent coding style across various modules, no signs of bulk commits, or copied code from well-known sources. The functionality aligns well with the claims in the project description, showcasing a solid understanding of concurrent programming and the project objectives.']


breakpoint()

