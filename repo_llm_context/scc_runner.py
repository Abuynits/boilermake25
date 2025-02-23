import sys
import shlex
import subprocess
import requests as re
from pathlib import Path
import tarfile
from tempfile import TemporaryFile

CACHE_DIR = Path("./.cache")
CACHE_DIR.mkdir(exist_ok=True)


def cmd(cmd: str):
    cmd = shlex.split(cmd)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode != 0:
        raise Exception(
            f'cmd "{cmd}" failed with code {proc.returncode}. stderr:\n{err}\n'
        )

    return out.decode()


os = cmd("uname -s").strip()
arch = cmd("uname -m").strip()
uri = f"https://github.com/boyter/scc/releases/download/v3.5.0/scc_{os}_{arch}.tar.gz"

SCC_DIR = CACHE_DIR / "scc"
SCC_BIN = SCC_DIR / "scc"

if not SCC_DIR.exists() or not SCC_BIN.exists():
    SCC_DIR.mkdir(exist_ok=True)
    print(f"scc not found at {SCC_DIR}, downloading from {uri}", file=sys.stderr)
    r = re.get(uri)
    with TemporaryFile(suffix=".tar.gz") as f:
        f.write(r.content)
        f.seek(0)

        with tarfile.open(fileobj=f, mode="r:gz") as tar:
            with SCC_BIN.open("wb") as scc:
                scc.write(tar.extractfile("scc").read())
        SCC_BIN.chmod(0o755)
    print(f"finished downloading scc to {SCC_DIR}", file=sys.stderr)

print(f"using scc at {SCC_BIN}", file=sys.stderr)


def run_scc(args: list[str]):
    cmd = [SCC_BIN, *args]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode != 0:
        raise Exception(
            f'cmd "{cmd}" failed with code {proc.returncode}. stderr:\n{err}\n'
        )

    return out.decode()
