---
name: script
description: Telugu narration script writer for Health Decode, Zumba Fitness and The Dark World. Each channel has its own rules folder in script-system/rules/; only Health Decode has rules yet. Use when the user gives a topic or new writing rules.
---

# Telugu Narration Script Writer

## Status
| Category | Rules folder (read ONLY this folder for that channel) |
|---|---|
| Health Decode | `script-system/rules/health-decode/` (5 files: 01-style-dna, 02-style-examples, 03-ymyl-and-structure, 04-shorts-tts-blacklist, 05-past-scripts-log) |
| Zumba Fitness | `script-system/rules/zumba-fitness/` (same 5 files, fitness version; run steps below with this folder) |
| The Dark World | `script-system/rules/dark-world/` (no rules yet) |
- A channel whose folder has no rules: do NOT write scripts for it; ask the user for rules. Never reuse any old rule, old script style, `sample script/`, earlier `output/` scripts or anything from git history.
- New rules go into that channel's folder only (channels never mix). A later rule replaces the line it contradicts in the same edit (no stacking, no duplicates).

## Health Decode / Zumba Fitness run (use only that channel's folder)
1. Read all 5 files in the channel folder (05 = PAST_SCRIPTS_LOG: hooks, intro lines, analogies already used).
2. Research -> `output/YYYY-MM-DD-<slug>/facts.md`.
3. Write `script.txt` (main, Module 4-5) and `short.txt` (Module 6: YouTube ending in the script, Reels ending as one extra line after a blank line).
4. Check with Python (not grep; grep misses Telugu here): no digits, no Module 8 / 1.4 banned words.
5. Show both scripts in chat, then append the 4-line log (Module 9) to `05-past-scripts-log.md`.

## Health Decode Sheet run (`/script run`) - tab "Health-Decode", script `script-system/hd_sheet.py`
Columns: D/E = AI long/short | F = RUN status | G/H = user edits (NEVER write) | I = TEMPLATES CHECK result | J = CHECK status.
1. `python -X utf8 script-system/hd_sheet.py pending` -> rows with F=START (generate) or J=START (check).
2. Generate (F=START): `status <row> run RUNNING` -> do the Health Decode run above for topic B (+ extra C) -> save to `output/YYYY-MM-DD-<slug>/` -> `write <row> script.txt short.txt` (sets D, E, F=DONE). On failure: `status <row> run ERROR`.
3. Template check (J=START): `status <row> check RUNNING` -> `texts` (final text = G/H if the user edited, else D/E) + `overlap <row>` + `05-past-scripts-log.md`. Judge STRUCTURE, not just words, against every other row and the log:
   - hook type/shape, intro closing line, authority line wording, transition/bridge lines, analogies, end CTA + comment question, Short ending, paragraph order, repeated sentence openings or frames (e.g. "X అంటే...", "మరి ... ఎందుకు?") used the same way.
   - Write `I` in Telugu, short: `NO REPEAT ✅` + one line why, OR `REPEATED ⚠️` + bullets (what repeats, which row ID, suggested fix). Save to a temp file -> `check-result <row> <file>` (sets I, J=DONE). On failure: `status <row> check ERROR`.
4. Never touch columns A, B, C, G, H or formatting; `hd_sheet.py` refuses to write them.
5. Columns H, I, J are the user's manual controls (user, 2026-11-22). After generating (step 2) STOP: never start the template check yourself and never set J (or I) on your own. Run step 3 only for rows where the user has set J=START.

## Mechanics kept (not writing style)
- Research: English sources into `output/YYYY-MM-DD-<slug>/facts.md` (claim - source URL - confidence), optionally via one Sonnet subagent; write only from facts.md, re-tell, never translate.
- Sheet connector: `script-system/hd_sheet.py` (Health Decode tab only), key in `script-system/credentials/` (gitignored).
