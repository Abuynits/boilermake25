import sys
import json
import shlex
import tempfile
import subprocess
from pathlib import Path
from dataclasses import dataclass


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
    entropy: float
    language: str
    binary: bool
    minified: bool
    generated: bool

    @property
    def human(self):
        return not (self.binary or self.minified or self.generated)
    
    def with_entropy(self):
        return FileInfo(
            path=self.path,
            n_bytes=self.n_bytes,
            complexity=self.complexity,
            entropy=file_pigz_entropy(self.path),
            language=self.language,
            binary=self.binary,
            minified=self.minified,
            generated=self.generated,
        )


def transform_scc(input_data):
    result = []

    # Iterate through each language category
    for language_category in input_data:
        # Iterate through each file in the category
        for file_info in language_category.get("Files", []):
            # Create a FileInfo object
            loc = Path(file_info.get("Location", ""))
            file_entry = FileInfo(
                path=loc,
                n_bytes=file_info.get("Bytes", 0),
                complexity=file_info.get("Complexity", 0),
                language=file_info.get("Language", ""),
                binary=file_info.get("Binary", False),
                minified=file_info.get("Minified", False),
                generated=file_info.get("Generated", False),
                entropy=None,
            )
            result.append(file_entry)

    return result


def repo_to_context(path: Path, char_limit=350000):
    # cmd = shlex.split("scc --by-file --format json")
    # cmd.append(str(path))
    cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{path}:/repo",
        "ghcr.io/boyter/scc:master",
        "scc",
        "--by-file",
        "--format",
        "json",
        "/repo",
    ]
    scc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    out, _ = scc.communicate()
    out = out.decode("utf-8")
    out = out.replace('"/repo', f'"{path}')
    if scc.returncode != 0:
        raise Exception("scc failed")

    code_files = transform_scc(json.loads(out))
    code_files = filter(lambda x: x.human, code_files)
    code_files = filter(lambda x: x.complexity > 0, code_files)
    code_files = filter(lambda x: "test" not in str(x.path), code_files)
    code_files = map(lambda x: x.with_entropy(), code_files)
    code_files = sorted(code_files, key=lambda x: x.entropy, reverse=True)

    pruned_files = []
    total_bytes = sum(x.n_bytes for x in code_files)
    while total_bytes > char_limit:
        removed = code_files.pop()
        total_bytes -= removed.n_bytes
        pruned_files.append(removed)

    for f in pruned_files:
        print(f, file=sys.stderr)

    out = ""
    code_files = sorted(code_files, key=lambda x: str(x.path))
    for f in code_files:
        rel_path = str(f.path)[len(str(path)) + 1 :]
        out += f'<file name="{rel_path}">\n'
        out += f.path.read_text() + "\n"
        out += f"</file> <!-- {rel_path} -->\n"

    return out


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
    out = repo_to_context(repo.path)
    repo.close()

    print(out)
