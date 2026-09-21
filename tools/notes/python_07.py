"""Python §7: File Handling & Serialization, as traditional notes."""
from notelib import *

TOPIC, SECTION = 'python', 7
TITLE = 'File Handling & Serialization'
DESCRIPTION = 'Python notes: text files, CSV and JSON, pickle, directories with os and pathlib, and logging to files.'
LEAD = 'Python · Section 7. Reading and writing files, CSV and JSON, pickle, working with directories, and logging to files.'
YT = 'https://www.youtube.com/watch?v=o-TAYRMQzIQ&t='

S = []   # (id, heading, html)

# ============================================================== 1. Text files
S.append(('s1', '1. Reading and writing text files', f'''
<p>Variables live in memory and disappear when the program ends. Files are how data survives. Working with a file always follows three steps: <strong>open</strong> it, <strong>read or write</strong>, then <strong>close</strong> it.</p>

<h3>Opening a file</h3>
<p><code>open(path, mode, encoding=...)</code> returns a <em>file object</em>. The file object keeps track of a <em>position</em> in the file, which moves forward as you read or write. The mode says what you intend to do:</p>
{table(['Mode', 'Meaning', 'If the file exists', 'If it doesn\'t'], [
    ['<code>"r"</code>', 'read (default)', 'reads from the start', '<code>FileNotFoundError</code>'],
    ['<code>"w"</code>', 'write', '<strong>empties it first</strong>', 'creates it'],
    ['<code>"a"</code>', 'append', 'writes at the end', 'creates it'],
    ['<code>"x"</code>', 'create', '<code>FileExistsError</code>', 'creates it'],
    ['<code>"b"</code> suffix', 'binary (bytes, not text)', 'e.g. <code>"rb"</code>, <code>"wb"</code>', ''],
])}

<h3>Writing</h3>
{code("""
with open("notes.txt", "w", encoding="utf-8") as f:
    print(f.write("tokens\\n"))
    f.write("embeddings\\n")

with open("notes.txt", "a", encoding="utf-8") as f:
    f.write("attention\\n")

print(open("notes.txt", encoding="utf-8").read())
""")}
<ul class="points">
  <li><code>write()</code> returns the number of characters written (7 here, counting the newline).</li>
  <li>It writes exactly what you give it. Unlike <code>print()</code> it adds no newline, so put <code>\\n</code> in yourself.</li>
  <li><code>writelines(lines)</code> writes a list (or any iterable) of strings in one call, again without adding newlines.</li>
</ul>

<h3>Reading</h3>
{table(['Method', 'Returns', 'Use when'], [
    ['<code>f.read()</code>', 'the whole file as one string', 'the file is small'],
    ['<code>f.read(n)</code>', 'the next <em>n</em> characters', 'reading in chunks'],
    ['<code>f.readline()</code>', 'the next line', 'you need one line at a time'],
    ['<code>f.readlines()</code>', 'a list of all lines', 'the file is small and you want a list'],
    ['<code>for line in f:</code>', 'one line per loop', 'the file may be large (the usual choice)'],
])}
{code("""
open("notes.txt", "w", encoding="utf-8").write("tokens\\nembeddings\\nattention\\n")

with open("notes.txt", encoding="utf-8") as f:
    for n, line in enumerate(f, start=1):
        print(n, repr(line))
    print("at the end:", repr(f.read()))
""")}
<p>Each line keeps its trailing <code>\\n</code>; use <code>line.rstrip("\\n")</code> to drop it. At the end of the file <code>read()</code> returns an empty string rather than raising an error, which is how loops know to stop.</p>
<p>Memory matters for big files. On a 50 MB test file of 100-character lines, <code>read()</code> held all 50,000,000 characters at once, while <code>for line in f</code> held one 100-character line at a time.</p>

<h3>Closing, and why <code>with</code> is used</h3>
<p>Writes don't go straight to disk. They collect in a buffer of 8,192 bytes and are written out when the buffer fills or the file is closed:</p>
{code("""
import os
f = open("buf.txt", "w", encoding="utf-8")
f.write("Hello world")
print("before close:", os.path.getsize("buf.txt"), "bytes")
f.close()
print("after close: ", os.path.getsize("buf.txt"), "bytes")
""")}
<p>So a file that's never closed can lose its last writes. A <code>with</code> block closes the file automatically when the block ends, even if an exception happens inside it, which is why it's the standard way to open files.</p>

<h3>Encoding</h3>
<p>Text files are stored as bytes, and the encoding is the rule for converting between characters and bytes. Without <code>encoding=</code>, Python uses the operating system's default: UTF-8 on this Mac, but often cp1252 on Windows. A file containing "₹" or Hindi text can then fail to open on another machine. Always pass <code>encoding="utf-8"</code>.</p>

<h3>Key points</h3>
{ul(['Use <code>with open(...) as f:</code> so files are always closed.',
     '<code>"w"</code> erases an existing file as soon as it opens; <code>"a"</code> adds to it; <code>"x"</code> refuses to overwrite.',
     'Always specify <code>encoding="utf-8"</code> for text files.',
     'Loop over the file object for large files instead of calling <code>read()</code>.'])}
<h3>Common mistakes</h3>
{ul(['Opening an existing file with <code>"w"</code> by mistake. The contents are gone before your first write.',
     'Forgetting <code>\\n</code> when writing lines, so everything ends up on one line.',
     'Writing a number directly: <code>f.write(5)</code> raises <code>TypeError</code>. Convert with <code>str()</code> or an f-string.'])}

<div class="aside"><strong>Note on the CampusX session.</strong> It says <code>open()</code> loads the file into RAM and that you close files for memory and security. Neither is right: <code>open()</code> reads nothing by itself, and the reason to close is the unflushed buffer shown above.</div>

{resources([
    (YT + '890s', 'CampusX Session 10, 14:50–26:55', 'writing, <code>"w"</code> vs <code>"a"</code>'),
    (YT + '2010s', 'CampusX Session 10, 33:30–39:30', '<code>read</code>, <code>read(n)</code>, <code>readline</code>'),
    (YT + '2725s', 'CampusX Session 10, 45:25–48:00', 'the <code>with</code> statement'),
    (YT + '3010s', 'CampusX Session 10, 50:10–61:30', 'reading a large file in chunks'),
    (DOCS + 'tutorial/inputoutput.html#reading-and-writing-files', 'Python tutorial: Reading and writing files', ''),
])}
{practice('python/07/01_text_files.py', 'It writes two lines, appends a third and reads them back.',
    'change the second <code>open</code> from <code>"a"</code> to <code>"w"</code>.',
    'only <code>attention</code> is left; <code>"w"</code> emptied the file first.')}
'''))

# ============================================================== 2. CSV and JSON
S.append(('s2', '2. CSV and JSON', f'''
<p><strong>Serialization</strong> means converting a Python object into a format that can be saved to a file or sent over a network. <strong>Deserialization</strong> is the reverse. A plain text file can only hold strings, so structured data needs a format. CSV and JSON are the two most common.</p>

<h3>CSV</h3>
<p>CSV (comma-separated values) stores a table: one row per line, cells separated by commas. It's what spreadsheets and databases export. Use the <code>csv</code> module rather than splitting on commas yourself, because it handles quoting (a comma inside a cell) correctly.</p>
{code("""
import csv

rows = [{"name": "Asha", "score": 92}, {"name": "Ravi", "score": 78}]

with open("scores.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "score"])
    writer.writeheader()
    writer.writerows(rows)

print(open("scores.csv", encoding="utf-8").read())

with open("scores.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        print(row)
""")}
<ul class="points">
  <li><strong>Every value comes back as a string</strong>: the score is <code>'92'</code>, not <code>92</code>. Convert it yourself with <code>int(row["score"])</code>. (pandas' <code>read_csv</code> guesses types for you.)</li>
  <li>Open CSV files with <code>newline=""</code>. The csv module writes its own line endings, and without this Windows shows a blank line between rows.</li>
  <li><code>csv.writer</code> / <code>csv.reader</code> work with lists instead of dicts.</li>
</ul>

<h3>JSON</h3>
<p>JSON (JavaScript Object Notation) stores nested data: objects (like dicts) and arrays (like lists), to any depth. Almost every web API uses it, and every language can read it.</p>
{code("""
import json

data = {"name": "Asha", "score": 92, "tags": ("python", "sql"), "active": True, "mentor": None}

with open("asha.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(open("asha.json", encoding="utf-8").read())

with open("asha.json", encoding="utf-8") as f:
    back = json.load(f)
print(back)
""")}
{table(['Function', 'Converts', 'Between'], [
    ['<code>json.dump(obj, f)</code>', 'Python → JSON', 'object and <strong>file</strong>'],
    ['<code>json.load(f)</code>', 'JSON → Python', 'file and object'],
    ['<code>json.dumps(obj)</code>', 'Python → JSON', 'object and <strong>string</strong>'],
    ['<code>json.loads(s)</code>', 'JSON → Python', 'string and object'],
])}
<p>The <em>s</em> in <code>dumps</code>/<code>loads</code> stands for string. Useful arguments: <code>indent=2</code> for readable output, <code>ensure_ascii=False</code> to keep non-English text as-is instead of <code>\\u</code> escapes.</p>

<h3>What survives a JSON round trip</h3>
{table(['Python', 'JSON', 'Comes back as'], [
    ['<code>dict</code>', 'object', '<code>dict</code>'],
    ['<code>list</code>, <code>tuple</code>', 'array', '<code>list</code> (a tuple becomes a list)'],
    ['<code>str</code>, <code>int</code>, <code>float</code>', 'string, number', 'same'],
    ['<code>True</code> / <code>False</code> / <code>None</code>', '<code>true</code> / <code>false</code> / <code>null</code>', 'same'],
    ['dict with non-string keys', 'keys become strings', '<code>{1: "a"}</code> → <code>{\'1\': \'a\'}</code>'],
    ['<code>set</code>, <code>datetime</code>, your own class', '—', '<code>TypeError</code>'],
])}
{code("""
import json, datetime
print(json.loads(json.dumps({1: "a", 2: "b"})))
print(json.dumps({"joined": datetime.date(2026, 9, 21)}, default=str))
json.dumps({"skills": {"python", "sql"}})
""")}
<p><code>default=</code> is called for any object JSON can't handle. <code>default=str</code> is enough for dates; for your own classes, pass a function that returns a dict.</p>

<h3>CSV or JSON?</h3>
{table(['', 'CSV', 'JSON'], [
    ['Shape', 'flat table', 'nested objects and lists'],
    ['Types', 'everything is text', 'numbers, booleans and null kept'],
    ['Opens in', 'Excel, Sheets, pandas', 'any programming language, APIs'],
    ['Typical use', 'datasets, exports', 'configs, API data, records with nesting'],
])}

<h3>Common mistakes</h3>
{ul(['Doing arithmetic on CSV values without converting them: <code>"92" * 2</code> is <code>"9292"</code>.',
     'Looking up a JSON dict with an int key after loading it: the key is now a string.',
     'Expecting a tuple or set back from JSON.'])}

{resources([
    (YT + '4568s', 'CampusX Session 10, 76:08–82:30', 'why text files can\'t hold lists and dicts'),
    (YT + '5160s', 'CampusX Session 10, 86:00–96:30', '<code>json.dump</code>, <code>json.load</code>, tuples, nested dicts'),
    (YT + '5785s', 'CampusX Session 10, 96:25–104:30', 'saving your own objects with <code>default=</code>'),
    ('https://www.youtube.com/watch?v=dA6ZksRR6aw&t=1447s', 'CampusX Session 27, 24:07–56:30', 'CSV with pandas (Session 10 doesn\'t cover CSV)'),
    ('https://www.youtube.com/watch?v=dA6ZksRR6aw&t=3856s', 'CampusX Session 27, 64:16–70:49', 'JSON with pandas (<code>read_json</code>)'),
    (DOCS + 'library/csv.html#csv.DictReader', 'Python docs: csv.DictReader', ''),
    (DOCS + 'library/json.html#json-to-py-table', 'Python docs: JSON ↔ Python conversion table', ''),
])}
{practice('python/07/02_csv_json.py', 'It saves the same records as CSV and JSON and prints the type of each value that comes back.',
    'make Asha\'s <code>tags</code> a set, <code>{"python", "sql"}</code>.',
    '<code>TypeError: Object of type set is not JSON serializable</code>.')}
'''))

# ============================================================== 3. Pickle
S.append(('s3', '3. Pickle', f'''
<p><code>pickle</code> is Python's own serialization format. It saves almost any Python object, including instances of your own classes, sets and tuples, and restores them exactly. The result is bytes, so the file must be opened in binary mode (<code>"wb"</code> / <code>"rb"</code>).</p>
{code("""
import pickle

class Student:
    def __init__(self, name, skills):
        self.name, self.skills = name, skills

data = {"student": Student("Asha", {"python", "sql"}), "scores": (92, 78)}

with open("data.pkl", "wb") as f:
    pickle.dump(data, f)

with open("data.pkl", "rb") as f:
    back = pickle.load(f)

print(type(back["student"]).__name__, back["student"].name, sorted(back["student"].skills), back["scores"])
print(open("data.pkl", "rb").read()[:12])
""")}
<p>The object, the set and the tuple all came back unchanged. Like JSON, there's <code>dumps</code>/<code>loads</code> for working with bytes in memory instead of files.</p>

<h3>Pros and cons</h3>
{table(['Pros', 'Cons'], [
    ['Handles almost any Python object', 'Only Python can read it'],
    ['Types come back exactly (sets, tuples, class instances)', 'Not human-readable'],
    ['No conversion code to write', 'The class must be importable when loading'],
    ['Common for saving ML models and caches', '<strong>Loading a pickle can run arbitrary code</strong>'],
])}

<h3>The class must exist when loading</h3>
<p>A pickle stores an object's data and the <em>name</em> of its class, not the class's code. Loading it in a program where <code>Student</code> isn't defined fails:</p>
<pre class="output">AttributeError: Can't get attribute 'Student' on &lt;module '__main__' (built-in)&gt;</pre>
<p>Renaming or moving the class breaks old pickle files in the same way, which is why pickle is a poor choice for long-term storage.</p>

<h3>Security</h3>
<p>Unpickling can execute code: an object can tell pickle to call any function while it's being loaded. This harmless example calls <code>print</code>; a malicious file could run a system command instead.</p>
{code("""
import pickle

class Surprise:
    def __reduce__(self):
        return (print, ("this line ran inside pickle.loads()",))

pickle.loads(pickle.dumps(Surprise()))
""")}
<p>Never unpickle data from a source you don't trust: downloads, uploads, email attachments. The same applies to <code>joblib.load</code>, which uses pickle underneath. This is why model weights are increasingly shared in the safetensors format.</p>

<h3>When to use what</h3>
{ul(['<strong>Pickle</strong>: your own short-lived caches or models, used only by Python, from a source you trust.',
     '<strong>JSON</strong>: anything shared, stored long-term, or read by other tools.'])}

<div class="aside"><strong>Note on the CampusX session.</strong> At 107:30 it says an unpickled object works even where its class isn't present. Its own demo fails a few minutes later with the error above. The session also doesn't mention the security risk.</div>

{resources([
    (YT + '6379s', 'CampusX Session 10, 106:19–109:30', '<code>pickle.dump</code> and the <code>"wb"</code> requirement'),
    (YT + '6570s', 'CampusX Session 10, 109:30–112:30', 'loading fails without the class, works with it'),
    (YT + '6772s', 'CampusX Session 10, 112:52–113:54', 'pickle vs JSON'),
    (DOCS + 'library/pickle.html#comparison-with-json', 'Python docs: pickle (see the warning at the top)', ''),
])}
{practice('python/07/03_pickle.py', 'It pickles an object with a set inside, loads it back, and shows code running during a load.',
    'add <code>import json</code> and <code>json.dumps(data)</code> at the end.',
    '<code>TypeError: Object of type Student is not JSON serializable</code>.')}
'''))

# ============================================================== 4. Directories
S.append(('s4', '4. Working with directories (os, pathlib)', f'''
<p>A <strong>path</strong> is a file's address. An <em>absolute</em> path starts at the top of the disk (<code>/Users/darshan/data/a.csv</code>). A <em>relative</em> path (<code>data/a.csv</code>) is resolved from the <strong>current working directory</strong>, the folder Python was started from, which is not necessarily the folder the script is in.</p>
<p>Python has two ways to work with paths: the older <code>os</code> / <code>os.path</code> functions, which use plain strings, and <code>pathlib</code>, which represents paths as objects. New code should use <code>pathlib</code>.</p>

<h3>pathlib basics</h3>
{code("""
from pathlib import Path

p = Path("project") / "data" / "scores.csv"      # / joins parts, on any OS
print(p)
print(p.name, p.stem, p.suffix, p.parent)
print(p.exists())

p.parent.mkdir(parents=True, exist_ok=True)       # create all missing folders
p.write_text("name,score\\nAsha,92\\n", encoding="utf-8")
print(p.exists(), p.read_text(encoding="utf-8").splitlines())
""")}

<h3>Listing and finding files</h3>
{code("""
from pathlib import Path

data = Path("data")
(data / "raw").mkdir(parents=True)
for name in ["b.csv", "a.csv", "notes.txt", "raw/c.csv"]:
    (data / name).write_text("x", encoding="utf-8")

print(sorted(p.name for p in data.iterdir()))       # everything in the folder
print(sorted(p.name for p in data.glob("*.csv")))   # CSVs in this folder
print(sorted(p.name for p in data.glob("**/*.csv")))  # CSVs here and below
""")}
<p><code>iterdir()</code> and <code>glob()</code> return files in whatever order the operating system gives, so wrap them in <code>sorted()</code> when order matters. The practice script below shows it: on a Mac, <code>glob("*.csv")</code> returned <code>['a.csv', 'b.csv']</code>, while the same code run in this page's browser runner returned <code>['b.csv', 'a.csv']</code>.</p>

<h3>Common operations: pathlib vs os</h3>
{table(['Task', 'pathlib', 'os / shutil'], [
    ['Join paths', '<code>Path("data") / "a.csv"</code>', '<code>os.path.join("data", "a.csv")</code>'],
    ['Current directory', '<code>Path.cwd()</code>', '<code>os.getcwd()</code>'],
    ['Exists?', '<code>p.exists()</code>, <code>p.is_file()</code>, <code>p.is_dir()</code>', '<code>os.path.exists(p)</code>'],
    ['Create folders', '<code>p.mkdir(parents=True, exist_ok=True)</code>', '<code>os.makedirs(p, exist_ok=True)</code>'],
    ['List a folder', '<code>p.iterdir()</code>, <code>p.glob("*.csv")</code>', '<code>os.listdir(p)</code>'],
    ['Rename / move', '<code>p.rename(new)</code>', '<code>os.rename(p, new)</code>'],
    ['Delete a file', '<code>p.unlink()</code>', '<code>os.remove(p)</code>'],
    ['Delete an empty folder', '<code>p.rmdir()</code>', '<code>os.rmdir(p)</code>'],
    ['Delete a folder and its contents', '—', '<code>shutil.rmtree(p)</code> (no undo)'],
    ['Name parts', '<code>p.name</code>, <code>p.stem</code>, <code>p.suffix</code>, <code>p.parent</code>', '<code>os.path.basename</code>, <code>splitext</code>, <code>dirname</code>'],
])}

<h3>Relative paths and the working directory</h3>
<p>A script that does <code>open("data/scores.csv")</code> works when run from its own folder and raises <code>FileNotFoundError</code> when run from anywhere else, because the path is resolved from the working directory. To make a path relative to the script itself, build it from the script's location:</p>
<pre class="code">BASE = Path(__file__).parent
scores = BASE / "data" / "scores.csv"</pre>
<p>Also note that <code>open()</code> does not create missing folders: writing to <code>no_such_folder/x.txt</code> raises <code>FileNotFoundError</code> until the folder exists.</p>

<h3>Key points</h3>
{ul(['Prefer <code>pathlib</code>; know the <code>os</code> equivalents for reading older code.',
     'Relative paths depend on where Python was started. Anchor them with <code>Path(__file__).parent</code>.',
     'Use <code>mkdir(parents=True, exist_ok=True)</code> before writing into a new folder.',
     'Sort directory listings if the order matters.'])}

{resources([
    (YT + '1920s', 'CampusX Session 10, 32:00–33:00', 'saving a file into another folder (done through the Colab file panel)'),
    (DOCS + 'library/pathlib.html#basic-use', 'Python docs: pathlib basic use', ''),
    (DOCS + 'library/pathlib.html#corresponding-tools', 'Python docs: pathlib ↔ os equivalents', ''),
    (DOCS + 'library/os.html#files-and-directories', 'Python docs: os, files and directories', 'the os functions in full'),
])}
{practice('python/07/04_directories.py', 'It builds a small folder tree, lists and renames files, and shows the working-directory effect.',
    'change <code>glob("*.csv")</code> to <code>glob("**/*.csv")</code>.',
    '<code>c.csv</code> from the <code>raw</code> subfolder is found too.')}
'''))

# ============================================================== 5. Logging
S.append(('s5', '5. Logging to files', f'''
<p><code>print()</code> output disappears when the terminal closes and can't be filtered by importance. The <code>logging</code> module writes messages with a severity level, a source and a format, and can send them to a file, so there's a record to check after a script has run unattended.</p>

<h3>Levels</h3>
{table(['Level', 'Value', 'Use for'], [
    ['<code>DEBUG</code>', '10', 'detailed information for diagnosing problems'],
    ['<code>INFO</code>', '20', 'confirmation that things are working as expected'],
    ['<code>WARNING</code>', '30', 'something unexpected, but the program continues (the default level)'],
    ['<code>ERROR</code>', '40', 'a function failed'],
    ['<code>CRITICAL</code>', '50', 'the program itself may not be able to continue'],
])}
<p>The level set in the configuration is a threshold: messages below it are dropped.</p>

<h3>Logging to a file</h3>
{code("""
import logging

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    encoding="utf-8",
)
log = logging.getLogger("etl")

log.debug("row 17 raw=%r", {"score": "92"})    # below INFO: dropped
log.info("loaded %d rows", 250)
log.warning("3 rows had no score")
try:
    1 / 0
except ZeroDivisionError:
    log.exception("average failed")            # ERROR level + traceback

print(open("app.log", encoding="utf-8").read())
""")}
<ul class="points">
  <li><code>basicConfig(filename=...)</code> sends log lines to a file instead of the screen. The file is opened in append mode, so it grows across runs.</li>
  <li><code>log.exception()</code> inside an <code>except</code> block logs at ERROR level and includes the full traceback.</li>
  <li>Pass values as arguments (<code>log.info("loaded %d rows", n)</code>) rather than building an f-string, so the text is only formatted if the message is actually written.</li>
  <li>Common format fields: <code>%(asctime)s</code> time, <code>%(levelname)s</code> level, <code>%(name)s</code> logger name, <code>%(message)s</code> the message.</li>
</ul>

<h3>Loggers per module</h3>
<p>In a larger program, each module gets its own logger with <code>log = logging.getLogger(__name__)</code>, so every line shows which module wrote it. Configuration (<code>basicConfig</code>) is done once, in the program's entry point.</p>

<h3>Screen and file together</h3>
<pre class="code">logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[logging.FileHandler("app.log", encoding="utf-8"), logging.StreamHandler()],
)</pre>

<h3>Common mistakes</h3>
{ul(['Calling <code>log.info()</code> with no configuration. The default level is WARNING, so INFO messages go nowhere.',
     'Calling <code>basicConfig</code> twice. Only the first call takes effect; a second one is silently ignored unless you pass <code>force=True</code>. This also happens when an imported library configured logging first.',
     'Logging secrets such as API keys or passwords. Log files get copied into bug reports and chats.'])}

{resources([
    (DOCS + 'howto/logging.html#logging-to-a-file', 'Python docs: Logging HOWTO, logging to a file', ''),
    (DOCS + 'howto/logging.html#when-to-use-logging', 'Python docs: when to use logging', 'which level for which situation'),
])}
<p class="small">CampusX Session 10 doesn't cover logging.</p>
{practice('python/07/05_logging.py', 'It logs at four levels to <code>app.log</code> and prints the file.',
    'change <code>level=logging.INFO</code> to <code>level=logging.DEBUG</code>.',
    'the DEBUG line appears as well.')}
'''))

SUMMARY = f'''
<section class="sect" id="summary">
<h2>Summary</h2>
{table(['Need', 'Use'], [
    ['Plain text, logs, notes', 'text file with <code>open()</code> and <code>encoding="utf-8"</code>'],
    ['A flat table for Excel or pandas', 'CSV (<code>csv</code> module, or pandas)'],
    ['Nested data for other programs or APIs', 'JSON'],
    ['Exact Python objects, for yourself only', 'pickle, never from untrusted sources'],
    ['Paths, folders, finding files', '<code>pathlib</code>'],
    ['A record of what a script did', '<code>logging</code> to a file'],
])}
</section>
'''

QUESTIONS = [
    ('What happens to an existing file when it\'s opened with <code>"w"</code>, and when exactly does it happen?',
     'It\'s emptied immediately when <code>open()</code> runs, before any write.'),
    ('Why can data be lost if a file isn\'t closed?',
     'Writes are held in a buffer and only reach the disk when the buffer fills or the file is closed.'),
    ('A value read from a CSV file is <code>"92"</code>. What is <code>row["score"] * 2</code>?',
     '<code>"9292"</code>. The value is a string; convert it with <code>int()</code> first.'),
    ('What do a tuple, a set and a dict with integer keys become after a JSON round trip?',
     'A list; a <code>TypeError</code> (sets aren\'t supported); a dict with string keys.'),
    ('Give two reasons not to use pickle for data you\'ll share with others.',
     'Only Python can read it, and loading it can execute code. (Also: it needs the original class, and it isn\'t human-readable.)'),
    ('A script opens <code>"data/scores.csv"</code>. It works from the project folder but not from its parent. Why, and how do you fix it?',
     'Relative paths are resolved from the working directory. Build the path from <code>Path(__file__).parent</code>.'),
    ('Your <code>log.info()</code> messages appear nowhere. Name two possible causes.',
     'The level is still the default WARNING, or <code>basicConfig</code> was already called earlier (use <code>force=True</code>).'),
]


def build():
    return page(TITLE, DESCRIPTION, LEAD, S, SUMMARY + review(QUESTIONS))
