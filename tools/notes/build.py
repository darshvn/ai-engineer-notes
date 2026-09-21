#!/usr/bin/env python3
"""Build a note from tools/notes/<name>.py and install it into the site.

    python3 tools/notes/build.py python_07
    python3 tools/notes/build.py llm_101_01 llm_101_02

The note sources use Python 3.12 f-string syntax, so on an older interpreter
this re-runs itself under Python 3.13 through uv.
"""
import importlib, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))

if sys.version_info < (3, 12):
    os.execvp('uv', ['uv', 'run', '--no-project', '--python', '3.13', 'python', *sys.argv])

sys.path.insert(0, HERE)
for name in sys.argv[1:]:
    mod = importlib.import_module(name)
    html = mod.build()
    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False) as f:
        f.write(html)
    subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'add_note.py'), '--file', f.name,
                    '--topic', mod.TOPIC, '--section', str(mod.SECTION)], check=True)
    os.unlink(f.name)
