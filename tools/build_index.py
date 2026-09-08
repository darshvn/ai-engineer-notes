#!/usr/bin/env python3
"""Generate index.html from data/roadmap.json + data/notes.json, and refresh the
navigation chrome inside every note page.

Chrome lives between CHROME markers inside each note so it can be regenerated as
new notes land — otherwise prev/next links would freeze at whatever existed when
the note was first added.

    python3 tools/build_index.py
"""
import html, json, os, re, datetime

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


def index_sections(roadmap):
    """Flatten to {(topic_slug, n): (track, topic, section)} for quick lookup."""
    out = {}
    for tr in roadmap["tracks"]:
        for t in tr["topics"]:
            for s in t["sections"]:
                out[(t["slug"], s["n"])] = (tr, t, s)
    return out


# ---------------------------------------------------------------- note chrome

def chrome_for(note, notes_by_topic, lookup):
    tr, t, s = lookup[(note["topic"], note["section"])]
    siblings = sorted(notes_by_topic[note["topic"]], key=lambda x: x["section"])
    i = next(k for k, x in enumerate(siblings) if x["section"] == note["section"])
    prev = siblings[i - 1] if i > 0 else None
    nxt = siblings[i + 1] if i < len(siblings) - 1 else None

    def link(n, label):
        if not n:
            return ""
        _, _, ns = lookup[(n["topic"], n["section"])]
        href = f"../../{n['topic']}/{ns['slug']}/"
        return (f'<a class="nav-adj" href="{e(href)}">'
                f'<span class="nav-dir">{label}</span>'
                f'<span class="nav-t">&sect;{ns["n"]} {e(ns["name"])}</span></a>')

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
  .nav-adj{{display:inline-flex;gap:7px;align-items:baseline;max-width:280px}}
  .nav-dir{{color:var(--muted)}}
  .nav-t{{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
  #theme-toggle{{font-family:var(--f-mono);font-size:11px;letter-spacing:.08em;
    text-transform:uppercase;font-weight:600;color:var(--muted);background:transparent;
    border:1px solid var(--rule);border-radius:2px;padding:5px 9px;cursor:pointer;line-height:1}}
  #theme-toggle:hover{{color:var(--accent);border-color:var(--accent)}}
  @media print{{.note-chrome{{display:none}}}}
</style>
<nav class="note-chrome"><div class="inner">
  <a href="../../../">&larr; All notes</a>
  <span class="crumb">{e(tr['name'])} / {e(t['name'])} / <b>&sect;{s['n']}</b></span>
  <span class="spacer"></span>
  {link(prev, '&larr; Prev')}
  {link(nxt, 'Next &rarr;')}
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
            new = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, src, flags=re.S)
        else:
            new = src.replace("<body>", "<body>\n" + block, 1)
            if new == src:                      # no <body> tag — fall back to prepend
                new = block + "\n" + src
        if new != src:
            open(path, "w").write(new)
            touched += 1
    return touched


# ------------------------------------------------------------------- the hub

def build_hub(roadmap, notes):
    have = {(n["topic"], n["section"]): n for n in notes}
    parts = []

    for tr in roadmap["tracks"]:
        tr_notes = sum(1 for t in tr["topics"] for s in t["sections"]
                       if (t["slug"], s["n"]) in have)
        parts.append(f'<section class="track">\n<h2>{e(tr["name"])}</h2>')
        parts.append(
            f'<p class="track-sub">{len(tr["topics"])} topics &middot; '
            f'{sum(len(t["sections"]) for t in tr["topics"])} sections &middot; '
            f'{tr["hours_done"]:g} / {tr["hours"]:g} hrs &middot; '
            f'{tr_notes} note{"" if tr_notes == 1 else "s"} written</p>')

        for t in tr["topics"]:
            n_notes = sum(1 for s in t["sections"] if (t["slug"], s["n"]) in have)
            pct = (t["hours_done"] / t["hours"] * 100) if t["hours"] else 0
            # topics we've actually touched open by default; the rest stay folded
            # so the page reads as a dashboard instead of a 181-row wall
            openattr = " open" if n_notes or t["hours_done"] else ""
            rows = []
            for s in t["sections"]:
                note = have.get((t["slug"], s["n"]))
                name = e(s["name"])
                if note:
                    name = f'<a href="{e(note["path"])}/">{name}</a>'
                pill = ""
                if s["complete"]:
                    pill = '<span class="pill" style="color:var(--accent)">done</span>'
                elif s["done"]:
                    pill = f'<span class="pill">{s["done"]}/{s["total"]}</span>'
                rows.append(
                    f'<li class="{"has-note" if note else ""}">'
                    f'<span class="sec-n">{s["n"]:02d}</span>'
                    f'<span class="sec-name">{name}{pill}</span>'
                    f'<span class="sec-meta">{s["hours"]:g}h</span></li>')
            parts.append(
                f'<details class="topic"{openattr}><summary>'
                f'<span class="topic-name"><span class="caret">&#9656;</span>{e(t["name"])}</span>'
                f'<span class="topic-stat">{n_notes or "&mdash;"} notes &middot; '
                f'{t["hours_done"]:g}/{t["hours"]:g} h</span>'
                f'<span class="bar{"" if pct else " none"}"><i style="width:{pct:.1f}%"></i></span>'
                f'</summary>\n<ul class="sections">\n' + "\n".join(rows) +
                '\n</ul>\n</details>')
        parts.append("</section>")

    total_notes = len(notes)
    total_secs = sum(len(t["sections"]) for tr in roadmap["tracks"] for t in tr["topics"])
    pct = roadmap["hours_done"] / roadmap["hours"] * 100 if roadmap["hours"] else 0

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI Engineer Notes</title>
<meta name="description" content="Study notes built while working through the CampusX AI Engineer roadmap — one note per roadmap section, each in prose and diagrams.">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;450;500;600&display=swap">
<link rel="stylesheet" href="assets/hub.css">
</head>
<body>
<button id="theme-toggle" type="button">Theme</button>
<div class="wrap">
<header class="mast">
  <div class="eyebrow">CampusX AI Engineer Roadmap</div>
  <h1>AI Engineer Notes</h1>
  <p class="standfirst">One note per roadmap section &mdash; each idea written out in prose, drawn as the mechanism it actually is, and closed with a retrieval bank rather than a summary to re-read.</p>
  <div class="meta-strip">
    <div><span class="meta-k">Notes written</span><span class="meta-v">{total_notes} / {total_secs}</span></div>
    <div><span class="meta-k">Hours done</span><span class="meta-v">{roadmap['hours_done']:g} / {roadmap['hours']:g}</span></div>
    <div><span class="meta-k">Progress</span><span class="meta-v">{pct:.1f}%</span></div>
    <div><span class="meta-k">Updated</span><span class="meta-v">{datetime.date.today().isoformat()}</span></div>
  </div>
</header>
{chr(10).join(parts)}
<footer>
  <span>AI Engineer Notes</span>
  <span>Roadmap data generated {e(roadmap['generated'])}</span>
  <span>Retrieval-practice format after Dunlosky et al. 2013</span>
</footer>
</div>
{TOGGLE_JS}
</body>
</html>
"""


def main():
    roadmap, notes = load("roadmap.json"), load("notes.json")["notes"]
    lookup = index_sections(roadmap)
    notes = [n for n in notes if (n["topic"], n["section"]) in lookup]

    touched = refresh_chrome(notes, lookup)
    with open(os.path.join(ROOT, "index.html"), "w") as f:
        f.write(build_hub(roadmap, notes))
    print(f"built index.html  ({len(notes)} notes linked, chrome refreshed in {touched})")


if __name__ == "__main__":
    main()
