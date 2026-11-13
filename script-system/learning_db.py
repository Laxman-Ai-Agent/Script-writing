"""Script Learning Database: local store (learning-db.json) mirrored to one Google Sheet tab.

Columns: Original Script | Revised / Updated Script | Changes Made | My Feedback | Learning Rules.
Local JSON is the source of truth (keeps every revision/feedback); the sheet is a mirror.
A row is identified by its Column 1 text (the original never changes) -> no extra id column.

Usage (run from project root):
  python script-system/learning_db.py check
  python script-system/learning_db.py add-original output/<dir>/script.txt [--id ID]
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
REQ_HEADERS = ["S.No", "Topic / Script", "Extra Data", "Minutes", "ON/OFF", "Status"]
RUN_STATES = ["Idle", "RUN NOW"]  # cell B1 of the requests tab; data rows start at 3
WORDS_PER_MIN = 150  # same estimate as writing-dna.md section 8
MINUTE_OPTIONS = (
    [f"Up to {n} min" for n in ("1", "2", "3", "5", "10", "15")]
    + [f"Exact {n} min" for n in ("1", "1.30", "2", "3", "5", "7", "10", "15", "20", "30")]
    + ["5-7 min", "7-10 min", "10-15 min", "15-20 min", "20-30 min"]
    + [f"{n}+ min" for n in ("5", "10", "15", "20", "30")]
)
HEADERS = ["Original Script", "Revised / Updated Script", "Changes Made", "My Feedback", "Learning Rules"]
CELL_LIMIT = 50000  # Google Sheets hard limit per cell


def today():
    return datetime.date.today().isoformat()


# ---------- local store ----------

def load(path=DB_PATH):
    if not path.exists():
        return {"records": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def save(db, path=DB_PATH):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)  # atomic: never leave a half-written DB


def get(db, rid):
    if rid not in db["records"]:
        sys.exit(f"No record '{rid}'. Known: {', '.join(db['records']) or '(none)'}")
    return db["records"][rid]


def add_original(db, rid, text):
    text = text.strip("\n")
    rec = db["records"].get(rid)
    if rec:
        if rec["original"] == text:
            return rec, False  # duplicate -> no-op
        raise ValueError(f"Record '{rid}' already has a different original; originals are never overwritten.")
    for other_id, other in db["records"].items():
        if other["original"] == text:
            raise ValueError(f"Same original already stored as '{other_id}'.")
    rec = {"created": today(), "original": text, "revisions": [], "changes": [],
           "feedback": [], "rules": [], "synced": False}
    db["records"][rid] = rec
    return rec, True


def append_entry(rec, key, text, **extra):
    text = text.strip("\n")
    if any(e["text"] == text for e in rec[key]):
        return False  # duplicate entry
    rec[key].append({"date": today(), "text": text, **extra})
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


def row_values(rec):
    if len(rec["original"]) > CELL_LIMIT:
        raise ValueError("Original script exceeds the 50,000-char cell limit; refusing to truncate.")
    revised = stacked(rec["revisions"], "Revision")
    if len(revised) > CELL_LIMIT:
        # ponytail: older revisions then live only in learning-db.json; split across rows if this ever matters
        revised = stacked(rec["revisions"][-1:], "Revision") + "\n\n(older revisions kept in learning-db.json)"
    cells = [rec["original"], revised, stacked(rec["changes"], "Changes for revision"),
             stacked(rec["feedback"], "Feedback"), render_rules(rec["rules"])]
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
        self.ensure(TAB, HEADERS)

    def _sheet_id(self, tab):
        meta = self.run(self.api.get(spreadsheetId=SHEET_ID, fields="sheets.properties(sheetId,title)"))
        return next((s["properties"]["sheetId"] for s in meta["sheets"] if s["properties"]["title"] == tab), None)

    def ensure_requests(self):
        """Row 1 = RUN control, row 2 = headers, data from row 3. Idempotent; adds dropdowns, S.No formulas, formatting."""
        if self._sheet_id(REQ_TAB) is not None:
            a2 = self.run(self.api.values().get(spreadsheetId=SHEET_ID, range=f"'{REQ_TAB}'!A2")).get("values", [[""]])[0][0]
            if a2 not in ("", "S.No"):
                raise RuntimeError("Script Requests has rows in the old layout; move them down before upgrading.")
        self.ensure(REQ_TAB, REQ_HEADERS, row=2)
        sid = self._sheet_id(REQ_TAB)
        top = self.run(self.api.values().get(spreadsheetId=SHEET_ID, range=f"'{REQ_TAB}'!B1")).get("values", [[""]])[0][0]
        if top not in RUN_STATES:
            self.run(self.api.values().clear(spreadsheetId=SHEET_ID, range=f"'{REQ_TAB}'!A1:F1"))
            self.run(self.api.values().update(
                spreadsheetId=SHEET_ID, range=f"'{REQ_TAB}'!A1:C1", valueInputOption="RAW",
                body={"values": [["RUN", "Idle", "Set RUN NOW to start. Only ON rows are written; Done rows are skipped."]]}))
        f = self.run(self.api.values().get(spreadsheetId=SHEET_ID, range=f"'{REQ_TAB}'!A3",
                                           valueRenderOption="FORMULA")).get("values", [[""]])[0][0]
        if not str(f).startswith("=IF"):
            self.run(self.api.values().update(
                spreadsheetId=SHEET_ID, range=f"'{REQ_TAB}'!A3:A1000", valueInputOption="USER_ENTERED",
                body={"values": [[f'=IF(B{r}<>"",ROW()-2,"")'] for r in range(3, 1001)]}))
        rng = lambda r0, r1, c0, c1: {"sheetId": sid, "startRowIndex": r0, "endRowIndex": r1,
                                      "startColumnIndex": c0, "endColumnIndex": c1}
        dv = lambda r, vals, strict: {"setDataValidation": {"range": r, "rule": {"condition": {
            "type": "ONE_OF_LIST", "values": [{"userEnteredValue": v} for v in vals]},
            "showCustomUi": True, "strict": strict}}}
        bold = lambda r: {"repeatCell": {"range": r, "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
                                         "fields": "userEnteredFormat.textFormat.bold"}}
        wrap = {"repeatCell": {"range": rng(2, 1000, 1, 3), "cell": {"userEnteredFormat": {
            "wrapStrategy": "WRAP", "verticalAlignment": "TOP"}},
            "fields": "userEnteredFormat(wrapStrategy,verticalAlignment)"}}
        width = lambda c, px: {"updateDimensionProperties": {"range": {
            "sheetId": sid, "dimension": "COLUMNS", "startIndex": c, "endIndex": c + 1},
            "properties": {"pixelSize": px}, "fields": "pixelSize"}}
        self.run(self.api.batchUpdate(spreadsheetId=SHEET_ID, body={"requests": [
            dv(rng(0, 1, 1, 2), RUN_STATES, True),
            dv(rng(2, 1000, 3, 4), MINUTE_OPTIONS, False),
            dv(rng(2, 1000, 4, 5), ["ON", "OFF"], True),
            {"updateSheetProperties": {"properties": {"sheetId": sid, "gridProperties": {"frozenRowCount": 2}},
                                       "fields": "gridProperties.frozenRowCount"}},
            bold(rng(0, 1, 0, 1)), bold(rng(1, 2, 0, 6)), wrap,
            *[width(c, px) for c, px in enumerate((60, 520, 300, 130, 80, 280))]]}))

    def pending_requests(self):
        """-> (ON rows still to write, {'off': n, 'done': n})"""
        self.ensure_requests()
        res = self.run(self.api.values().get(spreadsheetId=SHEET_ID, range=f"'{REQ_TAB}'!A3:F"))
        return parse_requests(res.get("values", []))

    def run_flag(self):
        return self.run(self.api.values().get(spreadsheetId=SHEET_ID, range=f"'{REQ_TAB}'!B1")).get("values", [[""]])[0][0]

    def run_message(self):
        return self.run(self.api.values().get(spreadsheetId=SHEET_ID, range=f"'{REQ_TAB}'!C1")).get("values", [[""]])[0][0]

    def set_request_status(self, row, text):
        res = self.run(self.api.values().update(
            spreadsheetId=SHEET_ID, range=f"'{REQ_TAB}'!F{row}", valueInputOption="RAW", body={"values": [[text]]}))
        if not res.get("updatedCells"):
            raise RuntimeError("API did not confirm the status update")

    def set_run_state(self, flag, message):
        res = self.run(self.api.values().update(
            spreadsheetId=SHEET_ID, range=f"'{REQ_TAB}'!B1:C1", valueInputOption="RAW", body={"values": [[flag, message]]}))
        if not res.get("updatedCells"):
            raise RuntimeError("API did not confirm the run-state update")

    def column_a(self):
        res = self.run(self.api.values().get(spreadsheetId=SHEET_ID, range=f"'{TAB}'!A:A"))
        return [r[0] if r else "" for r in res.get("values", [])]

    def write_row(self, row, values):
        res = self.run(self.api.values().update(
            spreadsheetId=SHEET_ID, range=f"'{TAB}'!A{row}:E{row}",
            valueInputOption="RAW", body={"values": [values]}))
        if not res.get("updatedCells"):
            raise RuntimeError("API did not confirm the write")
        return row

    def append_row(self, values):
        res = self.run(self.api.values().append(
            spreadsheetId=SHEET_ID, range=f"'{TAB}'!A:E", valueInputOption="RAW",
            insertDataOption="INSERT_ROWS", body={"values": [values]}))
        upd = res.get("updates", {})
        if not upd.get("updatedCells"):
            raise RuntimeError("API did not confirm the append")
        return int(re.search(r"![A-Z]+(\d+)", upd["updatedRange"]).group(1))


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


def parse_requests(values):
    """Rows from A3:F -> (to_run, skipped). Written only if topic filled, ON/OFF == ON and Status not 'Done...'.
    Blank/Pending/Running/Failed statuses are retried; a blank ON/OFF counts as OFF (no accidental token spend)."""
    out, skipped = [], {"off": 0, "done": 0}
    for i, r in enumerate(values, start=3):
        sno, topic, extra, mins, onoff, status = ([str(c).strip() for c in r] + [""] * 6)[:6]
        if not topic:
            continue
        if status.lower().startswith("done"):
            skipped["done"] += 1
        elif onoff.upper() != "ON":
            skipped["off"] += 1
        else:
            out.append({"row": i, "sno": sno or str(i - 2), "topic": topic, "extra": extra, "minutes": mins or "1",
                        "kind": "SCRIPT (rewrite in our style)" if len(topic) > 300 else "TOPIC",
                        "length": describe_minutes(mins)})
    return out, skipped


def sync_record(sheet, rec):
    """Upsert one record. Row found by exact Column 1 match -> no duplicates."""
    values = row_values(rec)
    col_a = sheet.column_a()
    row = next((i + 1 for i, v in enumerate(col_a) if i > 0 and v == rec["original"]), None)
    row = sheet.write_row(row, values) if row else sheet.append_row(values)
    rec["synced"] = True
    return row


def sync_pending(db, sheet_factory=GoogleSheet):
    pending = [(rid, r) for rid, r in db["records"].items() if not r["synced"]]
    if not pending:
        return "Nothing pending."
    try:
        sheet = sheet_factory()
        sheet.ensure_tab()
        out = [f"SYNCED {rid} -> row {sync_record(sheet, r)}" for rid, r in pending]
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

    if args.cmd == "check":
        s = GoogleSheet(); s.ensure_tab()
        print(f"OK: {s.email} can read/write '{TAB}' ({len(s.column_a())} rows incl. header)")
        return
    if args.cmd == "words":  # narration word count (title line excluded), for the length check
        body = Path(args.file).read_text(encoding="utf-8").split(chr(10), 1)
        print(len(body[1].split()) if len(body) > 1 else 0)
        return
    if args.cmd == "requests":
        sheet = GoogleSheet()
        reqs, skipped = sheet.pending_requests()
        for r in reqs:
            print(f"--- #{r['sno']} (sheet row {r['row']}) | {r['kind']} | {r['minutes']} ---")
            print(f"TOPIC/SCRIPT: {r['topic']}")
            print(f"EXTRA DATA: {r['extra'] or '(none)'}")
            print(f"LENGTH: {r['length']}")
        print(f"{len(reqs)} ON row(s) to write | skipped: {skipped['off']} OFF, {skipped['done']} Done | RUN cell: {sheet.run_flag()}")
        return
    if args.cmd == "request-start":
        GoogleSheet().set_request_status(args.row, "Running")
        print(f"Row {args.row} -> Running")
        return
    if args.cmd == "request-fail":
        GoogleSheet().set_request_status(args.row, f"Failed: {args.reason}")
        print(f"Row {args.row} -> Failed: {args.reason}")
        return
    if args.cmd == "run-finish":
        GoogleSheet().set_run_state("Idle", f"{datetime.datetime.now():%Y-%m-%d %H:%M} - {args.summary}")
        print("Run finished; RUN cell reset to Idle.")
        return
    if args.cmd == "request-done":
        if args.id not in db["records"]:
            sys.exit(f"No record '{args.id}' - save the original first.")
        status = f"Done: {args.id}" + (f" ({args.note})" if args.note else "")
        GoogleSheet().set_request_status(args.row, status)
        print(f"Row {args.row} -> {status}")
        return
    if args.cmd == "list":
        for rid, r in db["records"].items():
            print(f"{rid}: {len(r['revisions'])} revisions, {len(r['feedback'])} feedback, "
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
        f = Path(args.file)
        rid = args.id or (f.parent.name if f.stem == "script" else f"{f.parent.name}-{f.stem.replace('script-', '')}")
        _, new = add_original(db, rid, read(f))
        print(f"{'Added' if new else 'Already stored'}: {rid}")
    elif args.cmd in ("add-revision", "add-changes", "add-feedback"):
        rec = get(db, args.id)
        key = {"add-revision": "revisions", "add-changes": "changes", "add-feedback": "feedback"}[args.cmd]
        extra = {"revision": len(rec["revisions"])} if key == "changes" else {}
        print("Added." if append_entry(rec, key, read(args.file), **extra) else "Duplicate, skipped.")
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

    save(db)  # local first, so nothing is lost if the sheet is down
    print(sync_pending(db))
    save(db)


if __name__ == "__main__":
    main()
