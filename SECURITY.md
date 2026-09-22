# What is and isn't protected here

This site is a set of static files on GitHub Pages, served from a public repo.
There is no password: every page is public, and so is everything in the repo.

**The sheet.** The roadmap page that synced with the Google Sheet has been
removed. The sheet itself stays private, but the Apps Script web app it used
may still be deployed, and its URL is in `data/sheet.json` and in git history.
Nothing on the site uses it any more, so the safe move is to switch it off:
Apps Script → Deploy → Manage deployments → Archive.
