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
/* the site follows the system light/dark setting; drop any choice saved by the old toggle */
try{localStorage.removeItem('aen-theme')}catch(e){}
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
  .note-chrome{{font-size:14px;color:var(--muted)}}
  .note-chrome .inner{{max-width:720px;margin:0 auto;padding:20px 20px 0;
    display:flex;flex-wrap:wrap;gap:6px 18px;align-items:baseline}}
  .note-chrome a{{color:var(--muted);text-decoration:none}}
  .note-chrome a:hover{{color:var(--ink)}}
  .note-chrome .spacer{{flex:1 1 auto}}
  .nav-adj{{display:inline-flex;gap:6px;align-items:baseline;max-width:220px}}
  .nav-t{{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
  @media print{{.note-chrome{{display:none}}}}
</style>
<nav class="note-chrome"><div class="inner">
  <a href="../../../">Notes</a>
  <span class="crumb">{e(t['name'])} &middot; &sect;{s['n']}</span>
  <span class="spacer"></span>
  {link(prev, '&larr;')}
  {link(nxt, '&rarr;')}
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
<meta name="description" content="Study notes on Python and language models, with runnable exercises.">
<link rel="stylesheet" href="assets/hub.css?v={asset_version("assets/hub.css")}">
</head>
<body>
<div class="wrap">
<header class="mast">
  <h1>AI Engineer Notes</h1>
</header>
{chr(10).join(parts)}
</div>
{TOGGLE_JS}
<script src="assets/gate.js"></script>\n</body>
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
