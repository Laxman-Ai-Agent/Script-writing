"""Self-check for learning_db.py with an in-memory fake sheet. Run: python script-system/test_learning_db.py"""
import learning_db as L


class FakeSheet:
    def __init__(self):
        self.rows = []

    def ensure_tab(self):
        if not self.rows:
            self.rows.append(L.HEADERS)

    def column_a(self):
        return [r[0] for r in self.rows]

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
    long_script = "తెలుగు narration line. " * 1500  # ~34k chars, a 30-min script
    rec, new = L.add_original(db, "s1", long_script)
    assert new and rec["original"] == long_script.strip("\n")

    # duplicate original -> no-op; different original under same id -> refused
    assert L.add_original(db, "s1", long_script)[1] is False
    try:
        L.add_original(db, "s1", "different"); assert False
    except ValueError:
        pass

    # API failure -> stays local + pending
    msg = L.sync_pending(db, sheet_factory=down)
    assert msg.startswith("PENDING") and not rec["synced"]

    # recovery -> synced once, no duplicate rows on re-sync
    sheet = FakeSheet()
    assert "row 2" in L.sync_pending(db, sheet_factory=lambda: sheet)
    assert len(sheet.rows) == 2 and sheet.rows[1][0] == rec["original"]  # full text, not truncated

    # revisions preserved, feedback/changes appended, same row updated
    assert L.append_entry(rec, "revisions", "rev one")
    assert L.append_entry(rec, "revisions", "rev two")
    assert not L.append_entry(rec, "revisions", "rev two")  # duplicate skipped
    L.append_entry(rec, "feedback", "my reason")
    L.append_entry(rec, "changes", "- a\n+ b", revision=2)
    rec["rules"].append({"date": "2026-11-13", "scope": "general", "text": "R1", "status": "proposed"})
    rec["rules"].append({"date": "2026-11-13", "scope": "topic", "text": "R2", "status": "approved"})
    L.sync_pending(db, sheet_factory=lambda: sheet)
    row = sheet.rows[1]
    assert len(sheet.rows) == 2 and len(row) == 5
    assert "rev one" in row[1] and "rev two" in row[1] and row[1].index("rev two") < row[1].index("rev one")
    assert "my reason" in row[3] and "⏳ PROPOSED" in row[4] and "✅ APPROVED" in row[4]

    # only approved rules are retrieved
    assert L.approved_rules(db) == ["[TOPIC] R2  (from s1)"]

    # over-limit original is refused, never truncated
    try:
        L.row_values({**rec, "original": "x" * 50001}); assert False
    except ValueError:
        pass

    # sentence diff
    d = L.sentence_diff("ధర తగ్గింది. బాగుంది.", "Price తగ్గింది. బాగుంది.")
    assert "- ధర తగ్గింది." in d and "+ Price తగ్గింది." in d and "బాగుంది" not in d

    # local store round-trip keeps Telugu intact
    import tempfile, pathlib
    p = pathlib.Path(tempfile.mkdtemp()) / "db.json"
    L.save(db, p)
    assert L.load(p) == db
    # request rows (A3:F): written only if topic + ON + Status not Done; blank toggle = OFF; failed/running are retried
    reqs, sk = L.parse_requests([
        ["1", "కిడ్నీ ఎలా పనిచేస్తుంది", "", "1.30", "ON", ""],
        ["2", "x" * 301, "notes", "5", "on", "Failed: net"],
        ["3", "old topic", "", "2", "ON", "Done: s1"],
        ["4", "off topic", "", "2", "OFF", ""],
        [], ["", "", "extra only"],
        ["7", "forgot toggle", "", "5", "", ""],
        ["8", "stale", "", "5", "ON", "Running"]])
    assert [r["row"] for r in reqs] == [3, 4, 10] and sk == {"off": 2, "done": 1}
    assert reqs[0]["kind"] == "TOPIC" and reqs[0]["minutes"] == "1.30" and reqs[0]["sno"] == "1"
    assert reqs[1]["kind"].startswith("SCRIPT") and reqs[1]["extra"] == "notes"
    assert L.parse_requests([["1", "t", "", "", "ON", ""]])[0][0]["minutes"] == "1"  # default 1 min

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
    # watcher: acts only on RUN NOW, only when ON rows exist, always reports back in the sheet
    import watcher as W

    class FS:
        def __init__(s, flag, reqs):
            s.flag, s.reqs, s.msg = flag, reqs, ""

        def run_flag(s): return s.flag
        def pending_requests(s): return s.reqs, {"off": 1, "done": 2}
        def run_message(s): return s.msg

        def set_run_state(s, f, m):
            s.flag, s.msg = f, m

    calls = []
    ok = lambda: (calls.append(1) or True, "")
    s = FS("Idle", [1]); assert W.tick(s, ok, print) == "idle" and not calls
    s = FS("RUN NOW", []); assert W.tick(s, ok, print) == "empty" and not calls and s.flag == "Idle" and "no ON rows" in s.msg
    s = FS("RUN NOW", [1, 2]); assert W.tick(s, ok, print) == "done" and len(calls) == 1 and s.flag == "Idle"
    assert "finished" in s.msg  # claude never wrote run-finish -> watcher closes the message itself
    s = FS("RUN NOW", [1]); assert W.tick(s, lambda: (False, "timed out"), print) == "failed" and "timed out" in s.msg and s.flag == "Idle"
    print("all checks passed")


if __name__ == "__main__":
    test()
