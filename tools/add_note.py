#!/usr/bin/env python3
"""Install a published note into the site.

Takes the self-contained HTML of a note (as published to an Artifact), files it
under the section it belongs to, records it in data/notes.json, and
rebuilds the hub.

    python3 tools/add_note.py --file note.html --topic llm-101 --section 2

Topic slugs and section numbers come from data/structure.json; run with --list to
see what is available.
"""
import argparse, datetime, json, os, re, subprocess, sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


def load(name):
    with open(os.path.join(ROOT, "data", name)) as f:
        return json.load(f)


def find_section(structure, topic_slug, n):
    for tr in structure["tracks"]:
        for t in tr["topics"]:
            if t["slug"] != topic_slug:
                continue
            for s in t["sections"]:
                if s["n"] == n:
                    return tr, t, s
            raise SystemExit(
                f"topic '{topic_slug}' has no section {n}. Sections: "
                + ", ".join(str(x["n"]) for x in t["sections"]))
    raise SystemExit(f"no topic '{topic_slug}'. Use --list to see them.")


def list_topics(structure):
    for tr in structure["tracks"]:
        print(f"\n{tr['name']}")
        for t in tr["topics"]:
            ns = ", ".join(str(s["n"]) for s in t["sections"])
            print(f"  {t['slug']:<28} sections {ns}")


def title_of(src):
    m = re.search(r"<title>(.*?)</title>", src, re.S | re.I)
    return m.group(1).strip() if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", help="self-contained note HTML")
    ap.add_argument("--topic", help="topic slug")
    ap.add_argument("--section", type=int, help="section number within the topic")
    ap.add_argument("--artifact", help="artifact URL, recorded for later re-syncing")
    ap.add_argument("--list", action="store_true", help="list topics and exit")
    a = ap.parse_args()

    structure = load("structure.json")
    if a.list:
        list_topics(structure)
        return
    if not (a.file and a.topic and a.section):
        ap.error("--file, --topic and --section are required")

    tr, t, s = find_section(structure, a.topic, a.section)
    src = open(os.path.expanduser(a.file)).read()

    rel = os.path.join("notes", t["slug"], s["slug"])
    dest = os.path.join(ROOT, rel)
    os.makedirs(dest, exist_ok=True)
    with open(os.path.join(dest, "index.html"), "w") as f:
        f.write(src)

    notes_path = os.path.join(ROOT, "data", "notes.json")
    data = load("notes.json") if os.path.exists(notes_path) else {"notes": []}
    entry = {
        "topic": t["slug"],
        "section": s["n"],
        "title": title_of(src) or s["name"],
        "path": rel.replace(os.sep, "/"),
        "track": tr["slug"],
        "added": datetime.date.today().isoformat(),
    }
    if a.artifact:
        entry["artifact"] = a.artifact

    data["notes"] = [n for n in data["notes"]
                     if not (n["topic"] == entry["topic"] and n["section"] == entry["section"])]
    data["notes"].append(entry)
    data["notes"].sort(key=lambda n: (n["track"], n["topic"], n["section"]))
    with open(notes_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"installed  {entry['title']}\n        ->  {rel}/")
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "build_index.py")], check=True)


if __name__ == "__main__":
    main()
