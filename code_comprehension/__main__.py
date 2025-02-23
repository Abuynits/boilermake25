from . import get_code_snippet
import time

if __name__ == "__main__":
    import sys

    git_url = sys.argv[1]
    topic = sys.argv[2]

    start = time.time()
    thoughts, rel_path, code, explaination = get_code_snippet(git_url, topic)
    took = time.time() - start

    print(f"Took {took:.2f}s to process repo", file=sys.stderr)
    print("=== Thoughts ===")
    print(thoughts)
    print(f"\n=== {rel_path} ===")
    print(code)
    print("\n=== Explaination ===")
    print(explaination)
