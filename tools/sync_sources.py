#!/usr/bin/env python3
"""Clone or update upstream documentation repositories locally."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources"
REPOS = {
    "bedrock-wiki": "https://github.com/Bedrock-OSS/bedrock-wiki.git",
    "minecraft-creator": "https://github.com/MicrosoftDocs/minecraft-creator.git",
}

def run(args, cwd=None):
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=cwd, check=True)

def main():
    SOURCES.mkdir(parents=True, exist_ok=True)
    for name, url in REPOS.items():
        dest = SOURCES / name
        if (dest / ".git").exists():
            run(["git", "fetch", "--all", "--prune"], cwd=dest)
            run(["git", "pull", "--ff-only"], cwd=dest)
        elif dest.exists() and any(dest.iterdir()):
            raise RuntimeError(f"{dest} exists and is not a Git checkout; move it before syncing")
        else:
            run(["git", "clone", "--filter=blob:none", url, str(dest)])
    print("Sources synchronized. Review upstream licenses before republishing material.")

if __name__ == "__main__":
    try:
        main()
    except (subprocess.CalledProcessError, RuntimeError) as exc:
        print(f"Sync failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
