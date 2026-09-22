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
            '<span class="rhint">Editable · ⌘/Ctrl + Enter</span></div>'
            '<pre class="rout" hidden></pre></div>')
    else:
        missing = ', '.join(sorted(imports & NOT_IN_BROWSER))
        parts.append(f'<pre class="code">{e(src)}</pre>')
        parts.append(f'<p class="small">This one needs {missing}, which can\'t run in a browser. Run it locally:</p>'
                     f'<pre class="code">cd ~/Downloads/ai-engineer-notes/exercises\n'
                     f'source .venv/bin/activate\npython {rel}</pre>')
    parts.append(f'<div class="out-label">Output</div><pre class="output">{e(recorded)}</pre>')
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
<style>
:root {
  --bg:#ffffff; --surface:#f5f5f3; --ink:#1d1d1f; --muted:#6e6e73; --rule:#e5e5e2;
  --accent:#2457c5; --signal:#b8431f; --accent-dim:#e8eefb; --signal-dim:#fbeae3;
  --f-body:-apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
  --f-mono:ui-monospace, "SF Mono", Menlo, Consolas, monospace;
}
@media (prefers-color-scheme: dark) { :root {
  --bg:#141414; --surface:#1e1e1e; --ink:#e8e8e6; --muted:#9a9a97; --rule:#2c2c2c;
  --accent:#8ab4f8; --signal:#f28b6b; --accent-dim:#1c2538; --signal-dim:#3a231b; } }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); font-family: var(--f-body); font-size: 17px; line-height: 1.7; -webkit-font-smoothing: antialiased; }
.wrap { max-width: 720px; margin: 0 auto; padding: 0 20px 120px; }
.doc h1 { font-size: 2rem; font-weight: 700; line-height: 1.2; letter-spacing: -.02em; margin: 56px 0 8px; }
.doc .lead { color: var(--muted); margin: 0 0 32px; }
.doc .toc { margin: 0 0 48px; }
.doc .toc h2 { font-size: .9rem; font-weight: 600; color: var(--muted); margin: 0 0 6px; }
.doc .toc ol { margin: 0; padding-left: 20px; color: var(--muted); } .doc .toc li { margin: 2px 0; }
.doc .toc a { color: var(--ink); text-decoration: none; } .doc .toc a:hover { color: var(--accent); }
.doc a { color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 3px; }
.doc .sect { margin-top: 64px; scroll-margin-top: 24px; }
.doc h2 { font-size: 1.45rem; font-weight: 700; letter-spacing: -.01em; line-height: 1.3; margin: 0 0 12px; }
.doc h3 { font-size: 1.05rem; font-weight: 600; margin: 32px 0 8px; }
.doc p { margin: 14px 0; }
.doc ul, .doc ol { padding-left: 22px; } .doc li { margin: 6px 0; }
.doc code { font-family: var(--f-mono); font-size: .86em; background: var(--surface); padding: 2px 5px; border-radius: 4px; }
.doc pre { font-family: var(--f-mono); font-size: 13.5px; line-height: 1.6; padding: 14px 16px; overflow-x: auto; margin: 16px 0 6px; border-radius: 8px; white-space: pre; background: var(--surface); }
.doc pre code { background: none; padding: 0; }
.doc pre.output { background: transparent; border: 1px solid var(--rule); color: var(--muted); margin-top: 0; }
.doc .out-label { font-size: 13px; color: var(--muted); margin: 12px 0 4px; }
.doc .tbl-hold { overflow-x: auto; margin: 16px 0; }
.doc table { border-collapse: collapse; width: 100%; font-size: 15px; }
.doc th, .doc td { border-bottom: 1px solid var(--rule); padding: 8px 12px 8px 0; text-align: left; vertical-align: top; }
.doc th { font-weight: 600; color: var(--muted); font-size: 14px; }
.doc .aside { padding-left: 16px; border-left: 2px solid var(--rule); margin: 24px 0; color: var(--muted); }
.doc .small { color: var(--muted); font-size: 15px; }
.doc figure { margin: 28px 0; } .doc figure svg { max-width: 100%; height: auto; display: block; color: var(--ink); }
.doc figcaption { font-size: 15px; color: var(--muted); margin-top: 10px; }
.doc details.answers { margin-top: 20px; } .doc details.answers summary { cursor: pointer; font-weight: 600; }
/* practice runner */
.runner { background: var(--surface); border-radius: 8px; margin: 16px 0 6px; overflow: hidden; }
.runner .rcode { display: block; width: 100%; border: 0; background: transparent; color: var(--ink);
  font-family: var(--f-mono); font-size: 13.5px; line-height: 1.6; padding: 14px 16px; resize: none; overflow: hidden; tab-size: 4; white-space: pre; overflow-x: auto; }
.runner .rcode:focus { outline: none; }
.runner .rbar { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; padding: 4px 16px 12px; }
.runner button { font: inherit; font-size: 14px; font-weight: 600; padding: 4px 14px; border-radius: 6px; cursor: pointer;
  border: 0; background: var(--ink); color: var(--bg); }
.runner .rreset { background: transparent; color: var(--muted); padding: 4px 2px; font-weight: 500; }
.runner button:disabled { opacity: .5; cursor: wait; }
.runner .rhint { font-size: 13px; color: var(--muted); margin-left: auto; }
.runner .rout { margin: 0; border-radius: 0; border-top: 1px solid var(--rule); background: transparent; color: var(--ink); }
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
            + f'<nav class="toc"><h2>On this page</h2><ol>{toc_items}</ol></nav>\n'
            + body + extra
            + '</div></div>\n<script src="../../../assets/runner.js"></script>\n'
            + '</body>\n</html>\n')


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
