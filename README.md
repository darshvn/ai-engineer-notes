# AI Engineer Notes

Notes on language models, Python, and the systems around them.
Read them at **<https://darshvn.github.io/ai-engineer-notes/>**.

Every idea appears twice — once in prose, once as a diagram of the mechanism —
and each note ends with a retrieval bank instead of a summary, so it is meant to
be answered from memory rather than re-read.

## Layout

```
index.html                  generated index
notes/<topic>/<nn>-<slug>/  one directory per note, self-contained HTML
assets/hub.css              styling for the index
data/structure.json         topic and section outline
data/notes.json             which notes exist and where they live
tools/                      the scripts below
```

Notes carry their CSS inline rather than linking a shared stylesheet, so any one
of them can be opened alone or embedded elsewhere without the rest of the site.

## Exercises

Every section of every note ends with a short script in `exercises/`, one per
section, named after the section it belongs to. Each one says what to predict
before you run it and ends with a change to try. The outputs quoted in the notes
are what these scripts actually print.

```bash
cd exercises
uv venv --python 3.11 .venv      # or: python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python llm-101/01/01_next_token_table.py
```

`requirements.txt` is pinned for an Intel Mac: PyTorch 2.2.2 is the last release
with x86_64 macOS wheels and needs Python 3.11 or older.

## Scripts

```bash
python3 tools/add_note.py --file note.html --topic python --section 1
python3 tools/build_index.py
```

`add_note.py` files a note under its section, records it, and rebuilds the
index; `--list` shows the available topic slugs. `build_index.py` regenerates
the index and refreshes the navigation inside every note, so prev/next links
stay correct as later notes land.

Diagrams are hand-authored SVG with absolute coordinates, so a moved label can
land on top of something without anyone noticing. `tools/check_figures.js`
reports elements that escape their viewBox and text labels that collide:

```bash
agent-browser open <note url>
agent-browser eval "$(cat tools/check_figures.js)"
```
