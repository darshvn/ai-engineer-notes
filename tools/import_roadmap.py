#!/usr/bin/env python3
"""Derive data/roadmap.json from the CampusX roadmap workbook.

The workbook is a personal progress tracker and deliberately stays out of this
repo; only the derived JSON is committed. Re-run this whenever progress changes:

    python3 tools/import_roadmap.py "~/Downloads/CampusX AI Roadmap (1).xlsx"
"""
import json, os, re, sys, datetime

SHEET_TRACKS = {"Basics": "Prerequisites", "AI Engineering": "AI Engineer Track"}
SKIP_SHEETS = {"Config"}


def slug(text):
    text = re.sub(r"^\s*\d+[.)]\s*", "", str(text))       # drop leading "1. "
    text = re.sub(r"\([^)]*\)", " ", text)                 # drop parentheticals
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return re.sub(r"-{2,}", "-", text)


def section_number(name):
    m = re.match(r"\s*(\d+)[.)]", str(name))
    return int(m.group(1)) if m else None


def cell(row, i):
    return row[i].value if i < len(row) else None


def parse(path):
    import openpyxl
    wb = openpyxl.load_workbook(path, data_only=True)
    tracks = []

    for ws in wb.worksheets:
        if ws.title in SKIP_SHEETS:
            continue
        track = {"name": SHEET_TRACKS.get(ws.title, ws.title),
                 "slug": slug(SHEET_TRACKS.get(ws.title, ws.title)),
                 "topics": []}
        topic = heading = None
        auto_n = 0

        for row in ws.iter_rows(min_row=2):
            name, status, hrs = cell(row, 0), cell(row, 1), cell(row, 2)
            kind = cell(row, 8)
            if not name or not kind:
                continue
            name = str(name).strip()

            if kind == "topic":
                # sheet-level banner rows repeat the track name; skip them
                if name == track["name"] or (track["topics"] and track["topics"][-1]["name"] == name):
                    continue
                topic = {"name": name, "slug": slug(name), "sections": []}
                heading, auto_n = None, 0
                track["topics"].append(topic)

            elif kind == "heading" and topic is not None:
                auto_n += 1
                n = section_number(name) or auto_n
                clean = re.sub(r"^\s*\d+[.)]\s*", "", name).strip()
                heading = {
                    "n": n,
                    "name": clean,
                    "slug": f"{n:02d}-{slug(clean)}",
                    "raw_progress": str(status).strip() if status else None,
                    "items": [],
                    "hours": 0.0,
                }
                topic["sections"].append(heading)

            elif kind == "item" and heading is not None:
                h = float(hrs) if isinstance(hrs, (int, float)) else 0.0
                heading["items"].append({
                    "name": name,
                    "status": (str(status).strip() if status else "Not started"),
                    "hours": h,
                })
                heading["hours"] = round(heading["hours"] + h, 2)

        # roll up counts
        for t in track["topics"]:
            for s in t["sections"]:
                done = sum(1 for i in s["items"] if i["status"].lower() == "done")
                s["done"] = done
                s["total"] = len(s["items"])
                s["hours_done"] = round(
                    sum(i["hours"] for i in s["items"] if i["status"].lower() == "done"), 2)
                s["complete"] = s["total"] > 0 and done == s["total"]
            t["hours"] = round(sum(s["hours"] for s in t["sections"]), 2)
            t["hours_done"] = round(sum(s["hours_done"] for s in t["sections"]), 2)
            t["sections_total"] = len(t["sections"])
            t["sections_complete"] = sum(1 for s in t["sections"] if s["complete"])
        track["topics"] = [t for t in track["topics"] if t["sections"]]
        track["hours"] = round(sum(t["hours"] for t in track["topics"]), 2)
        track["hours_done"] = round(sum(t["hours_done"] for t in track["topics"]), 2)
        tracks.append(track)

    return {
        "generated": datetime.date.today().isoformat(),
        "tracks": tracks,
        "hours": round(sum(t["hours"] for t in tracks), 2),
        "hours_done": round(sum(t["hours_done"] for t in tracks), 2),
    }


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
        "~/Downloads/CampusX AI Roadmap (1).xlsx")
    data = parse(os.path.expanduser(src))
    out = os.path.join(os.path.dirname(__file__), "..", "data", "roadmap.json")
    with open(out, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    n = sum(len(t["sections"]) for tr in data["tracks"] for t in tr["topics"])
    print(f"wrote {os.path.normpath(out)}")
    print(f"  {len(data['tracks'])} tracks, "
          f"{sum(len(t['topics']) for t in data['tracks'])} topics, {n} sections")
    print(f"  {data['hours_done']} / {data['hours']} hrs done")
