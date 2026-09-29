"""release_sample.py - builds the zip of ONE sample for its GitHub release.

    python tools/release_sample.py excel-range-to-html-table-v1.0.0

The tag is <sample id>-v<version>. The script checks that samples/<id>/sample.yml carries that version and that
CHANGELOG.md has its section, then writes:
    dist/<id>-v<version>.zip     the folder samples/<id>/ as <id>/... (extract it anywhere, the flow files are in flow/)
    dist/<id>-v<version>.md      the release notes: the CHANGELOG section of this version
In GitHub Actions it also sets the step outputs zip, notes and title.
"""
import os
import re
import sys
import zipfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def fail(message):
    print(f"FAIL {message}")
    sys.exit(1)


def main():
    if len(sys.argv) != 2:
        fail("usage: python tools/release_sample.py <sample id>-v<x.y.z>")
    tag = sys.argv[1]
    m = re.fullmatch(r"(.+)-v(\d+\.\d+\.\d+)", tag)
    if not m:
        fail(f"tag '{tag}' is not <sample id>-v<x.y.z>")
    sample_id, version = m.group(1), m.group(2)
    folder = ROOT / "samples" / sample_id
    if not (folder / "sample.yml").exists():
        fail(f"no sample '{sample_id}' (samples/{sample_id}/sample.yml)")
    card = yaml.safe_load((folder / "sample.yml").read_text(encoding="utf-8"))
    if str(card.get("version")) != version:
        fail(f"sample.yml says version {card.get('version')}, the tag says {version}: change one of them")
    changelog = (folder / "CHANGELOG.md").read_text(encoding="utf-8") if (folder / "CHANGELOG.md").exists() else ""
    section = re.search(rf"^## {re.escape(version)}\b.*?(?=^## |\Z)", changelog, re.M | re.S)
    if not section:
        fail(f"CHANGELOG.md has no section '## {version}'")

    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    name = f"{sample_id}-v{version}"
    zip_path = dist / f"{name}.zip"
    files = sorted((p for p in folder.rglob("*") if p.is_file()), key=lambda p: p.relative_to(folder).as_posix().lower())
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files:
            z.write(p, f"{sample_id}/{p.relative_to(folder).as_posix()}")
    notes_path = dist / f"{name}.md"
    title = f"{card['title']} {version}"
    notes = [section.group(0).strip(), "",
             f"Tested on Power Automate Desktop {card['tested'][-1]['pad']} ({card['tested'][-1]['date']}).", "",
             f"**Start here:** [the setup page](https://github.com/PowerAutomateDesktop-CopilotStudio/pad-samples/blob/{tag}/samples/{sample_id}/SETUP.md) "
             f"begins with the lightest way to try it. The zip holds the same folder.", "",
             "For e-learning purposes: try it in a test environment and review it before any real use."]
    notes_path.write_text("\n".join(notes) + "\n", encoding="utf-8")
    print(f"ok   {zip_path.relative_to(ROOT)}: {len(files)} files ; notes {notes_path.relative_to(ROOT)}")

    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write(f"zip={zip_path}\nnotes={notes_path}\ntitle={title}\n")


if __name__ == "__main__":
    main()
