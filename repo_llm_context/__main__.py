import sys
from . import RepoInstance, repo_to_context

if __name__ == "__main__":
    git_url = sys.argv[1]

    import time
    start = time.time()
    print(f"Cloning {git_url}", file=sys.stderr)
    repo = RepoInstance(git_url)
    repo.open()
    clone_time = time.time() - start
    print(f"Took {clone_time:.2f}s to clone repo", file=sys.stderr)

    start = time.time()
    out = repo_to_context(repo.path)
    repo.close()
    proc_time = time.time() - start
    print(f"Took {proc_time:.2f}s to process repo", file=sys.stderr)

    print(out)