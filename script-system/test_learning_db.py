"""Self-check for learning_db.py with an in-memory fake sheet. Run: python script-system/test_learning_db.py"""
import learning_db as L


class FakeSheet:
    def __init__(self, rows=None):
        self.rows = rows if rows is not None else []

    def ensure_tab(self):
        if not self.rows:
            self.rows.append(L.HEADERS)

    def first_cols(self):
        return [r[:3] for r in self.rows]

    def write_row(self, row, values):
        self.rows[row - 1] = values
        return row

    def append_row(self, values):
        self.rows.append(values)
        return len(self.rows)


def down():
    raise RuntimeError("network down")


def test():
    db = {"records": {}}
    long_script = "TITLE of the long script\n\n" + "తెలుగు narration line. " * 1500  # ~34k chars, a 30-min script
    rid, rec, new = L.add_original(db, None, long_script)
    assert rid == "S001" and new and rec["original"] == long_script.strip("\n")
    assert rec["title"] == "TITLE of the long script"

    # next script gets the next ID; same original again = same record (idempotent); bad / reused ids refused
    assert L.add_original(db, None, "Second title\nbody")[0] == "S002"
    assert L.add_original(db, None, long_script)[0::2] == ("S001", False)
    for bad_id, text in (("x1", "other"), ("S001", "different"), ("S002", long_script)):
        try:
            L.add_original(db, bad_id, text); assert False, bad_id
        except ValueError:
            pass
    assert L.new_id(db) == "S003"

    # API failure -> stays local + pending
    msg = L.sync_pending(db, sheet_factory=down)
    assert msg.startswith("PENDING") and not rec["synced"]

    # recovery -> both synced, one row each, no duplicate rows on re-sync, full text, 7 columns
    sheet = FakeSheet()
    out = L.sync_pending(db, sheet_factory=lambda: sheet)
    assert "S001 -> row 2" in out and "S002 -> row 3" in out
    assert len(sheet.rows) == 3 and sheet.rows[1][:3] == ["S001", rec["title"], rec["original"]]

    # revisions preserved (newest first), title follows the latest revision, same row updated
    assert L.append_entry(rec, "revisions", "New title\nrev one")
    assert L.append_entry(rec, "revisions", "Newer title\nrev two")
    assert not L.append_entry(rec, "revisions", "Newer title\nrev two")  # duplicate skipped
    assert rec["title"] == "Newer title" and rec["original"].startswith("TITLE of the long script")
    L.append_entry(rec, "feedback", "my reason")
    L.append_entry(rec, "changes", "- a\n+ b", revision=2)
    rec["rules"].append({"date": "2026-11-13", "scope": "general", "text": "R1", "status": "proposed"})
    rec["rules"].append({"date": "2026-11-13", "scope": "topic", "text": "R2", "status": "approved"})
    L.sync_pending(db, sheet_factory=lambda: sheet)
    row = sheet.rows[1]
    assert len(sheet.rows) == 3 and len(row) == 7 and row[0] == "S001" and row[1] == "Newer title"
    assert "rev one" in row[3] and "rev two" in row[3] and row[3].index("rev two") < row[3].index("rev one")
    assert "my reason" in row[5] and "⏳ PROPOSED" in row[6] and "✅ APPROVED" in row[6]

    # only approved rules are retrieved
    assert L.approved_rules(db) == ["[TOPIC] R2  (from S001)"]

    # over-limit original is refused, never truncated
    try:
        L.row_values("S001", {**rec, "original": "x" * 50001}); assert False
    except ValueError:
        pass

    # sentence diff
    d = L.sentence_diff("ధర తగ్గింది. బాగుంది.", "Price తగ్గింది. బాగుంది.")
    assert "- ధర తగ్గింది." in d and "+ Price తగ్గింది." in d and "బాగుంది" not in d

    # local store round-trip keeps Telugu intact
    import tempfile, pathlib
    p = pathlib.Path(tempfile.mkdtemp()) / "db.json"
    db["schema"] = L.SCHEMA  # what save() persists after the first load
    L.save(db, p)
    assert L.load(p) == db

    # upgrade of the old format: slug id -> S001 (slug kept as alias), title filled, flagged for re-sync
    old = {"records": {"2026-11-13-old-slug": {"created": "2026-11-13", "original": "Old title\nbody", "revisions": [],
                                              "changes": [], "feedback": [], "rules": [], "synced": True}}}
    L.normalize(old)
    assert list(old["records"]) == ["S001"] and old["records"]["S001"]["slug"] == "2026-11-13-old-slug"
    assert old["records"]["S001"]["title"] == "Old title" and old["records"]["S001"]["synced"] is False
    assert L.resolve(old, "2026-11-13-old-slug") == "S001" and L.resolve(old, "s001") == "S001"
    assert L.new_id(old) == "S002"

    # a row written before IDs existed (original text in column A of the old 5-column layout) is updated in place
    legacy = FakeSheet([["Original Script", "Revised", "Changes", "Feedback", "Rules"],
                        ["Old title\nbody", "rev", "chg", "fb", "rules"]])
    L.sync_pending(old, sheet_factory=lambda: legacy)
    assert len(legacy.rows) == 2 and legacy.rows[1][0] == "S001" and legacy.rows[1][2] == "Old title\nbody"

    # request rows (A2:G): manual mode = topic + ON + not done; blank toggle = OFF; failed/running are retried
    reqs, sk = L.parse_requests([
        ["", "కిడ్నీ ఎలా పనిచేస్తుంది", "", "1.30", "ON", "", "▶ RUN"],
        ["", "x" * 301, "notes", "5", "on", "❌ Failed: net", "▶ RUN"],
        ["S009", "old topic", "", "2", "ON", "✅", "▶ RUN"],
        ["", "off topic", "", "2", "OFF", "", "▶ RUN"],
        [], ["", "", "extra only"],
        ["", "forgot toggle", "", "5", "", ""],
        ["", "stale", "", "5", "ON", "⏳ RUNNING"],
        ["S003", "legacy", "", "2", "ON", "Done (old style)"]])
    assert [r["row"] for r in reqs] == [2, 3, 9] and sk == {"off": 2, "done": 2}
    assert reqs[0]["kind"] == "TOPIC" and reqs[0]["minutes"] == "1.30"
    assert reqs[1]["kind"].startswith("SCRIPT") and reqs[1]["extra"] == "notes"
    assert L.parse_requests([["", "t", "", "", "ON", ""]])[0][0]["minutes"] == "1"  # default 1 min
    # claimed mode (RUN cell = running): exactly the claimed rows, even OFF or already-done ones
    reqs, sk = L.parse_requests([["", "a", "", "1", "ON", "", "▶ RUN"], ["S1", "b", "", "5", "OFF", "✅", "⏳ RUNNING"],
                                 ["", "c", "", "2", "ON", "", "⏳ RUNNING"]])
    assert [r["row"] for r in reqs] == [3, 4]

    # what the watcher reads from the whole grid (row 1 = headers, G1 = RUN ALL control)
    grid = [["Script ID", "Topic / Script", "Extra", "Minutes", "ON/OFF", "Status", "▶ START ALL"],
            ["", "t1", "", "1", "ON", "", ""],               # row 2: ON, RUN cell blank -> fill
            ["", "t2", "", "1", "OFF", "", "▶ START"],       # row 3: clicked START
            ["", "", "", "", "", "", "▶ RUN"],               # row 4: empty row with a stale button -> clear
            ["S2", "t3", "", "1", "ON", "✅", "▶ RUN"],      # row 5: done
            ["", "t4", "", "1", "ON", "⏳ RUNNING", "⏳ RUNNING"]]  # row 6: claimed
    sc = L.scan(grid)
    assert sc["run_all"] and sc["starts"] == [3] and sc["claimed"] == [6] and sc["fill"] == [2] and sc["clear"] == [4]
    assert sc["on_rows"] == [2, 6]
    grid[0][6] = "▶ RUN ALL"
    assert not L.scan(grid)["run_all"]

    # Minutes dropdown values -> length instructions (every dropdown option must parse)
    for o in L.MINUTE_OPTIONS:
        L.describe_minutes(o)
    assert "at most ~750 words" in L.describe_minutes("Up to 5 min") and "at most ~750" in L.describe_minutes("5")
    assert "at most ~225 words" in L.describe_minutes("1.30")  # 1.30 = 1 min 30 s
    assert "1500-2250 words" in L.describe_minutes("10-15 min")
    assert "at least ~1500 words" in L.describe_minutes("10+ min") and "~2250" in L.describe_minutes("10+ min")
    assert "EXACTLY" in L.describe_minutes("Exact 10 min") and "~1500 words" in L.describe_minutes("Exact 10 min")
    assert "at most ~150 words" in L.describe_minutes("")  # blank -> 1 min max
    try:
        L.describe_minutes("soon"); assert False
    except ValueError:
        pass

    # watcher: acts only on RUN ALL / row START, claims exactly the chosen rows, always reports back (G1 note)
    import watcher as W

    class FS:
        def __init__(s, grid):
            s.g, s.log = grid, []

        def grid(s): return s.g
        def fill_run_cells(s, fill, clear=()): s.log.append(("fill", list(fill), list(clear)))
        def claim(s, rows): s.log.append(("claim", list(rows)))
        def release(s, rows): s.log.append(("release", list(rows)))
        def set_all_cell(s, text, note=None): s.log.append(("all", text, note))

    H = lambda g1: ["Script ID", "Topic / Script", "Extra", "Minutes", "ON/OFF", "Status", g1]
    calls = []
    ok = lambda: (calls.append(1) or True, "")
    s = FS([H("▶ RUN ALL"), ["", "t1", "", "1", "ON", "", ""]])
    assert W.tick(s, ok, print) == "idle" and not calls and ("fill", [2], []) in s.log  # tidy only
    s = FS([H("▶ START ALL"), ["", "t1", "", "1", "ON", "", "▶ RUN"], ["", "t2", "", "1", "OFF", "", "▶ RUN"]])
    assert W.tick(s, ok, print) == "done" and len(calls) == 1 and ("claim", [2]) in s.log  # RUN ALL = ON rows only
    assert s.log[-1][:2] == ("all", L.ALL_REST) and "finished" in s.log[-1][2]
    s = FS([H("▶ RUN ALL"), ["", "t1", "", "1", "ON", "", "▶ RUN"], ["", "t2", "", "1", "OFF", "", "▶ START"]])
    assert W.tick(s, ok, print) == "done" and ("claim", [3]) in s.log  # one row clicked, OFF is ignored
    s = FS([H("▶ START ALL"), ["", "t2", "", "1", "OFF", "", "▶ RUN"]])
    n = len(calls)
    assert W.tick(s, ok, print) == "empty" and len(calls) == n and "no ON rows" in s.log[-1][2]
    s = FS([H("▶ START ALL"), ["", "t1", "", "1", "ON", "", "▶ RUN"]])
    assert W.tick(s, lambda: (True, "3 steps, ~$1.23"), print) == "done" and "3 steps, ~$1.23" in s.log[-1][2]
    s = FS([H("▶ START ALL"), ["", "t1", "", "1", "ON", "⏳ RUNNING", "⏳ RUNNING"]])
    assert W.tick(s, lambda: (False, "timed out"), print) == "failed" and "timed out" in s.log[-1][2]
    assert ("release", [2]) in s.log and s.log[-1][:2] == ("all", L.ALL_REST)  # stopped run frees its rows
    txt, st = W.summarize('{"result": "hi", "num_turns": 3, "duration_ms": 125000, "total_cost_usd": 1.234, '
                          '"usage": {"input_tokens": 10, "cache_read_input_tokens": 200000, '
                          '"cache_creation_input_tokens": 30000, "output_tokens": 15000}, "modelUsage": {"claude-opus-5-5": {}}}')
    assert txt == "hi" and st["cost"] == 1.23 and st["output"] == 15000
    assert W.stats_line(st) == "3 steps, 2m05s, claude-opus-5-5: new in 30k + cached 200k, out 15k, ~$1.23 list price"
    assert W.summarize("not json")[1] == {}
    print("all checks passed")


if __name__ == "__main__":
    test()
