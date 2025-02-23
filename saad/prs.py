import sys
import requests
import json
import random
import openai
import base64
import hashlib
from pathlib import Path
from rapidfuzz import fuzz
from importlib.resources import read_text

from saad.utils import extract_valid_json
from saad.heuristics import valid_extensions
from saad.heuristics import language_build_files
import saad.prompts

from _secrets import GITHUB_TOKEN
from _secrets import HYPERBOLIC_API_KEY

GRAPHQL_URL = "https://api.github.com/graphql"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

CACHE_DIR = Path("./.cache")
CACHE_DIR.mkdir(exist_ok=True)

def _get_cache_path(identifier: str):
    """Generate a cache file path based on an identifier (hashed key)."""
    hash_key = hashlib.md5(identifier.encode()).hexdigest()
    return CACHE_DIR / f"{hash_key}.json"

def _load_cache(identifier: str):
    """Loads cached data if it exists."""
    cache_path = _get_cache_path(identifier)
    if cache_path.exists():
        with open(cache_path, "r") as f:
            return json.load(f)
    return None

def _save_cache(identifier: str, data):
    """Saves data to the cache file."""
    cache_path = _get_cache_path(identifier)
    with open(cache_path, "w") as f:
        json.dump(data, f)
    
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
    query = read_text(sys.modules[__name__], "query.graphql")
    query = query.replace("{programming_language}", language).replace("{build_file_queries}", build_file_queries)
    return query

def execute_query(query):
    """Execute GraphQL query, caching results."""
    cache_key = json.dumps({"query": query}, sort_keys=True)
    cached_result = _load_cache(cache_key)

    if cached_result:
        return cached_result  # Return cached result if available

    response = requests.post(GRAPHQL_URL, json={"query": query}, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"Error executing query: {response.status_code} - {response.text}")
        return []

    result = response.json()
    _save_cache(cache_key, result)  # Cache response
    return result

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
    """Extract relevant source code file changes, filtering by valid extensions. Cache results."""
    cache_key = json.dumps({"repo": repo_name, "owner": repo_owner, "pr_number": pr_number}, sort_keys=True)
    cached_result = _load_cache(cache_key)

    if cached_result:
        return cached_result  # Return cached result if available

    relevant_changes = []
    files = pr_data.get("files", {}).get("nodes", [])
    file_diffs = get_file_diffs(repo_owner=repo_owner, repo_name=repo_name, pr_number=pr_number)

    for file in files:
        file_path = file["path"]
        file_extension = file_path.split(".")[-1]

        if file_extension in valid_extensions:
            file_diff = file_diffs.get(file_path, "No diff available")
            contents = get_file_contents(repo_owner, repo_name, file_path)
            relevant_changes.append({
                "file": file_path,
                "diff": file_diff,
                "contents": contents
            })

    _save_cache(cache_key, relevant_changes)  # Cache results
    return relevant_changes

def get_exercise(pr_diff):
    """Generate exercises from PR diff using LLM. Cache results."""
    cache_key = json.dumps({"pr_diff": pr_diff}, sort_keys=True)
    cached_result = _load_cache(cache_key)

    if cached_result:
        return cached_result  # Return cached result if available

    user_content = str(pr_diff)
    system_content = read_text(saad.prompts, 'prompt_get_exercise.txt')

    client = openai.OpenAI(
        api_key=HYPERBOLIC_API_KEY,
        base_url="https://api.hyperbolic.xyz/v1",
    )

    chat_completion = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ],
        temperature=0.7,
        max_tokens=9192,
    )

    response = chat_completion.choices[0].message.content
    _save_cache(cache_key, response)  # Cache the exercise
    return response

def driver(topics):
    """Fetch relevant PRs, analyze diffs, and generate exercises, caching results."""
    
    # Create a cache key from the input topics
    cache_key = json.dumps({"topics": topics}, sort_keys=True)
    cached_result = _load_cache(cache_key)

    if cached_result:
        return cached_result  # Return cached result if available

    # Fetch PRs related to the language and topics
    language = topics[0]
    build_files = language_build_files.get(language, [])
    
    prs = fetch_prs(language, build_files)
    prs = get_relevant_prs(prs, topics)

    pr = prs[0]
    repo_owner, repo_name = pr["repository"]["nameWithOwner"].split("/")
    pr_number = pr["url"].split("/")[-1] 

    pr_diff = generate_pr_diff(pr, valid_extensions, repo_name, repo_owner, pr_number)

    print(pr_diff)

    exercises = []
    for diff in pr_diff:
        diff = pr_diff
        exercises.append(get_exercise(diff))

    # Store the result in cache before returning
    _save_cache(cache_key, exercises)
    
    return exercises

if __name__ == "__main__":
    topics = ["JavaScript", "Full Stack Development", "React", "Express", "PostgreSQL", "GraphQL"]
    # topics = ["Python", "PostgreSQL", "MongoDB", "Git"]

    language = topics[0]
    build_files = language_build_files.get(language, [])
    
    prs = fetch_prs(language, build_files)
    prs = get_relevant_prs(prs, topics)

    # prs = None
    # with open("prs2.json", "r") as f:
    #     prs = json.load(f)
    
    pr_diffs = []

    for pr in prs[0:1]:
        repo_owner, repo_name = pr["repository"]["nameWithOwner"].split("/")
        pr_number = pr["url"].split("/")[-1] 

        pr_diff = generate_pr_diff(pr, valid_extensions, repo_name, repo_owner, pr_number)

        pr_diffs.append({
            "nameWithOwner": repo_owner + "/" + repo_name,
            "prNumber": pr_number,
            "diffs": pr_diff,
        })

    exercises = get_exercise(pr_diffs)

    print(json.dumps(exercises, indent=4))
