"""Topic Ideas: fresh science/tech news topics per category, in the sheet tab "Topic Ideas".

  python script-system/ideas.py setup             # create/upgrade the tabs "Topic Ideas" and "Topic Settings"
  python script-system/ideas.py context           # settings + what to avoid (read by the finder run, SKILL.md Mode G)
  python script-system/ideas.py add <file.json>   # validate + de-duplicate + insert the new ideas at the TOP of the sheet
  python script-system/ideas.py finish "<text>"   # reset the FIND control (H1); the text becomes its hover note
  python script-system/ideas.py use               # handle USE / SKIP / USED clicks now (the watcher does it every minute)
  python script-system/ideas.py list [category]

Local copy: ideas-db.json (append-only: every idea ever suggested, so nothing is suggested twice, even after a row is
deleted in the sheet). Sheet columns: Date | Category | Title (English) | Telugu hook | Key points | Sources | News date | USE
(H1 = the FIND TOPICS control). USE cell: pick ▶ USE -> the idea becomes a row in "Script Requests" and the cell shows ✅ USED;
✖ SKIP = never show this idea again; ✅ USED picked by hand = mark only.
"""
import argparse
import datetime
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import learning_db as L  # noqa: E402

IDEAS_TAB, SET_TAB = "Topic Ideas", "Topic Settings"
DB_PATH = HERE / "ideas-db.json"
IDEA_HEADERS = ["Date", "Category", "Title (English)", "Telugu hook", "Key points", "Sources", "News date"]  # H = USE
SET_HEADERS = ["Category", "ON/OFF", "How many", "Focus", "RUN"]
COUNTS = ["3", "5", "7", "10"]
DEFAULT_CATS = [["AI", "ON", "5", "latest models, tools, research, India angle"], ["Space", "ON", "5", ""],
                ["Health", "ON", "5", "for Health Decode; WHO / NIH / ICMR level sources"],
                ["Technology", "ON", "5", ""], ["Science", "ON", "5", ""]]
FIND_REST, FIND_START, FIND_RUN = "▶ FIND TOPICS", "▶ START FIND", "⏳ FINDING"
FIND_STATES = [FIND_REST, FIND_START, FIND_RUN]
CAT_REST, CAT_START = "▶ RUN", "▶ START"  # Topic Settings column E: find topics for just this category
CAT_STATES = [CAT_REST, CAT_START, FIND_RUN]
USE_NEW, USE, USE_SKIP, USE_DONE = "⬜ NEW", "▶ USE", "✖ SKIP", "✅ USED"
WINDOW_DAYS = 7  # news must be this fresh

STOP = {"the", "a", "an", "of", "to", "in", "on", "for", "and", "new", "is", "are", "with", "how", "why", "what", "by", "at", "from"}


# ---------- local store + checks (pure) ----------

def load(path=DB_PATH):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"ideas": []}


def save(db, path=DB_PATH):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def words(text):
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP and len(w) > 1}


def similar(a, b):
    """Same topic = same headline or >= 60% shared meaningful words (Latin words; Telugu-only titles compare equal only)."""
    wa, wb = words(a), words(b)
    if not wa or not wb:
        return a.strip().lower() == b.strip().lower()
    return len(wa & wb) / len(wa | wb) >= 0.6


def parse_settings(rows):
    """Rows of Topic Settings A:E. While any row's RUN cell is ⏳ FINDING (a per-category run), only those rows
    count as ON, whatever ON/OFF says; otherwise ON/OFF decides."""
    out = []
    for i, r in enumerate(rows):
        r = ([str(c).strip() for c in r] + [""] * 5)[:5]
        if r[0]:
            out.append({"category": r[0], "on": r[1].upper() == "ON", "count": int(r[2]) if r[2].isdigit() else 5,
                        "focus": r[3], "run": r[4], "row": i + 2})
    if any(s["run"] == FIND_RUN for s in out):
        for s in out:
            s["on"] = s["run"] == FIND_RUN
    return out


def check(db, items, settings, known_titles, today=None):
    """-> (accepted ideas, [(title, reason)]). An idea needs: an ON category, English title + Telugu hook, >= 2 key points,
    >= 2 sources from different sites with dates (newest within WINDOW_DAYS), no duplicate of anything known."""
    today = today or datetime.date.today()
    on = {s["category"].lower(): s for s in settings if s["on"]}
    titles = [i["title"] for i in db["ideas"]] + list(known_titles)
    urls_seen = {u for i in db["ideas"] for u in i.get("urls", [])}
    taken, ok, bad = {}, [], []
    for it in items:
        title = str(it.get("title") or "").strip()
        cat = on.get(str(it.get("category") or "").strip().lower())
        srcs = [s for s in (it.get("sources") or []) if str(s.get("url", "")).startswith("http")]
        urls = [s["url"] for s in srcs]
        hosts = {urlparse(u).netloc.lower().removeprefix("www.") for u in urls}
        dates = []
        for s in srcs:
            try:
                dates.append(datetime.date.fromisoformat(str(s.get("date", ""))[:10]))
            except ValueError:
                pass
        reason = None
        if cat is None:
            reason = "category is not ON in Topic Settings"
        elif not title or not str(it.get("hook") or "").strip():
            reason = "missing English title or Telugu hook"
        elif len(it.get("points") or []) < 2:
            reason = "needs at least 2 key points"
        elif len(hosts) < 2:
            reason = "needs 2 sources from different sites"
        elif not dates or max(dates) < today - datetime.timedelta(days=WINDOW_DAYS) or max(dates) > today + datetime.timedelta(days=1):
            reason = f"news is not from the last {WINDOW_DAYS} days (or a source date is missing)"
        elif any(similar(title, t) for t in titles):
            reason = "same topic already suggested or already made"
        elif any(u in urls_seen for u in urls):
            reason = "a source was already used for another idea"
        elif taken.get(cat["category"], 0) >= cat["count"]:
            reason = f"over the limit of {cat['count']} for {cat['category']}"
        if reason:
            bad.append((title or "(no title)", reason))
            continue
        taken[cat["category"]] = taken.get(cat["category"], 0) + 1
        titles.append(title)
        urls_seen.update(urls)
        ok.append({"date": today.isoformat(), "category": cat["category"], "title": title, "hook": str(it["hook"]).strip(),
                   "points": [str(p).strip() for p in it["points"]], "sources": [{"url": s["url"], "date": str(s.get("date", ""))[:10]} for s in srcs],
                   "news_date": max(dates).isoformat(), "urls": urls, "status": "new"})
    return ok, bad


def idea_row(i):
    return [i["date"], i["category"], i["title"], i["hook"], "\n".join("• " + p for p in i["points"]),
            "\n".join(f"{s['url']} ({s['date']})" for s in i["sources"]), i["news_date"], USE_NEW]


def request_extra(i):
    """What the script writer gets as 'Extra Data' when an idea is used."""
    return "\n".join([f"Telugu hook idea: {i['hook']}", "Key points:", *("- " + p for p in i["points"]), "Sources:",
                      *(f"- {s['url']} ({s['date']})" for s in i["sources"])])


def process_use(sheet, db, ctl, say=print):
    """USE / SKIP / USED clicks in column H. USE -> row in Script Requests + ✅ USED. Returns True if the local db changed."""
    by_title = {i["title"]: i for i in db["ideas"]}
    changed = False
    for row, title, h in ctl["rows"]:
        if not title or not h:
            continue
        idea = by_title.get(title)
        if h == USE:
            if idea is None:  # a row the local copy does not know: build it from the sheet cells
                cur = sheet.get_idea_row(row)
                cell = lambda k: cur[k] if len(cur) > k else ""
                idea = {"hook": cell(3), "points": [p.lstrip("• ").strip() for p in cell(4).split("\n") if p.strip()],
                        "sources": [{"url": u.split(" (")[0], "date": ""} for u in cell(5).split("\n") if u.strip()], "status": "new"}
            req_row = sheet.add_request(title, request_extra(idea))
            sheet.mark(row, USE_DONE)
            idea["status"] = "used"
            changed = True
            say(f"idea '{title[:50]}' -> Script Requests row {req_row}")
        elif idea and h in (USE_SKIP, USE_DONE):
            want = "skip" if h == USE_SKIP else "used"
            if idea["status"] != want:
                idea["status"] = want
                changed = True
    return changed


# ---------- sheet ----------

class IdeasSheet(L.GoogleSheet):
    def has_tab(self, tab):
        return self._sheet_id(tab) is not None

    def _note(self, tab, row, col, text):
        self.run(self.api.batchUpdate(spreadsheetId=L.SHEET_ID, body={"requests": [{"updateCells": {
            "range": {"sheetId": self._sheet_id(tab), "startRowIndex": row - 1, "endRowIndex": row,
                      "startColumnIndex": col, "endColumnIndex": col + 1},
            "rows": [{"values": [{"note": text}]}], "fields": "note"}}]}))

    def ensure_ideas(self):
        self.ensure(IDEAS_TAB, IDEA_HEADERS, row=1)
        sid = self._sheet_id(IDEAS_TAB)
        h1 = (self.run(self.api.values().get(spreadsheetId=L.SHEET_ID, range=f"'{IDEAS_TAB}'!H1")).get("values") or [[""]])[0][0]
        if h1 not in FIND_STATES:
            self._put([{"range": f"'{IDEAS_TAB}'!H1", "values": [[FIND_REST]]}])
        meta = self.run(self.api.get(spreadsheetId=L.SHEET_ID, fields="sheets(properties.sheetId,conditionalFormats)"))
        n_rules = len(next(s for s in meta["sheets"] if s["properties"]["sheetId"] == sid).get("conditionalFormats", []))
        rng = lambda r0, r1, c0, c1: {"sheetId": sid, "startRowIndex": r0, "endRowIndex": r1,
                                      "startColumnIndex": c0, "endColumnIndex": c1}
        dv = lambda r, vals: {"setDataValidation": {"range": r, "rule": {"condition": {
            "type": "ONE_OF_LIST", "values": [{"userEnteredValue": v} for v in vals]}, "showCustomUi": True, "strict": True}}}
        GREEN, ORANGE, AMBER, GREY, BLUE = (0.72, 0.88, 0.80), (1.0, 0.85, 0.55), (1.0, 0.95, 0.62), (0.88, 0.88, 0.88), (0.85, 0.91, 0.98)
        colour = lambda text, rgb: {"addConditionalFormatRule": {"index": 0, "rule": {"ranges": [rng(0, 1000, 7, 8)], "booleanRule": {
            "condition": {"type": "TEXT_STARTS_WITH", "values": [{"userEnteredValue": text}]},
            "format": {"backgroundColor": {"red": rgb[0], "green": rgb[1], "blue": rgb[2]}}}}}}
        width = lambda c, px: {"updateDimensionProperties": {"range": {"sheetId": sid, "dimension": "COLUMNS", "startIndex": c, "endIndex": c + 1},
                                                             "properties": {"pixelSize": px}, "fields": "pixelSize"}}
        self.run(self.api.batchUpdate(spreadsheetId=L.SHEET_ID, body={"requests": [
            *[{"deleteConditionalFormatRule": {"sheetId": sid, "index": 0}} for _ in range(n_rules)],  # ours only
            colour("▶ FIND", GREEN), colour("▶ START", AMBER), colour("▶ USE", AMBER), colour("⏳", ORANGE),
            colour("✅", GREEN), colour("✖", GREY), colour("⬜", BLUE),
            dv(rng(0, 1, 7, 8), FIND_STATES), dv(rng(1, 1000, 7, 8), [USE_NEW, USE, USE_SKIP, USE_DONE]),
            {"repeatCell": {"range": rng(1, 1000, 2, 6), "cell": {"userEnteredFormat": {"wrapStrategy": "WRAP", "verticalAlignment": "TOP"}},
                            "fields": "userEnteredFormat(wrapStrategy,verticalAlignment)"}},
            {"repeatCell": {"range": rng(0, 1000, 7, 8), "cell": {"userEnteredFormat": {"textFormat": {"bold": True}, "horizontalAlignment": "CENTER"}},
                            "fields": "userEnteredFormat(textFormat,horizontalAlignment)"}},
            {"repeatCell": {"range": rng(0, 1, 0, 7), "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
                            "fields": "userEnteredFormat.textFormat.bold"}},
            {"updateSheetProperties": {"properties": {"sheetId": sid, "gridProperties": {"frozenRowCount": 1}}, "fields": "gridProperties.frozenRowCount"}},
            {"setBasicFilter": {"filter": {"range": rng(0, 1000, 0, 8)}}},  # filter by Category / Date / USE
            *[width(c, px) for c, px in enumerate((95, 90, 330, 330, 420, 360, 95, 130))]]}))

    def ensure_settings(self):
        self.ensure(SET_TAB, SET_HEADERS, row=1)
        sid = self._sheet_id(SET_TAB)
        if not self.run(self.api.values().get(spreadsheetId=L.SHEET_ID, range=f"'{SET_TAB}'!A2:D50")).get("values"):
            self.run(self.api.values().update(spreadsheetId=L.SHEET_ID, range=f"'{SET_TAB}'!A2:D{1 + len(DEFAULT_CATS)}",
                                              valueInputOption="RAW", body={"values": DEFAULT_CATS}))
        rng = lambda c0, c1: {"sheetId": sid, "startRowIndex": 1, "endRowIndex": 50, "startColumnIndex": c0, "endColumnIndex": c1}
        dv = lambda r, vals: {"setDataValidation": {"range": r, "rule": {"condition": {
            "type": "ONE_OF_LIST", "values": [{"userEnteredValue": v} for v in vals]}, "showCustomUi": True, "strict": True}}}
        self.run(self.api.batchUpdate(spreadsheetId=L.SHEET_ID, body={"requests": [
            dv(rng(1, 2), ["ON", "OFF"]), dv(rng(2, 3), COUNTS), dv(rng(4, 5), CAT_STATES),
            {"repeatCell": {"range": {"sheetId": sid, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": 5},
                            "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}}, "fields": "userEnteredFormat.textFormat.bold"}},
            {"repeatCell": {"range": rng(4, 5), "cell": {"userEnteredFormat": {"textFormat": {"bold": True}, "horizontalAlignment": "CENTER"}},
                            "fields": "userEnteredFormat(textFormat,horizontalAlignment)"}},
            {"updateSheetProperties": {"properties": {"sheetId": sid, "gridProperties": {"frozenRowCount": 1}}, "fields": "gridProperties.frozenRowCount"}},
            *[{"updateDimensionProperties": {"range": {"sheetId": sid, "dimension": "COLUMNS", "startIndex": c, "endIndex": c + 1},
                                              "properties": {"pixelSize": px}, "fields": "pixelSize"}} for c, px in enumerate((130, 80, 100, 520, 120))]]}))
        self.set_cat_run({s["row"]: CAT_REST for s in self.settings() if s["run"] not in CAT_STATES})

    def settings(self):
        return parse_settings(self.run(self.api.values().get(spreadsheetId=L.SHEET_ID, range=f"'{SET_TAB}'!A2:E50")).get("values", []))

    def set_cat_run(self, states):
        """{settings row: RUN cell text}"""
        if states:
            self._put([{"range": f"'{SET_TAB}'!E{r}", "values": [[t]]} for r, t in states.items()])

    def idea_controls(self):
        res = self.run(self.api.values().batchGet(spreadsheetId=L.SHEET_ID, ranges=[f"'{IDEAS_TAB}'!C1:C1000", f"'{IDEAS_TAB}'!H1:H1000"]))
        c, h = [vr.get("values", []) for vr in res["valueRanges"]]
        cell = lambda col, i: (col[i][0].strip() if i < len(col) and col[i] else "")
        return {"h1": cell(h, 0), "rows": [(i + 1, cell(c, i), cell(h, i)) for i in range(1, max(len(c), len(h)))]}

    def get_idea_row(self, row):
        return (self.run(self.api.values().get(spreadsheetId=L.SHEET_ID, range=f"'{IDEAS_TAB}'!A{row}:H{row}")).get("values") or [[]])[0]

    def mark(self, row, text):
        self._put([{"range": f"'{IDEAS_TAB}'!H{row}", "values": [[text]]}])

    def fill_new(self, rows):
        """Idea rows with an empty USE cell get the visible resting state ⬜ NEW."""
        if rows:
            self._put([{"range": f"'{IDEAS_TAB}'!H{r}", "values": [[USE_NEW]]} for r in rows])

    def set_find(self, text, note=None):
        self._put([{"range": f"'{IDEAS_TAB}'!H1", "values": [[text]]}])
        if note is not None:
            self._note(IDEAS_TAB, 1, 7, note)

    def insert_ideas(self, ideas):
        """Newest on top; older ideas stay below (use the filter on Category / Date)."""
        n = len(ideas)
        self.run(self.api.batchUpdate(spreadsheetId=L.SHEET_ID, body={"requests": [{"insertDimension": {"range": {
            "sheetId": self._sheet_id(IDEAS_TAB), "dimension": "ROWS", "startIndex": 1, "endIndex": 1 + n}, "inheritFromBefore": False}}]}))
        res = self.run(self.api.values().update(spreadsheetId=L.SHEET_ID, range=f"'{IDEAS_TAB}'!A2:H{1 + n}", valueInputOption="RAW",
                                                body={"values": [idea_row(i) for i in ideas]}))
        if res.get("updatedRows") != n:
            raise RuntimeError("API did not confirm the new ideas")
        self.ensure_ideas()

    def add_request(self, topic, extra, minutes="Up to 1 min"):
        """Put the idea into the first empty row of Script Requests (ON). Same topic already there -> that row."""
        col = self.run(self.api.values().get(spreadsheetId=L.SHEET_ID, range=f"'{L.REQ_TAB}'!B2:B1000")).get("values", [])
        topics = [r[0].strip() if r else "" for r in col]
        if topic in topics:
            return topics.index(topic) + 2
        row = next((i + 2 for i, t in enumerate(topics) if not t), len(topics) + 2)
        self.run(self.api.values().update(spreadsheetId=L.SHEET_ID, range=f"'{L.REQ_TAB}'!B{row}:E{row}", valueInputOption="RAW",
                                          body={"values": [[topic, extra, minutes, "ON"]]}))
        return row

    def made_titles(self):
        """Everything already made or requested: Learning DB titles, history.json topics, Script Requests topics."""
        out = [r["title"] for r in L.load()["records"].values()]
        hist = HERE / "history.json"
        if hist.exists():
            out += [h.get("topic", "") for h in json.loads(hist.read_text(encoding="utf-8"))]
        col = self.run(self.api.values().get(spreadsheetId=L.SHEET_ID, range=f"'{L.REQ_TAB}'!B2:B1000")).get("values", [])
        return [t for t in out + [r[0] for r in col if r] if t]


# ---------- CLI ----------

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for n in ("setup", "context", "use"):
        sub.add_parser(n)
    sub.add_parser("add").add_argument("file")
    sub.add_parser("finish").add_argument("text")
    sub.add_parser("list").add_argument("category", nargs="?")
    args = p.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    db = load()

    if args.cmd == "list":
        for i in db["ideas"]:
            if not args.category or i["category"].lower() == args.category.lower():
                print(f"{i['date']} | {i['category']} | {i['status']:5} | {i['title']}")
        return
    s = IdeasSheet()
    if args.cmd == "setup" or not (s.has_tab(IDEAS_TAB) and s.has_tab(SET_TAB)):
        s.ensure_settings()
        s.ensure_ideas()
        print("Tabs ready: 'Topic Ideas', 'Topic Settings'.")
        if args.cmd == "setup":
            return
    if args.cmd == "context":
        today = datetime.date.today()
        print(f"TODAY: {today.isoformat()} | news must be from {(today - datetime.timedelta(days=WINDOW_DAYS)).isoformat()} or later")
        for c in s.settings():
            if c["on"]:
                print(f"CATEGORY: {c['category']} | topics wanted: {c['count']} | focus: {c['focus'] or '(none)'}")
        print("DO NOT REPEAT (ideas already suggested, including skipped ones):")
        for i in db["ideas"]:
            print(f"- [{i['category']}] {i['title']}")
        print("DO NOT REPEAT (scripts already made or requested):")
        for t in dict.fromkeys(s.made_titles()):
            print(f"- {t}")
        return
    if args.cmd == "add":
        items = json.loads(Path(args.file).read_text(encoding="utf-8"))
        ok, bad = check(db, items, s.settings(), s.made_titles())
        if ok:
            db["ideas"] += ok
            save(db)
            s.insert_ideas(ok)
        for i in ok:
            print(f"ADDED [{i['category']}] {i['title']}")
        for t, why in bad:
            print(f"REJECTED {t[:70]} -> {why}")
        print(f"{len(ok)} added, {len(bad)} rejected")
        return
    if args.cmd == "finish":
        s.set_find(FIND_REST, f"{datetime.datetime.now():%Y-%m-%d %H:%M} - {args.text}")
        print("Finder finished; FIND control reset.")
        return
    if args.cmd == "use":
        if process_use(s, db, s.idea_controls()):
            save(db)
        print("USE clicks handled.")


if __name__ == "__main__":
    main()
