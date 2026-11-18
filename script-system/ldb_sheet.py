"""Learning DB: Google Sheets access (GoogleSheet) and record sync."""
import argparse
import datetime
import difflib
import json
import os
import re
import sys
from pathlib import Path

from ldb_core import *  # noqa: F401,F403
from ldb_core import _mins  # noqa: F401


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

    def ensure(self, tab, headers, row=1):
        meta = self.run(self.api.get(spreadsheetId=SHEET_ID, fields="sheets.properties.title"))
        if tab not in [s["properties"]["title"] for s in meta["sheets"]]:
            self.run(self.api.batchUpdate(spreadsheetId=SHEET_ID, body={
                "requests": [{"addSheet": {"properties": {"title": tab}}}]}))
        end = chr(64 + len(headers))
        head = self.run(self.api.values().get(spreadsheetId=SHEET_ID, range=f"'{tab}'!A{row}:{end}{row}")).get("values", [[]])
        if head[0] != headers:
            self.run(self.api.values().update(spreadsheetId=SHEET_ID, range=f"'{tab}'!A{row}:{end}{row}",
                                              valueInputOption="RAW", body={"values": [headers]}))

    def ensure_tab(self):
        """Learning DB tab: headers + the RUN column H (H1 = RUN ALL). Formatting is rebuilt only when it is missing."""
        self.ensure(TAB, HEADERS)
        sid = self._sheet_id(TAB)
        h1 = (self.run(self.api.values().get(spreadsheetId=SHEET_ID, range=f"'{TAB}'!H1")).get("values") or [[""]])[0][0]
        meta = self.run(self.api.get(spreadsheetId=SHEET_ID, fields="sheets(properties.sheetId,conditionalFormats)"))
        n_rules = len(next(s for s in meta["sheets"] if s["properties"]["sheetId"] == sid).get("conditionalFormats", []))
        if h1 not in ALL_STATES or n_rules != 5:
            self._put([{"range": f"'{TAB}'!H1", "values": [[h1 if h1 in ALL_STATES else ALL_REST]]}])
            rng = lambda r0, r1, c0, c1: {"sheetId": sid, "startRowIndex": r0, "endRowIndex": r1,
                                          "startColumnIndex": c0, "endColumnIndex": c1}
            dv = lambda r, vals: {"setDataValidation": {"range": r, "rule": {"condition": {
                "type": "ONE_OF_LIST", "values": [{"userEnteredValue": v} for v in vals]},
                "showCustomUi": True, "strict": True}}}
            GREEN, ORANGE, RED, AMBER = (0.72, 0.88, 0.80), (1.0, 0.85, 0.55), (0.96, 0.78, 0.76), (1.0, 0.95, 0.62)
            colour = lambda text, rgb: {"addConditionalFormatRule": {"index": 0, "rule": {"ranges": [rng(0, 1000, 7, 8)], "booleanRule": {
                "condition": {"type": "TEXT_STARTS_WITH", "values": [{"userEnteredValue": text}]},
                "format": {"backgroundColor": {"red": rgb[0], "green": rgb[1], "blue": rgb[2]}}}}}}
            self.run(self.api.batchUpdate(spreadsheetId=SHEET_ID, body={"requests": [
                *[{"deleteConditionalFormatRule": {"sheetId": sid, "index": 0}} for _ in range(n_rules)],  # ours only
                colour("▶ RUN", GREEN), colour("▶ START", AMBER), colour("⏳", ORANGE), colour("✅", GREEN), colour("❌", RED),
                dv(rng(0, 1, 7, 8), ALL_STATES),
                dv(rng(1, 1000, 7, 8), [G_REST, G_START, G_RUN, DONE_CELL, ASK_CELL]),
                {"repeatCell": {"range": rng(0, 1000, 7, 8), "cell": {"userEnteredFormat": {
                    "textFormat": {"bold": True}, "horizontalAlignment": "CENTER"}},
                    "fields": "userEnteredFormat(textFormat,horizontalAlignment)"}},
                {"updateDimensionProperties": {"range": {"sheetId": sid, "dimension": "COLUMNS", "startIndex": 7, "endIndex": 8},
                                               "properties": {"pixelSize": 130}, "fields": "pixelSize"}}]}))
        sc = ldb_scan(self.ldb_controls())
        self.ldb_fill(sc["fill"], sc["clear"])

    def _sheet_id(self, tab):
        meta = self.run(self.api.get(spreadsheetId=SHEET_ID, fields="sheets.properties(sheetId,title)"))
        return next((s["properties"]["sheetId"] for s in meta["sheets"] if s["properties"]["title"] == tab), None)

    def ensure_requests(self):
        """Row 1 = headers (G1 = the RUN ALL control), data from row 2:
        Script ID | Topic | Extra | Minutes | ON/OFF | Status | per-row RUN. Idempotent. Upgrades the earlier layout that
        had a RUN/Idle control row on top: that row is deleted and everything moves up one row."""
        g = lambda rng, **kw: self.run(self.api.values().get(
            spreadsheetId=SHEET_ID, range=f"'{REQ_TAB}'!{rng}", **kw)).get("values", [])
        sid = self._sheet_id(REQ_TAB)
        if sid is not None:
            a1 = (g("A1") or [[""]])[0][0]
            if a1 == "RUN":
                self.run(self.api.batchUpdate(spreadsheetId=SHEET_ID, body={"requests": [{"deleteDimension": {"range": {
                    "sheetId": sid, "dimension": "ROWS", "startIndex": 0, "endIndex": 1}}}]}))
            elif a1 not in ("", "Script ID"):
                raise RuntimeError("Script Requests has rows in an unknown layout; move them aside before upgrading.")
        self.ensure(REQ_TAB, REQ_HEADERS, row=1)
        sid = self._sheet_id(REQ_TAB)
        if (g("G1") or [[""]])[0][0] not in ALL_STATES:
            self.set_all_cell(ALL_REST)
        meta = self.run(self.api.get(spreadsheetId=SHEET_ID, fields="sheets(properties.sheetId,conditionalFormats)"))
        n_rules = len(next(s for s in meta["sheets"] if s["properties"]["sheetId"] == sid).get("conditionalFormats", []))
        rng = lambda r0, r1, c0, c1: {"sheetId": sid, "startRowIndex": r0, "endRowIndex": r1,
                                      "startColumnIndex": c0, "endColumnIndex": c1}
        dv = lambda r, vals, strict: {"setDataValidation": {"range": r, "rule": {"condition": {
            "type": "ONE_OF_LIST", "values": [{"userEnteredValue": v} for v in vals]},
            "showCustomUi": True, "strict": strict}}}
        bold = lambda r: {"repeatCell": {"range": r, "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
                                         "fields": "userEnteredFormat.textFormat.bold"}}
        wrap = {"repeatCell": {"range": rng(1, 1000, 1, 3), "cell": {"userEnteredFormat": {
            "wrapStrategy": "WRAP", "verticalAlignment": "TOP"}},
            "fields": "userEnteredFormat(wrapStrategy,verticalAlignment)"}}
        runcol = {"repeatCell": {"range": rng(0, 1000, 6, 7), "cell": {"userEnteredFormat": {
            "textFormat": {"bold": True}, "horizontalAlignment": "CENTER"}},
            "fields": "userEnteredFormat(textFormat,horizontalAlignment)"}}
        width = lambda c, px: {"updateDimensionProperties": {"range": {
            "sheetId": sid, "dimension": "COLUMNS", "startIndex": c, "endIndex": c + 1},
            "properties": {"pixelSize": px}, "fields": "pixelSize"}}
        GREEN, ORANGE, RED, AMBER = (0.72, 0.88, 0.80), (1.0, 0.85, 0.55), (0.96, 0.78, 0.76), (1.0, 0.95, 0.62)
        colour = lambda r, kind, text, rgb: {"addConditionalFormatRule": {"index": 0, "rule": {"ranges": [r], "booleanRule": {
            "condition": {"type": kind, "values": [{"userEnteredValue": text}]},
            "format": {"backgroundColor": {"red": rgb[0], "green": rgb[1], "blue": rgb[2]}}}}}}
        status, runc = rng(1, 1000, 5, 6), rng(0, 1000, 6, 7)
        self.run(self.api.batchUpdate(spreadsheetId=SHEET_ID, body={"requests": [
            *[{"deleteConditionalFormatRule": {"sheetId": sid, "index": 0}} for _ in range(n_rules)],  # ours only; rebuilt below
            colour(status, "TEXT_STARTS_WITH", "✅", GREEN), colour(status, "TEXT_STARTS_WITH", "⏳", ORANGE),
            colour(status, "TEXT_STARTS_WITH", "❌", RED),
            colour(runc, "TEXT_STARTS_WITH", "▶ RUN", GREEN), colour(runc, "TEXT_STARTS_WITH", "▶ START", AMBER),
            colour(runc, "TEXT_STARTS_WITH", "⏳", ORANGE),
            # leftovers from earlier layouts (e.g. the old Minutes dropdown that now sits under Extra Data): no rule = cleared
            {"setDataValidation": {"range": rng(0, 1000, 0, 3)}}, {"setDataValidation": {"range": rng(0, 1000, 5, 6)}},
            dv(rng(0, 1, 6, 7), ALL_STATES, True),
            dv(rng(1, 1000, 6, 7), [G_REST, G_START, G_RUN], True),
            dv(rng(1, 1000, 3, 4), MINUTE_OPTIONS, False),
            dv(rng(1, 1000, 4, 5), ["ON", "OFF"], True),
            {"updateSheetProperties": {"properties": {"sheetId": sid, "gridProperties": {"frozenRowCount": 1}},
                                       "fields": "gridProperties.frozenRowCount"}},
            bold(rng(0, 1, 0, 6)), wrap, runcol,
            *[width(c, px) for c, px in enumerate((90, 520, 300, 130, 80, 280, 130))]]}))
        sc = scan(self.grid())
        self.fill_run_cells(sc["fill"], sc["clear"])

    def pending_requests(self):
        """-> (ON rows still to write, {'off': n, 'done': n})"""
        self.ensure_requests()
        res = self.run(self.api.values().get(spreadsheetId=SHEET_ID, range=f"'{REQ_TAB}'!A2:G"))
        return parse_requests(res.get("values", []))

    def run_flag(self):
        """State of the RUN ALL control (G1)."""
        return (self.run(self.api.values().get(spreadsheetId=SHEET_ID, range=f"'{REQ_TAB}'!G1")).get("values") or [[""]])[0][0]

    def grid(self):
        return self.run(self.api.values().get(spreadsheetId=SHEET_ID, range=f"'{REQ_TAB}'!A1:G1000")).get("values", [])

    def _put(self, data):
        res = self.run(self.api.values().batchUpdate(spreadsheetId=SHEET_ID, body={"valueInputOption": "RAW", "data": data}))
        if res.get("totalUpdatedCells") != sum(len(d["values"][0]) for d in data):
            raise RuntimeError("API did not confirm the update")

    def set_row_state(self, row, status, run_cell, script_id=None):
        data = [{"range": f"'{REQ_TAB}'!F{row}:G{row}", "values": [[status, run_cell]]}]
        if script_id:
            data.append({"range": f"'{REQ_TAB}'!A{row}", "values": [[script_id]]})
        self._put(data)

    def claim(self, rows):
        """Mark the rows a run will write: Status and RUN cell both show running."""
        self._put([{"range": f"'{REQ_TAB}'!F{r}:G{r}", "values": [[G_RUN, G_RUN]]} for r in rows])

    def release(self, rows):
        """Rows a stopped run left claimed: button back to RUN, an unfinished status becomes a failure."""
        for r in rows:
            st = (self.run(self.api.values().get(spreadsheetId=SHEET_ID, range=f"'{REQ_TAB}'!F{r}")).get("values")
                  or [[""]])[0][0]
            self.set_row_state(r, "❌ Failed: run stopped" if st.startswith("⏳") else st, G_REST)

    def fill_run_cells(self, fill, clear=()):
        if fill:
            self._put([{"range": f"'{REQ_TAB}'!G{r}", "values": [[G_REST]]} for r in fill])
        if clear:
            self.run(self.api.values().batchClear(spreadsheetId=SHEET_ID, body={
                "ranges": [f"'{REQ_TAB}'!G{r}" for r in clear]}))

    def set_all_cell(self, text, note=None):
        """The RUN ALL control (G1). `note` = hover note with the last run's summary (no clutter in the grid)."""
        self._put([{"range": f"'{REQ_TAB}'!G1", "values": [[text]]}])
        if note is not None:
            self.run(self.api.batchUpdate(spreadsheetId=SHEET_ID, body={"requests": [{"updateCells": {
                "range": {"sheetId": self._sheet_id(REQ_TAB), "startRowIndex": 0, "endRowIndex": 1,
                          "startColumnIndex": 6, "endColumnIndex": 7},
                "rows": [{"values": [{"note": note}]}], "fields": "note"}}]}))

    def first_cols(self):
        """Columns A:C of every row (Script ID, Title, Original Script) - used to find a record's row."""
        return self.run(self.api.values().get(spreadsheetId=SHEET_ID, range=f"'{TAB}'!A:C")).get("values", [])

    def get_row(self, row):
        return (self.run(self.api.values().get(spreadsheetId=SHEET_ID, range=f"'{TAB}'!A{row}:H{row}")).get("values") or [[]])[0]

    def write_row(self, row, values, skip=()):
        """Write the row's cells A..G; indexes in `skip` (typed/pasted input) are left untouched."""
        data, i = [], 0
        while i < len(values):
            if i in skip:
                i += 1
                continue
            j = i
            while j < len(values) and j not in skip:
                j += 1
            data.append({"range": f"'{TAB}'!{chr(65 + i)}{row}:{chr(64 + j)}{row}", "values": [values[i:j]]})
            i = j
        res = self.run(self.api.values().batchUpdate(spreadsheetId=SHEET_ID, body={"valueInputOption": "RAW", "data": data}))
        if res.get("totalUpdatedCells", 0) < 1:
            raise RuntimeError("API did not confirm the write")
        return row

    def append_row(self, values):
        res = self.run(self.api.values().append(
            spreadsheetId=SHEET_ID, range=f"'{TAB}'!A:{LAST_COL}", valueInputOption="RAW",
            insertDataOption="INSERT_ROWS", body={"values": [values]}))
        upd = res.get("updates", {})
        if not upd.get("updatedCells"):
            raise RuntimeError("API did not confirm the append")
        return int(re.search(r"![A-Z]+(\d+)", upd["updatedRange"]).group(1))

    # ---- Learning DB RUN column (H): only columns A and H are polled, the big script cells are not
    def ldb_controls(self):
        res = self.run(self.api.values().batchGet(spreadsheetId=SHEET_ID, ranges=[f"'{TAB}'!A1:A1000", f"'{TAB}'!H1:H1000"]))
        a, h = [vr.get("values", []) for vr in res["valueRanges"]]
        cell = lambda col, i: (col[i][0].strip() if i < len(col) and col[i] else "")
        return {"h1": cell(h, 0), "rows": [(i + 1, cell(a, i), cell(h, i)) for i in range(1, max(len(a), len(h)))]}

    def ldb_all(self):
        return self.run(self.api.values().get(spreadsheetId=SHEET_ID, range=f"'{TAB}'!A1:H1000")).get("values", [])

    def ldb_note(self, row, col, text):
        self.run(self.api.batchUpdate(spreadsheetId=SHEET_ID, body={"requests": [{"updateCells": {
            "range": {"sheetId": self._sheet_id(TAB), "startRowIndex": row - 1, "endRowIndex": row,
                      "startColumnIndex": col, "endColumnIndex": col + 1},
            "rows": [{"values": [{"note": text}]}], "fields": "note"}}]}))

    def ldb_mark(self, row, text, note=None):
        self._put([{"range": f"'{TAB}'!H{row}", "values": [[text]]}])
        if note is not None:
            self.ldb_note(row, 7, note)

    def ldb_fill(self, fill, clear=()):
        if fill:
            self._put([{"range": f"'{TAB}'!H{r}", "values": [[G_REST]]} for r in fill])
        if clear:
            self.run(self.api.values().batchClear(spreadsheetId=SHEET_ID, body={"ranges": [f"'{TAB}'!H{r}" for r in clear]}))

    def ldb_claim(self, rows):
        self._put([{"range": f"'{TAB}'!H{r}", "values": [[G_RUN]]} for r in rows])

    def ldb_release(self, rows, why="run stopped"):
        """Rows a stopped run did not reach: back to RUN (not ASK - nothing is wrong with the row), reason in the note."""
        for r in rows:
            self.ldb_mark(r, G_REST, f"Not processed: {why}. Click START again.")

    def ldb_set_all(self, text, note=None):
        self._put([{"range": f"'{TAB}'!H1", "values": [[text]]}])
        if note is not None:
            self.ldb_note(1, 7, note)


def sync_record(sheet, rid, rec):
    """Upsert one record by Script ID -> no duplicate rows. Pasted/typed input in D and F is left alone."""
    values = row_values(rid, rec)
    row = find_row(sheet.first_cols(), rid, rec["original"])
    if row is None:
        row = sheet.append_row(values)
    else:
        row = sheet.write_row(row, values, skip=(3, 5) if pending_input(sheet.get_row(row), rec) else ())
    rec["synced"] = True
    return row


def finish_revision(sheet, rid, rec, note=None):
    """After a pasted update was processed: the row gets the clean script in D, the rebuilt E/F/G, and RUN cell = done."""
    row = find_row(sheet.first_cols(), rid, rec["original"])
    if row is None:
        raise RuntimeError(f"{rid} has no row in the sheet yet")
    sheet.write_row(row, row_values(rid, rec))
    sheet.ldb_mark(row, DONE_CELL, note if note is not None else f"{today()} - update processed")
    rec["synced"] = True
    return row


def sync_pending(db, sheet_factory=GoogleSheet):
    pending = [(rid, r) for rid, r in db["records"].items() if not r["synced"]]
    if not pending:
        return "Nothing pending."
    try:
        sheet = sheet_factory()
        sheet.ensure_tab()
        out = [f"SYNCED {rid} -> row {sync_record(sheet, rid, r)}" for rid, r in pending]
    except Exception as e:  # keep local data, report honestly
        left = [rid for rid, r in pending if not r["synced"]]
        return f"PENDING ({len(left)}: {', '.join(left)}) — sheet not updated: {e}"
    return "\n".join(out)

