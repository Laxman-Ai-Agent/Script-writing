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
import datetime
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
LOCK = HERE / "watcher.lock"
TASK = "ScriptWatcher"
ALLOWED = ["Read", "Glob", "Grep", "WebSearch", "WebFetch", "Skill",
           "Write(output/**)", "Edit(output/**)", "Edit(script-system/history.json)",
           "Bash(python script-system/learning_db.py:*)"]
PROMPT = ("Invoke the Skill tool with skill 'script' and args 'run'. Follow its Mode E exactly for every ON row "
          "in the Google Sheet. Do nothing else.")


def log(msg):
    line = f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def stamp():
    return f"{datetime.datetime.now():%Y-%m-%d %H:%M}"


def run_claude():
    """-> (ok, reason). Unattended headless run; ponytail: one run at a time, no resume of a half-finished run."""
    exe = shutil.which("claude")
    if not exe:
        return False, "claude CLI not found on PATH"
    # narrow, documented recovery switches of the project's fact-forcing hook: it would only stall an unattended run
    env = {**os.environ, "GATEGUARD_BASH_ROUTINE_DISABLED": "1",
           "GATEGUARD_EXEMPT_GLOBS": "output/**,script-system/history.json"}
    try:
        p = subprocess.run([exe, "-p", PROMPT, "--permission-mode", "dontAsk", "--max-budget-usd", BUDGET_USD,
                            "--no-session-persistence", "--allowedTools", *ALLOWED],  # variadic flag goes last
                           cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8",
                           timeout=RUN_TIMEOUT_MIN * 60)
    except subprocess.TimeoutExpired:
        return False, f"timed out after {RUN_TIMEOUT_MIN} min"
    out = (p.stdout or "") + (p.stderr or "")
    log("claude output (tail):\n" + out[-2000:])
    if "Failed to authenticate" in out:
        return False, "Claude login expired - run `claude auth login` once in a terminal"
    return (True, "") if p.returncode == 0 else (False, f"claude exited with code {p.returncode}")


def tick(sheet, runner=run_claude, say=log):
    """One poll. Acts only on RUN NOW and only when ON rows exist. Always leaves the RUN cell at Idle + a message."""
    if sheet.run_flag() != "RUN NOW":
        return "idle"
    reqs, sk = sheet.pending_requests()
    if not reqs:
        sheet.set_run_state("Idle", f"{stamp()} - nothing to run: no ON rows ({sk['off']} OFF, {sk['done']} Done skipped)")
        say("RUN NOW but no ON rows")
        return "empty"
    sheet.set_run_state("Idle", f"{stamp()} - Running {len(reqs)} script(s)... please do not edit ON rows")
    say(f"RUN NOW: starting {len(reqs)} row(s)")
    ok, why = runner()
    if not ok:
        sheet.set_run_state("Idle", f"{stamp()} - Run stopped: {why}. Failed/Running rows are retried next time. See watcher.log")
        say(f"run failed: {why}")
        return "failed"
    if "Running" in sheet.run_message():  # claude never wrote its own run-finish summary
        sheet.set_run_state("Idle", f"{stamp()} - finished; see the Status column")
    say("run finished")
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
