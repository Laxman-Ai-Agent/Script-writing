# Other /script modes (loaded only when needed: Mode F revise, G topics, D user revision, B update, C reanalyze)
Same rules as SKILL.md (categories, sentence-formation-first, unattended = never ask questions).

## Mode F: `/script revise` (updated scripts pasted in the Script Learning Database sheet)
The user pastes an update into the **Revised** column (D) of the script's row - the paste may also hold the old script, a comparison, reasons and rules - and/or types reasons in **My Feedback** (F), then picks START in that row's RUN cell (H) or RUN ALL (H1). The watcher claims the rows (H = ⏳ RUNNING). Unattended: never ask questions.
1. `python script-system/learning_db.py revisions-pending` -> for every row: Script ID, ORIGINAL SCRIPT, D raw, F raw, NEW INPUT / NO NEW INPUT.
2. Per row, find the updated script inside D: the part under a heading like UPDATED / NEW / REVISED SCRIPT (కొత్త SCRIPT, "new script", ...) - or all of D if it holds only a script. Ignore OLD / ORIGINAL SCRIPT parts. Everything else (comparison, reasons, rules / guidelines) is explanation. If you cannot tell which text is the updated script, or the row says NO NEW INPUT: `python script-system/learning_db.py revision-fail <ID> "<what is unclear>"` and go on to the next row. Never guess, never invent feedback.
3. Write files under `output/_revise/<ID>/`: `script.txt` = the updated script exactly as pasted (title line + narration, nothing else); `feedback.txt` = the user's reasons VERBATIM (what they typed in F + the why-parts of the paste), nothing added; `changes.txt` = detailed Changes Made as in Mode D step 2 (run `add-revision` first, then `diff <ID>`; user's reason where given, "no reason given" otherwise).
4. `python script-system/learning_db.py add-revision <ID> output/_revise/<ID>/script.txt`, then `add-feedback` (skip if there are no reasons) and `add-changes`. Rules: the user's updated script is FINAL, so every rule from it (stated outright or inferred from their edits) -> `add-rule <ID> general|topic "<rule>" --approved`. Never PROPOSED.
5. `python script-system/learning_db.py revision-done <ID>` rewrites the row: D = the clean script only, E/F/G rebuilt, H = ✅ DONE. Any failure -> `revision-fail <ID> "<reason>"` (H = ❌ ASK, reason as hover note).
6. After the last row: `python script-system/learning_db.py ldb-finish "<n> processed, <m> need you"`.

## Mode G: `/script topics` (fresh topic ideas into the "Topic Ideas" tab)
Triggered by START FIND (H1 of "Topic Ideas"). Unattended: never ask questions.
1. `python script-system/ideas.py context` -> today's date, the categories that are ON (how many topics N, focus) and everything to avoid (ideas already suggested incl. skipped ones, scripts already made or requested).
2. For EVERY ON category start one subagent (Agent tool, `subagent_type: general-purpose`, `model: sonnet`), all in the same message so they run in parallel. Prompt: the category, its focus, today's date; "find the N+3 most interesting NEWS items from the last 7 days in this category, suited to a Telugu explainer channel (science / tech / history / AI; health goes to Health Decode); for each give an English headline, 3-4 key points with the exact numbers, and 2 or more links from DIFFERENT sites, each with its publication date (YYYY-MM-DD); skip rumours, ads and anything on this avoid list: <the titles>; reply with JSON only".
3. You choose the N best per category (surprising, explainable in 1-5 minutes, not overlapping the avoid list), and for each write a Telugu hook title in natural Tanglish (English words in Latin letters, one line, curiosity-driven, no hype the facts do not support). Write `output/_ideas/<date>.json` = a list of {"category", "title" (English headline), "hook", "points": [...], "sources": [{"url", "date"}]}. Never invent a source, a date or a number: use only what the subagents returned.
4. `python script-system/ideas.py add output/_ideas/<date>.json` rejects unsafe items and prints why (too old, one source, duplicate, over the limit...). Fix what can be fixed once (e.g. take another candidate), otherwise drop it.
5. `python script-system/ideas.py finish "<n> added, <m> rejected"`.
The user then picks ideas in the sheet: USE sends one to "Script Requests" (and shows a tick), SKIP hides it for good.

## Mode D: user sends a revised script / feedback (Script Learning Database)
1. Find the script by its Script ID (the user may say "S002"; `python script-system/learning_db.py list` shows IDs and titles). Save the user's complete revised script to `output/.../script.txt` AND `python script-system/learning_db.py add-revision <id> <file>` — full text, never shortened. Never touch the original.
2. `python script-system/learning_db.py diff <id>` for the raw sentence diff, then write a detailed Changes Made analysis (added / removed / rewritten / sentence formation (order, merging/splitting, connectors, endings) / word swaps / hook / storytelling / narration / Telugu grammar / English vocab / flow / facts / rearrangement — with the user's reason where given, "no reason given" otherwise) → `python script-system/learning_db.py add-changes <id> <file>`.
3. User's explanation, verbatim, never invented → `python script-system/learning_db.py add-feedback <id> <file>`.
4. Rules: the user's revised script is FINAL — every rule from it (stated or inferred from their edits) → `python script-system/learning_db.py add-rule <id> general|topic "<rule>" --approved`. Never PROPOSED. Don't turn every one-off edit into a rule. The row's CATEGORY (printed by `revisions-pending`, taken from column H) decides everything: `add-rule` stores it with the rule. In an interactive session also fold each approved general rule into that category's rule file (`rules/dark-world.md` or `rules/health.md`; the older line it replaces is removed) and run `learning_db.py mark-merged "Dark World"` / `mark-merged Health`. Unattended runs only add to the DB; `rules <category>` keeps showing those rules to every new script until an interactive session merges them.
5. Report SYNCED or PENDING exactly as the tool printed. `python script-system/learning_db.py sync` retries pending records.

## Mode B: `/script update`
1. List `sample script/` with byte sizes. Compare to `script-system/manifest.json`.
2. New or changed files only (name not in manifest, or bytes differ): read them.
3. Merge new findings into the matching rule file (Dark World samples → `rules/dark-world.md`; Health / Zumba samples → `rules/health.md`) — add new openings/structures/endings/phrases in their sections. Keep it compact; never duplicate or stack a line that an existing one already covers.
4. Update `manifest.json` (status `analyzed` / `skipped` with note for duplicates, empty, or non-script files).
5. Report in 2–3 lines what changed in the profile.

## Mode C: `/script reanalyze`
Only on explicit request. Read all samples, rebuild the sample-derived sections of `rules/dark-world.md` / `rules/health.md` but KEEP every user-correction rule (user rules always beat sample habits), rebuild `manifest.json`.
