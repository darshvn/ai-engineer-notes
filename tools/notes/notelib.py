"""Shared pieces for building the notes as traditional study notes.

A note source (for example tools/notes/python_07.py) describes its sections in
HTML and calls the helpers here. Anything that prints output is run for real:
code() runs a snippet in a throwaway folder, practice() runs the exercise
script from the exercises folder, and the page shows what actually came out.

    python3 tools/notes/build.py python_07      # build one note and install it
"""
import html, os, re, subprocess, tempfile, textwrap

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
EX = os.path.join(ROOT, 'exercises')
PY = os.path.join(EX, '.venv', 'bin', 'python')
GH = 'https://github.com/darshvn/ai-engineer-notes/blob/main/exercises/'
DOCS = 'https://docs.python.org/3/'

# Packages that can't run inside the browser (Pyodide): these exercises show
# their recorded output and a local command instead of a Run button.
NOT_IN_BROWSER = {'torch', 'transformers', 'sentence_transformers', 'tiktoken'}

e = lambda s: html.escape(s, quote=False)


def yt(video, seconds):
    return f'https://www.youtube.com/watch?v={video}&t={seconds}s'


# ---------------------------------------------------------------- running code

def _run(args, cwd):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=600)
    err = r.stderr.strip()
    # A traceback is reduced to its last line, which is what a reader needs.
    last = err.splitlines()[-1] if err and 'Traceback' in err else err
    lines = [x for x in (r.stdout.rstrip('\n'), last) if x]
    return '\n'.join(lines)


def run_snippet(src):
    with tempfile.TemporaryDirectory() as d:
        return _run([PY, '-c', src], d).replace(d, '/tmp/example')


def run_script(rel):
    """Run an exercise the way the notes tell you to: from the exercises folder."""
    r = subprocess.run([PY, rel], cwd=EX, capture_output=True, text=True, timeout=900)
    out = (r.stdout + r.stderr).rstrip('\n')
    return out.replace(os.path.join(EX, ''), '…/exercises/')


# ---------------------------------------------------------------- building blocks

def code(src, output=True, label='Output'):
    src = textwrap.dedent(src).strip('\n')
    block = f'<pre class="code">{e(src)}</pre>'
    if output:
        block += f'\n<div class="out-label">{label}</div>\n<pre class="output">{e(run_snippet(src))}</pre>'
    return block


def show(text, cls='code'):
    """A block shown as-is, not run (pseudo-output, configuration, shell commands)."""
    return f'<pre class="{cls}">{e(textwrap.dedent(text).strip(chr(10)))}</pre>'


def table(head, rows):
    th = ''.join(f'<th>{h}</th>' for h in head)
    tr = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
    return f'<div class="tbl-hold"><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


def ul(items, cls='points'):
    return f'<ul class="{cls}">' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'


def aside(text):
    return f'<div class="aside">{text}</div>'


def figure(svg, caption):
    return f'<figure>{svg}<figcaption>{caption}</figcaption></figure>'


def resources(items):
    """items: (url, title, what) — what may be empty."""
    return '<h3>Resources</h3>' + ul(
        [f'<a href="{u}">{t}</a>{" — " + d if d else ""}' for u, t, d in items], 'res')


def practice(rel, what, change=None, result=None):
    """The exercise, shown in full. Runs in the browser unless it needs PyTorch or tiktoken."""
    src = open(os.path.join(EX, rel)).read().rstrip('\n')
    imports = set(re.findall(r'^\s*(?:import|from)\s+([A-Za-z_]+)', src, re.M))
    in_browser = not (imports & NOT_IN_BROWSER)
    recorded = run_script(rel)

    parts = [f'<h3>Practice</h3>',
             f'<p><a href="{GH}{rel}"><code>exercises/{rel}</code></a> — {what}</p>']
    if in_browser:
        parts.append(
            f'<div class="runner" data-file="{rel}">'
            f'<textarea class="rcode" spellcheck="false" aria-label="Code for {rel}">{e(src)}</textarea>'
            '<div class="rbar"><button class="rrun" type="button">Run</button>'
            '<button class="rreset" type="button">Reset</button>'
            '<span class="rhint">Edit the code and run it. It runs in your browser; ⌘/Ctrl + Enter also runs.</span></div>'
            '<pre class="rout" hidden></pre></div>')
    else:
        missing = ', '.join(sorted(imports & NOT_IN_BROWSER))
        parts.append(f'<pre class="code">{e(src)}</pre>')
        parts.append(f'<p class="small">This one needs {missing}, which can\'t run in a browser. Run it locally:</p>'
                     f'<pre class="code">cd ~/Downloads/ai-engineer-notes/exercises\n'
                     f'source .venv/bin/activate\npython {rel}</pre>')
    parts.append(f'<div class="out-label">Output from a real run</div><pre class="output">{e(recorded)}</pre>')
    if change:
        parts.append(f'<p><strong>Try:</strong> {change}' + (f' <span class="small">Result: {result}</span>' if result else '') + '</p>')
    return '\n'.join(parts)


# ---------------------------------------------------------------- the page

HEAD = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;450;500;600&display=swap">
<style>
:root {
  --bg:#E9EBE7; --surface:#F6F7F4; --surface-2:#DFE3DE; --ink:#14181A; --muted:#59635F;
  --rule:#C9CFC8; --accent:#146B5F; --accent-dim:#DCE8E4; --signal:#9A2C6B; --signal-dim:#F0DEE8;
  --f-display:"Newsreader", Georgia, "Times New Roman", serif;
  --f-body:"IBM Plex Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --f-mono:"IBM Plex Mono", ui-monospace, "SF Mono", Menlo, monospace;
}
@media (prefers-color-scheme: dark) { :root {
  --bg:#121614; --surface:#1A201D; --surface-2:#232A27; --ink:#E6EAE6; --muted:#929F99;
  --rule:#2E3733; --accent:#56BCAC; --accent-dim:#1C2E2B; --signal:#E982B8; --signal-dim:#33202B; } }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); font-family: var(--f-body); font-size: 16.5px; line-height: 1.62; -webkit-font-smoothing: antialiased; }
.wrap { max-width: 900px; margin: 0 auto; padding: 0 24px 96px; }
.doc { max-width: 76ch; margin: 0 auto; }
.doc h1 { font-family: var(--f-display); font-weight: 500; font-size: clamp(2.1rem, 5vw, 3rem); line-height: 1.1; margin: 48px 0 12px; }
.doc .lead { font-size: 1.1rem; color: var(--muted); margin: 0 0 28px; }
.doc .toc { border: 1px solid var(--rule); background: var(--surface); padding: 14px 20px; margin: 0 0 40px; }
.doc .toc h2 { font-family: var(--f-mono); font-size: 11.5px; letter-spacing: .12em; text-transform: uppercase; color: var(--muted); margin: 0 0 8px; }
.doc .toc ol { margin: 0; padding-left: 20px; } .doc .toc li { margin: 4px 0; }
.doc a { color: var(--accent); }
.doc .sect { border-top: 1px solid var(--rule); padding-top: 28px; margin-top: 44px; scroll-margin-top: 60px; }
.doc h2 { font-family: var(--f-display); font-weight: 500; font-size: 1.9rem; margin: 0 0 14px; line-height: 1.2; }
.doc h3 { font-size: 1.08rem; font-weight: 600; margin: 30px 0 10px; }
.doc p { margin: 12px 0; }
.doc ul, .doc ol { padding-left: 22px; } .doc li { margin: 6px 0; }
.doc code { font-family: var(--f-mono); font-size: .88em; background: var(--surface-2); padding: 1px 5px; border-radius: 2px; }
.doc pre { font-family: var(--f-mono); font-size: 13.5px; line-height: 1.6; padding: 14px 16px; overflow-x: auto; margin: 14px 0 6px; border: 1px solid var(--rule); white-space: pre; }
.doc pre code { background: none; padding: 0; }
.doc pre.code { background: var(--surface); }
.doc pre.output { background: var(--bg); color: var(--muted); margin-top: 0; }
.doc .out-label { font-family: var(--f-mono); font-size: 10.5px; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); margin: 10px 0 4px; }
.doc .tbl-hold { overflow-x: auto; margin: 14px 0; }
.doc table { border-collapse: collapse; width: 100%; font-size: 15px; }
.doc th, .doc td { border: 1px solid var(--rule); padding: 7px 10px; text-align: left; vertical-align: top; }
.doc th { background: var(--surface-2); font-weight: 600; }
.doc .aside { border-left: 3px solid var(--rule); padding: 8px 14px; margin: 22px 0; color: var(--muted); font-size: 15px; }
.doc .small { color: var(--muted); font-size: 14.5px; }
.doc figure { margin: 24px 0; } .doc figure svg { max-width: 100%; height: auto; display: block; color: var(--ink); }
.doc figcaption { font-size: 14.5px; color: var(--muted); margin-top: 10px; }
.doc details.answers { margin-top: 18px; } .doc details.answers summary { cursor: pointer; font-weight: 600; }
.doc footer { margin-top: 56px; padding-top: 14px; border-top: 1px solid var(--rule); font-family: var(--f-mono); font-size: 11.5px; color: var(--muted); display: flex; flex-wrap: wrap; gap: 8px 22px; }
/* practice runner */
.runner { border: 1px solid var(--rule); background: var(--surface); margin: 14px 0 6px; }
.runner .rcode { display: block; width: 100%; border: 0; border-bottom: 1px solid var(--rule); background: transparent; color: var(--ink);
  font-family: var(--f-mono); font-size: 13.5px; line-height: 1.6; padding: 14px 16px; resize: none; overflow: hidden; tab-size: 4; white-space: pre; overflow-x: auto; }
.runner .rcode:focus { outline: 2px solid var(--accent); outline-offset: -2px; }
.runner .rbar { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; padding: 8px 12px; }
.runner button { font-family: var(--f-mono); font-size: 12px; font-weight: 600; padding: 5px 14px; border-radius: 2px; cursor: pointer;
  border: 1px solid var(--accent); background: var(--accent); color: var(--bg); }
.runner .rreset { background: transparent; color: var(--muted); border-color: var(--rule); }
.runner button:disabled { opacity: .5; cursor: wait; }
.runner .rhint { font-size: 13px; color: var(--muted); }
.runner .rout { margin: 0; border: 0; border-top: 1px solid var(--rule); background: var(--bg); color: var(--ink); }
.runner .rout.err { color: var(--signal); }
</style>
</head>
<body>
<div class="wrap"><div class="doc">
'''


def page(title, description, lead, sections, extra=''):
    """sections: list of (id, heading, html). extra: summary / review HTML after them."""
    toc_items = ''.join(f'<li><a href="#{sid}">{re.sub(r"^[0-9]+[.] ", "", h)}</a></li>' for sid, h, _ in sections)
    toc_items += ''.join(f'<li><a href="#{sid}">{name}</a></li>' for sid, name in re.findall(
        r'<section class="sect" id="([^"]+)">\s*<h2>([^<]+)</h2>', extra))
    body = ''.join(f'\n<section class="sect" id="{sid}">\n<h2>{h}</h2>\n{content}\n</section>\n'
                   for sid, h, content in sections)
    return (HEAD.replace('{title}', e(title)).replace('{description}', e(description))
            + f'<h1>{e(title)}</h1>\n<p class="lead">{lead}</p>\n'
            + f'<nav class="toc"><h2>Contents</h2><ol>{toc_items}</ol></nav>\n'
            + body + extra
            + '\n<footer><span>' + e(title) + '</span><span>Every output on this page comes from running the code.</span></footer>\n'
            + '</div></div>\n<script src="../../../assets/runner.js"></script>\n'
            + '<script src="../../../assets/gate.js"></script>\n</body>\n</html>\n')


def review(questions):
    """questions: list of (question, answer)."""
    qs = ''.join(f'<li>{q}</li>' for q, _ in questions)
    ans = ''.join(f'<li>{a}</li>' for _, a in questions)
    return (f'<section class="sect" id="review">\n<h2>Review questions</h2>\n<ol class="review">{qs}</ol>\n'
            f'<details class="answers"><summary>Answers</summary><ol class="review">{ans}</ol></details>\n</section>\n')


def fig(name, caption=None):
    """A saved diagram from tools/notes/figures, with its saved caption unless one is given."""
    base = os.path.join(os.path.dirname(__file__), 'figures', name)
    svg = open(base + '.svg').read()
    if caption is None and os.path.exists(base + '.caption.html'):
        caption = open(base + '.caption.html').read()
    return figure(svg, caption or '')
