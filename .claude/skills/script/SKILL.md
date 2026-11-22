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

## Mechanics kept (not writing style)
- Research: English sources into `output/YYYY-MM-DD-<slug>/facts.md` (claim - source URL - confidence), optionally via one Sonnet subagent; write only from facts.md, re-tell, never translate.
- No Google Sheet connector exists now (removed 2026-11-22); `script-system/credentials/` (service-account key) is kept for when a new one is built.
