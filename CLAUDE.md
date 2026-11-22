# Telugu Script Writing System

Research a topic in English -> write a natural Telugu narration script in the user's channel voice. **All writing rules cleared 2026-11-22 (second reset) - the user will give new rules.**

## User
- Runs Telugu YouTube channels: **Health Decode**, **Zumba Fitness**, **The Dark World**. None has writing rules now; the user gives new ones.
- Reply in **Telugu script** (user writes Telugu / Tanglish). Native speaker - their language corrections are final.
- Wants narration text only in script.txt: no b-roll cues, no timestamps. Final script shown directly (no fact-sheet approval step).

## How to use
- `/script run` processes all three sheet tabs (RUN=START generate, CHECK=START template check); Zumba = Short only. See SKILL.md.

## File map
| Path | What it is |
|---|---|
| `.claude/skills/script/SKILL.md` | Status (no rules) + research mechanics |
| `script-system/rules/health-decode/` | ALL Health Decode rules, nothing else: 01-style-dna (Directive, Module 1.1-1.6, 2), 02-style-examples (1.7 training pack), 03-ymyl-and-structure (3-5), 04-shorts-tts (6-7), 05-past-scripts-log (9 + log), 06-banned-words (8 + 10: every banned word of the channel, by section) |
| `script-system/rules/zumba-fitness/` | ALL Zumba Fitness rules: same 6-file layout, adapted to fitness science (independent copy made 2026-11-22; never sync with health-decode/) |
| `script-system/rules/dark-world/` | ALL Dark World rules: 01-style-dna (voice, narrator opinion rule), 02-style-examples, 03-monetization-and-structure (3-5), 04-shorts-tts (6-7), 05-past-scripts-log (9), 06-banned-words (8 + 10: word bans, gossip, limited frames, monetization words); `sample_content.txt` = style reference only (2026-11-22) |
| `script-system/check.py` | Script checker per channel; reads 06-banned-words.md live. `selftest` command |
| `script-system/sheet.py` | Google Sheet connector, tabs "Health-Decode" + "Dark-World" (long+short, A-J) and "Zumba-Fitness" (short only, A-H). Never writes *-UPDATED user columns. `selftest` command |
| `script-system/credentials/service-account.json` | Google service-account key (gitignored, never commit) |
| `output/YYYY-MM-DD-<slug>/` | per-script outputs: facts.md, script.txt / short.txt (old.txt = imported old version) |
| `sample script/` | User's old sample scripts (Health-decode.txt removed). NOT analyzed, NOT used |

## Rules for future changes
- **No file over 450 lines**: split code into modules.
- **Three rule categories that never mix:** each has its own folder in `script-system/rules/` (`health-decode/`, `zumba-fitness/`, `dark-world/`) with its own Writing DNA. A script for one channel reads only that folder. Nothing carries over between them.
- **No stacking:** a new rule goes into its section of the right file and the older line it replaces is deleted or rewritten in the same edit. Show corrections as a table (old | new | reason).
- Words/min (~150) is an estimate; recalibrate when the user reports a real recorded duration.
- Git: remote `origin` = https://github.com/Laxman-Ai-Agent/Script-writing.git (branch `main`). Author "Script-writing". Commit + push only when the user asks.

## Status
- 2026-11-22: all old rules/outputs reset (old code only in git history, commit 7c8ea07 and earlier). Current rules written fresh per channel.
- 2026-11-22 restructure: every channel folder = 01 style DNA, 02 examples, 03 structure, 04 shorts + TTS, 05 log, 06 ALL banned words (Module 8 blacklist + word swaps + Module 10 lists). New banned words go only into that channel's 06. `script-system/check.py` enforces 06 automatically.
