"""build_site.py - builds the GitHub Pages site from the pages of the repository.

    python tools/build_site.py          # site_src/ (the pages, ready for MkDocs) then site/ (the HTML), strict build

Nothing is written twice: the gallery, the sample pages, Start here, the guides and CONTRIBUTING are the very files of the
repository (tools/build_docs.py writes the sample pages). This script only:
  - copies them into site_src/ (README.md stays README.md: MkDocs makes it the index of its folder),
  - adds to each sample page the front matter read from its sample.yml: the description (search engines),
  - lets MkDocs read the Markdown inside <details> blocks (the code of each subflow),
  - turns a link to a file that is not on the site (templates/, .github/ ...) into a link to the repository on GitHub,
  - writes the navigation (samples grouped by category) and runs 'mkdocs build --strict'.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "site_src"
REPO_BLOB = "https://github.com/PowerAutomateDesktop-CopilotStudio/pad-samples/blob/main"
REPO_TREE = "https://github.com/PowerAutomateDesktop-CopilotStudio/pad-samples/tree/main"
LINK = re.compile(r"(\]\()([^)\s]+)(\))|(\b(?:src|href)=\")([^\"]+)(\")")

SITE_CSS = """/* pad-samples site: small touches on top of Material */
.md-typeset table img { border-radius: 4px; }
.md-typeset details { font-size: .78rem; }
.md-typeset .md-typeset__table { width: 100%; }
.md-typeset h1 { font-weight: 600; }
/* a variable name is read and typed whole: never cut it */
.md-typeset td:first-child code { white-space: nowrap; }
/* long Robin lines wrap on screen; the copy button still copies each line as one line */
.md-typeset pre > code { white-space: pre-wrap; word-break: break-word; }
"""



def copy_pages():
    if SRC.exists():
        shutil.rmtree(SRC)
    SRC.mkdir()
    for name in ("README.md", "START-HERE.md", "TECHNIQUES.md", "CONTRIBUTING.md", "LICENSE", "samples.json"):
        shutil.copy2(ROOT / name, SRC / name)
    shutil.copytree(ROOT / "docs", SRC / "docs")
    shutil.copytree(ROOT / "samples", SRC / "samples")
    (SRC / "assets").mkdir()
    (SRC / "assets" / "site.css").write_text(SITE_CSS, encoding="utf-8")



def front_matter(card):
    """The description for search engines. Samples are grouped by technique (TECHNIQUES.md), not by tags."""
    return "---\n" + yaml.safe_dump({"description": card["summary"]}, sort_keys=False, allow_unicode=True) + "---\n\n"


def fix_links(md_path: Path, text: str) -> str:
    """A relative link to a file that is not on the site points to the repository on GitHub instead."""
    def repl(m):
        pre, target, post = (m.group(1), m.group(2), m.group(3)) if m.group(1) else (m.group(4), m.group(5), m.group(6))
        if re.match(r"^(https?:|mailto:|#|/)", target):
            return m.group(0)
        path, _, anchor = target.partition("#")
        resolved = (md_path.parent / path).resolve()
        if resolved.is_file():   # a folder is not a page of the site: it opens on GitHub
            # MkDocs serves X.md as X/index.html: it rewrites Markdown links, not the src / href of raw HTML
            if m.group(4) and md_path.name != "README.md":
                return f"{pre}../{target}{post}"
            return m.group(0)
        try:
            rel = (ROOT / md_path.parent.relative_to(SRC) / path).resolve().relative_to(ROOT).as_posix()
        except ValueError:
            return m.group(0)
        base = REPO_TREE if (ROOT / rel).is_dir() else REPO_BLOB
        return f"{pre}{base}/{rel}{'#' + anchor if anchor else ''}{post}"
    return LINK.sub(repl, text)


def prepare_markdown():
    cards = []
    for md in sorted(SRC.rglob("*.md"), key=lambda p: p.as_posix().lower()):
        text = md.read_text(encoding="utf-8")
        text = text.replace("<details>", '<details markdown="1">')
        text = fix_links(md, text)
        card_path = md.parent / "sample.yml"
        if md.name == "README.md" and card_path.exists():
            card = yaml.safe_load(card_path.read_text(encoding="utf-8"))
            text = front_matter(card) + text
            cards.append((card, md.relative_to(SRC).as_posix()))
        md.write_text(text, encoding="utf-8")
    return cards


def write_config(cards):
    by_category = {}
    for card, rel in cards:
        pages = [{"Overview": rel}, {"Setup": rel.rsplit("/", 1)[0] + "/SETUP.md"}]
        by_category.setdefault(card["category"], []).append({card["title"]: pages})
    nav = [
        {"Samples": [{"Gallery": "README.md"}] + [{cat: sorted(items, key=lambda d: list(d)[0])} for cat, items in sorted(by_category.items())]},
        {"Techniques": "TECHNIQUES.md"},
        {"How it is organised": "START-HERE.md"},
        {"PAD basics": [
            {"Create a subflow": "docs/create-a-subflow.md"},
            {"Create input and output variables": "docs/create-variables.md"},
            {"Sensitive values": "docs/sensitive-values.md"},
            {"Troubleshooting a paste": "docs/troubleshooting.md"},
        ]},

        {"Copilot Studio samples": "https://powerautomatedesktop-copilotstudio.github.io/copilot-studio-samples/"},
        {"Contribute": "CONTRIBUTING.md"},
    ]
    config = ROOT / ".site.yml"
    config.write_text("# Generated by tools/build_site.py: the navigation of the site. Settings live in mkdocs.yml.\n"
                      "INHERIT: mkdocs.yml\n" + yaml.safe_dump({"nav": nav}, sort_keys=False, allow_unicode=True),
                      encoding="utf-8")
    return config


def main():
    copy_pages()
    cards = prepare_markdown()
    config = write_config(cards)
    print(f"ok   site_src/: {len(cards)} sample(s), {sum(1 for _ in SRC.rglob('*.md'))} pages")
    result = subprocess.run([sys.executable, "-m", "mkdocs", "build", "--strict", "-f", str(config)], cwd=ROOT)
    if result.returncode:
        print("FAIL mkdocs build --strict: read the warnings above (a broken link, a page missing from the navigation)")
        sys.exit(result.returncode)
    print(f"ok   site/: open site/index.html, or serve it: python -m http.server 8797 --directory site")


if __name__ == "__main__":
    main()
