import sys
import json
import shlex
import tempfile
import subprocess
from pathlib import Path
from dataclasses import dataclass


@dataclass
class FileInfo:
    path: str
    lines: int
    complexity: int
    language: str
    binary: bool
    minified: bool
    generated: bool

    def human_written(self):
        return not (self.binary or self.minified or self.generated)


def transform_scc(input_data):
    result = []

    # Iterate through each language category
    for language_category in input_data:
        # Iterate through each file in the category
        for file_info in language_category.get("Files", []):
            # Create a FileInfo object
            file_entry = FileInfo(
                path=file_info.get("Location", ""),
                lines=file_info.get("Lines", 0),
                complexity=file_info.get("Complexity", 0),
                language=file_info.get("Language", ""),
                binary=file_info.get("Binary", False),
                minified=file_info.get("Minified", False),
                generated=file_info.get("Generated", False),
            )
            result.append(file_entry)

    return result


def repo_to_context(path: Path):
    cmd = shlex.split("scc --by-file --format json")
    cmd.append(str(path))
    scc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    out, _ = scc.communicate()
    if scc.returncode != 0:
        raise Exception("scc failed")

    code_files = transform_scc(json.loads(out))
    code_files = filter(lambda x: x.human_written(), code_files)
    code_files = filter(lambda x: x.complexity > 0, code_files)
    for code_file in code_files:
        print(code_file)


class RepoInstance:
    def __init__(self, git_urL: str):
        self.git_url = git_url

        # make temporary directory
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp_dir.name)

    def open(self):
        cmd = shlex.split("git clone --depth 1")
        cmd.append(self.git_url)
        cmd.append(str(self.path))
        git = subprocess.Popen(cmd)
        git.communicate()
        if git.returncode != 0:
            raise Exception("git failed")

    def close(self):
        self.tmp_dir.cleanup()


if __name__ == "__main__":
    git_url = sys.argv[1]

    repo = RepoInstance(git_url)
    repo.open()
    repo_to_context(repo.path)
    repo.close()