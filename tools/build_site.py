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
import datetime
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "site_src"
REPO_BLOB = "https://github.com/anne-automates/pad-samples/blob/main"
REPO_TREE = "https://github.com/anne-automates/pad-samples/tree/main"
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
/* Anne's logo stays in the header on narrow screens too (the theme hides it below 76.25em) */
@media screen and (max-width: 76.2344em) { .md-header__button.md-logo { display: inline-block; } .md-header__button.md-logo img { height: 1.6rem; } }
/* the gallery: one card per sample, a search box and one filter per category, in the style of the illustrations */
.ag-toolbar { display: flex; flex-wrap: wrap; gap: .8rem; align-items: center; justify-content: space-between; margin: 1.2rem 0 1.2rem; }
.ag-searchbox { flex: 1 1 15rem; max-width: 21rem; display: flex; align-items: center; gap: .5rem; padding: .35rem .7rem;
  border: 1px solid var(--md-default-fg-color--lightest); border-radius: .6rem; background: var(--md-default-bg-color);
  box-shadow: 0 .05rem .3rem rgba(63,81,181,.08); }
.ag-searchbox:focus-within { border-color: var(--md-primary-fg-color); }
.ag-search { flex: 1; border: 0; outline: 0; background: transparent; color: var(--md-default-fg-color); font: inherit; font-size: .75rem; }
.ag-icon { width: 1.1rem; height: 1.1rem; flex: none; filter: drop-shadow(0 .05rem .1rem rgba(0,0,0,.15)); }
.ag-filters { display: flex; flex-wrap: wrap; gap: .45rem; }
.md-typeset .ag-filter { display: inline-flex; align-items: center; gap: .4rem; border: 1px solid var(--md-default-fg-color--lightest);
  border-radius: 999px; padding: .28rem .75rem .28rem .4rem; background: var(--md-default-bg-color); color: var(--md-default-fg-color);
  cursor: pointer; font: inherit; font-size: .72rem; box-shadow: 0 .05rem .25rem rgba(0,0,0,.06); transition: all .15s; }
.md-typeset .ag-filter span { font-size: .62rem; color: var(--md-default-fg-color--light); background: var(--md-code-bg-color);
  border-radius: 999px; padding: 0 .4rem; }
.md-typeset .ag-filter:hover { border-color: var(--md-primary-fg-color--light); }
.md-typeset .ag-filter.is-active { border-color: var(--md-primary-fg-color); color: var(--md-primary-fg-color); font-weight: 700;
  box-shadow: 0 0 0 .1rem rgba(63,81,181,.15); }
.ag-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(15.5rem, 1fr)); gap: 1.3rem; }
.ag-card { position: relative; display: flex; flex-direction: column; background: var(--md-default-bg-color); border-radius: .8rem;
  border: 1px solid var(--md-default-fg-color--lightest); box-shadow: 0 .15rem .6rem rgba(63,81,181,.08); overflow: hidden;
  transition: transform .18s, box-shadow .18s; }
.ag-card:hover { transform: translateY(-.15rem); box-shadow: 0 .5rem 1.4rem rgba(63,81,181,.18); }
.ag-thumb { display: block; height: 10.5rem; background: #F6F7FB; border-bottom: 1px solid var(--md-default-fg-color--lightest); }
.ag-thumb img { width: 100%; height: 100%; object-fit: cover; display: block; }
.ag-thumb.is-cover img { object-position: center; }
.ag-thumb.is-shot img { object-position: left top; }
.ag-badge { position: absolute; top: 9.1rem; left: .9rem; width: 2.8rem; height: 2.8rem; border-radius: 50%;
  background: var(--md-default-bg-color); box-shadow: 0 .15rem .5rem rgba(0,0,0,.18); display: flex; align-items: center; justify-content: center; }
.md-typeset .ag-badge img { width: 1.6rem; height: 1.6rem; }
.ag-body { padding: 1.8rem 1rem .3rem; flex: 1; }
.md-typeset .ag-body h3 { margin: 0 0 .4rem; font-size: 1rem; line-height: 1.3; font-weight: 700; }
.md-typeset .ag-body h3 a { color: var(--md-primary-fg-color); }
.md-typeset .ag-body p { margin: 0 0 .6rem; font-size: .72rem; color: var(--md-default-fg-color--light);
  display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; }
.ag-chips { display: flex; flex-wrap: wrap; gap: .3rem; }
.ag-chip { display: inline-flex; align-items: center; gap: .3rem; font-size: .6rem; padding: .12rem .5rem; border-radius: 999px;
  background: var(--md-code-bg-color); color: var(--md-default-fg-color--light); }
.ag-chip .ag-icon { width: .85rem; height: .85rem; }
.ag-author { display: flex; align-items: center; gap: .6rem; padding: .7rem 1rem .9rem; font-size: .66rem; line-height: 1.35;
  border-top: 1px solid var(--md-default-fg-color--lightest); margin-top: .6rem; }
.ag-author img { width: 2rem; height: 2rem; border-radius: 50%; box-shadow: 0 .05rem .2rem rgba(0,0,0,.12); }
.ag-empty { color: var(--md-default-fg-color--light); }
"""

KIND_LABEL = {"flow": "End-to-end flow", "component": "Reusable component"}

# The lab's icons, in the style of the sample illustrations: a coloured tile with a darker lower edge (a hint of depth),
# a soft highlight and a white line glyph. One source for the site and for the home page (write_icons copies them).
ICON_SET = {   # name: (colour, lower edge, glyph drawn on a 24-unit grid)
    "excel":   ("#43A047", "#2E7D32", "M4 5h16v14H4z M4 10h16 M4 14.5h16 M10 5v14"),
    "email":   ("#3F51B5", "#283593", "M3.5 6h17v12h-17z M3.5 6.5 12 13l8.5-6.5"),
    "pdf":     ("#E53935", "#B71C1C", "M6 3h8l4 4v14H6z M14 3v4h4 M9 12h6 M9 16h6"),
    "web":     ("#00897B", "#00695C", "M12 3a9 9 0 1 0 0 18a9 9 0 1 0 0-18z M3 12h18 M12 3c3 3 3 15 0 18 M12 3c-3 3-3 15 0 18"),
    "desktop": ("#1E88E5", "#1565C0", "M3 5h18v14H3z M3 9h18 M6 7h.01 M9 7h.01"),
    "files":   ("#FFB300", "#FF8F00", "M3 6h6l2 2h10v11H3z"),
    "all":     ("#78909C", "#546E7A", "M5 5h5v5H5z M14 5h5v5h-5z M5 14h5v5H5z M14 14h5v5h-5z"),
    "quick":   ("#00897B", "#00695C", "M13 2 5 13h6l-1 9 8-11h-6z"),
    "full":    ("#3F51B5", "#283593", "M12 3l9 5-9 5-9-5z M3 13l9 5 9-5"),
    "own":     ("#43A047", "#2E7D32", "M8 3v5 M16 3v5 M5 8h14v3a7 7 0 0 1-14 0z M12 18v3"),
    "search":  ("#3F51B5", "#283593", "M10.5 4a6.5 6.5 0 1 0 0 13a6.5 6.5 0 1 0 0-13z M15.5 15.5 20 20"),
}
CATEGORY_ICON = {"Excel": "excel", "Email": "email", "PDF": "pdf", "Web": "web", "Desktop apps": "desktop", "Files & text": "files"}


def icon_svg(name):
    colour, edge, glyph = ICON_SET[name]
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">'
            '<defs><linearGradient id="h" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".28"/>'
            '<stop offset=".6" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>'
            f'<rect x="3" y="5" width="42" height="41" rx="11" fill="{edge}"/>'
            f'<rect x="3" y="2" width="42" height="41" rx="11" fill="{colour}"/>'
            '<rect x="3" y="2" width="42" height="41" rx="11" fill="url(#h)"/>'
            '<g transform="translate(12 10.5)" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="{glyph}"/></g></svg>\n')


def write_icons(folder: Path):
    folder.mkdir(parents=True, exist_ok=True)
    for name in ICON_SET:
        (folder / f"{name}.svg").write_text(icon_svg(name), encoding="utf-8")


def icon(name, cls="ag-icon"):
    return f'<img class="{cls}" src="assets/icons/{name}.svg" alt="" width="20" height="20">'
# the product logo on every card of this collection (the disclaimer states that the lab is not affiliated with Microsoft)
PAD_ICON = '<img src="docs/images/pad-logo.png" alt="" width="48" height="48">'
GALLERY_JS = """// The gallery: a search box and one filter per category. Without script, every card stays visible.
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".anne-gallery").forEach(g => {
    const search = g.querySelector(".ag-search"), cards = [...g.querySelectorAll(".ag-card")], empty = g.querySelector(".ag-empty");
    let category = "";
    const apply = () => {
      const words = (search.value || "").toLowerCase().split(/\\s+/).filter(Boolean);
      let shown = 0;
      cards.forEach(c => {
        const ok = (!category || c.dataset.category === category) && words.every(w => c.dataset.text.includes(w));
        c.hidden = !ok; shown += ok;
      });
      empty.hidden = shown > 0;
    };
    search.addEventListener("input", apply);
    g.querySelectorAll(".ag-filter").forEach(b => b.addEventListener("click", () => {
      g.querySelectorAll(".ag-filter").forEach(x => x.classList.toggle("is-active", x === b));
      category = b.dataset.filter; apply();
    }));
  });
});
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
    (SRC / "assets" / "gallery.js").write_text(GALLERY_JS, encoding="utf-8")
    write_icons(SRC / "assets" / "icons")


def gallery_html():
    """The cards of the website, newest first, from samples.json: picture, title, summary, category, author, date."""
    samples = json.loads((ROOT / "samples.json").read_text(encoding="utf-8"))["samples"]
    order = list(yaml.safe_load((ROOT / "categories.yml").read_text(encoding="utf-8")))
    labels = {k: v.get("label", v["title"]) for k, v in yaml.safe_load((ROOT / "techniques.yml").read_text(encoding="utf-8")).items()}
    cats = [c for c in order if any(s["category"] == c for s in samples)]
    e = html.escape
    count = {c: sum(1 for s in samples if s["category"] == c) for c in cats}
    out = ['## Samples', '', '<div class="anne-gallery">', '<div class="ag-toolbar">',
           f'<label class="ag-searchbox">{icon("search")}'
           '<input class="ag-search" type="search" placeholder="Search samples" aria-label="Search samples"></label>',
           '<div class="ag-filters" role="group" aria-label="Category">',
           f'<button type="button" class="ag-filter is-active" data-filter="">{icon("all")}All<span>{len(samples)}</span></button>']
    out += [f'<button type="button" class="ag-filter" data-filter="{e(c)}">{icon(CATEGORY_ICON.get(c, "all"))}{e(c)}<span>{count[c]}</span></button>'
            for c in cats]
    out += ['</div>', '</div>', '<div class="ag-grid">']
    for s in sorted(samples, key=lambda s: (s.get("released") or "", s["title"]), reverse=True):
        href = s["page"].rsplit("/", 1)[0] + "/"
        tech = [labels.get(t, t) for t in s.get("techniques", [])]
        text = " ".join([s["title"], s["summary"], s["category"], *tech, *s.get("requires", [])]).lower()
        date = datetime.date.fromisoformat(s["released"]).strftime("%b %d %Y") if s.get("released") else ""
        thumb, kind = (s["cover"], "is-cover") if s.get("cover") else (s["image"], "is-shot")
        out += [f'<article class="ag-card" data-category="{e(s["category"])}" data-text="{e(text)}">',
                f'<a class="ag-thumb {kind}" href="{href}" tabindex="-1" aria-hidden="true"><img src="{e(thumb)}" alt="" loading="lazy"></a>',
                f'<span class="ag-badge" title="Power Automate Desktop">{PAD_ICON}</span>',
                '<div class="ag-body">',
                f'<h3><a href="{href}">{e(s["title"])}</a></h3>',
                f'<p>{e(s["summary"])}</p>',
                '<div class="ag-chips">'
                f'<span class="ag-chip">{icon(CATEGORY_ICON.get(s["category"], "all"))}{e(s["category"])}</span>'
                f'<span class="ag-chip">{KIND_LABEL.get(s["kind"], s["kind"])}</span>'
                f'<span class="ag-chip">v{e(s["version"])}</span></div>',
                '</div>',
                '<div class="ag-author"><img src="docs/images/anne-favicon.png" alt="">'
                f'<span><b>Anne (AI agent)</b><br>Updated {date}</span></div>',
                '</article>']
    out += ['</div>', '<p class="ag-empty" hidden>No sample matches. Clear the search or choose All.</p>', '</div>']
    return "\n".join(out)



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
        if md == SRC / "README.md":   # after fix_links: the cards link to pages of the site, never to GitHub
            text = re.sub(r"<!-- gallery:start -->.*?<!-- gallery:end -->", lambda m: gallery_html(), text, flags=re.S)
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

        {"Copilot Studio samples": "https://anne-automates.github.io/copilot-studio-samples/"},
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
