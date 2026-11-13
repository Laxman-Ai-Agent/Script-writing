"""Script Learning Database: local store (learning-db.json) mirrored to one Google Sheet tab.

Columns: Script ID | Title | Original Script | Revised / Updated Script | Changes Made | My Feedback | Learning Rules.
Local JSON is the source of truth (keeps every revision/feedback); the sheet is a mirror.
A row is identified by its Script ID (S001, S002, ... assigned when the script is written; column A).

Usage (run from project root):
  python script-system/learning_db.py check
  python script-system/learning_db.py add-original output/<dir>/script.txt   # assigns the next Script ID (S001, S002, ...)
  python script-system/learning_db.py add-revision <id> <file>
  python script-system/learning_db.py diff <id>                 # raw sentence diff, helps write Changes
  python script-system/learning_db.py add-changes <id> <file>
  python script-system/learning_db.py add-feedback <id> <file>
  python script-system/learning_db.py add-rule <id> general|topic "<rule>" [--approved]
  python script-system/learning_db.py approve <id> <rule-number>
  python script-system/learning_db.py rules                     # approved rules, read before writing
  python script-system/learning_db.py show <id> | list | sync
  python script-system/learning_db.py words <file>               # narration word count (title line excluded)
  python script-system/learning_db.py requests                  # ON rows still to write (+ skipped counts, RUN cell); creates/upgrades the tab
  python script-system/learning_db.py request-start <row> | request-fail <row> "<reason>" | run-finish "<summary>"
  python script-system/learning_db.py revisions-pending | revision-done <id> [--note ...] | revision-fail <id> "<why>" | ldb-finish "<summary>"
  python script-system/learning_db.py request-done <row> <id> [--note "6 min, material short"]   # Status = Done: <id> (note)

Auth: service account JSON at $GOOGLE_APPLICATION_CREDENTIALS or script-system/credentials/service-account.json
(gitignored). Share the sheet with the service account's client_email as Editor.
"""
import argparse
import datetime
import difflib
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB_PATH = HERE / "learning-db.json"
SHEET_ID = "141B4qwm4Un9dXPzULWClZaUrjhcugjhoczSGrjik040"
TAB = "Script Learning Database"
REQ_TAB = "Script Requests"
REQ_HEADERS = ["Script ID", "Topic / Script", "Extra Data", "Minutes", "ON/OFF", "Status"]
RUN_STATES = ["Idle", "RUN NOW"]  # cell B1 of the requests tab; data rows start at 3
G_REST, G_START, G_RUN = "▶ RUN", "▶ START", "⏳ RUNNING"  # per-row RUN control (column G)
ALL_REST, ALL_START, ALL_RUN = "▶ RUN ALL", "▶ START ALL", "⏳ RUNNING ALL"  # RUN ALL control (cell G2)
ALL_STATES = [ALL_REST, ALL_START, ALL_RUN]
DONE_CELL, ASK_CELL = "✅ DONE", "❌ ASK"  # Learning DB row RUN cell: pasted update processed / needs the user (see hover note)
WORDS_PER_MIN = 150  # same estimate as writing-dna.md section 8
MINUTE_OPTIONS = (
    [f"Up to {n} min" for n in ("1", "2", "3", "5", "10", "15")]
    + [f"Exact {n} min" for n in ("1", "1.30", "2", "3", "5", "7", "10", "15", "20", "30")]
    + ["5-7 min", "7-10 min", "10-15 min", "15-20 min", "20-30 min"]
    + [f"{n}+ min" for n in ("5", "10", "15", "20", "30")]
)
HEADERS = ["Script ID", "Title", "Original Script", "Revised / Updated Script", "Changes Made", "My Feedback",
           "Learning Rules"]
LAST_COL = chr(64 + len(HEADERS))  # G
ID_RE = re.compile(r"S[0-9]{3,}")
SCHEMA = 2  # 2 = Script ID + Title columns
CELL_LIMIT = 50000  # Google Sheets hard limit per cell


def today():
    return datetime.date.today().isoformat()


# ---------- local store ----------

def title_of(text):
    return next((ln.strip() for ln in text.splitlines() if ln.strip()), "")


def new_id(db):
    n = max([int(k[1:]) for k in db["records"] if ID_RE.fullmatch(k)], default=0) + 1
    return f"S{n:03d}"


def normalize(db):
    """Idempotent upgrade: old slug ids -> S001..., titles filled, everything re-synced once after a schema change."""
    recs = db["records"]
    n = max([int(k[1:]) for k in recs if ID_RE.fullmatch(k)], default=0)
    for k in [k for k in recs if not ID_RE.fullmatch(k)]:
        n += 1
        rec = recs.pop(k)
        rec.update(slug=k, synced=False)
        recs[f"S{n:03d}"] = rec
    for rec in recs.values():
        rec.setdefault("title", title_of(rec["revisions"][-1]["text"] if rec["revisions"] else rec["original"]))
        if db.get("schema") != SCHEMA:
            rec["synced"] = False
    db["schema"] = SCHEMA
    db["records"] = dict(sorted(recs.items()))
    return db


def load(path=DB_PATH):
    db = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"records": {}}
    return normalize(db)


def save(db, path=DB_PATH):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)  # atomic: never leave a half-written DB


def resolve(db, rid):
    """'S001', 's001' or an old slug -> the record's Script ID."""
    recs = db["records"]
    if rid in recs:
        return rid
    if rid.upper() in recs:
        return rid.upper()
    key = next((k for k, r in recs.items() if r.get("slug") == rid), None)
    if key is None:
        sys.exit(f"No script '{rid}'. Known: {', '.join(recs) or '(none)'}")
    return key


def get(db, rid):
    return db["records"][resolve(db, rid)]


def add_original(db, rid, text):
    """-> (id, record, is_new). rid None = assign the next Script ID. Same original text again = existing record."""
    text = text.strip("\n")
    for other_id, other in db["records"].items():
        if other["original"] == text:
            if rid not in (None, other_id):
                raise ValueError(f"Same original already stored as '{other_id}'.")
            return other_id, other, False
    if rid is None:
        rid = new_id(db)
    elif not ID_RE.fullmatch(rid):
        raise ValueError(f"Script ID must look like S001, got '{rid}'.")
    elif rid in db["records"]:
        raise ValueError(f"'{rid}' already has a different original; originals are never overwritten.")
    rec = {"created": today(), "title": title_of(text), "original": text, "revisions": [], "changes": [],
           "feedback": [], "rules": [], "synced": False}
    db["records"][rid] = rec
    return rid, rec, True


def append_entry(rec, key, text, **extra):
    text = text.strip("\n")
    if any(e["text"] == text for e in rec[key]):
        return False  # duplicate entry
    rec[key].append({"date": today(), "text": text, **extra})
    if key == "revisions":
        rec["title"] = title_of(text)  # Title follows the latest revision; the Original Script cell never changes
    rec["synced"] = False
    return True


# ---------- cell rendering ----------

def stacked(entries, label):
    """Newest first, each entry with a header, nothing dropped."""
    n = len(entries)
    return "\n\n".join(f"=== {label} {n - i} ({e['date']}) ===\n{e['text']}"
                       for i, e in enumerate(reversed(entries)))


def render_rules(rules):
    lines = []
    for i, r in enumerate(rules, 1):
        mark = "✅ APPROVED" if r["status"] == "approved" else "⏳ PROPOSED"
        lines.append(f"{i}. [{mark}] [{r['scope'].upper()}] {r['text']}")
    return "\n".join(lines)


def render_feedback(rec):
    return stacked(rec["feedback"], "Feedback")


def row_values(rid, rec):
    """Revised column = the latest updated script ONLY (older revisions stay in learning-db.json)."""
    latest = rec["revisions"][-1]["text"] if rec["revisions"] else ""
    cells = [rid, rec["title"], rec["original"], latest, stacked(rec["changes"], "Changes for revision"),
             render_feedback(rec), render_rules(rec["rules"])]
    for name, c in zip(HEADERS, cells):
        if len(c) > CELL_LIMIT:
            raise ValueError(f"'{name}' exceeds the 50,000-char cell limit; refusing to truncate.")
    return cells


# ---------- sheet ----------

class GoogleSheet:
    """Thin wrapper over the official Sheets API v4."""

    def __init__(self):
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or str(HERE / "credentials" / "service-account.json")
        if not Path(cred_path).exists():
            raise RuntimeError(f"No credentials at {cred_path}")
        creds = service_account.Credentials.from_service_account_file(
            cred_path, scopes=["https://www.googleapis.com/auth/spreadsheets"])
        self.email = creds.service_account_email
        self.api = build("sheets", "v4", credentials=creds, cache_discovery=False).spreadsheets()

    def run(self, req):
        return req.execute(num_retries=5)  # exponential backoff on 429/5xx

    def ensure(self, tab, headers, row=1):
        meta = self.run(self.api.get(spreadsheetId=SHEET_ID, fields="sheets.properties.title"))
        if tab not in [s["properties"]["title"] for s in meta["sheets"]]:
            self.run(self.api.batchUpdate(spreadsheetId=SHEET_ID, body={
                "requests": [{"addSheet": {"properties": {"title": tab}}}]}))
        end = chr(64 + len(headers))
        head = self.run(self.api.values().get(spreadsheetId=SHEET_ID, range=f"'{tab}'!A{row}:{end}{row}")).get("values", [[]])
        if head[0] != headers:
            self.run(self.api.values().update(spreadsheetId=SHEET_ID, range=f"'{tab}'!A{row}:{end}{row}",
                                              valueInputOption="RAW", body={"values": [headers]}))

    def ensure_tab(self):
        """Learning DB tab: headers + the RUN column H (H1 = RUN ALL). Formatting is rebuilt only when it is missing."""
        self.ensure(TAB, HEADERS)
        sid = self._sheet_id(TAB)
        h1 = (self.run(self.api.values().get(spreadsheetId=SHEET_ID, range=f"'{TAB}'!H1")).get("values") or [[""]])[0][0]
        meta = self.run(self.api.get(spreadsheetId=SHEET_ID, fields="sheets(properties.sheetId,conditionalFormats)"))
        n_rules = len(next(s for s in meta["sheets"] if s["properties"]["sheetId"] == sid).get("conditionalFormats", []))
        if h1 not in ALL_STATES or n_rules != 5:
            self._put([{"range": f"'{TAB}'!H1", "values": [[h1 if h1 in ALL_STATES else ALL_REST]]}])
            rng = lambda r0, r1, c0, c1: {"sheetId": sid, "startRowIndex": r0, "endRowIndex": r1,
                                          "startColumnIndex": c0, "endColumnIndex": c1}
            dv = lambda r, vals: {"setDataValidation": {"range": r, "rule": {"condition": {
                "type": "ONE_OF_LIST", "values": [{"userEnteredValue": v} for v in vals]},
                "showCustomUi": True, "strict": True}}}
            GREEN, ORANGE, RED, AMBER = (0.72, 0.88, 0.80), (1.0, 0.85, 0.55), (0.96, 0.78, 0.76), (1.0, 0.95, 0.62)
            colour = lambda text, rgb: {"addConditionalFormatRule": {"index": 0, "rule": {"ranges": [rng(0, 1000, 7, 8)], "booleanRule": {
                "condition": {"type": "TEXT_STARTS_WITH", "values": [{"userEnteredValue": text}]},
                "format": {"backgroundColor": {"red": rgb[0], "green": rgb[1], "blue": rgb[2]}}}}}}
            self.run(self.api.batchUpdate(spreadsheetId=SHEET_ID, body={"requests": [
                *[{"deleteConditionalFormatRule": {"sheetId": sid, "index": 0}} for _ in range(n_rules)],  # ours only
                colour("▶ RUN", GREEN), colour("▶ START", AMBER), colour("⏳", ORANGE), colour("✅", GREEN), colour("❌", RED),
                dv(rng(0, 1, 7, 8), ALL_STATES),
                dv(rng(1, 1000, 7, 8), [G_REST, G_START, G_RUN, DONE_CELL, ASK_CELL]),
                {"repeatCell": {"range": rng(0, 1000, 7, 8), "cell": {"userEnteredFormat": {
                    "textFormat": {"bold": True}, "horizontalAlignment": "CENTER"}},
                    "fields": "userEnteredFormat(textFormat,horizontalAlignment)"}},
                {"updateDimensionProperties": {"range": {"sheetId": sid, "dimension": "COLUMNS", "startIndex": 7, "endIndex": 8},
                                               "properties": {"pixelSize": 130}, "fields": "pixelSize"}}]}))
        sc = ldb_scan(self.ldb_controls())
        self.ldb_fill(sc["fill"], sc["clear"])

    def _sheet_id(self, tab):
        meta = self.run(self.api.get(spreadsheetId=SHEET_ID, fields="sheets.properties(sheetId,title)"))
        return next((s["properties"]["sheetId"] for s in meta["sheets"] if s["properties"]["title"] == tab), None)

    def ensure_requests(self):
        """Row 1 = headers (G1 = the RUN ALL control), data from row 2:
        Script ID | Topic | Extra | Minutes | ON/OFF | Status | per-row RUN. Idempotent. Upgrades the earlier layout that
        had a RUN/Idle control row on top: that row is deleted and everything moves up one row."""
        g = lambda rng, **kw: self.run(self.api.values().get(
            spreadsheetId=SHEET_ID, range=f"'{REQ_TAB}'!{rng}", **kw)).get("values", [])
        sid = self._sheet_id(REQ_TAB)
        if sid is not None:
            a1 = (g("A1") or [[""]])[0][0]
            if a1 == "RUN":
                self.run(self.api.batchUpdate(spreadsheetId=SHEET_ID, body={"requests": [{"deleteDimension": {"range": {
                    "sheetId": sid, "dimension": "ROWS", "startIndex": 0, "endIndex": 1}}}]}))
            elif a1 not in ("", "Script ID"):
                raise RuntimeError("Script Requests has rows in an unknown layout; move them aside before upgrading.")
        self.ensure(REQ_TAB, REQ_HEADERS, row=1)
        sid = self._sheet_id(REQ_TAB)
        if (g("G1") or [[""]])[0][0] not in ALL_STATES:
            self.set_all_cell(ALL_REST)
        meta = self.run(self.api.get(spreadsheetId=SHEET_ID, fields="sheets(properties.sheetId,conditionalFormats)"))
        n_rules = len(next(s for s in meta["sheets"] if s["properties"]["sheetId"] == sid).get("conditionalFormats", []))
        rng = lambda r0, r1, c0, c1: {"sheetId": sid, "startRowIndex": r0, "endRowIndex": r1,
                                      "startColumnIndex": c0, "endColumnIndex": c1}
        dv = lambda r, vals, strict: {"setDataValidation": {"range": r, "rule": {"condition": {
            "type": "ONE_OF_LIST", "values": [{"userEnteredValue": v} for v in vals]},
            "showCustomUi": True, "strict": strict}}}
        bold = lambda r: {"repeatCell": {"range": r, "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
                                         "fields": "userEnteredFormat.textFormat.bold"}}
        wrap = {"repeatCell": {"range": rng(1, 1000, 1, 3), "cell": {"userEnteredFormat": {
            "wrapStrategy": "WRAP", "verticalAlignment": "TOP"}},
            "fields": "userEnteredFormat(wrapStrategy,verticalAlignment)"}}
        runcol = {"repeatCell": {"range": rng(0, 1000, 6, 7), "cell": {"userEnteredFormat": {
            "textFormat": {"bold": True}, "horizontalAlignment": "CENTER"}},
            "fields": "userEnteredFormat(textFormat,horizontalAlignment)"}}
        width = lambda c, px: {"updateDimensionProperties": {"range": {
            "sheetId": sid, "dimension": "COLUMNS", "startIndex": c, "endIndex": c + 1},
            "properties": {"pixelSize": px}, "fields": "pixelSize"}}
        GREEN, ORANGE, RED, AMBER = (0.72, 0.88, 0.80), (1.0, 0.85, 0.55), (0.96, 0.78, 0.76), (1.0, 0.95, 0.62)
        colour = lambda r, kind, text, rgb: {"addConditionalFormatRule": {"index": 0, "rule": {"ranges": [r], "booleanRule": {
            "condition": {"type": kind, "values": [{"userEnteredValue": text}]},
            "format": {"backgroundColor": {"red": rgb[0], "green": rgb[1], "blue": rgb[2]}}}}}}
        status, runc = rng(1, 1000, 5, 6), rng(0, 1000, 6, 7)
        self.run(self.api.batchUpdate(spreadsheetId=SHEET_ID, body={"requests": [
            *[{"deleteConditionalFormatRule": {"sheetId": sid, "index": 0}} for _ in range(n_rules)],  # ours only; rebuilt below
            colour(status, "TEXT_STARTS_WITH", "✅", GREEN), colour(status, "TEXT_STARTS_WITH", "⏳", ORANGE),
            colour(status, "TEXT_STARTS_WITH", "❌", RED),
            colour(runc, "TEXT_STARTS_WITH", "▶ RUN", GREEN), colour(runc, "TEXT_STARTS_WITH", "▶ START", AMBER),
            colour(runc, "TEXT_STARTS_WITH", "⏳", ORANGE),
            # leftovers from earlier layouts (e.g. the old Minutes dropdown that now sits under Extra Data): no rule = cleared
            {"setDataValidation": {"range": rng(0, 1000, 0, 3)}}, {"setDataValidation": {"range": rng(0, 1000, 5, 6)}},
            dv(rng(0, 1, 6, 7), ALL_STATES, True),
            dv(rng(1, 1000, 6, 7), [G_REST, G_START, G_RUN], True),
            dv(rng(1, 1000, 3, 4), MINUTE_OPTIONS, False),
            dv(rng(1, 1000, 4, 5), ["ON", "OFF"], True),
            {"updateSheetProperties": {"properties": {"sheetId": sid, "gridProperties": {"frozenRowCount": 1}},
                                       "fields": "gridProperties.frozenRowCount"}},
            bold(rng(0, 1, 0, 6)), wrap, runcol,
            *[width(c, px) for c, px in enumerate((90, 520, 300, 130, 80, 280, 130))]]}))
        sc = scan(self.grid())
        self.fill_run_cells(sc["fill"], sc["clear"])

    def pending_requests(self):
        """-> (ON rows still to write, {'off': n, 'done': n})"""
        self.ensure_requests()
        res = self.run(self.api.values().get(spreadsheetId=SHEET_ID, range=f"'{REQ_TAB}'!A2:G"))
        return parse_requests(res.get("values", []))

    def run_flag(self):
        """State of the RUN ALL control (G1)."""
        return (self.run(self.api.values().get(spreadsheetId=SHEET_ID, range=f"'{REQ_TAB}'!G1")).get("values") or [[""]])[0][0]

    def grid(self):
        return self.run(self.api.values().get(spreadsheetId=SHEET_ID, range=f"'{REQ_TAB}'!A1:G1000")).get("values", [])

    def _put(self, data):
        res = self.run(self.api.values().batchUpdate(spreadsheetId=SHEET_ID, body={"valueInputOption": "RAW", "data": data}))
        if res.get("totalUpdatedCells") != sum(len(d["values"][0]) for d in data):
            raise RuntimeError("API did not confirm the update")

    def set_row_state(self, row, status, run_cell, script_id=None):
        data = [{"range": f"'{REQ_TAB}'!F{row}:G{row}", "values": [[status, run_cell]]}]
        if script_id:
            data.append({"range": f"'{REQ_TAB}'!A{row}", "values": [[script_id]]})
        self._put(data)

    def claim(self, rows):
        """Mark the rows a run will write: Status and RUN cell both show running."""
        self._put([{"range": f"'{REQ_TAB}'!F{r}:G{r}", "values": [[G_RUN, G_RUN]]} for r in rows])

    def release(self, rows):
        """Rows a stopped run left claimed: button back to RUN, an unfinished status becomes a failure."""
        for r in rows:
            st = (self.run(self.api.values().get(spreadsheetId=SHEET_ID, range=f"'{REQ_TAB}'!F{r}")).get("values")
                  or [[""]])[0][0]
            self.set_row_state(r, "❌ Failed: run stopped" if st.startswith("⏳") else st, G_REST)

    def fill_run_cells(self, fill, clear=()):
        if fill:
            self._put([{"range": f"'{REQ_TAB}'!G{r}", "values": [[G_REST]]} for r in fill])
        if clear:
            self.run(self.api.values().batchClear(spreadsheetId=SHEET_ID, body={
                "ranges": [f"'{REQ_TAB}'!G{r}" for r in clear]}))

    def set_all_cell(self, text, note=None):
        """The RUN ALL control (G1). `note` = hover note with the last run's summary (no clutter in the grid)."""
        self._put([{"range": f"'{REQ_TAB}'!G1", "values": [[text]]}])
        if note is not None:
            self.run(self.api.batchUpdate(spreadsheetId=SHEET_ID, body={"requests": [{"updateCells": {
                "range": {"sheetId": self._sheet_id(REQ_TAB), "startRowIndex": 0, "endRowIndex": 1,
                          "startColumnIndex": 6, "endColumnIndex": 7},
                "rows": [{"values": [{"note": note}]}], "fields": "note"}}]}))

    def first_cols(self):
        """Columns A:C of every row (Script ID, Title, Original Script) - used to find a record's row."""
        return self.run(self.api.values().get(spreadsheetId=SHEET_ID, range=f"'{TAB}'!A:C")).get("values", [])

    def get_row(self, row):
        return (self.run(self.api.values().get(spreadsheetId=SHEET_ID, range=f"'{TAB}'!A{row}:H{row}")).get("values") or [[]])[0]

    def write_row(self, row, values, skip=()):
        """Write the row's cells A..G; indexes in `skip` (typed/pasted input) are left untouched."""
        data, i = [], 0
        while i < len(values):
            if i in skip:
                i += 1
                continue
            j = i
            while j < len(values) and j not in skip:
                j += 1
            data.append({"range": f"'{TAB}'!{chr(65 + i)}{row}:{chr(64 + j)}{row}", "values": [values[i:j]]})
            i = j
        res = self.run(self.api.values().batchUpdate(spreadsheetId=SHEET_ID, body={"valueInputOption": "RAW", "data": data}))
        if res.get("totalUpdatedCells", 0) < 1:
            raise RuntimeError("API did not confirm the write")
        return row

    def append_row(self, values):
        res = self.run(self.api.values().append(
            spreadsheetId=SHEET_ID, range=f"'{TAB}'!A:{LAST_COL}", valueInputOption="RAW",
            insertDataOption="INSERT_ROWS", body={"values": [values]}))
        upd = res.get("updates", {})
        if not upd.get("updatedCells"):
            raise RuntimeError("API did not confirm the append")
        return int(re.search(r"![A-Z]+(\d+)", upd["updatedRange"]).group(1))

    # ---- Learning DB RUN column (H): only columns A and H are polled, the big script cells are not
    def ldb_controls(self):
        res = self.run(self.api.values().batchGet(spreadsheetId=SHEET_ID, ranges=[f"'{TAB}'!A1:A1000", f"'{TAB}'!H1:H1000"]))
        a, h = [vr.get("values", []) for vr in res["valueRanges"]]
        cell = lambda col, i: (col[i][0].strip() if i < len(col) and col[i] else "")
        return {"h1": cell(h, 0), "rows": [(i + 1, cell(a, i), cell(h, i)) for i in range(1, max(len(a), len(h)))]}

    def ldb_all(self):
        return self.run(self.api.values().get(spreadsheetId=SHEET_ID, range=f"'{TAB}'!A1:H1000")).get("values", [])

    def ldb_note(self, row, col, text):
        self.run(self.api.batchUpdate(spreadsheetId=SHEET_ID, body={"requests": [{"updateCells": {
            "range": {"sheetId": self._sheet_id(TAB), "startRowIndex": row - 1, "endRowIndex": row,
                      "startColumnIndex": col, "endColumnIndex": col + 1},
            "rows": [{"values": [{"note": text}]}], "fields": "note"}}]}))

    def ldb_mark(self, row, text, note=None):
        self._put([{"range": f"'{TAB}'!H{row}", "values": [[text]]}])
        if note is not None:
            self.ldb_note(row, 7, note)

    def ldb_fill(self, fill, clear=()):
        if fill:
            self._put([{"range": f"'{TAB}'!H{r}", "values": [[G_REST]]} for r in fill])
        if clear:
            self.run(self.api.values().batchClear(spreadsheetId=SHEET_ID, body={"ranges": [f"'{TAB}'!H{r}" for r in clear]}))

    def ldb_claim(self, rows):
        self._put([{"range": f"'{TAB}'!H{r}", "values": [[G_RUN]]} for r in rows])

    def ldb_release(self, rows):
        for r in rows:
            self.ldb_mark(r, ASK_CELL, "The run stopped before this row was processed. Click START again.")

    def ldb_set_all(self, text, note=None):
        self._put([{"range": f"'{TAB}'!H1", "values": [[text]]}])
        if note is not None:
            self.ldb_note(1, 7, note)


def _mins(s):
    """'5' -> 5.0, '1.30' -> 1.5 (project convention: m.ss = minutes.seconds)."""
    m, _, sec = s.strip().partition(".")
    return int(m) + (int((sec + "0")[:2]) / 60 if sec else 0)


def describe_minutes(cell):
    """Dropdown/typed Minutes cell -> plain-English length instruction. Bare number = maximum."""
    s = (cell or "").strip().lower() or "1"
    w = lambda m: int(round(m * WORDS_PER_MIN))
    num = r"(\d+(?:\.\d+)?)"
    if m := re.match(rf"up to {num}", s) or re.fullmatch(num, s):
        v = _mins(m.group(1))
        return f"UP TO {v:g} min = at most ~{w(v)} words. Never pad; if the topic has less, write the natural shorter length and say so in the note."
    if m := re.match(rf"exact(?:ly)? {num}", s):
        v = _mins(m.group(1))
        return (f"EXACTLY ~{v:g} min = ~{w(v)} words (+-10%). If research is thin, add related angles that really belong to the topic "
                "(history, side angles, FAQs, examples) and name them in the note.")
    if m := re.match(rf"{num}\s*-\s*{num}", s):
        lo, hi = _mins(m.group(1)), _mins(m.group(2))
        return f"{lo:g}-{hi:g} min = {w(lo)}-{w(hi)} words. Stay inside the range; if the topic can't reach the low end, say so in the note."
    if m := re.match(rf"{num}\+", s):
        lo = _mins(m.group(1))
        return (f"{lo:g}+ min = at least ~{w(lo)} words; longer is fine (up to ~{w(lo * 1.5)}) if the topic supports it. "
                "If material is thin, write what is real and say so in the note.")
    raise ValueError(f"Unknown Minutes value '{cell}'. Use a dropdown option or a plain number.")


def is_done(status):
    return "✅" in status or status.strip().lower().startswith("done")  # "done" = rows written before the tick icon


def _fields(r):
    """Script ID, Topic, Extra, Minutes, ON/OFF, Status, RUN cell of one sheet row (missing cells = '')."""
    return ([str(c).strip() for c in r] + [""] * 7)[:7]


def scan(grid):
    """Whole grid (A1:G..., row 1 = headers) -> what the watcher has to do."""
    cell = lambda r, c: _fields(grid[r - 1])[c] if r <= len(grid) else ""
    out = {"run_all": cell(1, 6) == ALL_START, "starts": [], "claimed": [], "fill": [], "clear": [], "on_rows": []}
    for r in range(2, len(grid) + 1):
        _, topic, _, _, onoff, status, g = _fields(grid[r - 1])
        if not topic:
            if g == G_REST:
                out["clear"].append(r)
            continue
        if g == G_START:
            out["starts"].append(r)
        if g == G_RUN:
            out["claimed"].append(r)
        if g == "":
            out["fill"].append(r)
        if onoff.upper() == "ON" and not is_done(status):
            out["on_rows"].append(r)
    return out


def parse_requests(values):
    """Rows from A2:G -> (to_run, skipped). If any row is claimed (RUN cell = running, set by the watcher for a
    RUN ALL or a row click) exactly those rows run, whatever their ON/OFF or status. Otherwise (a manual
    /script run): topic filled + ON/OFF == ON + not done. Blank / running / failed rows are retried; blank ON/OFF = OFF."""
    claimed_mode = any(_fields(r)[1] and _fields(r)[6] == G_RUN for r in values)
    out, skipped = [], {"off": 0, "done": 0}
    for i, r in enumerate(values, start=2):
        sid, topic, extra, mins, onoff, status, g = _fields(r)
        if not topic:
            continue
        if claimed_mode:
            if g != G_RUN:
                continue
        elif is_done(status):
            skipped["done"] += 1
            continue
        elif onoff.upper() != "ON":
            skipped["off"] += 1
            continue
        out.append({"row": i, "sid": sid, "topic": topic, "extra": extra, "minutes": mins or "1",
                    "kind": "SCRIPT (rewrite in our style)" if len(topic) > 300 else "TOPIC",
                    "length": describe_minutes(mins)})
    return out, skipped


def find_row(rows, rid, original):
    """Row of this script: Script ID in column A, or (rows written before IDs existed) the original text."""
    for i, r in enumerate(rows, start=1):
        if i == 1:
            continue  # header
        a = r[0] if r else ""
        c = r[2] if len(r) > 2 else ""
        if a == rid or a == original or c == original:
            return i
    return None


def pending_input(cur, rec):
    """True if the sheet row holds text the user typed or pasted (updated script in D, reasons in F) that is not in the
    local record yet. Those cells are INPUT: a sync must never overwrite them."""
    cur = ([str(c) for c in cur] + [""] * 8)[:8]
    d, f = cur[3].strip(), cur[5].strip()
    latest = rec["revisions"][-1]["text"].strip() if rec["revisions"] else ""
    legacy = stacked(rec["revisions"], "Revision").strip()  # D used to hold every revision with headers
    return (d != "" and d not in (latest, legacy)) or (f != "" and f != render_feedback(rec).strip())


def pending_rows(db, rows):
    """Whole sheet (A1:H...) -> row numbers whose D/F hold a pasted update that is not processed yet."""
    out = []
    for i, cur in enumerate(rows, start=1):
        if i == 1 or not cur or not str(cur[0]).strip():
            continue
        rec = db["records"].get(str(cur[0]).strip())
        if rec and pending_input(cur, rec):
            out.append(i)
    return out


def ldb_scan(ctl):
    """Controls of the Learning DB tab ({'h1': ..., 'rows': [(row, script id, H cell)]}) -> what the watcher must do."""
    out = {"run_all": ctl["h1"] == ALL_START, "starts": [], "claimed": [], "fill": [], "clear": []}
    for row, rid, h in ctl["rows"]:
        if not rid:
            if h in (G_REST, DONE_CELL):
                out["clear"].append(row)
            continue
        if h == G_START:
            out["starts"].append(row)
        elif h == G_RUN:
            out["claimed"].append(row)
        elif h == "":
            out["fill"].append(row)
    return out


def sync_record(sheet, rid, rec):
    """Upsert one record by Script ID -> no duplicate rows. Pasted/typed input in D and F is left alone."""
    values = row_values(rid, rec)
    row = find_row(sheet.first_cols(), rid, rec["original"])
    if row is None:
        row = sheet.append_row(values)
    else:
        row = sheet.write_row(row, values, skip=(3, 5) if pending_input(sheet.get_row(row), rec) else ())
    rec["synced"] = True
    return row


def finish_revision(sheet, rid, rec, note=None):
    """After a pasted update was processed: the row gets the clean script in D, the rebuilt E/F/G, and RUN cell = done."""
    row = find_row(sheet.first_cols(), rid, rec["original"])
    if row is None:
        raise RuntimeError(f"{rid} has no row in the sheet yet")
    sheet.write_row(row, row_values(rid, rec))
    sheet.ldb_mark(row, DONE_CELL, note if note is not None else f"{today()} - update processed")
    rec["synced"] = True
    return row


def sync_pending(db, sheet_factory=GoogleSheet):
    pending = [(rid, r) for rid, r in db["records"].items() if not r["synced"]]
    if not pending:
        return "Nothing pending."
    try:
        sheet = sheet_factory()
        sheet.ensure_tab()
        out = [f"SYNCED {rid} -> row {sync_record(sheet, rid, r)}" for rid, r in pending]
    except Exception as e:  # keep local data, report honestly
        left = [rid for rid, r in pending if not r["synced"]]
        return f"PENDING ({len(left)}: {', '.join(left)}) — sheet not updated: {e}"
    return "\n".join(out)


def approved_rules(db):
    out = []
    for rid, rec in db["records"].items():
        for r in rec["rules"]:
            if r["status"] == "approved":
                out.append(f"[{r['scope'].upper()}] {r['text']}" + (f"  (from {rid})" if r["scope"] == "topic" else ""))
    return out


def sentence_diff(a, b):
    split = lambda t: [s.strip() for s in re.split(r"(?<=[.?!…])\s+|\n+", t) if s.strip()]
    sa, sb = split(a), split(b)
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, sa, sb, autojunk=False).get_opcodes():
        if op == "equal":
            continue
        for s in sa[i1:i2]:
            out.append(f"- {s}")
        for s in sb[j1:j2]:
            out.append(f"+ {s}")
        out.append("")
    return "\n".join(out) or "(no differences)"


# ---------- CLI ----------

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("requests")
    x = sub.add_parser("request-done"); x.add_argument("row", type=int); x.add_argument("id"); x.add_argument("--note", default="")
    sub.add_parser("words").add_argument("file")
    sub.add_parser("revisions-pending")
    x = sub.add_parser("revision-done"); x.add_argument("id"); x.add_argument("--note")
    x = sub.add_parser("revision-fail"); x.add_argument("id"); x.add_argument("reason")
    sub.add_parser("ldb-finish").add_argument("summary")
    sub.add_parser("request-start").add_argument("row", type=int)
    x = sub.add_parser("request-fail"); x.add_argument("row", type=int); x.add_argument("reason")
    sub.add_parser("run-finish").add_argument("summary")
    sub.add_parser("check"); sub.add_parser("sync"); sub.add_parser("list"); sub.add_parser("rules")
    a = sub.add_parser("add-original"); a.add_argument("file"); a.add_argument("--id")
    for name in ("add-revision", "add-changes", "add-feedback"):
        x = sub.add_parser(name); x.add_argument("id"); x.add_argument("file")
    x = sub.add_parser("add-rule"); x.add_argument("id"); x.add_argument("scope", choices=["general", "topic"])
    x.add_argument("text"); x.add_argument("--approved", action="store_true")
    x = sub.add_parser("approve"); x.add_argument("id"); x.add_argument("n", type=int)
    sub.add_parser("diff").add_argument("id")
    sub.add_parser("show").add_argument("id")
    args = p.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    db = load()
    read = lambda f: Path(f).read_text(encoding="utf-8")

    if args.cmd == "words":  # narration word count (title line excluded), for the length check
        body = Path(args.file).read_text(encoding="utf-8").split(chr(10), 1)
        print(len(body[1].split()) if len(body) > 1 else 0)
        return
    if args.cmd == "requests":
        sheet = GoogleSheet()
        reqs, skipped = sheet.pending_requests()
        for r in reqs:
            print(f"--- sheet row {r['row']} | {r['kind']} | {r['minutes']} ---")
            print(f"TOPIC/SCRIPT: {r['topic']}")
            print(f"EXTRA DATA: {r['extra'] or '(none)'}")
            print(f"LENGTH: {r['length']}")
        print(f"{len(reqs)} ON row(s) to write | skipped: {skipped['off']} OFF, {skipped['done']} Done | RUN cell: {sheet.run_flag()}")
        return
    if args.cmd == "revisions-pending":
        sheet = GoogleSheet()
        sheet.ensure_tab()
        rows = ldb_scan(sheet.ldb_controls())["claimed"] or pending_rows(db, sheet.ldb_all())  # claimed by the watcher, else any pasted update
        cell = lambda cur, i: (str(cur[i]) if len(cur) > i else "")
        for r in rows:
            cur = sheet.get_row(r)
            rid = cell(cur, 0).strip()
            rec = db["records"].get(rid)
            if rec is None:
                print(f"=== sheet row {r}: unknown Script ID '{rid}' - skip it ===")
                continue
            fresh = pending_input(cur, rec)
            print(f"=== {rid} (sheet row {r}) | title: {rec['title']} | {'NEW INPUT' if fresh else 'NO NEW INPUT'} ===")
            print("--- ORIGINAL SCRIPT ---")
            print(rec["original"])
            print("--- D: Revised column, raw (the pasted update; may also hold reasons / comparison / rules) ---")
            print(cell(cur, 3))
            print("--- F: My Feedback column, raw (the user's own reasons) ---")
            print(cell(cur, 5))
        print(f"{len(rows)} row(s) to process")
        return
    if args.cmd == "revision-done":
        rid = resolve(db, args.id)
        row = finish_revision(GoogleSheet(), rid, db["records"][rid], args.note)
        save(db)
        print(f"{rid} -> row {row}: Revised column = clean script, RUN cell = {DONE_CELL}")
        return
    if args.cmd == "revision-fail":
        rid = resolve(db, args.id)
        sheet = GoogleSheet()
        row = find_row(sheet.first_cols(), rid, db["records"][rid]["original"])
        sheet.ldb_mark(row, ASK_CELL, args.reason)
        print(f"{rid} -> row {row}: {ASK_CELL} ({args.reason})")
        return
    if args.cmd == "ldb-finish":
        GoogleSheet().ldb_set_all(ALL_REST, f"{datetime.datetime.now():%Y-%m-%d %H:%M} - {args.summary}")
        print("Learning DB run finished; RUN ALL cell reset.")
        return
    if args.cmd == "request-start":
        GoogleSheet().set_row_state(args.row, G_RUN, G_RUN)
        print(f"Row {args.row} -> Running")
        return
    if args.cmd == "request-fail":
        GoogleSheet().set_row_state(args.row, f"❌ Failed: {args.reason}", G_REST)
        print(f"Row {args.row} -> ❌ Failed: {args.reason}")
        return
    if args.cmd == "run-finish":
        sheet = GoogleSheet()
        sheet.set_all_cell(ALL_REST, f"{datetime.datetime.now():%Y-%m-%d %H:%M} - {args.summary}")
        print("Run finished; RUN cell reset to Idle.")
        return
    if args.cmd == "request-done":
        rid = resolve(db, args.id)  # the script must already be saved (add-original)
        status = "✅" + (f" ({args.note})" if args.note else "")
        GoogleSheet().set_row_state(args.row, status, G_REST, rid)
        print(f"Row {args.row} -> {status} | Script ID {rid}")
        return
    if args.cmd == "check":
        s = GoogleSheet(); s.ensure_tab()
        print(f"OK: {s.email} can read/write '{TAB}' ({len(s.first_cols())} rows incl. header)")
        return
    if args.cmd == "list":
        for rid, r in db["records"].items():
            print(f"{rid} | {r['title'][:60]} | {len(r['revisions'])} revisions, {len(r['feedback'])} feedback, "
                  f"{len(r['rules'])} rules, {'synced' if r['synced'] else 'PENDING'}")
        return
    if args.cmd == "rules":
        print("\n".join(approved_rules(db)) or "(no approved rules yet)")
        return
    if args.cmd == "show":
        print(json.dumps(get(db, args.id), ensure_ascii=False, indent=2))
        return
    if args.cmd == "diff":
        r = get(db, args.id)
        if not r["revisions"]:
            sys.exit("No revision yet.")
        print(sentence_diff(r["original"], r["revisions"][-1]["text"]))
        return

    if args.cmd == "add-original":
        try:
            rid, rec, new = add_original(db, args.id, read(args.file))
        except ValueError as e:
            sys.exit(str(e))
        print(f"{'Added' if new else 'Already stored'} | Script ID: {rid} | Title: {rec['title']}")
    elif args.cmd in ("add-revision", "add-changes", "add-feedback"):
        rid = resolve(db, args.id)
        rec = db["records"][rid]
        key = {"add-revision": "revisions", "add-changes": "changes", "add-feedback": "feedback"}[args.cmd]
        extra = {"revision": len(rec["revisions"])} if key == "changes" else {}
        print(f"Added to {rid}." if append_entry(rec, key, read(args.file), **extra) else "Duplicate, skipped.")
    elif args.cmd == "add-rule":
        rec = get(db, args.id)
        rec["rules"].append({"date": today(), "scope": args.scope, "text": args.text,
                             "status": "approved" if args.approved else "proposed"})
        rec["synced"] = False
        print(f"Rule {len(rec['rules'])} added ({'approved' if args.approved else 'proposed'}).")
    elif args.cmd == "approve":
        rec = get(db, args.id)
        rec["rules"][args.n - 1]["status"] = "approved"
        rec["synced"] = False
        print(f"Rule {args.n} approved.")
    elif args.cmd == "sync":
        pass

    save(db)  # local first, so nothing is lost if the sheet is down
    print(sync_pending(db))
    save(db)


if __name__ == "__main__":
    main()
