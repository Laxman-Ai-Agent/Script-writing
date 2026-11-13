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

    def ensure_tab(self):
        meta = self.run(self.api.get(spreadsheetId=SHEET_ID, fields="sheets.properties.title"))
        if TAB not in [s["properties"]["title"] for s in meta["sheets"]]:
            self.run(self.api.batchUpdate(spreadsheetId=SHEET_ID, body={
                "requests": [{"addSheet": {"properties": {"title": TAB}}}]}))
        head = self.run(self.api.values().get(spreadsheetId=SHEET_ID, range=f"'{TAB}'!A1:E1")).get("values", [[]])
        if head[0] != HEADERS:
            self.write_row(1, HEADERS)

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
