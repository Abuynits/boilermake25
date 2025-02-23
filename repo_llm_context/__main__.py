import sys
from . import repo_url_to_context

if __name__ == "__main__":
    git_url = sys.argv[1]

    import time
    start = time.time()
    out = repo_url_to_context(git_url, char_limit=100_000_000)
    took = time.time() - start
    print(f"Took {took:.2f}s to process repo", file=sys.stderr)

    print(out)