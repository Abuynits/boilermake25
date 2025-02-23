import requests
import json
import random
import openai
import base64

from utils import extract_valid_json
from heuristics import valid_extensions
from heuristics import language_build_files

from secrets import GITHUB_TOKEN
from secrets import HYPERBOLIC_API_KEY

GRAPHQL_URL = "https://api.github.com/graphql"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

def load_query(filename):
    with open(filename, "r") as file:
        return file.read()

def execute_query(query):
    response = requests.post(GRAPHQL_URL, json={"query": query}, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"Error executing query: {response.status_code} - {response.text}")
        return []

    return response.json()

def fetch_prs():
    query = load_query("query.graphql")
    data = execute_query(query)
    prs = data.get("data", {}).get("search", {}).get("nodes", [])
    prs = random.sample(prs, min(len(prs), 5))
    
    return prs


def extract_indicators(prs):
    """Extract relevant indicators from PR data."""
    indicators = []
    
    for pr in prs:
        readme = pr["repository"].get("object", {}).get("text", "")
        package_json_obj = pr["repository"].get("packageJson", {})
        package_json = ""
        if isinstance(package_json_obj, dict) and "text" in package_json_obj:
            package_json = package_json_obj["text"]
        file_paths = [file["path"] for file in pr.get("files", {}).get("nodes", [])]

        indicators.append({
            "id": pr["url"],  # Unique identifier for mapping back
            "readme": readme,
            "package_json": package_json,
            "file_paths": file_paths
        })

    return indicators

def get_relevant_prs(prs, topics):
    """Filter PRs based on relevance to topics."""
    
    indicators = extract_indicators(prs)
    
    with open('match_indicators_prompt.txt', 'r') as f:
        system_prompt = f.read()

    client = openai.OpenAI(
        api_key=HYPERBOLIC_API_KEY,
        base_url="https://api.hyperbolic.xyz/v1",
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps({"topics": topics, "indicators": indicators})},
    ]

    chat_completion = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct",
        messages=messages,
        temperature=0.7,
        max_tokens=1024,
    )

    response = chat_completion.choices[0].message.content
    response_json = extract_valid_json(response)

    relevant_ids = set(response_json["relevant_ids"])
    relevant_prs = [pr for pr in prs if pr["url"] in relevant_ids]

    return relevant_prs

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
    # prs = fetch_prs()
    # prs = get_relevant_prs(prs, topics)
    prs = None
    with open("prs2.json", "r") as f:
        prs = json.load(f)
    pr_diffs = []

    for pr in prs:
        repo_owner, repo_name = pr["repository"]["nameWithOwner"].split("/")
        pr_number = pr["url"].split("/")[-1] 

        pr_diff = generate_pr_diff(pr, valid_extensions, repo_name, repo_owner, pr_number)
        pr_diffs.append({
            "nameWithOwner": repo_owner + "/" + repo_name,
            "diffs": pr_diff,
        })

    print(json.dumps(pr_diffs, indent=4))
