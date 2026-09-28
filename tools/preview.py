"""preview.py - renders every .md of the repository to _preview/ as GitHub would show it (tables, alerts, mermaid,
copy buttons), so a page can be read before anything is published.   python tools/preview.py"""
import re
import shutil
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_preview"
ALERTS = {"NOTE": ("#0969da", "ℹ️ Note"), "TIP": ("#1a7f37", "💡 Tip"), "IMPORTANT": ("#8250df", "❗ Important"),
          "WARNING": ("#9a6700", "⚠️ Warning"), "CAUTION": ("#d1242f", "🛑 Caution")}
CSS = """
body{margin:0;background:#fff;color:#1f2328;font:16px/1.5 -apple-system,'Segoe UI',Helvetica,Arial,sans-serif}
.top{background:#f6f8fa;border-bottom:1px solid #d1d9e0;padding:12px 16px;font-size:14px;color:#59636e}
.top b{color:#1f2328}
main{max-width:980px;margin:24px auto;padding:32px;border:1px solid #d1d9e0;border-radius:6px}
h1,h2{border-bottom:1px solid #d1d9e0;padding-bottom:.3em}h1{font-size:2em}h2{font-size:1.5em;margin-top:24px}
a{color:#0969da;text-decoration:none}a:hover{text-decoration:underline}
code{background:#eff1f3;border-radius:6px;padding:.2em .4em;font:85% ui-monospace,Consolas,monospace}
pre{position:relative;background:#f6f8fa;border-radius:6px;padding:16px;overflow:auto;max-height:420px;font-size:85%}
pre code{background:none;padding:0}
table{border-collapse:collapse;display:block;overflow:auto;margin:16px 0}
th,td{border:1px solid #d1d9e0;padding:6px 13px;vertical-align:top}tr:nth-child(2n){background:#f6f8fa}th{font-weight:600}
img{max-width:100%}sub{color:#59636e}
details{margin:12px 0}summary{cursor:pointer;color:#0969da}
.alert{border-left:.25em solid;padding:4px 16px;margin:16px 0}.alert .t{font-weight:600;margin:8px 0 0}
blockquote{border-left:.25em solid #d1d9e0;color:#59636e;margin:0;padding:0 1em}
.copy{position:absolute;top:8px;right:8px;border:1px solid #d1d9e0;background:#fff;border-radius:6px;padding:3px 8px;cursor:pointer;font-size:12px}
.mermaid{background:#fff;text-align:center}
@media (max-width:700px){main{margin:0;border:0;padding:16px}}
"""
JS = """<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<script>
mermaid.initialize({startOnLoad:true,theme:'neutral',flowchart:{htmlLabels:true}});
document.querySelectorAll('pre').forEach(p=>{if(p.classList.contains('mermaid'))return;const b=document.createElement('button');
b.className='copy';b.textContent='Copy';b.onclick=()=>{navigator.clipboard.writeText(p.innerText.replace(/Copy$/,''));b.textContent='Copied';
setTimeout(()=>b.textContent='Copy',1500)};p.appendChild(b)});
</script>"""


def alerts(md):
    def rep(m):
        color, title = ALERTS[m.group(1)]
        body = re.sub(r"^> ?", "", m.group(2), flags=re.M)
        return f'<div class="alert" style="border-color:{color}" markdown="1"><p class="t" style="color:{color}">{title}</p>\n\n{body}\n</div>\n'
    return re.sub(r"^> \[!(\w+)\]\n((?:>.*\n?)+)", rep, md, flags=re.M)


def mermaids(md):
    return re.sub(r"```mermaid\n(.*?)```", lambda m: f'<pre class="mermaid">{m.group(1)}</pre>', md, flags=re.S)


def render(src: Path):
    md = src.read_text(encoding="utf-8")
    md = mermaids(alerts(md))
    html = markdown.markdown(md, extensions=["tables", "fenced_code", "md_in_html"])
    html = re.sub(r'href="([^"#:]+?)\.md(#[^"]*)?"', lambda m: f'href="{m.group(1)}.html{m.group(2) or ""}"', html)
    html = re.sub(r'href="([^"#:]*?)/"', r'href="\1/README.html"', html)
    rel = src.relative_to(ROOT)
    dst = OUT / rel.with_suffix(".html")
    dst.parent.mkdir(parents=True, exist_ok=True)
    crumbs = " / ".join(rel.parts)
    dst.write_text(f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{rel.stem} · pad-samples preview</title>
<style>{CSS}</style></head><body><div class="top">Local preview of <b>pad-samples</b> · {crumbs} · not published</div>
<main>{html}</main>{JS}</body></html>""", encoding="utf-8")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    for p in ROOT.rglob("*"):
        if "_preview" in p.parts or ".git" in p.parts:
            continue
        rel = p.relative_to(ROOT)
        if p.suffix == ".md":
            render(p)
        elif p.is_file() and p.suffix.lower() in (".png", ".jpg", ".gif", ".svg", ".txt", ".html", ".csv", ".xlsx", ".pdf", ".ps1", ".cs"):
            d = OUT / rel
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, d)
    print("preview:", OUT / "README.html")


if __name__ == "__main__":
    main()
