# What is and isn't protected here

This site is a set of static files on GitHub Pages, served from a public repo.

**The password prompt is a doorbell, not a lock.** `assets/gate.js` hides the
page until the password is typed, and it stores only a SHA-256 hash, so the
password itself isn't in the repo. But anyone can read the same pages straight
from github.com, or fetch the HTML directly, without ever seeing the prompt.
Treat everything published here as public.

If the notes ever need to be genuinely private, the published files themselves
have to be encrypted (with the sources kept out of the public repo), or moved
to a host that checks passwords on the server.

**The sheet.** The roadmap reads and writes the Google Sheet through an Apps
Script web app, deployed as "anyone with the link". The sheet itself stays
private; only the script URL is public, and it is in `data/sheet.json`.

The script's guard is a random token:

- The token is **not** in this repo. You paste it into the page once and it
  stays in that browser.
- It is sent in the POST body, never in a URL, so it doesn't end up in Apps
  Script execution logs, browser history or referer headers.
- The script only writes column B, only on rows marked `item` in the hidden
  kind column, and only the five values the sheet's dropdown allows.
- Anyone who gets hold of both the URL and the token could change those
  statuses. Nothing else in the sheet is reachable, and the sheet cannot be
  read without the token.

**To rotate:** change `TOKEN` in the Apps Script, deploy a new version, and
paste the new token into the page. To cut it off entirely: Deploy → Manage
deployments → Archive.
