#!/usr/bin/env python3
"""Generate index.html from data/structure.json + data/notes.json, and refresh
the navigation chrome inside every note page.

The index lists notes only. Chrome lives between CHROME markers inside each note
so it can be regenerated as new notes land — otherwise prev/next links would
freeze at whatever existed when the note was first added.

    python3 tools/build_index.py
"""
import hashlib, html, json, os, re

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
START, END = "<!--CHROME:START-->", "<!--CHROME:END-->"

TOGGLE_JS = """<script>
(function(){var r=document.documentElement,b=document.getElementById('theme-toggle'),K='aen-theme';
function sd(){return !!(window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches)}
function ap(t){t?r.setAttribute('data-theme',t):r.removeAttribute('data-theme');
var d=t?t==='dark':sd();b.textContent=d?'Light':'Dark';
b.setAttribute('aria-label','Switch to '+(d?'light':'dark')+' theme')}
var s=null;try{s=localStorage.getItem(K)}catch(e){}ap(s);
b.addEventListener('click',function(){var c=r.getAttribute('data-theme'),
d=c?c==='dark':sd(),n=d?'light':'dark';ap(n);try{localStorage.setItem(K,n)}catch(e){}});})();
</script>"""


def load(name):
    with open(os.path.join(ROOT, "data", name)) as f:
        return json.load(f)


def e(s):
    return html.escape(str(s), quote=True)


def index_sections(structure):
    """Flatten to {(topic_slug, n): (track, topic, section)} for quick lookup."""
    return {(t["slug"], s["n"]): (tr, t, s)
            for tr in structure["tracks"]
            for t in tr["topics"]
            for s in t["sections"]}


# ---------------------------------------------------------------- note chrome

def chrome_for(note, by_topic, lookup):
    tr, t, s = lookup[(note["topic"], note["section"])]
    sibs = sorted(by_topic[note["topic"]], key=lambda x: x["section"])
    i = next(k for k, x in enumerate(sibs) if x["section"] == note["section"])
    prev = sibs[i - 1] if i > 0 else None
    nxt = sibs[i + 1] if i < len(sibs) - 1 else None

    def link(n, label):
        if not n:
            return ""
        _, _, ns = lookup[(n["topic"], n["section"])]
        return (f'<a class="nav-adj" href="../../{e(n["topic"])}/{e(ns["slug"])}/">'
                f'<span class="nav-dir">{label}</span>'
                f'<span class="nav-t">{e(n["title"])}</span></a>')

    return f"""{START}
<style>
  .note-chrome{{position:sticky;top:0;z-index:40;background:var(--surface);
    border-bottom:1px solid var(--rule);font-family:var(--f-mono);font-size:11.5px}}
  .note-chrome .inner{{max-width:940px;margin:0 auto;padding:10px 24px;
    display:flex;flex-wrap:wrap;gap:8px 20px;align-items:center}}
  .note-chrome a{{color:var(--accent);text-decoration:none}}
  .note-chrome a:hover{{text-decoration:underline}}
  .crumb{{color:var(--muted);letter-spacing:.06em}}
  .crumb b{{color:var(--ink);font-weight:600}}
  .note-chrome .spacer{{flex:1 1 auto}}
  .nav-adj{{display:inline-flex;gap:7px;align-items:baseline;max-width:260px}}
  .nav-dir{{color:var(--muted);white-space:nowrap}}
  .nav-t{{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
  #theme-toggle{{font-family:var(--f-mono);font-size:11px;letter-spacing:.08em;
    text-transform:uppercase;font-weight:600;color:var(--muted);background:transparent;
    border:1px solid var(--rule);border-radius:2px;padding:5px 9px;cursor:pointer;line-height:1}}
  #theme-toggle:hover{{color:var(--accent);border-color:var(--accent)}}
  @media print{{.note-chrome{{display:none}}}}
</style>
<nav class="note-chrome"><div class="inner">
  <a href="../../../">&larr; All notes</a>
  <span class="crumb">{e(t['name'])} / <b>&sect;{s['n']}</b></span>
  <span class="spacer"></span>
  {link(prev, '&larr;')}
  {link(nxt, '&rarr;')}
  <button id="theme-toggle" type="button">Theme</button>
</div></nav>
{TOGGLE_JS}
{END}"""


def refresh_chrome(notes, lookup):
    by_topic = {}
    for n in notes:
        by_topic.setdefault(n["topic"], []).append(n)

    touched = 0
    for n in notes:
        path = os.path.join(ROOT, n["path"], "index.html")
        if not os.path.exists(path):
            print(f"  ! missing {n['path']}")
            continue
        src = open(path).read()
        block = chrome_for(n, by_topic, lookup)
        if START in src and END in src:
            new = re.sub(re.escape(START) + r".*?" + re.escape(END),
                         lambda _: block, src, flags=re.S)
        else:
            new = src.replace("<body>", "<body>\n" + block, 1)
            if new == src:
                new = block + "\n" + src
        if new != src:
            open(path, "w").write(new)
            touched += 1
    return touched


# ------------------------------------------------------------------- the index

def asset_version(rel):
    """Short content hash, appended to the stylesheet link so a rebuild never
    serves a stale cached copy to someone who visited before."""
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        return "0"
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:8]


def build_index(structure, notes):
    have = {}
    for n in notes:
        have.setdefault(n["topic"], {})[n["section"]] = n

    parts = []
    for tr in structure["tracks"]:
        topics = [t for t in tr["topics"] if have.get(t["slug"])]
        if not topics:
            continue
        parts.append(f'<section class="track">\n<h2>{e(tr["name"])}</h2>')
        for t in topics:
            rows = []
            for s in t["sections"]:
                n = have[t["slug"]].get(s["n"])
                if not n:
                    continue
                rows.append(
                    f'<li>'
                    f'<span class="sec-n">&sect;{s["n"]}</span>'
                    f'<span class="sec-name">'
                    f'<a href="{e(n["path"])}/">{e(n["title"])}</a>'
                    f'<span class="sec-sub">{e(s["name"])}</span>'
                    f'</span></li>')
            parts.append(f'<div class="topic"><h3>{e(t["name"])}</h3>\n'
                         f'<ul class="sections">\n' + "\n".join(rows) + '\n</ul></div>')
        parts.append("</section>")

    if not parts:
        parts = ['<section class="track"><p class="empty">No notes yet.</p></section>']

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI Engineer Notes</title>
<meta name="description" content="Notes on language models, Python and the systems around them — each idea in prose and as a diagram, closing with a retrieval bank.">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;450;500;600&display=swap">
<link rel="stylesheet" href="assets/hub.css?v={asset_version("assets/hub.css")}">
</head>
<body>
<button id="theme-toggle" type="button">Theme</button>
<div class="wrap">
<header class="mast">
  <h1>AI Engineer Notes</h1>
  <p class="standfirst">Every idea written out in prose, drawn as the mechanism it actually is, and closed with a retrieval bank rather than a summary to re-read.</p>
</header>
{chr(10).join(parts)}
<footer><span>AI Engineer Notes</span></footer>
</div>
{TOGGLE_JS}
</body>
</html>
"""


def main():
    structure, notes = load("structure.json"), load("notes.json")["notes"]
    lookup = index_sections(structure)
    notes = [n for n in notes if (n["topic"], n["section"]) in lookup]

    touched = refresh_chrome(notes, lookup)
    with open(os.path.join(ROOT, "index.html"), "w") as f:
        f.write(build_index(structure, notes))
    print(f"built index.html  ({len(notes)} notes, chrome refreshed in {touched})")


if __name__ == "__main__":
    main()
