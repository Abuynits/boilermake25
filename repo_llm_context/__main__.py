import sys
import json
from . import repo_url_to_context_json, files_json_to_model_context

if __name__ == "__main__":
    git_url = sys.argv[1]
    topic = sys.argv[2]

    import time
    start = time.time()
    out = repo_url_to_context_json(git_url, topic, char_limit=300_000)
    took = time.time() - start
    print(f"Took {took:.2f}s to process repo", file=sys.stderr)

    out = files_json_to_model_context(out)
    print(out)