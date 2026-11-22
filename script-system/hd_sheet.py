"""Health Decode <-> Google Sheet connector (tab "Health-Decode").

Columns: A Script ID | B Topic | C Extra Data | D LONG VIDEO (AI) | E SHORT VIDEO (AI)
         F RUN (START/RUNNING/DONE/ERROR) | G LONG VIDEO - UPDATED (user) | H SHORT VIDEO - UPDATED (user)
         I TEMPLATES CHECK (AI result) | J CHECK (START/RUNNING/DONE/ERROR)

This script only ever writes D, E, F, I, J. G and H (user edits) are never written.

Usage:
  python hd_sheet.py pending                     rows with F=START or J=START (JSON)
  python hd_sheet.py status <row> run|check RUNNING|DONE|ERROR
  python hd_sheet.py write <row> <long.txt> <short.txt>   D,E then F=DONE
  python hd_sheet.py texts                       every row's final text (G/H if edited, else D/E) as JSON
  python hd_sheet.py overlap <row>               shared 4-word phrases between this row and others
  python hd_sheet.py check-result <row> <result.txt>      I=result then J=DONE
  python hd_sheet.py selftest
"""
import json, re, sys
from pathlib import Path

SID = "141B4qwm4Un9dXPzULWClZaUrjhcugjhoczSGrjik040"
TAB = "Health-Decode"
KEY = Path(__file__).parent / "credentials" / "service-account.json"
COLS = "ABCDEFGHIJ"
WRITABLE = set("DEFIJ")          # G, H belong to the user
STATUS = {"run": "F", "check": "J"}
STATES = {"START", "RUNNING", "DONE", "ERROR"}


def api():
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    c = Credentials.from_service_account_file(str(KEY), scopes=["https://www.googleapis.com/auth/spreadsheets"])
    return build("sheets", "v4", credentials=c, cache_discovery=False).spreadsheets()


def rows():
    vals = api().values().get(spreadsheetId=SID, range=f"{TAB}!A2:J").execute().get("values", [])
    out = []
    for i, v in enumerate(vals, start=2):
        v = (v + [""] * 10)[:10]
        if any(x.strip() for x in v):
            out.append({"row": i, **{c: v[k] for k, c in enumerate(COLS)}})
    return out


def final_text(r):
    """User edits win: G/H if filled, else AI D/E."""
    return {"long": r["G"] or r["D"], "short": r["H"] or r["E"], "edited": bool(r["G"] or r["H"])}


def updates(row, cells):
    """cells = {col: value}. Refuses any column outside WRITABLE."""
    bad = set(cells) - WRITABLE
    if bad:
        raise ValueError(f"refusing to write user/locked columns {sorted(bad)}")
    return [{"range": f"{TAB}!{c}{row}", "values": [[v]]} for c, v in sorted(cells.items())]


def put(row, cells):
    api().values().batchUpdate(spreadsheetId=SID, body={"valueInputOption": "RAW", "data": updates(row, cells)}).execute()


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


def selftest():
    assert updates(5, {"D": "x", "F": "DONE"})[0]["range"] == "Health-Decode!D5"
    for c in "ABCGH":
        try:
            updates(5, {c: "x"}); raise AssertionError(c)
        except ValueError:
            pass
    r = {"D": "ai long", "E": "ai short", "G": "user long", "H": ""}
    assert final_text(r) == {"long": "user long", "short": "ai short", "edited": True}
    a = {"id": "S1", "long": "ఈ వీడియోలో మనం అసలు సైన్స్ తెలుసుకుందాం ok", "short": ""}
    b = {"id": "S2", "long": "మరి ఈ వీడియోలో మనం అసలు సైన్స్ తెలుసుకుందాం", "short": ""}
    assert "ఈ వీడియోలో మనం అసలు" in overlap(a, [b])["S2"]
    print("selftest ok")


def main(a):
    cmd = a[0] if a else ""
    if cmd == "selftest":
        return selftest()
    if cmd == "pending":
        p = [{"row": r["row"], "id": r["A"], "topic": r["B"], "extra": r["C"],
              "run": r["F"] == "START", "check": r["J"] == "START"} for r in rows()
             if r["F"] == "START" or r["J"] == "START"]
        return print(json.dumps(p, ensure_ascii=False, indent=1))
    if cmd == "status":
        row, kind, state = int(a[1]), a[2], a[3]
        assert kind in STATUS and state in STATES
        return put(row, {STATUS[kind]: state})
    if cmd == "write":
        row = int(a[1])
        long_t = Path(a[2]).read_text(encoding="utf-8").strip()
        short_t = Path(a[3]).read_text(encoding="utf-8").strip()
        return put(row, {"D": long_t, "E": short_t, "F": "DONE"})
    if cmd == "texts":
        return print(json.dumps([{"row": r["row"], "id": r["A"], "topic": r["B"], **final_text(r)}
                                 for r in rows() if r["D"] or r["G"]], ensure_ascii=False, indent=1))
    if cmd == "overlap":
        row = int(a[1]); all_r = rows()
        me = next(r for r in all_r if r["row"] == row)
        t = {"id": me["A"], **final_text(me)}
        others = [{"id": r["A"], **final_text(r)} for r in all_r if r["row"] != row and (r["D"] or r["G"])]
        return print(json.dumps(overlap(t, others), ensure_ascii=False, indent=1))
    if cmd == "check-result":
        row = int(a[1])
        return put(row, {"I": Path(a[2]).read_text(encoding="utf-8").strip(), "J": "DONE"})
    print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
