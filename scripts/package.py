"""Package Windows binaries with their corresponding patched source."""
import json
import shutil
import subprocess
import tarfile

from prepare import COMMIT, ROOT, apply_branding


def package():
    source = ROOT / ".cache" / "azahar"
    bundle = ROOT / "build" / "windows" / "bundle"
    apply_branding(source)
    for name in ("Denimulator3.exe", "platforms/qwindows.dll"):
        if not (bundle / name).is_file():
            raise RuntimeError(f"Missing {name}; build and bundle first")
    stage = ROOT / "dist" / "Denimulator3-windows-x64"
    if stage.exists():
        raise RuntimeError(f"{stage} exists; move it aside before packaging again")
    stage.parent.mkdir(exist_ok=True)
    shutil.copytree(bundle, stage)
    for name in ("LICENSE", "README.md", "THIRD_PARTY.md"):
        shutil.copy2(ROOT / name, stage / name)
    (stage / "BUILD-INFO.json").write_text(json.dumps({
        "name": "Denimulator3", "upstream": "Azahar 2123.3",
        "upstream_commit": COMMIT,
    }, indent=2) + "\n", encoding="utf-8")
    files = subprocess.check_output(
        ["git", "ls-files", "--recurse-submodules", "-z"], cwd=source
    ).decode().split("\0")
    with tarfile.open(stage / "corresponding-source.tar.gz", "w:gz") as archive:
        for name in filter(None, files):
            archive.add(source / name, arcname="azahar/" + name, recursive=False)
        for name in ("scripts", "patches", "tests", ".github", "README.md", "THIRD_PARTY.md", "LICENSE"):
            archive.add(ROOT / name, arcname="denimulator3/" + name,
                        filter=lambda info: None if "__pycache__" in info.name else info)
    shutil.make_archive(str(stage), "zip", stage.parent, stage.name)
    print(f"Package: {stage}.zip")


if __name__ == "__main__":
    package()
