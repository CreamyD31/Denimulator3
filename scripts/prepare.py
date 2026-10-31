"""Fetch pinned emulator sources and apply Denimulator3 branding."""
import argparse
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = "https://github.com/azahar-emu/azahar.git"
COMMIT = "01dc2bb7769befd791006ee83d3cc014cb1db3bd"  # Azahar 2123.3
PATCH = ROOT / "patches" / "denimulator3.patch"


def git(source, *args, capture=False):
    return subprocess.run(["git", "-C", str(source), *args], check=True,
                          stdout=subprocess.PIPE if capture else None).stdout


def apply_branding(source):
    head = git(source, "rev-parse", "HEAD", capture=True).decode().strip()
    if head != COMMIT:
        raise RuntimeError(f"Unexpected upstream HEAD: {head}; expected {COMMIT}")
    diff = git(source, "diff", "HEAD", "--binary", capture=True)
    if diff:
        if diff != PATCH.read_bytes():
            raise RuntimeError("Upstream has other local changes; refusing to overwrite them")
        print("Denimulator3 patch already applied", flush=True)
        return
    git(source, "apply", "--check", str(PATCH))
    git(source, "apply", str(PATCH))


def prepare(source, submodules=True):
    if not source.exists():
        source.mkdir(parents=True)
        git(source, "init")
        git(source, "remote", "add", "origin", UPSTREAM)
        git(source, "fetch", "--depth", "1", "origin", COMMIT)
        git(source, "checkout", "--detach", "FETCH_HEAD")
    elif not (source / ".git").exists():
        raise RuntimeError(f"{source} exists but is not a Git checkout")
    apply_branding(source)
    if submodules:
        git(source, "submodule", "update", "--init", "--recursive", "--jobs", "4")
        status = git(source, "submodule", "status", "--recursive", capture=True).decode()
        if any(line and line[0] != " " for line in status.splitlines()):
            raise RuntimeError("Submodules are not at the pinned revisions")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / ".cache" / "azahar")
    parser.add_argument("--no-submodules", action="store_true",
                        help="Only validate/apply branding; insufficient for a build")
    args = parser.parse_args()
    prepare(args.source.resolve(), not args.no_submodules)
