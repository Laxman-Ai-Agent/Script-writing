---
name: script
description: Telugu narration script writer for Health Decode, Zumba Fitness and The Dark World. Each channel has its own rules folder in script-system/rules/; only Health Decode has rules yet. Use when the user gives a topic or new writing rules.
---

# Telugu Narration Script Writer

## Status
| Category | Rules folder (read ONLY this folder for that channel) |
|---|---|
| Health Decode | `script-system/rules/health-decode/` (6 files: 01-style-dna, 02-style-examples, 03-ymyl-and-structure, 04-shorts-tts-blacklist, 05-past-scripts-log, 06-banned-words) |
| Zumba Fitness | `script-system/rules/zumba-fitness/` (same 6 files, fitness version; run steps below with this folder) |
| The Dark World | `script-system/rules/dark-world/` (6 files: 01-style-dna, 02-style-examples, 03-monetization-and-structure, 04-shorts-tts-blacklist, 05-past-scripts-log, 06-banned-words; style reference `sample_content.txt` - style only, never copy) |
- A channel whose folder has no rules: do NOT write scripts for it; ask the user for rules. Never reuse any old rule, old script style, `sample script/`, earlier `output/` scripts or anything from git history.
- New rules go into that channel's folder only (channels never mix). A later rule replaces the line it contradicts in the same edit (no stacking, no duplicates).

## Channel run - Health Decode / Zumba Fitness / The Dark World (use only that channel's folder)
1. Read all rule files in the channel folder (05 = PAST_SCRIPTS_LOG: hooks, intro lines, analogies already used; 06 = banned words -> replacements; new banned words the user gives go into 06's matching section).
2. Research -> `output/YYYY-MM-DD-<slug>/facts.md`.
3. Write `script.txt` (main, Module 4-5) and `short.txt` (Module 6: YouTube ending in the script, Reels ending as one extra line after a blank line).
4. Check with Python (not grep; grep misses Telugu here): no digits, no Module 8 / 1.4 banned words.
5. Show both scripts in chat, then append the 4-line log (Module 9) to `05-past-scripts-log.md`.

## Sheet run (`/script run`) - script `script-system/sheet.py <health|zumba> ...`, one tab per channel
| Tab | AI writes | RUN | User only (NEVER write) | TEMPLATES CHECK | CHECK |
|---|---|---|---|---|---|
| Health-Decode (`health`) | D long, E short | F | G, H | I | J |
| Dark-World (`dark`) | D long, E short | F | G, H | I | J |
| Zumba-Fitness (`zumba`) | D short only (NO long video) | E | F | G | H |
1. `python -X utf8 script-system/sheet.py <ch> pending` -> rows with RUN=START (generate) or CHECK=START (check). Do all three tabs.
2. Generate (RUN=START): `<ch> status <row> run RUNNING` -> run that channel's rules for topic B (+ extra C) -> save to `output/YYYY-MM-DD-<slug>/` -> health: `<ch> write <row> script.txt short.txt`; zumba: write ONLY a Short (Module 6) -> `zumba write <row> short.txt`. Sets RUN=DONE. On failure: `<ch> status <row> run ERROR`.
3. Template check (CHECK=START): `<ch> status <row> check RUNNING` -> `<ch> texts` (user edit wins over AI text) + `<ch> overlap <row>` + that channel's `05-past-scripts-log.md`. Judge STRUCTURE, not just words, against every other row of the same tab and the log:
   - hook type/shape, intro closing line, authority line wording, transition/bridge lines, analogies, end CTA + comment question, Short ending, paragraph order, repeated sentence openings or frames (e.g. "X అంటే...", "మరి ... ఎందుకు?") used the same way.
   - Write `I` in Telugu, short: `NO REPEAT ✅` + one line why, OR `REPEATED ⚠️` + bullets (what repeats, which row ID, suggested fix). Save to a temp file -> `<ch> check-result <row> <file>` (sets TEMPLATES CHECK, CHECK=DONE). On failure: `<ch> status <row> check ERROR`.
4. Never touch A, B, C, user columns or formatting; `sheet.py` refuses to write them.
5. The *-UPDATED, TEMPLATES CHECK and CHECK columns are the user's manual controls (user, 2026-11-22). After generating (step 2) STOP: never start the template check yourself. Run step 3 only for rows where the user set CHECK=START.

## Mechanics kept (not writing style)
- Research: English sources into `output/YYYY-MM-DD-<slug>/facts.md` (claim - source URL - confidence), optionally via one Sonnet subagent; write only from facts.md, re-tell, never translate.
- Sheet connector: `script-system/sheet.py` (tabs Health-Decode + Zumba-Fitness), key in `script-system/credentials/` (gitignored).
