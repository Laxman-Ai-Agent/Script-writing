"""Learning DB core: constants, local store, cell rendering, sheet-grid parsing (pure, no Google API)."""
import argparse
import datetime
import difflib
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB_DIR = HERE / "learning-db"  # one JSON file per Script ID
OLD_DB = HERE / "learning-db.json"  # pre-2026-11-18 single file, migrated by load()/save()
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
SCHEMA = 3  # 3 = Category column I (2 = Script ID + Title columns)
CATEGORIES = ["Dark World", "Health Decode", "Zumba Fitness"]
CAT_COL = "H"  # Category = column H, the RUN buttons are the last column (I)
RUN_COL = "I"
_HEALTH = re.compile(
    r"symptom|treatment|disease|health|doctor|cancer|insulin|diabet|thyroid|asthma|epilep|apnea|acidity|diarrh|ORS"
    r"|first aid|inhaler|blood pressure|kidney|an[a]?emia|vitamin|మలబద్ధ|విరేచన|ఆరోగ్య|వ్యాధి|క్యాన్సర్|మూర్ఛ|ఆస్తమా|షుగర్"
    r"|మధుమేహ|థైరాయిడ్|కిడ్నీ|డాక్టర్|వైద్య", re.I)
CELL_LIMIT = 50000  # Google Sheets hard limit per cell


def today():
    return datetime.date.today().isoformat()


# ---------- local store ----------

def title_of(text):
    return next((ln.strip() for ln in text.splitlines() if ln.strip()), "")


def category_of(title):
    """Zumba -> Zumba Fitness; health / body / disease / medicine topic -> Health Decode; everything else -> Dark World.
    A guess only: the Category cell in the sheet can be changed by hand and is never overwritten."""
    if re.search(r"zumba|జుంబా", title, re.I):
        return CATEGORIES[2]
    return CATEGORIES[1] if _HEALTH.search(title) else CATEGORIES[0]


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
        rec.setdefault("category", category_of(rec["title"]))
        if db.get("schema") != SCHEMA:
            rec["synced"] = False
    db["schema"] = SCHEMA
    db["records"] = dict(sorted(recs.items()))
    return db


def _write(path, text):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)  # atomic: never leave a half-written file


def load(path=DB_DIR):
    """One file per record (learning-db/S001.json ...) + _meta.json, so no file grows past a few hundred lines.
    Migrates the old single learning-db.json on first load."""
    if path.is_dir():
        db = json.loads((path / "_meta.json").read_text(encoding="utf-8")) if (path / "_meta.json").exists() else {}
        db["records"] = {f.stem: json.loads(f.read_text(encoding="utf-8")) for f in sorted(path.glob("S*.json"))}
    elif path == DB_DIR and OLD_DB.exists():
        db = json.loads(OLD_DB.read_text(encoding="utf-8"))
    else:
        db = {"records": {}}
    return normalize(db)


def save(db, path=DB_DIR):
    path.mkdir(exist_ok=True)
    for rid, rec in db["records"].items():
        _write(path / f"{rid}.json", json.dumps(rec, ensure_ascii=False, indent=2))
    for f in path.glob("S*.json"):  # ids renamed by normalize()
        if f.stem not in db["records"]:
            f.unlink()
    _write(path / "_meta.json", json.dumps({k: v for k, v in db.items() if k != "records"}, ensure_ascii=False))
    if path == DB_DIR and OLD_DB.exists():
        OLD_DB.unlink()  # migrated


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
    rec = {"created": today(), "title": title_of(text), "category": category_of(title_of(text)), "original": text, "revisions": [], "changes": [],
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
        mark = {"approved": "✅ APPROVED", "superseded": "⛔ SUPERSEDED"}.get(r["status"], "⏳ PROPOSED")
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
    """Controls of the Learning DB tab ({'h1': ..., 'rows': [(row, script id, RUN cell)]}) -> what the watcher must do."""
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


def rule_category(rec, r):
    """A rule belongs to the category of the script it came from (old rules: the record's category)."""
    return r.get("category") or rec.get("category") or category_of(rec["title"])


def approved_rules(db, category=None):
    """Approved rules; with `category` only that channel's rules: a rule never leaks into another category."""
    out = []
    for rid, rec in db["records"].items():
        for r in rec["rules"]:
            if r["status"] == "approved" and (category is None or rule_category(rec, r) == category):
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

