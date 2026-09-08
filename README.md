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

## Scripts

```bash
python3 tools/add_note.py --file note.html --topic python --section 1
python3 tools/build_index.py
```

`add_note.py` files a note under its section, records it, and rebuilds the
index; `--list` shows the available topic slugs. `build_index.py` regenerates
the index and refreshes the navigation inside every note, so prev/next links
stay correct as later notes land.
