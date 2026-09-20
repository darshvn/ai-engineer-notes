#!/usr/bin/env python3
"""Turn the roadmap workbook into data/roadmap.json for the browser app.

Reads every row of both sheets: the hierarchy (topic / heading / subheading /
item), status, hours and target date, plus the resource columns that hold the
label, type and link, the "Also read" link and the note.

    python3 tools/export_roadmap.py [path/to/workbook.xlsx]

Defaults to ~/Downloads/CampusX AI Roadmap(2).xlsx. Pass --sheet-url to record
where the live Google Sheet lives, so the app can offer a link back to it.
"""
import argparse, datetime, json, os, sys

try:
    import openpyxl
except ImportError:                                           # pragma: no cover
    sys.exit("openpyxl missing: pip install openpyxl, or run with uvx --with openpyxl python")

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT = os.path.expanduser("~/Downloads/CampusX AI Roadmap(2).xlsx")
COLS = dict(name=1, status=2, hours=3, target=4, label=5, type=6, link=7, kind=9, also=10, note=11)


def cell(row, key):
    i = COLS[key] - 1
    return row[i] if i < len(row) else None


def clean(v):
    if v is None:
        return None
    if isinstance(v, datetime.datetime):
        return v.date().isoformat()
    if isinstance(v, float) and v.is_integer():
        return int(v)
    v = str(v).strip()
    return v or None


def resource(row):
    label, kind, link = (clean(cell(row, k)) for k in ("label", "type", "link"))
    if not (label or link):
        return None
    return {"label": label, "type": kind or ("note" if not link else "link"), "url": link}


def export(path, sheet_url=None):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    tracks = []
    for ws in wb.worksheets:
        track = {"name": ws.title, "topics": []}
        topic = section = sub = None
        for n, row in enumerate(ws.iter_rows(values_only=True), 1):
            kind, name = clean(cell(row, "kind")), clean(cell(row, "name"))
            if not kind or kind == "_Kind" or not name:
                continue
            common = {"row": n, "name": name}
            if kind == "topic":
                # The sheets repeat the track name as a topic row; keep real topics only.
                topic = {**common, "sections": []}
                track["topics"].append(topic)
                section = sub = None
            elif kind in ("heading", "subheading") and topic is not None:
                node = {**common, "items": []}
                if kind == "heading":
                    section, sub = node, None
                    topic["sections"].append(section)
                else:
                    sub = node
                    (section or topic).setdefault("subsections", []).append(sub)
            elif kind in ("item", "link", "note"):
                entry = {
                    **common, "kind": kind,
                    "status": clean(cell(row, "status")),
                    "hours": clean(cell(row, "hours")),
                    "target": clean(cell(row, "target")),
                    "resource": resource(row),
                    "also": clean(cell(row, "also")),
                    "note": clean(cell(row, "note")),
                }
                target = sub or section
                if target is None:                 # stray rows before any heading
                    section = {"row": n, "name": topic["name"] if topic else track["name"], "items": []}
                    (topic or track).setdefault("sections", []).append(section)
                    target = section
                target["items"].append(entry)
        track["topics"] = [t for t in track["topics"] if t["sections"] or t.get("subsections")]
        tracks.append(track)

    data = {"generated": datetime.date.today().isoformat(), "source": os.path.basename(path),
            "sheet_url": sheet_url, "tracks": tracks}
    out = os.path.join(ROOT, "data", "roadmap.json")
    with open(out, "w") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)

    items = [i for t in tracks for tp in t["topics"] for s in tp["sections"]
             for i in s["items"] + [x for sub in s.get("subsections", []) for x in sub["items"]]]
    print(f"{out}: {len(tracks)} tracks, {sum(len(t['topics']) for t in tracks)} topics, "
          f"{len(items)} rows, {sum(1 for i in items if i['resource'])} with a resource, "
          f"{sum(1 for i in items if i['note'])} with a note")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("workbook", nargs="?", default=DEFAULT)
    ap.add_argument("--sheet-url", default=None)
    a = ap.parse_args()
    export(a.workbook, a.sheet_url)
