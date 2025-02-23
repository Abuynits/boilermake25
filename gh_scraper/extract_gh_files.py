import numpy as np
from path import Path
from gh_scraper.parsing_utils import bs_utils
import json
import os
from openai import OpenAI
import openai
import time
from urllib.request import urlopen
from repo_llm_context import repo_url_to_commits
data_name = 'example_res.json'

api_key = os.environ.get("OPENAI_API_KEY")
openai.api_key = api_key
client = OpenAI()
#gh_username = "Abuynits"
#gh_email = "abuynits@gmail.com"
#resume_file = Path(__file__).parent / 'data' / f'{data_name}'

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

def extract_gh_files(resume_data, gh_username, gh_email):

    experience_lines = []
    for exper in resume_data['experience']:
        for line in exper['highlights']:
            experience_lines.append(line.replace(".",""))
    # now feed to LLM to verify quality

    sys_prompt =  """You are reviewing a candidate’s resume for a large company. Given a list of lines from their resume, your task is to evaluate the accuracy and validity of each claim on a scale of 1 to 5:
    1: Clearly false, fabricated, or nonsensical
    5: Completely valid and credible
    Format your output as follows. Just answer the question (your response should start with 1. [rating]):
    line 1: 5
    Reasoning: Creating automation scripts in multiple programming languages is quite practical 
    line 2: 2 
    Reasoning: The candiate claimed that they had access to gpt4 weights which is not possible.
    ...
    """
    prompt = "\n".join(experience_lines)
    exper_rating = prompt_gpt(prompt, sys_prompt)
    exper_rating_data = {}
    count = 0
    int_exper_rating = []
    str_exper_rating = []
    breakpoint()
    for line in exper_rating.split("\n"):
        if len(line) < 1:
            continue
        if count % 2 == 0:
            rating = int(line.split(":")[-1].strip())
            int_exper_rating.append(rating)
        else:
            str_exper_rating.append(line)
        count += 1
    res_exper_rating = []
    breakpoint()
    for line, rate, reason in zip(experience_lines, int_exper_rating, str_exper_rating):
        res_exper_rating.append((line,rate,reason))


    user_path = Path(__file__).parent / 'data' / gh_username
    full_prompt = ""


    full_prompt += "\n\nCandidate Resume Projects:\n"
    if 'projects' in resume_data:
        for i, proj in enumerate(resume_data['projects']):
            full_prompt += f"Project {i} [{proj['title']}]:\n"
            desc = '\n\t- '.join(proj['description'])
            full_prompt += f"Descrition: {desc}\n"
    else:
        full_prompt += "None\n"

    full_prompt += "\n\nCandidate Resume Experiences:\n"

    if 'experience' in resume_data:
        for i, exp in enumerate(resume_data['experience']):
            full_prompt += f"Experience {i} [{exp['role']} @ {exp['company']}]:\n"
            desc = '\n\t- '.join(exp['highlights'])
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
    resume project #0: github project# 4
    resume project #1: None
    ...
    """
    proj_gh_match = prompt_gpt(full_prompt, sys_prompt)
    # proj_gh_match = "resume project #0: github project #8\nresume project #1: github project #13\nresume project #2: github project #3"
    proj_gh_match = proj_gh_match.split("\n")
    proj_gh_match = [resp for resp in proj_gh_match if len(resp) > 1]

    repo_scores = []
    breakpoint()
    for i, resp in enumerate(proj_gh_match):
        proj_id = int(resp.split(":")[0].split("#")[-1].strip())
        gh_id = resp.split(":")[-1]
        if 'none' in gh_id.lower():
            print("no proj found")
            repo_scores.append((resume_data['projects'][i], 'None', 'YELLOW'))
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

    *Red Flags to Watch For*:
    - Large initial commits followed by minimal contributions (suggesting bulk copy-pasting)
    - Code copied from well-known sources (e.g., GitHub repositories, Stack Overflow, or open-source projects)
    - Minimal meaningful code contributions (e.g., mostly modifying comments, formatting, or renaming variables)
    - Inconsistent coding style (indicating possible multiple authors)
    - Commits with drastic jumps in complexity (suggesting pasted code rather than iterative development)
    - Sudden, short bursts of activity followed by long inactivity (suggesting last-minute additions rather than steady progress)
    - Missing implementation details for complex claims in the resume

    *Response Format*:
    Repo #0: 5
    Resoning: The candidate's contributions are well-documented and show a clear progression of work. The commits are consistent with the candidate's resume and demonstrate a deep understanding of the project requirements.
    Repo #1: 1
    Reasoning: The initial commits contain large blocks of code copied from external sources, and the subsequent contributions are minimal. The candidate's work appears to be plagiarized or embellished.
    ...
    """
    # resp = prompt_gpt(prompt, sys_prompt_2)
    all_resps = {}
    # now need to iteratore through repos
    for i, resp in enumerate(proj_gh_match):
        prompt = ""
        proj_data, repo_data, status = repo_scores[i]
        if status == 'YELLOW':
            continue
        url = f"https://github.com/{repo_data['owner']}/{repo_data['title']}.git"
        # resp = repo_url_to_context(url)
        eval = repo_url_to_commits(url, gh_email)[:300000]
        prompt += f"**Repo #{i}**:\n"
        prompt += f"**Description**: {proj_data['description']}\n"
        prompt += f"**Git Log**: {eval}\n"
        model_rating = prompt_gpt(prompt, sys_prompt_2)
        all_resps[i]= model_rating

    breakpoint()

    # now need to iteratore through repos
    all_user_project_data = []
    for i, resp in enumerate(repo_scores):
        proj_data, repo_data, status = repo_scores[i]
        if status == 'YELLOW':
            rating = -1
            reasoning = 'No project found'
        else:
            rating = int(all_resps[i].split("\n")[0].strip().split()[-1])
            reasoning = '\n'.join(all_resps[i].split("\n")[1:])
        all_user_project_data.append((proj_data, repo_data, status, rating,reasoning))

    # output_file = Path(__file__).parent / 'data' / f'{gh_username}.json'
    breakpoint()
    full_data = {
        'project_data': all_user_project_data,
        'experience_data': res_exper_rating
    }

    return full_data 
