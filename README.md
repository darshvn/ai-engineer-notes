# AI Engineer Notes

Study notes written while working through the CampusX AI Engineer roadmap.
One note per roadmap section. Live at
**<https://darshvn.github.io/ai-engineer-notes/>**.

Each note gives every idea twice — once in prose, once as a diagram of the
mechanism — and closes with a retrieval bank instead of a summary. That format
is deliberate: Dunlosky et al. (2013) rate re-reading and summarisation as
*low utility* and retrieval practice and spacing as the only two *high utility*
techniques, so the notes are built to be answered from memory, not re-read.

## Layout

```
index.html                      generated hub — roadmap tree and progress
notes/<topic>/<nn>-<slug>/      one directory per note, self-contained HTML
assets/hub.css                  styling for the hub only
data/roadmap.json               roadmap structure + progress, derived from the workbook
data/notes.json                 which sections have notes, and where they live
tools/                          the three scripts below
```

Notes carry their own CSS inline rather than linking a shared stylesheet. That
keeps each page standalone, so any note can be opened on its own or embedded in
Notion without depending on the rest of the site. The trade-off is that a
restyle means regenerating the notes from their sources rather than editing one
file.

## Adding a note

```bash
python3 tools/add_note.py --file note.html --topic llm-101 --section 2
```

Files the HTML under the right section, records it in `data/notes.json`, and
rebuilds the hub. `--list` prints the available topic slugs and section numbers.

## Updating progress

The roadmap workbook is a personal tracker and stays out of this repo; only the
derived JSON is committed.

```bash
python3 tools/import_roadmap.py "~/Downloads/CampusX AI Roadmap (1).xlsx"
python3 tools/build_index.py
```

## Rebuilding

```bash
python3 tools/build_index.py
```

Regenerates `index.html` and refreshes the navigation chrome inside every note.
Chrome is regenerated rather than baked in once, so prev/next links stay correct
as new notes land.

## Embedding a note in Notion

Paste the note's URL into a Notion page and choose **Create embed**. Notion's
embed block takes a URL, never raw HTML, and the page must permit framing —
GitHub Pages sends no `X-Frame-Options` or CSP, so these pages embed cleanly.
Each note has a theme toggle because an iframe follows the operating system's
colour scheme rather than Notion's own.
