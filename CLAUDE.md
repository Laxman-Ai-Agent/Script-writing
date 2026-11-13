# Telugu Script Writing System

Research a topic in English → write a natural, human-sounding Telugu narration script in the user's channel voice.

## User
- Runs two Telugu YouTube channels: **The Dark World** (science / tech / history / AI explainers) and **Health Decode** (health, "AI డాక్టర్" persona).
- Reply in **Telugu script** (user writes Telugu / Tanglish). Native speaker — their language corrections are final.
- Wants narration text only: no b-roll cues, no timestamps. Final script shown directly (no fact-sheet approval step).

## How to use
- `/script <topic> <duration>` — e.g. `/script కిడ్నీ ఎలా పనిచేస్తుంది 1.30`. Durations used: 40s, 50s, 1, 1.30, 2, 3, 5, 7, 8, 10, 12, 15, 20, 30 (min).
- `/script run` - reads Pending rows from the Google Sheet tab "Script Requests" (Script ID, Topic / Script, Extra Data, Minutes dropdown, ON/OFF, Status; row 1 = RUN control). Only ON rows run, one at a time; Done rows are skipped, writes each script, saves the original to the Learning DB, marks the row Done.
- `/script update` — analyze only new files in `sample script/` and merge into the profile.
- `/script reanalyze` — full rebuild (only on explicit request).

## File map
| Path | What it is | When to change |
|---|---|---|
| `.claude/skills/script/SKILL.md` | The workflow: research → fact sheet → plan → write → human-narration refinement → validation → deliver | Change the *process* |
| `script-system/writing-dna.md` | Style profile. §1–10 Dark World voice, §11 user corrections (highest priority), §12 phrase table, §13 gold reference script, §14 Health Decode mode + 7-point rubric | Change the *style* |
| `script-system/manifest.json` | Which sample files were analyzed (name + bytes) | Auto, by `/script update` |
| `script-system/history.json` | Openings/structures used per script, to avoid repeats | Auto, after each script |
| `sample script/` | User's original samples (01–35 + Health-decode.txt). 21=22 duplicate, 36 empty, 34/35 vocab lists | User adds files |
| `script-system/learning_db.py` | Script Learning Database CLI: local `learning-db.json` (source of truth: originals, all revisions, changes, feedback, rules) mirrored to Google Sheet tab "Script Learning Database" (7 columns: Script ID, Title, Original, Revised, Changes, Feedback, Rules; IDs S001, S002, ...). Self-check: `python script-system/test_learning_db.py` | Change the learning/sync logic |
| `script-system/watcher.py` | Auto-run: polls the sheet's RUN cell (B1); on `RUN NOW` starts one unattended `claude -p` run of Mode E (dontAsk mode, writes only output/ + history.json, $10 cap). `--dry-run`, `--once`, `install-startup`. Needs `claude auth login` once. Log `watcher.log` (gitignored) | Change the auto-run behaviour |
| `script-system/credentials/service-account.json` | Google service-account key (gitignored, never commit) | User sets up once |
| `output/YYYY-MM-DD-<slug>/` | `facts.md` (claims + sources) and `script.txt` per script | Auto |

## Rules for future changes
- **Do not re-read `sample script/`** for normal script writing — load `writing-dna.md` only (token saving).
- User style feedback → add a dated one-line bullet to DNA §11; word-level swaps → add a row to §12. Present corrections to the user as a side-by-side table (old | new | reason).
- Latest user corrections override older sample habits and older corrections. As of 2026-11-09 (both channels, long + short): natural Tanglish with English words in **Latin script** (chest pain, hospital, doctor) — this replaced the earlier "Telugu words first / Telugu-script loanwords" rule. Connected paragraphs still apply.
- Words/min (~150) in DNA §8 is still an **estimate** — recalibrate when the user reports a real recorded duration.
- Git: remote `origin` = https://github.com/Laxman-Ai-Agent/Script-writing.git (branch `main`). Author is set per-repo as "Script-writing". Commit + push when the user asks.

## Status (2026-11-09)
- System built; DNA covers both channels; user corrections through 2026-11-09 are in §11/§12/§13.
- Scripts done: onion (Dark World, rewritten by user → §13 gold), goosebumps (Dark World), anaemia (Health Decode, user approved "బాగుంది"), AI Doctor 5-min + 1-min (Health Decode, both rewritten by user → style rules in DNA §11).
- 2026-11-13: Claude Fable/Mythos 5.2 (Dark World, 5 min) — user rewrite saved; new rules: mandatory "ఈ video లో మనం…" intro paragraph before the hook, English words people say in English stay Latin (price, simple, powerful, daily). See DNA §4 note, §11, §12.
- 2026-11-13: Script Learning Database built (learning_db.py). Fable/Mythos record backfilled (3 approved + 3 proposed rules). Google Sheets sync LIVE: GCP project `script-learning-514611`, service account `script-sync@script-learning-514611.iam.gserviceaccount.com` (Editor on the sheet), key in gitignored `script-system/credentials/`. Verified read/write, no-dup re-sync, full-length cells.
- 2026-11-13: `/script run` + "Script Requests" tab added (learning_db.py `requests`, `request-done`).
- 2026-11-13: ON/OFF + S.No + RUN control added; `watcher.py` built (tests + real-sheet idle check pass). NOT yet run end-to-end: the `claude` CLI login had expired (`claude auth login` needed).
- 2026-11-13: Script IDs (S001...) + Title column: Learning DB is now 7 columns, Script Requests gets a Script ID column; old slug ids became aliases (Fable/Mythos = S001).
- 2026-11-13: Script Requests: Script ID is column A (S.No removed); Status shows ⏳ Running (orange) -> ✅ (green) / ❌ Failed (red).
- 2026-11-13: Script Requests column G = per-row RUN (▶ RUN / ▶ START / ⏳ RUNNING), G2 = RUN ALL; watcher claims the chosen rows. B1 RUN NOW still works. No Apps Script (an unused, unauthorized bound project "Untitled project" exists on the user's Drive).
- 2026-11-13: Cost cut (watcher runs): lean flags (project settings only, no MCP, fewer tools: ~18k vs ~56k baseline tokens/step) + research/facts.md delegated to a Sonnet subagent (SKILL.md step 1), Opus writes the Telugu. Same-topic test: old $0.79 / 20 steps -> new $0.47 / 10 steps (list price), quality comparable. Per-run usage goes to run-costs.csv + sheet C1. Test outputs: output/_compare-old|new (not committed).
- Open: words/min calibration (no recorded duration reported yet).
