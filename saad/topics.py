import openai
import json
import hashlib
from pathlib import Path
from rapidfuzz import fuzz, process
from importlib.resources import read_text

from . import topic_examples
from . import prompts
from . import utils
from _secrets import HYPERBOLIC_API_KEY

CACHE_DIR = Path("./.cache")
CACHE_DIR.mkdir(exist_ok=True)

topics_examples = topic_examples.topics

def _get_cache_path(identifier: str):
    """Returns the cache file path based on an identifier (hashed key)."""
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

def get_relevant_topics(resume_topics, job_posting_topics):
    cache_key = json.dumps({"resume_topics": resume_topics, "job_posting_topics": job_posting_topics}, sort_keys=True)
    cached_result = _load_cache(cache_key)
    
    if cached_result:
        return cached_result  # Return cached result if available

    relevant_topics = []
    for topic in resume_topics:
        match, score, _ = process.extractOne(topic, job_posting_topics, scorer=fuzz.ratio)
        if score >= 80:
            relevant_topics.append(match)

    condensed_topics = get_condensed_topics(relevant_topics)
    _save_cache(cache_key, condensed_topics)  # Store result in cache
    return condensed_topics

def get_condensed_topics(topics):
    cache_key = json.dumps({"topics": topics}, sort_keys=True)
    cached_result = _load_cache(cache_key)
    
    if cached_result:
        return cached_result  # Return cached result if available

    user_content = str(topics)
    system_content = read_text(prompts, 'prompt.txt')

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
        max_tokens=1024,
    )

    response = chat_completion.choices[0].message.content
    response = utils.extract_valid_json(response)
    _save_cache(cache_key, response["topics_condensed"])  # Cache result
    return response["topics_condensed"]

# if __name__ == "__main__":
#     posting = ["HTML", "CSS", "JavaScript", "React", "Vue.js", "Angular", "Node.js", "Python", "PHP", "Ruby", "Java", "MySQL", "PostgreSQL", "MongoDB", "Git", "RESTful APIs"]
#     skills = ["C", "C++", "Python", "Scala", "Haskell", "Rust", "Linux", "Bash", "Git", "FreeRTOS", "Javascript", "Typescript", "PyTorch", "Langchain", "Docker", "Kubernetes", "AWS (S3, EC2, Lambda)", "React", "Svelte", "Node", "Express", "Flask", "PostgreSQL", "MongoDB", "Redis", "CI/CD", "OpenCL", "OpenGL", "CUDA", "WebAssembly", "x86(-64) AT&T Assembly", "ARM Assembly", "GCC", "Valgrind", "GDB", "CMake", "Make", "Meson", "Ninja", "Blender", "Unity", "Vim", "TCP/IP", "UDP", "HTTP(S)", "REST", "GraphQL", "gRPC"]
    
#     topics = get_relevant_topics(posting, skills)
#     condensed_topics = get_condensed_topics(topics)

#     print(condensed_topics)