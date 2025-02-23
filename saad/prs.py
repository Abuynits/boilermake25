import requests
import json
import random
import openai
import base64
from rapidfuzz import fuzz

from utils import extract_valid_json
from heuristics import valid_extensions
from heuristics import language_build_files

from secrets import GITHUB_TOKEN
from secrets import HYPERBOLIC_API_KEY

GRAPHQL_URL = "https://api.github.com/graphql"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

    
def generate_query(language, build_files):
    build_file_queries = ""
    for bf in build_files:
        alias = bf.replace('.', '_').replace('-', '_')          # valid alias
        build_file_queries += f'''
              {alias}: object(expression: "HEAD:{bf}") {{
                ... on Blob {{
                  text
                }}
              }}
        '''
    with open('query.graphql', 'r') as f:
        query = f.read()
    query = query.replace("{programming_language}", language).replace("{build_file_queries}", build_file_queries)
    return query

def execute_query(query):
    response = requests.post(GRAPHQL_URL, json={"query": query}, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"Error executing query: {response.status_code} - {response.text}")
        return []

    return response.json()

def fetch_prs(language, build_files):
    query = generate_query(language, build_files)
    data = execute_query(query)
    prs = data.get("data", {}).get("search", {}).get("nodes", [])

    prs = random.sample(prs, min(len(prs), 5))
    
    return prs


def extract_indicators(prs):
    """Extract relevant indicators from PR data."""
    indicators = []
    
    for pr in prs:
        readme = pr["repository"].get("object", {}).get("text", "")
        file_paths = [file["path"] for file in pr.get("files", {}).get("nodes", [])]

        build_files_contents = {}
        for key, value in pr["repository"].items():
            if isinstance(value, dict) and "text" in value:
                build_files_contents[key] = value["text"]

        indicators.append({
            "id": pr["url"],  # Unique identifier for mapping back
            "readme": readme,
            "build_files": build_files_contents
        })

    return indicators

def get_relevant_prs(prs, topics):
    """Filter PRs based on relevance to topics."""
    
    indicators = extract_indicators(prs)
    pr_scores = []

    for indicator in indicators:
        pr_id = indicator["id"]
        combined_text = indicator["readme"] + " " + " ".join(indicator["build_files"].values())

        if not combined_text.strip():
            continue  # Skip PRs with no relevant indicators

        combined_text_lower = combined_text.lower()
        max_score = 0  # Track highest match score for this PR

        for topic in topics:
            score = fuzz.partial_ratio(topic.lower(), combined_text_lower)
            if score >= 70:
                max_score = max(max_score, score)  # Store highest match score

        if max_score > 0:
            pr_scores.append((pr_id, max_score))

    pr_scores.sort(key=lambda x: x[1], reverse=True)
    top_pr_ids = {pr_id for pr_id, _ in pr_scores[:2]}
    top_relevant_prs = [pr for pr in prs if pr["url"] in top_pr_ids]

    return top_relevant_prs

def get_file_diffs(repo_owner, repo_name, pr_number):
    """Fetch file diffs using REST API."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/files"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        raise Exception(f"REST API Error: {response.json()}")

    return {file["filename"]: file.get("patch", "") for file in response.json()}

def get_file_contents(repo_owner, repo_name, file_path):
    """Fetch raw file content using REST API."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}?ref=main"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        content = response.json().get("content", "")
        return base64.b64decode(content).decode("utf-8")  # Decode Base64 content
    return None

def generate_pr_diff(pr_data, valid_extensions, repo_name, repo_owner, pr_number):
    """Extract relevant source code file changes, filtering by valid extensions."""
    relevant_changes = []

    files = pr_data.get("files", {}).get("nodes", [])
    file_diffs = get_file_diffs(repo_owner=repo_owner, repo_name=repo_name, pr_number=pr_number)

    for file in files:
        file_path = file["path"]
        file_extension = file_path.split(".")[-1]

        if file_extension in valid_extensions:
            file_diff = file_diffs.get(file_path, "No diff available")
            relevant_changes.append({
                "file": file_path,
                "diff": file_diff,
            })

    return relevant_changes


if __name__ == "__main__":
    # topics = ["JavaScript", "Full Stack Development", "React", "Express", "PostgreSQL", "GraphQL"]
    topics = ["Python", "PyTorch", "Deep Learning", "CNNs", "RNNs", "GANs", "AutoML"]

    language = topics[0]
    build_files = language_build_files.get(language, [])
    
    prs = fetch_prs(language, build_files)
    prs = get_relevant_prs(prs, topics)

    # prs = None
    # with open("prs2.json", "r") as f:
    #     prs = json.load(f)
    
    pr_diffs = []

    for pr in prs:
        repo_owner, repo_name = pr["repository"]["nameWithOwner"].split("/")
        pr_number = pr["url"].split("/")[-1] 

        pr_diff = generate_pr_diff(pr, valid_extensions, repo_name, repo_owner, pr_number)
        pr_diffs.append({
            "nameWithOwner": repo_owner + "/" + repo_name,
            "prNumber": pr_number,
            "diffs": pr_diff,
        })

    print(json.dumps(pr_diffs, indent=4))
