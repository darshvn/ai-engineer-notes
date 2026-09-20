/**
 * Roadmap sync — paste this into the sheet's Apps Script editor.
 *
 * It lets the notes site read the Status column and write it back, while the
 * sheet itself stays private: only this script's URL is public.
 *
 * Setup
 *  1. Open the sheet → Extensions → Apps Script. Delete whatever is there and
 *     paste this file in.
 *  2. Put the long random token I generated into TOKEN below. Don't reuse the
 *     site password: this one authorises writes to your sheet.
 *  3. Deploy → New deployment → type "Web app".
 *       Execute as: Me
 *       Who has access: Anyone
 *     Authorise it when Google asks, then copy the /exec URL.
 *  4. Open the roadmap page and paste the token when it asks. It is kept for
 *     that browser only and never committed to the repo.
 *
 * Read   POST <url>  {"token":"…","action":"read"}
 * Write  POST <url>  {"token":"…","updates":[{"sheet":"Basics","row":5,"status":"Done"}]}
 *
 * Worth knowing: "Who has access: Anyone" means anyone holding the URL can
 * call it, and the token sits in the site's JavaScript, so treat this as a
 * convenience rather than a lock. Deploy → Manage deployments → Archive kills
 * the URL any time.
 */

var TOKEN = 'paste-the-long-random-token-here';
var STATUS_COL = 2;   // B
var KIND_COL = 9;     // I, the hidden helper column
var ALLOWED = ['Not started', 'In progress', 'Done', 'Revisit', 'Skipped'];   // matches the sheet's dropdown

function doGet(e) {
  // Reads happen through doPost so the token never travels in a URL, where it
  // would land in the execution log, browser history and referer headers.
  return reply({ error: 'post instead' });
}

function readStatuses() {
  var out = {};
  SpreadsheetApp.getActive().getSheets().forEach(function (sheet) {
    var last = sheet.getLastRow();
    if (last < 2) return;
    var values = sheet.getRange(1, 1, last, KIND_COL).getValues();
    var statuses = {};
    values.forEach(function (row, i) {
      if (String(row[KIND_COL - 1]).trim() === 'item') {
        statuses[i + 1] = String(row[STATUS_COL - 1] || '').trim();
      }
    });
    out[sheet.getName()] = statuses;
  });
  return out;
}

function doPost(e) {
  var body;
  try {
    body = JSON.parse(e.postData.contents);
  } catch (err) {
    return reply({ error: 'bad json' });
  }
  if (body.token !== TOKEN) return reply({ error: 'bad token' });
  if (body.action === 'read') return reply({ statuses: readStatuses(), read: new Date().toISOString() });

  var book = SpreadsheetApp.getActive(), done = 0, skipped = [];
  (body.updates || []).forEach(function (u) {
    var sheet = book.getSheetByName(u.sheet);
    if (!sheet) return skipped.push(u.row + ' (no sheet ' + u.sheet + ')');
    if (ALLOWED.indexOf(u.status) < 0) return skipped.push(u.row + ' (bad status)');
    if (String(sheet.getRange(u.row, KIND_COL).getValue()).trim() !== 'item') {
      return skipped.push(u.row + ' (not an item row)');
    }
    sheet.getRange(u.row, STATUS_COL).setValue(u.status);
    done++;
  });
  return reply({ updated: done, skipped: skipped });
}

function reply(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
