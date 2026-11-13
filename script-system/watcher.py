"""Watcher: polls the RUN cell (B1) of the "Script Requests" tab. When it is RUN NOW, starts ONE unattended
`claude -p` run that writes every ON row (see SKILL.md Mode E), then goes back to polling.

  python script-system/watcher.py                  # loop, Ctrl+C to stop (idle polling = 1 Sheets call/min, no tokens)
  python script-system/watcher.py --once           # check once; run if RUN NOW
  python script-system/watcher.py --dry-run        # show the RUN cell + rows that WOULD run; starts nothing
  python script-system/watcher.py install-startup  # start at Windows logon (Task Scheduler)   [you run this]
  python script-system/watcher.py remove-startup

Safety: claude runs with --permission-mode dontAsk (anything not allow-listed is denied, never prompted),
writes only under output/ + script-system/history.json, runs only learning_db.py via Bash, and stops itself at
BUDGET_USD per run. Log: script-system/watcher.log
"""
import csv
import datetime
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import learning_db as L  # noqa: E402

POLL_SECONDS = 60
RUN_TIMEOUT_MIN = 120
BUDGET_USD = "10"  # claude stops itself at this spend per run
LOG = HERE / "watcher.log"
COSTS = HERE / "run-costs.csv"  # one line per run: tokens + cost (local only)
LOCK = HERE / "watcher.lock"
TASK = "ScriptWatcher"
ALLOWED = ["Read", "Glob", "Grep", "WebSearch", "WebFetch", "Skill",
           "Write(output/**)", "Edit(output/**)", "Edit(script-system/history.json)",
           "Bash(python script-system/learning_db.py:*)", "Agent"]
MODEL = "opus"  # writes the Telugu; research is delegated to a Sonnet subagent by the skill (SKILL.md step 1)
# Lean run: project settings only (no user plugins/hooks/MCP), fewer built-in tools -> ~18k instead of ~56k baseline tokens per step
LEAN = ["--setting-sources", "project", "--strict-mcp-config", "--exclude-dynamic-system-prompt-sections",
        "--tools", "Read,Write,Edit,Bash,WebSearch,WebFetch,Glob,Grep,Skill,Agent"]
PROMPT_REVISE = ("Invoke the Skill tool with skill 'script' and args 'revise'. Follow its Mode F exactly for every claimed row in the "
                 "Script Learning Database sheet. Do nothing else.")
PROMPT = ("Invoke the Skill tool with skill 'script' and args 'run'. Follow its Mode E exactly for every ON row "
          "in the Google Sheet. Do nothing else.")


def log(msg):
    line = f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def stamp():
    return f"{datetime.datetime.now():%Y-%m-%d %H:%M}"


def summarize(out):
    """`claude -p --output-format json` output -> (result text, usage stats). Stats are {} if it is not JSON."""
    try:
        d = json.loads(out)
    except ValueError:
        return out, {}
    u = d.get("usage") or {}
    return d.get("result") or "", {
        "turns": d.get("num_turns", 0), "seconds": round(d.get("duration_ms", 0) / 1000),
        "models": ",".join((d.get("modelUsage") or {}).keys()),
        "input": u.get("input_tokens", 0), "cache_write": u.get("cache_creation_input_tokens", 0),
        "cache_read": u.get("cache_read_input_tokens", 0), "output": u.get("output_tokens", 0),
        "cost": round(d.get("total_cost_usd", 0), 2), "error": bool(d.get("is_error"))}


def stats_line(st):
    k = lambda n: f"{n / 1000:.0f}k" if n >= 1000 else str(n)
    return (f"{st['turns']} steps, {st['seconds'] // 60}m{st['seconds'] % 60:02d}s, {st['models']}: "
            f"new in {k(st['input'] + st['cache_write'])} + cached {k(st['cache_read'])}, out {k(st['output'])}, "
            f"~${st['cost']:.2f} list price")


def run_claude(prompt=PROMPT):
    """-> (ok, reason). On success `reason` is the usage line (tokens, cost). Unattended headless run;
    ponytail: one run at a time, no resume of a half-finished run."""
    exe = shutil.which("claude")
    if not exe:
        return False, "claude CLI not found on PATH"
    # narrow, documented recovery switches of the project's fact-forcing hook: it would only stall an unattended run
    env = {**os.environ, "GATEGUARD_BASH_ROUTINE_DISABLED": "1",
           "GATEGUARD_EXEMPT_GLOBS": "output/**,script-system/history.json"}
    try:
        p = subprocess.run([exe, "-p", prompt, "--output-format", "json", "--permission-mode", "dontAsk",
                            "--max-budget-usd", BUDGET_USD, "--no-session-persistence", "--model", MODEL, *LEAN,
                            "--allowedTools", *ALLOWED],  # variadic flag goes last
                           cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8",
                           timeout=RUN_TIMEOUT_MIN * 60)
    except subprocess.TimeoutExpired:
        return False, f"timed out after {RUN_TIMEOUT_MIN} min"
    text, st = summarize(p.stdout or "")
    out = text + (p.stderr or "") + (p.stdout if not st else "")
    log("claude output (tail):\n" + out[-2000:])
    if st:
        line = stats_line(st)
        log("usage: " + line)
        new = not COSTS.exists()
        with open(COSTS, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if new:
                w.writerow(["date", *st.keys()])
            w.writerow([f"{datetime.datetime.now():%Y-%m-%d %H:%M}", *st.values()])
    if "Failed to authenticate" in out:
        return False, "Claude login expired - run `claude auth login` once in a terminal"
    if p.returncode != 0 or st.get("error"):
        return False, f"claude exited with code {p.returncode}"
    return True, stats_line(st) if st else ""


def tick(sheet, runner=run_claude, say=log):
    """One poll. Keeps the RUN cells tidy; acts on RUN ALL (every ON row) and on per-row START clicks.
    The chosen rows are claimed (RUN cell = running) so `learning_db.py requests` hands claude exactly those.
    The last run's summary lives in the hover note of the RUN ALL cell (G1)."""
    sc = L.scan(sheet.grid())
    if sc["fill"] or sc["clear"]:
        sheet.fill_run_cells(sc["fill"], sc["clear"])
    if not (sc["run_all"] or sc["starts"]):
        return "idle"
    rows = sorted(set(sc["starts"]) | (set(sc["on_rows"]) if sc["run_all"] else set()))
    if not rows:
        sheet.set_all_cell(L.ALL_REST, f"{stamp()} - nothing to run: no ON rows")
        say("run requested but no rows to run")
        return "empty"
    sheet.claim(rows)
    sheet.set_all_cell(L.ALL_RUN, f"{stamp()} - running {len(rows)} script(s)")
    say(f"starting {len(rows)} row(s): {rows}")
    ok, why = runner()
    left = L.scan(sheet.grid())["claimed"]  # anything a stopped run did not finish
    if left:
        sheet.release(left)
    if not ok:
        sheet.set_all_cell(L.ALL_REST, f"{stamp()} - run stopped: {why}. Unfinished rows are marked Failed; click RUN again. See watcher.log")
        say(f"run failed: {why}")
        return "failed"
    sheet.set_all_cell(L.ALL_REST, f"{stamp()} - finished" + (f" | {why}" if why else ""))  # why = usage line
    say("run finished" + (f": {why}" if why else ""))
    return "done"


def tick_ldb(sheet, runner=None, say=log, pending_rows=None):
    """Same idea for the Script Learning Database tab: START in a row's RUN cell (H), or RUN ALL (H1), starts one
    unattended run of SKILL.md Mode F that splits a pasted update into clean script / reasons / changes / rules."""
    runner = runner or (lambda: run_claude(PROMPT_REVISE))
    sc = L.ldb_scan(sheet.ldb_controls())
    if sc["fill"] or sc["clear"]:
        sheet.ldb_fill(sc["fill"], sc["clear"])
    if not (sc["run_all"] or sc["starts"]):
        return "idle"
    rows = set(sc["starts"])
    if sc["run_all"]:
        rows |= set((pending_rows or (lambda: L.pending_rows(L.load(), sheet.ldb_all())))())
    rows = sorted(rows)
    if not rows:
        sheet.ldb_set_all(L.ALL_REST, f"{stamp()} - nothing to process: no pasted updates")
        say("learning db: nothing to process")
        return "empty"
    sheet.ldb_claim(rows)
    sheet.ldb_set_all(L.ALL_RUN, f"{stamp()} - processing {len(rows)} update(s)")
    say(f"learning db: starting {len(rows)} row(s): {rows}")
    ok, why = runner()
    left = L.ldb_scan(sheet.ldb_controls())["claimed"]  # anything a stopped run did not finish
    if left:
        sheet.ldb_release(left)
    if not ok:
        sheet.ldb_set_all(L.ALL_REST, f"{stamp()} - run stopped: {why}. Click START again. See watcher.log")
        say(f"learning db run failed: {why}")
        return "failed"
    sheet.ldb_set_all(L.ALL_REST, f"{stamp()} - finished" + (f" | {why}" if why else ""))
    say("learning db run finished" + (f": {why}" if why else ""))
    return "done"


def pid_alive(pid):
    if os.name == "nt":  # os.kill(pid, 0) would TERMINATE the process on Windows
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True).stdout
        return str(pid) in out
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def acquire_lock():
    if LOCK.exists():
        try:
            old = int(LOCK.read_text().strip())
        except ValueError:
            old = 0
        if old and old != os.getpid() and pid_alive(old):
            sys.exit(f"Watcher already running (PID {old}).")
    LOCK.write_text(str(os.getpid()))


def main(argv=None):
    args = (argv if argv is not None else sys.argv[1:])
    if "install-startup" in args or "remove-startup" in args:
        if "remove-startup" in args:
            subprocess.run(["schtasks", "/Delete", "/TN", TASK, "/F"], check=True)
            print("Startup task removed.")
        else:
            pyw = Path(sys.executable).with_name("pythonw.exe")  # no console window
            subprocess.run(["schtasks", "/Create", "/TN", TASK, "/TR", f'"{pyw}" "{Path(__file__).resolve()}"',
                            "/SC", "ONLOGON", "/F"], check=True)
            print(f"Startup task '{TASK}' created: watcher starts at every logon (log: {LOG}).")
        return
    if "--dry-run" in args:
        s = L.GoogleSheet()
        reqs, sk = s.pending_requests()
        print(f"RUN cell: {s.run_flag()} | would write {len(reqs)} row(s) | skipped {sk['off']} OFF, {sk['done']} Done")
        for r in reqs:
            print(f"  #{r['sno']} (row {r['row']}) {r['kind']} | {r['minutes']} | {r['topic'][:60]}")
        return
    acquire_lock()
    sheet = None
    try:
        while True:
            try:
                sheet = sheet or L.GoogleSheet()
                tick(sheet)
                tick_ldb(sheet)
            except Exception as e:  # network/API hiccup: retry on the next poll
                log(f"error: {e}")
                sheet = None
            if "--once" in args:
                return
            time.sleep(POLL_SECONDS)
    finally:
        if LOCK.exists() and LOCK.read_text().strip() == str(os.getpid()):
            LOCK.unlink()


if __name__ == "__main__":
    main()
