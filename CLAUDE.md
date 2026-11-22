# Telugu Script Writing System

Research a topic in English -> write a natural Telugu narration script in the user's channel voice. **All writing rules cleared 2026-11-22 (second reset) - the user will give new rules.**

## User
- Runs Telugu YouTube channels: **Health Decode**, **Zumba Fitness**, **The Dark World**. None has writing rules now; the user gives new ones.
- Reply in **Telugu script** (user writes Telugu / Tanglish). Native speaker - their language corrections are final.
- Wants narration text only in script.txt: no b-roll cues, no timestamps. Final script shown directly (no fact-sheet approval step).

## How to use
- No script writing until new rules exist. No sheet connector exists now.

## File map
| Path | What it is |
|---|---|
| `.claude/skills/script/SKILL.md` | Status (no rules) + research mechanics |
| `script-system/rules/health-decode.md` | Health Decode rules, full (Part 1 Modules 1-3: YMYL shield, deliverables, 7-step flow; Part 2 Modules 4-7: Shorts, TTS, blacklist, PAST_SCRIPTS_LOG). Other channels: no rules yet |
| `script-system/credentials/service-account.json` | Google service-account key (gitignored, never commit); kept for a future sheet connector |
| `output/YYYY-MM-DD-<slug>/` | per-script outputs (all health outputs removed 2026-11-22) |
| `sample script/` | User's old sample scripts (Health-decode.txt removed). NOT analyzed, NOT used |

## Rules for future changes
- **No file over 450 lines**: split code into modules.
- **Three rule categories that never mix:** each gets its own file in `script-system/rules/` when the user gives its new rules. Nothing carries over between them.
- **No stacking:** a new rule goes into its section of the right file and the older line it replaces is deleted or rewritten in the same edit. Show corrections as a table (old | new | reason).
- Words/min (~150) is an estimate; recalibrate when the user reports a real recorded duration.
- Git: remote `origin` = https://github.com/Laxman-Ai-Agent/Script-writing.git (branch `main`). Author "Script-writing". Commit + push only when the user asks.

## Status
- 2026-11-22 (first reset): old DNA, Learning DB, Topic Ideas, watcher removed; old code only in git history (commit 7c8ea07 and earlier).
- 2026-11-22 (second reset, user): the Health Decode rules (4-part master prompt + Part 5 series splitter) and all writing steps in SKILL.md were removed. 
- 2026-11-22 (third clean-up, user "motham remove it"): all health outputs in output/, sample script/Health-decode.txt, hd_sheet.py + test removed. Nothing health-related is left.
- 2026-11-22: new Health Decode rules Part 2 (Modules 4-7) saved in rules/health-decode.md; Part 1 (Modules 1-3) added same day. Health Decode rules complete.
