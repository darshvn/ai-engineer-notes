/* Practice runner: executes the exercise scripts in the browser with Pyodide,
 * which is CPython compiled to WebAssembly. Nothing is sent to a server; the
 * code runs in this tab, against an in-memory filesystem.
 *
 * Markup it drives (written by tools/notes/notelib.py):
 *   <div class="runner" data-file="python/07/01_text_files.py">
 *     <textarea class="rcode">…</textarea>
 *     <button class="rrun">Run</button> <button class="rreset">Reset</button>
 *     <pre class="rout" hidden></pre>
 *   </div>
 */
(function () {
  var BASE = 'https://cdn.jsdelivr.net/pyodide/v0.28.3/full/';
  var HOME = '/home/pyodide/exercises/';
  var loading = null;

  function pyodide() {
    if (loading) return loading;
    loading = new Promise(function (resolve, reject) {
      var s = document.createElement('script');
      s.src = BASE + 'pyodide.js';
      s.onload = function () { window.loadPyodide({ indexURL: BASE }).then(resolve, reject); };
      s.onerror = function () { reject(new Error('Could not download Python. Check the connection.')); };
      document.head.appendChild(s);
    });
    return loading;
  }

  // Pyodide's tracebacks include its own internal frames; keep only the script's.
  function cleanTraceback(message) {
    var lines = String(message).replace(/\s+$/, '').split('\n'), out = [], keep = true;
    lines.forEach(function (line) {
      if (/^  File "/.test(line)) keep = line.indexOf('"<exec>"') !== -1;
      else if (!/^\s/.test(line)) keep = true;
      if (keep) out.push(line.replace('"<exec>"', '"script"'));
    });
    return out.join('\n');
  }

  function fit(area) {
    area.style.height = 'auto';
    area.style.height = area.scrollHeight + 2 + 'px';
  }

  async function run(box) {
    var area = box.querySelector('.rcode'), out = box.querySelector('.rout'),
        btn = box.querySelector('.rrun'), code = area.value;
    btn.disabled = true;
    out.hidden = false;
    out.classList.remove('err');
    out.textContent = loading ? 'Running…' : 'Loading Python in your browser (about 10 MB, first run only)…';
    try {
      var py = await pyodide();
      out.textContent = 'Running…';
      await py.loadPackagesFromImports(code);
      var file = HOME + box.dataset.file, text = '';
      py.FS.mkdirTree(file.slice(0, file.lastIndexOf('/')));
      py.FS.writeFile(file, code);
      py.setStdout({ batched: function (s) { text += s + '\n'; } });
      py.setStderr({ batched: function (s) { text += s + '\n'; } });
      // Behave as if run from the exercises folder, like the notes tell you to,
      // and start each run with logging unconfigured so basicConfig works again.
      py.globals.set('__file__', file);
      py.runPython([
        'import os, logging',
        'os.chdir(' + JSON.stringify(HOME) + ')',
        'for _h in list(logging.root.handlers): logging.root.removeHandler(_h)',
      ].join('\n'));
      try {
        await py.runPythonAsync(code);
      } catch (err) {
        text += cleanTraceback(err.message) + '\n';
        out.classList.add('err');
      }
      out.textContent = text.replace(/\n$/, '') || '(no output)';
    } catch (err) {
      out.textContent = err.message;
      out.classList.add('err');
    } finally {
      btn.disabled = false;
    }
  }

  document.querySelectorAll('.runner').forEach(function (box) {
    var area = box.querySelector('.rcode');
    var original = area.value;
    fit(area);
    area.addEventListener('input', function () { fit(area); });
    area.addEventListener('keydown', function (e) {
      if (e.key === 'Tab') {                         // indent instead of leaving the box
        e.preventDefault();
        var s = area.selectionStart;
        area.setRangeText('    ', s, area.selectionEnd, 'end');
      } else if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        run(box);
      }
    });
    box.querySelector('.rrun').addEventListener('click', function () { run(box); });
    box.querySelector('.rreset').addEventListener('click', function () {
      area.value = original;
      fit(area);
      box.querySelector('.rout').hidden = true;
    });
  });
})();
