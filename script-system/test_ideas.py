"""Self-check for ideas.py and the watcher's Topic Ideas tick. Run: python script-system/test_ideas.py"""
import datetime

import ideas as I
import watcher as W

TODAY = datetime.date(2026, 11, 14)
SET = I.parse_settings([["AI", "ON", "2", "x"], ["Space", "OFF", "5"], ["Health", "on", "x"]])
_n = [0]


def item(title="OpenAI ships GPT-9", cat="AI", **kw):
    _n[0] += 1
    d = {"category": cat, "title": title, "hook": "తెలుగు hook", "points": ["a 1", "b 2"],
         "sources": [{"url": f"https://a.com/{_n[0]}", "date": "2026-11-12"}, {"url": f"https://www.b.org/{_n[0]}", "date": "2026-11-13"}]}
    d.update(kw)
    return d


class FakeIdeas:
    def __init__(self, h1="▶ FIND TOPICS", rows=(), settings=SET):
        self.marks, self.reqs, self.log, self.h1, self.rows, self.st = [], [], [], h1, list(rows), settings

    def has_tab(self, t): return True
    def idea_controls(self): return {"h1": self.h1, "rows": self.rows}
    def settings(self): return self.st
    def add_request(self, topic, extra): self.reqs.append((topic, extra)); return 2
    def mark(self, row, text): self.marks.append((row, text))
    def set_find(self, text, note=None): self.log.append((text, note))

    def get_idea_row(self, row):
        return ["d", "AI", "Typed by hand", "hook", "• p1\n• p2", "https://z.com (2026-11-10)", "2026-11-10", "▶ USE"]


def test():
    assert [(s["category"], s["on"], s["count"]) for s in SET] == [("AI", True, 2), ("Space", False, 5), ("Health", True, 5)]
    assert I.similar("OpenAI ships GPT-9 model", "OpenAI ships the GPT-9") and not I.similar("Mars rover finds water", "OpenAI ships GPT-9")

    # a good idea is accepted and stored with its freshest source date
    db = {"ideas": []}
    ok, bad = I.check(db, [item()], SET, [], TODAY)
    assert len(ok) == 1 and not bad and ok[0]["news_date"] == "2026-11-13" and ok[0]["status"] == "new" and ok[0]["date"] == "2026-11-14"
    db["ideas"] += ok

    def why(it, known=()):
        o, b = I.check(db, [it], SET, known, TODAY)
        return b[0][1] if b else "ACCEPTED"

    assert "not ON" in why(item("Mars thing", cat="Space")) and "not ON" in why(item("Cooking thing", cat="Cooking"))
    assert "2 sources" in why(item("Single source topic", sources=[{"url": "https://a.com/solo", "date": "2026-11-13"}]))
    assert "different sites" in why(item("Same site topic", sources=[{"url": "https://a.com/1", "date": "2026-11-13"}, {"url": "https://a.com/2", "date": "2026-11-13"}]))
    old = [{"url": "https://a.com/o1", "date": "2026-10-01"}, {"url": "https://b.org/o2", "date": "2026-10-02"}]
    assert "last 7 days" in why(item("Old news topic", sources=old))
    assert "last 7 days" in why(item("Undated topic", sources=[{"url": "https://a.com/u1"}, {"url": "https://b.org/u2"}]))
    assert "already suggested" in why(item("OpenAI ships GPT-9"))                                       # same as an earlier idea
    assert "already suggested" in why(item("Brand new quantum chip"), known=["Brand new quantum chip"])  # same as a script already made
    assert "source was already used" in why(item("Totally different robot story", sources=[{"url": db["ideas"][0]["urls"][0], "date": "2026-11-13"}, {"url": "https://c.net/z", "date": "2026-11-13"}]))
    assert "2 key points" in why(item("One point topic", points=["only"])) and "hook" in why(item("No hook topic", hook=""))
    o3, b3 = I.check({"ideas": []}, [item("Alpha chip one"), item("Beta robot two"), item("Gamma lab three")], SET, [], TODAY)
    assert [i["title"] for i in o3] == ["Alpha chip one", "Beta robot two"] and "over the limit of 2" in b3[0][1]  # count per category

    row = I.idea_row(ok[0])
    assert row[2] == "OpenAI ships GPT-9" and row[4].startswith("• a 1") and row[7] == "" and "Key points" in I.request_extra(ok[0])

    # USE -> Script Requests row + tick; SKIP / hand-marked USED only change the local status; unknown titles are built from the sheet row
    db2 = {"ideas": [dict(ok[0]), {**ok[0], "title": "Other one", "status": "new"}]}
    fs = FakeIdeas()
    ctl = {"h1": "▶ FIND TOPICS", "rows": [(2, "OpenAI ships GPT-9", "▶ USE"), (3, "Other one", "✖ SKIP"), (4, "Typed by hand", "▶ USE"), (5, "", "▶ USE")]}
    assert I.process_use(fs, db2, ctl, lambda m: None)
    assert [r[0] for r in fs.reqs] == ["OpenAI ships GPT-9", "Typed by hand"] and fs.marks == [(2, I.USE_DONE), (4, I.USE_DONE)]
    assert db2["ideas"][0]["status"] == "used" and db2["ideas"][1]["status"] == "skip"
    assert not I.process_use(fs, db2, {"h1": "", "rows": [(2, "OpenAI ships GPT-9", "✅ USED")]}, print)  # nothing new

    # watcher tick: clicks handled without claude; START FIND runs one finder pass; failures are reported
    calls, saved = [], []
    okr = lambda: (calls.append(1) or True, "")
    st = lambda: {"ideas": []}
    sv = lambda d: saved.append(1)
    assert W.tick_ideas(FakeIdeas(), okr, print, st, sv) == "idle" and not calls
    fi = FakeIdeas("▶ START FIND")
    assert W.tick_ideas(fi, okr, print, st, sv) == "done" and len(calls) == 1 and fi.log[0][0] == I.FIND_RUN and fi.log[-1][0] == I.FIND_REST
    fi = FakeIdeas("▶ START FIND", settings=[{"category": "AI", "on": False, "count": 5, "focus": ""}])
    assert W.tick_ideas(fi, okr, print, st, sv) == "empty" and len(calls) == 1 and "no category" in fi.log[-1][1]
    fi = FakeIdeas("▶ START FIND")
    assert W.tick_ideas(fi, lambda: (False, "timed out"), print, st, sv) == "failed" and "timed out" in fi.log[-1][1]
    fi = FakeIdeas(rows=[(2, "OpenAI ships GPT-9", "▶ USE")])
    assert W.tick_ideas(fi, okr, print, lambda: {"ideas": [dict(ok[0])]}, sv) == "idle" and fi.marks == [(2, I.USE_DONE)] and saved
    print("ideas checks passed")


if __name__ == "__main__":
    test()
