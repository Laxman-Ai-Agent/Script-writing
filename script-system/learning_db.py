"""Script Learning Database: local store (learning-db/S###.json, one file per script) mirrored to one Google Sheet tab.

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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ldb_core import *  # noqa: E402,F401,F403
from ldb_sheet import *  # noqa: E402,F401,F403


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
    sub.add_parser("check"); sub.add_parser("sync"); sub.add_parser("list")
    rp = sub.add_parser("rules"); rp.add_argument("category", nargs="?", choices=CATEGORIES)
    rp.add_argument("--all", action="store_true", help="show every approved rule (default: newest 20 general ones)")
    a = sub.add_parser("add-original"); a.add_argument("file"); a.add_argument("--id")
    for name in ("add-revision", "add-changes", "add-feedback"):
        x = sub.add_parser(name); x.add_argument("id"); x.add_argument("file")
    x = sub.add_parser("add-rule"); x.add_argument("id"); x.add_argument("scope", choices=["general", "topic"])
    x.add_argument("text"); x.add_argument("--approved", action="store_true")
    x = sub.add_parser("approve"); x.add_argument("id"); x.add_argument("n", type=int)
    x = sub.add_parser("supersede"); x.add_argument("id"); x.add_argument("n", type=int); x.add_argument("by")
    x = sub.add_parser("history-last"); x.add_argument("channel", choices=["dark", "health", "zumba"]); x.add_argument("--n", type=int, default=3)
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
    if args.cmd == "history-last":  # only what the no-repeat check needs, instead of reading all of history.json
        hist = json.loads((Path(__file__).parent / "history.json").read_text(encoding="utf-8"))
        mine = [h for h in hist if h.get("channel", "dark") == args.channel][-args.n:]
        for h in mine:
            print(f"{h['date']} | opening {h['opening']} | structure {h['structure']} | ending {h['ending']} | {h['topic'][:60]}")
            f = Path(__file__).resolve().parent.parent / h.get("file", "")
            if f.is_file():  # the actual wording, so the new script can avoid reusing it (not just the type codes)
                paras = [p.strip() for p in f.read_text(encoding="utf-8").split("\n")[1:] if p.strip()]
                if paras:
                    print(f"   starts: {paras[0][:110]}\n   intro ends: ...{paras[0][-90:]}\n   ends: ...{paras[-1][-140:]}")
        print(f"({len(mine)} most recent {args.channel} scripts; do NOT reuse their wording; append new entries to script-system/history.json)")
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
            if cell(cur, 7).strip() in CATEGORIES and rec.get("category") != cell(cur, 7).strip():
                rec["category"] = cell(cur, 7).strip()  # the Category the user picked in the sheet decides which rules this update feeds
                save(db)
            print(f"=== {rid} (sheet row {r}) | title: {rec['title']} | CATEGORY: {rec['category']} | {'NEW INPUT' if fresh else 'NO NEW INPUT'} ===")
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
    if args.cmd == "rules":  # one category = only its rules; no argument = every category, each under its own heading
        for cat in ([args.category] if args.category else CATEGORIES):
            print(f"## {cat}\n" + ("\n".join(approved_rules(db, cat, None if args.all else 20)) or "(no approved rules yet)"))
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
        rec["rules"].append({"date": today(), "scope": args.scope, "text": args.text, "category": rule_category(rec, {}),
                             "status": "approved" if args.approved else "proposed"})
        rec["synced"] = False
        print(f"Rule {len(rec['rules'])} added ({'approved' if args.approved else 'proposed'}).")
    elif args.cmd == "approve":
        rec = get(db, args.id)
        rec["rules"][args.n - 1]["status"] = "approved"
        rec["synced"] = False
        print(f"Rule {args.n} approved.")
    elif args.cmd == "supersede":  # kept for history, no longer printed by `rules`
        rec = get(db, args.id)
        r = rec["rules"][args.n - 1]
        r["status"], r["superseded_by"] = "superseded", args.by
        rec["synced"] = False
        print(f"Rule {args.n} superseded by {args.by}.")
    elif args.cmd == "sync":
        pass

    save(db)  # local first, so nothing is lost if the sheet is down
    print(sync_pending(db))
    save(db)


if __name__ == "__main__":
    main()
