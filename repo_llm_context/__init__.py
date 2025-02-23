import sys
import time
import json
import shlex
import tempfile
import subprocess
from pathlib import Path
from joblib import Memory
from .groq import groq_filter_list
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from .code_exts import code_file_extensions as lang_exts

FULL_CLONE = False
GIT_LOG_RANK = False
USE_ENTROPY = False

if GIT_LOG_RANK and not FULL_CLONE:
    raise Exception("GIT_LOG_RANK requires FULL_CLONE")

memory = Memory("./.cache", verbose=0)


def file_pigz_entropy(path: Path):
    orig_size = path.stat().st_size
    if orig_size == 0:
        return 0

    cmd = ["pigz", "-c", str(path)]
    pigz = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    out, _ = pigz.communicate()
    if pigz.returncode != 0:
        raise Exception("pigz failed")

    pigz_size = len(out)
    return pigz_size / orig_size


@dataclass
class FileInfo:
    path: Path
    n_bytes: int
    complexity: int
    weighted_complexity: float
    entropy: float
    language: str
    human: bool
    change_count: int = None

    @property
    def heuristic(self):
        if GIT_LOG_RANK:
            return self.change_count
        elif USE_ENTROPY:
            return self.entropy
        else:
            return self.complexity

    def with_entropy(self):
        return FileInfo(
            path=self.path,
            n_bytes=self.n_bytes,
            complexity=self.complexity,
            weighted_complexity=self.weighted_complexity,
            entropy=file_pigz_entropy(self.path),
            language=self.language,
            human=self.human,
            change_count=self.change_count,
        )

    def with_change_count(self, count):
        return FileInfo(
            path=self.path,
            n_bytes=self.n_bytes,
            complexity=self.complexity,
            weighted_complexity=self.weighted_complexity,
            entropy=self.entropy,
            language=self.language,
            human=self.human,
            change_count=count,
        )


def transform_scc(input_data):
    result = []

    # Iterate through each language category
    for language_category in input_data:
        # Iterate through each file in the category
        for file_info in language_category.get("Files", []):
            # Create a FileInfo object
            binary = file_info.get("Binary", False)
            minified = file_info.get("Minified", False)
            generated = file_info.get("Generated", False)

            loc = Path(file_info.get("Location", ""))
            file_entry = FileInfo(
                path=loc,
                n_bytes=file_info.get("Bytes", 0),
                complexity=file_info.get("Complexity", -1),
                weighted_complexity=file_info.get("WeightedComplexity", -1),
                language=file_info.get("Language", ""),
                entropy=None,
                human=not (binary or minified or generated),
            )
            result.append(file_entry)

    return result


def repo_to_commits(path: Path, gh_username: str, char_limit=350000):
    char_limit *= 0.94  # account for xml tags overhead
    # cmd = shlex.split("scc --by-file --format json")
    # cmd.append(str(path))
    import os

    cwd = os.getcwd()
    os.chdir(path)
    cmd = ["git", "log", "-p", f"--author={gh_username}", "--diff-filter=ACDMRTUXB"]
    # `git log -p --author="<author email>" --diff-filter=ACDMRTUXB`
    s_out = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    out, _ = s_out.communicate()
    out = out.decode("utf-8")
    out = out.replace('"/repo', f'"{path}')
    os.chdir(cwd)
    if s_out.returncode != 0:
        raise Exception("scc failed")
    return out


def repo_to_context_json(path: Path, topic: str, char_limit):
    char_limit *= 0.94  # account for xml tags overhead

    cmd = shlex.split(
        f"docker run --rm -v {path}:/repo ghcr.io/boyter/scc:master scc --by-file --format json /repo"
    )
    scc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    out, _ = scc.communicate()
    out = out.decode("utf-8")
    out = out.replace('"/repo', f'"{path}')
    if scc.returncode != 0:
        raise Exception("scc failed")

    out = json.loads(out)
    # print(json.dumps(out, indent=2), file=sys.stderr)
    code_files = transform_scc(out)

    if GIT_LOG_RANK:
        cmd = [
            "git",
            "--git-dir",
            f"{path}/.git",
            "log",
            "--pretty=format:",
            "--name-only",
        ]
        git = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        out, _ = git.communicate()
        if git.returncode != 0:
            raise Exception("git failed")
        out = out.decode("utf-8")
        out = out.split("\n")
        # count each unique entry in out
        file_counts = {}
        for line in out:
            if line not in file_counts:
                file_counts[line] = 0
            file_counts[line] += 1

    code_files = [x for x in code_files if x.human]
    code_files = [
        x for x in code_files if any(x.path.name.endswith(y) for y in lang_exts)
    ]
    original_files = code_files
    code_files = [x for x in code_files if "/tests/" not in str(x.path)]
    code_files = [x for x in code_files if x.complexity > 0]
    if USE_ENTROPY:
        with ThreadPoolExecutor() as executor:
            code_files = list(executor.map(lambda x: x.with_entropy(), code_files))

    if GIT_LOG_RANK:
        code_files = list(
            map(
                lambda x: x.with_change_count(
                    file_counts.get(str(x.path)[len(str(path)) + 1 :], 0)
                ),
                code_files,
            )
        )

    if USE_ENTROPY or GIT_LOG_RANK:
        code_files = sorted(code_files, key=lambda x: x.heuristic, reverse=True)

    start = time.time()
    code_file_map = {str(x.path)[len(str(path)) + 1 :]: x for x in code_files}
    filtered_file_names = groq_filter_list(sorted(code_file_map.keys()), topic)
    code_files = [code_file_map[x] for x in filtered_file_names]
    took = time.time() - start
    print(f"groq filter list took {took:.2f}s", file=sys.stderr)

    pruned_files = [x for x in original_files if x not in code_files]
    print(f"code files before length pruning: {len(code_files)}", file=sys.stderr)

    total_bytes = sum(x.n_bytes for x in code_files)
    while total_bytes > char_limit:
        removed = code_files.pop()
        total_bytes -= removed.n_bytes
        pruned_files.append(removed)

    print(f"code files: {len(code_files)}", file=sys.stderr)
    print(f"total size: {total_bytes}", file=sys.stderr)

    # for f in code_files:
    #     print(str(f.path)[len(str(path)) + 1 :], file=sys.stderr)

    code_files = sorted(code_files, key=lambda x: str(x.path))
    # pruned_files = sorted(pruned_files, key=lambda x: x.complexity)

    out = []
    for f in code_files:
        rel_path = str(f.path)[len(str(path)) + 1 :]
        content = f.path.read_text()
        out.append(
            {
                "name": rel_path,
                "content": content,
            }
        )

    return out


def files_json_to_model_context(files_json):
    out = ""
    for file in files_json:
        out += f'<file name="{file["name"]}">\n'
        out += file["content"] + "\n"
        out += f"</file> <!-- {file['name']} -->\n"

    return out


class RepoInstance:
    def __init__(self, git_url: str):
        self.git_url = git_url

        # make temporary directory
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp_dir.name)

    def open(self):
        start = time.time()
        print(f"cloning {self.git_url} to {self.path}", file=sys.stderr)
        if FULL_CLONE:
            cmd = shlex.split("git clone")
        else:
            cmd = shlex.split("git clone --depth 1")
        cmd.append(self.git_url)
        cmd.append(str(self.path))
        # git = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        git = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        git.communicate()
        if git.returncode != 0:
            raise Exception("git failed")
        took = time.time() - start
        print(f"cloned in {took:.2f}s", file=sys.stderr)

    def close(self):
        self.tmp_dir.cleanup()


def repo_url_to_context_json(git_url: str, topic: str, char_limit):
    repo = RepoInstance(git_url)
    repo.open()
    out = repo_to_context_json(repo.path, topic, char_limit)
    repo.close()
    return out


def repo_url_to_commits(git_url: str, gh_username: str):
    repo = RepoInstance(git_url)
    repo.open()
    out = repo_to_commits(repo.path, gh_username)
    repo.close()
    return out
