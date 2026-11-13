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
    print("all checks passed")


if __name__ == "__main__":
    test()
