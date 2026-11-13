---
name: script
description: Research a topic in English and write a natural, human-sounding Telugu narration script in "The Dark World" channel's voice. Use when the user gives a topic (and optionally a duration like 40s, 1, 1.30, 5, 30) or asks to update the writing profile from new sample scripts.
---

# Telugu Narration Script Writer

Usage:
- `/script <topic> <duration>` — e.g. `/script why is the sky blue 1.30`. Duration in minutes (`1.30` = 1 min 30 s) or seconds (`40s`). No duration → ask once, default 1 min.
- Channel: health / body / disease / medicine topics → **Health Decode** (DNA §14). Everything else → **The Dark World**. User can force with `health` or `dark` anywhere in the request.
- `/script run` - write scripts for every Pending row in the Google Sheet tab "Script Requests" (see Mode E).
- `/script revise` - process updated scripts pasted in the Script Learning Database sheet (see Mode F).
- `/script topics` - find fresh news topics per category into the "Topic Ideas" tab (see Mode G).
- `/script update` — analyze only new sample files and update the profile.
- `/script reanalyze` — full re-analysis of every sample (only when the user explicitly asks).

All system files live in `script-system/` (project root). Samples live in `sample script/`.

---

## Mode A: write a script

### 1. Research (English sources)
**Cost rule - steps 1-2 are delegated whenever the Agent tool exists (always in unattended `/script run`).** Start ONE subagent with the Agent tool (`subagent_type: general-purpose`, `model: sonnet`). Its prompt must contain: the topic; the target duration (research depth below); the channel (health: at least one WHO/NIH/CDC/ICMR/NHS/Mayo source + one why-it-matters number); the exact output path `output/YYYY-MM-DD-<english-slug>/facts.md`; the fact-sheet format of step 2; the rule "confirm recent-event facts in 2 independent sources"; and "reply in 3 lines: path written, number of sources, any disputed claims". When it returns, Read facts.md once and continue from step 3 - do NOT repeat the research yourself. Writing the Telugu stays with you. If the Agent tool is not available, do steps 1-2 yourself.
- Use WebSearch (load via ToolSearch if deferred), then WebFetch the best pages. Prefer: encyclopedias, official/agency sites (NASA, NOAA, WHO, etc.), peer-reviewed or university sources, major news outlets for events. Avoid content farms and unsourced listicles.
- Depth by length: ≤1 min → 2–3 sources; 1.5–5 min → 4–6; 7–15 min → 6–10; 20–30 min → 10+.
- For recent events (news, AI releases), confirm key facts in at least 2 independent sources and note the date.

### 2. Fact sheet
Write `output/YYYY-MM-DD-<english-slug>/facts.md` BEFORE any Telugu:
```
# <topic>
- claim — source URL — confidence (high / medium / disputed)
...
## Angle
- the surprising core insight / twist this script is built around
- common misconception to correct (if any)
```
English bullets, short. From here on, write from these notes only — never from the article text — so the Telugu is re-told, not translated.

### 3. Load style
Read `script-system/writing-dna.md` (whole file) and `script-system/history.json`. Do NOT open `sample script/`. Section 11 "Learned corrections" overrides everything else. Also run `python script-system/learning_db.py rules` and apply every APPROVED rule (only approved ones; skip `[TOPIC]` rules that don't fit this topic). §13 gold reference = target quality (style only — never reuse its facts).

### 4. Plan
- Target words from DNA §8 for the duration.
- Health Decode: research must include at least one authoritative health source (WHO, NIH, CDC, ICMR, NHS, Mayo Clinic) and one why-it-matters number for rubric point 5. Use §14 openings (H1–H6), "normal body first, then what goes wrong" structure, §14 CTAs and safety rules.
- Pick one opening (§4), one structure (§5), one ending (§6). None of them may match any of the last 3 entries in `history.json`. Choose what fits the topic, not at random.
- Pick 1 everyday analogy and 1 concrete example to carry through (if the topic allows).
- Durations ≥10 min: outline chapters first (each ~400–600 words, each opening with a bridge question).

### 5. Write
- Telugu narration following DNA §2 (fixed voice) and §3 (signature moves). Title line first (§7), then the mandatory straight intro paragraph (DNA §4 note: "ఈ video లో మనం … తెలుసుకోబోతున్నాం …"), then the chosen hook and narration in connected paragraphs (blank line between paragraphs), then CTA (§6).
- Explain in your own Telugu, as if telling a friend at home — understand the fact first, then say it. Never translate a sentence from the sources.
- ≤8 min: write in one pass into `output/.../script.txt`.
- ≥10 min: write chapter by chapter, appending to `script.txt`; re-read only the previous chapter's last ~10 lines before writing the next, to keep continuity without bloating context.
- Narration text only. No headings inside, no b-roll / visual cues, no timestamps, no notes.

### 6. Human narration refinement (rewrite pass on the draft — fix in place)
Go paragraph by paragraph and ask "would a Telugu person say this out loud to a friend?". Rewrite anything that fails:
- **English → Telugu:** every English word that has a common spoken Telugu equivalent gets replaced (DNA §2.3, §12). Daily-use loanwords → Telugu script. Latin script only for names / compounds / YES-NO.
- **Labels → descriptions:** jargon labels ("chain reaction", "self-defense system") become plain explanations ("ఒకదాని తర్వాత ఒకటి మార్పులు జరుగుతూ", "తనను తాను కాపాడుకునే పద్ధతి").
- **Rhythm:** merge choppy one-liners into flowing paragraphs; vary sentence length; no two consecutive sentences with the same opening word.
- **Connector budget:** నిజానికి / అయితే / దాంతో / అందుకే / మరి — at most ~2 each per 300 words.
- **Tone:** remove drama the facts don't support (ఆయుధం, షాక్, ఏకంగా); keep suspense only where the content really turns.
- **Hedging:** certainty words match `facts.md` confidence ("తగ్గవచ్చు" vs "తగ్గుతాయి").
- **Speakability:** no sentence that needs a breath in an awkward place; no stacked suffixes that trip the tongue.
- Changing words must never change facts. If a natural phrasing would distort a fact, keep the accurate phrasing.

### 7. Final validation (fix in place, don't report the checklist)
- Every number, name, date matches `facts.md`. Disputed claims are hedged or omitted. Nothing added that isn't in `facts.md`.
- No calques, no గ్రాంథిక / newsreader phrasing, §9 "Never" list clean.
- Paragraphs, not one-liners; no stretch of ~4 sentences of dry exposition without a question / example / turn.
- Word count within ±10% of target (`python script-system/learning_db.py words <file>` counts the narration, title excluded).
- Opening / structure / ending are not repeats from history.
- Health Decode only: run the §14 7-point rubric; fix until every point is ✅. After the script, show the rubric as a one-line ✅ list (the user wants to see it).

### 8. Deliver
- Append to `history.json`: `{"date": "YYYY-MM-DD", "channel": "dark" | "health", "topic": "...", "duration": "...", "opening": "O#" | "H#", "structure": "S#", "ending": "E#", "file": "output/.../script.txt"}`. Opening-repeat checks compare only within the same channel.
- Save the untouched original to the Script Learning Database: `python script-system/learning_db.py add-original output/.../script.txt` (do this BEFORE any user edits; it syncs to Google Sheets or reports PENDING — never claim it synced unless it printed SYNCED). It also prints the **Script ID** (S001, S002, ...) and stores the Title (first line) - keep the ID for the delivery line and for Mode E.
- Show the full script in chat. One line after it: Script ID, word count and file path. Nothing else unless something was uncertain in the facts — then one line naming it.

### 9. Learning from feedback
When the user corrects style ("ఇలా రాయను", "this word is wrong", "too formal"), append a dated bullet to DNA §11 with the rule in one line; if they give word-level swaps, add rows to DNA §12 (keep it ≤ ~30 rows — merge or drop the least useful). If they supply a full rewritten script, it may replace §13 as the gold reference. If they report a real recorded duration, recompute words/min in §8.

---

## Mode E: `/script run` (requests from the Google Sheet)
Tab "Script Requests": row 1 = headers (G1 = the RUN ALL control; its hover note = last run summary), data from row 2.
Columns: Script ID (filled when the row is done) | Topic / Script | Extra Data | Minutes | ON/OFF | Status (⏳ RUNNING / ✅ done / ❌ Failed: reason; colour-coded) | RUN (column G: per-row ▶ RUN / ▶ START / ⏳ RUNNING; G2 = RUN ALL). Rows picked by a START click or RUN ALL are claimed by the watcher (G = ⏳ RUNNING) and `requests` lists exactly those; with no claimed rows (manual `/script run`) it lists the ON rows. Re-running a ✅ row writes a new script with a new Script ID.
- ON/OFF: only `ON` rows are written. Blank counts as OFF. A ✅ Status (or legacy `Done`) is always skipped (never regenerated; to redo a row the user clears its Status). Blank / Running / Failed are retried.
- Minutes dropdown: `Up to N min` (maximum, never pad), `Exact N min` (add real related angles if material is thin), ranges like `10-15 min`, `N+ min` (at least N). A typed plain number counts as `Up to`.
1. `python script-system/learning_db.py requests` -> prints every ON row still to write (sheet row, TOPIC or SCRIPT, extra data, LENGTH) and the skipped counts. "0 ON row(s)" -> tell the user and stop.
2. Process rows ONE AT A TIME, top to bottom; finish one completely before starting the next:
   a. `python script-system/learning_db.py request-start <row>` (Status and RUN cell = ⏳ RUNNING).
   b. Run Mode A: topic = Topic/Script, extra data = the user's own notes to include (still fact-check numbers), duration = the `LENGTH:` line (words target, ~150 words/min, what to do if material is short). Channel is not a column: health -> Health Decode, else The Dark World. If the kind is SCRIPT (full script pasted): keep its facts and flow, rewrite in our style with the approved rules, research only to verify numbers. Mode A step 8 saves the original to the Learning Database; use the Script ID it printed (S###).
   c. `python script-system/learning_db.py request-done <row> <id>`; add `--note "6 min, material for 10 min not enough"` when the length differs from the request or related angles were added (Status becomes ✅, or `✅ (note)`; the Script ID goes into column A of that row). On any failure: `python script-system/learning_db.py request-fail <row> "<reason>"`, then go on to the next row.
3. After the last row: `python script-system/learning_db.py run-finish "3 done, 1 failed"` (resets the RUN ALL cell G1 and stores the summary as its hover note).
4. Show every script in chat as in Mode A.
Triggers: the user types `/script run` in Claude Code (runs regardless of the RUN cell), or `script-system/watcher.py` starts an unattended run when RUN ALL (G1) = START ALL or a row's RUN cell = START. In an unattended run you cannot ask questions: decide with defaults, never wait for input, and only touch output/, history.json and learning_db.py.

## Mode F: `/script revise` (updated scripts pasted in the Script Learning Database sheet)
The user pastes an update into the **Revised** column (D) of the script's row - the paste may also hold the old script, a comparison, reasons and rules - and/or types reasons in **My Feedback** (F), then picks START in that row's RUN cell (H) or RUN ALL (H1). The watcher claims the rows (H = ⏳ RUNNING). Unattended: never ask questions.
1. `python script-system/learning_db.py revisions-pending` -> for every row: Script ID, ORIGINAL SCRIPT, D raw, F raw, NEW INPUT / NO NEW INPUT.
2. Per row, find the updated script inside D: the part under a heading like UPDATED / NEW / REVISED SCRIPT (కొత్త SCRIPT, "new script", ...) - or all of D if it holds only a script. Ignore OLD / ORIGINAL SCRIPT parts. Everything else (comparison, reasons, rules / guidelines) is explanation. If you cannot tell which text is the updated script, or the row says NO NEW INPUT: `python script-system/learning_db.py revision-fail <ID> "<what is unclear>"` and go on to the next row. Never guess, never invent feedback.
3. Write files under `output/_revise/<ID>/`: `script.txt` = the updated script exactly as pasted (title line + narration, nothing else); `feedback.txt` = the user's reasons VERBATIM (what they typed in F + the why-parts of the paste), nothing added; `changes.txt` = detailed Changes Made as in Mode D step 2 (run `add-revision` first, then `diff <ID>`; user's reason where given, "no reason given" otherwise).
4. `python script-system/learning_db.py add-revision <ID> output/_revise/<ID>/script.txt`, then `add-feedback` (skip if there are no reasons) and `add-changes`. Rules: ones the user states outright -> `add-rule <ID> general|topic "<rule>" --approved`; rules you infer -> without `--approved` (PROPOSED).
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
2. `python script-system/learning_db.py diff <id>` for the raw sentence diff, then write a detailed Changes Made analysis (added / removed / rewritten / word swaps / hook / storytelling / narration / Telugu grammar / English vocab / flow / facts / rearrangement — with the user's reason where given, "no reason given" otherwise) → `python script-system/learning_db.py add-changes <id> <file>`.
3. User's explanation, verbatim, never invented → `python script-system/learning_db.py add-feedback <id> <file>`.
4. Rules: rules the user states outright → `python script-system/learning_db.py add-rule <id> general|topic "<rule>" --approved`. Rules you infer → add without `--approved` (PROPOSED) and ask the user; on their yes → `python script-system/learning_db.py approve <id> <n>`. Don't turn every one-off edit into a rule. Approved general rules also go into DNA §11 (§9 learning step).
5. Report SYNCED or PENDING exactly as the tool printed. `python script-system/learning_db.py sync` retries pending records.

## Mode B: `/script update`
1. List `sample script/` with byte sizes. Compare to `script-system/manifest.json`.
2. New or changed files only (name not in manifest, or bytes differ): read them.
3. Merge new findings into `writing-dna.md` — add new openings/structures/endings/phrases, adjust ratios. Keep the file compact; don't duplicate existing entries.
4. Update `manifest.json` (status `analyzed` / `skipped` with note for duplicates, empty, or non-script files).
5. Report in 2–3 lines what changed in the profile.

## Mode C: `/script reanalyze`
Only on explicit request. Read all samples, rebuild `writing-dna.md` from scratch but KEEP §11 Learned corrections, rebuild `manifest.json`.
