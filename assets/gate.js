/* Password prompt for the site.
 *
 * This is a doorbell, not a lock: the pages are static files in a public repo,
 * so anyone who knows the file URL can still read them. It keeps a casual
 * visitor out of the site, nothing more. Real privacy needs the published files
 * themselves to be encrypted, or a host that checks passwords on the server.
 */
(function () {
  var HASH = 'df653b0f29837c470a6e5a3ba805a5a409e74cd719fd814177f8b5ef44fe4c29';
  var KEY = 'aen-gate';

  function unlocked() {
    try { return sessionStorage.getItem(KEY) === HASH; } catch (e) { return false; }
  }
  function remember() {
    try { sessionStorage.setItem(KEY, HASH); } catch (e) { /* private mode */ }
  }
  async function digest(text) {
    var bytes = new TextEncoder().encode(text);
    var buf = await crypto.subtle.digest('SHA-256', bytes);
    return Array.from(new Uint8Array(buf)).map(function (b) {
      return b.toString(16).padStart(2, '0');
    }).join('');
  }

  if (unlocked() || !window.crypto || !crypto.subtle) return;

  var css = '#aen-gate{position:fixed;inset:0;z-index:9999;background:var(--bg,#fff);' +
    'display:flex;align-items:center;justify-content:center;padding:24px;' +
    'font-family:var(--f-body,-apple-system,system-ui,sans-serif)}' +
    '#aen-gate form{width:100%;max-width:300px;display:flex;flex-direction:column;gap:12px}' +
    '#aen-gate h1{font-weight:700;font-size:1.3rem;margin:0;color:var(--ink,#1d1d1f)}' +
    '#aen-gate p{margin:0;font-size:14px;color:var(--muted,#6e6e73)}' +
    '#aen-gate input{font:inherit;padding:10px 12px;border:1px solid var(--rule,#e5e5e2);outline:none;' +
    'background:var(--bg,#fff);color:var(--ink,#1d1d1f);border-radius:8px}' +
    '#aen-gate button{font:inherit;font-weight:600;padding:10px 12px;border:0;cursor:pointer;' +
    'background:var(--ink,#1d1d1f);color:var(--bg,#fff);border-radius:8px}' +
    '#aen-gate .err{color:var(--signal,#b8431f);min-height:18px;font-size:14px}';

  function mount() {
    var style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);

    var gate = document.createElement('div');
    gate.id = 'aen-gate';
    gate.innerHTML = '<form><h1>AI Engineer Notes</h1>' +
      '<p>Enter the password to read on.</p>' +
      '<input type="password" aria-label="Password" autocomplete="current-password" autofocus>' +
      '<button type="submit">Open</button><p class="err" role="alert"></p></form>';
    document.body.appendChild(gate);
    document.documentElement.style.overflow = 'hidden';

    var input = gate.querySelector('input'), err = gate.querySelector('.err');
    gate.querySelector('form').addEventListener('submit', async function (ev) {
      ev.preventDefault();
      if (await digest(input.value) === HASH) {
        remember();
        gate.remove();
        document.documentElement.style.overflow = '';
      } else {
        err.textContent = 'Not that one.';
        input.select();
      }
    });
    input.focus();
  }

  if (document.body) mount();
  else document.addEventListener('DOMContentLoaded', mount);
})();
