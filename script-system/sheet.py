"""Google Sheet connector for the channel tabs (one spreadsheet, one tab per channel).

health  (tab "Health-Decode") and dark (tab "Dark-World"), same columns:
          A ID | B Topic | C Extra | D LONG | E SHORT | F RUN
          | G LONG-UPDATED (user) | H SHORT-UPDATED (user) | I TEMPLATES CHECK | J CHECK
zumba   (tab "Zumba-Fitness"): A ID | B Topic | C Extra | D SHORT | E RUN
                               | F SHORT-UPDATED (user) | G TEMPLATES CHECK | H CHECK      (short only, no long video)

The script only writes the AI columns (long/short), RUN, TEMPLATES CHECK and CHECK.
User columns (*-UPDATED) are never written. Status values: START / RUNNING / DONE / ERROR.

Usage:  python sheet.py <health|dark|zumba> <command> ...
  pending                                 rows with RUN=START or CHECK=START (JSON)
  status <row> run|check RUNNING|DONE|ERROR
  write <row> <short.txt>                 zumba: short, RUN=DONE
  write <row> <long.txt> <short.txt>      health: long + short, RUN=DONE
  texts                                   final text per row (user edit if present, else AI) as JSON
  overlap <row>                           shared 4-word phrases with other rows
  check-result <row> <result.txt>         TEMPLATES CHECK=result, CHECK=DONE
python sheet.py selftest
"""
import json, re, sys
from pathlib import Path

SID = "141B4qwm4Un9dXPzULWClZaUrjhcugjhoczSGrjik040"
KEY = Path(__file__).parent / "credentials" / "service-account.json"
CHANNELS = {
    "health": {"tab": "Health-Decode", "last": "J", "long": "D", "short": "E", "run": "F",
               "long_user": "G", "short_user": "H", "result": "I", "check": "J"},
    "dark": {"tab": "Dark-World", "last": "J", "long": "D", "short": "E", "run": "F",
             "long_user": "G", "short_user": "H", "result": "I", "check": "J"},
    "zumba": {"tab": "Zumba-Fitness", "last": "H", "long": None, "short": "D", "run": "E",
              "long_user": None, "short_user": "F", "result": "G", "check": "H"},
}
STATES = {"START", "RUNNING", "DONE", "ERROR"}


def writable(ch):
    c = CHANNELS[ch]
    return {c[k] for k in ("long", "short", "run", "result", "check") if c[k]}


def api():
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    c = Credentials.from_service_account_file(str(KEY), scopes=["https://www.googleapis.com/auth/spreadsheets"])
    return build("sheets", "v4", credentials=c, cache_discovery=False).spreadsheets()


def rows(ch):
    c = CHANNELS[ch]
    cols = [chr(x) for x in range(ord("A"), ord(c["last"]) + 1)]
    vals = api().values().get(spreadsheetId=SID, range=f"{c['tab']}!A2:{c['last']}").execute().get("values", [])
    out = []
    for i, v in enumerate(vals, start=2):
        v = (v + [""] * len(cols))[:len(cols)]
        if any(x.strip() for x in v):
            out.append({"row": i, **dict(zip(cols, v))})
    return out


def get(r, col):
    return r.get(col, "") if col else ""


def final_text(ch, r):
    """User edits win over AI text."""
    c = CHANNELS[ch]
    lu, su = get(r, c["long_user"]), get(r, c["short_user"])
    return {"long": lu or get(r, c["long"]), "short": su or get(r, c["short"]), "edited": bool(lu or su)}


def updates(ch, row, cells):
    """cells = {col: value}. Refuses any column that is not an AI/status column of this channel."""
    bad = set(cells) - writable(ch)
    if bad:
        raise ValueError(f"refusing to write user/locked columns {sorted(bad)} on {ch}")
    tab = CHANNELS[ch]["tab"]
    return [{"range": f"{tab}!{col}{row}", "values": [[v]]} for col, v in sorted(cells.items())]


def put(ch, row, cells):
    api().values().batchUpdate(spreadsheetId=SID, body={"valueInputOption": "RAW", "data": updates(ch, row, cells)}).execute()


def ngrams(text, n=4):
    w = re.findall(r"[\wఀ-౿']+", text.lower())
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


def overlap(target, others, n=4):
    mine = ngrams(target["long"] + " " + target["short"], n)
    res = {}
    for o in others:
        shared = mine & ngrams(o["long"] + " " + o["short"], n)
        if shared:
            res[o["id"]] = sorted(shared)[:25]
    return res


def has_text(ch, r):
    t = final_text(ch, r)
    return bool(t["long"] or t["short"])


def selftest():
    assert updates("health", 5, {"D": "x", "F": "DONE"})[0]["range"] == "Health-Decode!D5"
    assert updates("zumba", 5, {"D": "x", "E": "DONE"})[1]["range"] == "Zumba-Fitness!E5"
    assert updates("dark", 3, {"E": "x"})[0]["range"] == "Dark-World!E3"
    for ch, locked in (("health", "ABCGH"), ("dark", "ABCGH"), ("zumba", "ABCFIJ")):
        for col in locked:
            try:
                updates(ch, 5, {col: "x"}); raise AssertionError((ch, col))
            except ValueError:
                pass
    assert final_text("health", {"D": "ai long", "E": "ai short", "G": "user long", "H": ""}) == \
        {"long": "user long", "short": "ai short", "edited": True}
    assert final_text("zumba", {"D": "ai short", "F": "user short"}) == {"long": "", "short": "user short", "edited": True}
    a = {"id": "S1", "long": "ఈ వీడియోలో మనం అసలు సైన్స్ తెలుసుకుందాం ok", "short": ""}
    b = {"id": "S2", "long": "మరి ఈ వీడియోలో మనం అసలు సైన్స్ తెలుసుకుందాం", "short": ""}
    assert "ఈ వీడియోలో మనం అసలు" in overlap(a, [b])["S2"]
    print("selftest ok")


def main(a):
    if a[:1] == ["selftest"]:
        return selftest()
    if len(a) < 2 or a[0] not in CHANNELS:
        return print(__doc__)
    ch, cmd, c = a[0], a[1], CHANNELS[a[0]]
    if cmd == "pending":
        p = [{"row": r["row"], "id": r["A"], "topic": r["B"], "extra": r["C"],
              "run": r[c["run"]] == "START", "check": r[c["check"]] == "START"} for r in rows(ch)
             if r[c["run"]] == "START" or r[c["check"]] == "START"]
        return print(json.dumps(p, ensure_ascii=False, indent=1))
    if cmd == "status":
        row, kind, state = int(a[2]), a[3], a[4]
        assert kind in ("run", "check") and state in STATES
        return put(ch, row, {c[kind]: state})
    if cmd == "write":
        row, files = int(a[2]), [Path(f).read_text(encoding="utf-8").strip() for f in a[3:]]
        if c["long"]:
            assert len(files) == 2, "health needs <long.txt> <short.txt>"
            cells = {c["long"]: files[0], c["short"]: files[1]}
        else:
            assert len(files) == 1, "zumba is short only: <short.txt>"
            cells = {c["short"]: files[0]}
        return put(ch, row, {**cells, c["run"]: "DONE"})
    if cmd == "texts":
        return print(json.dumps([{"row": r["row"], "id": r["A"], "topic": r["B"], **final_text(ch, r)}
                                 for r in rows(ch) if has_text(ch, r)], ensure_ascii=False, indent=1))
    if cmd == "overlap":
        row, all_r = int(a[2]), rows(ch)
        me = next(r for r in all_r if r["row"] == row)
        others = [{"id": r["A"], **final_text(ch, r)} for r in all_r if r["row"] != row and has_text(ch, r)]
        return print(json.dumps(overlap({"id": me["A"], **final_text(ch, me)}, others), ensure_ascii=False, indent=1))
    if cmd == "check-result":
        row = int(a[2])
        return put(ch, row, {c["result"]: Path(a[3]).read_text(encoding="utf-8").strip(), c["check"]: "DONE"})
    print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
