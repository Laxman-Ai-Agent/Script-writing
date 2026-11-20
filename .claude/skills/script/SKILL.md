---
name: script
description: Research a topic in English and write a natural, human-sounding Telugu narration script for The Dark World, Health Decode or Zumba Fitness. Use when the user gives a topic (and optionally a duration like 40s, 1, 1.30, 5, 30) or asks to update the writing rules from new sample scripts.
---

# Telugu Narration Script Writer

Usage:
- `/script <topic> <duration>` — e.g. `/script why is the sky blue 1.30`. Duration in minutes (`1.30` = 1 min 30 s) or seconds (`40s`). No duration → ask once, default 1 min.
- `/script run` - write scripts for every Pending row in the Google Sheet tab "Script Requests" (see Mode E).
- `/script revise` - process updated scripts pasted in the Script Learning Database sheet (see Mode F).
- `/script topics` - find fresh news topics per category into the "Topic Ideas" tab (see Mode G).
- `/script update` — analyze only new sample files and update the rules.
- `/script reanalyze` — full re-analysis of every sample (only when the user explicitly asks).

All system files live in `script-system/` (project root). Samples live in `sample script/`.

---

## Rule files - two categories that never mix (user rule 2026-11-20)
| Rule category | Channels (sheet Category value) | The ONLY rule file | history-last |
|---|---|---|---|
| **Dark World** | The Dark World (`Dark World`) | `script-system/rules/dark-world.md` | `dark` |
| **Health** | Health Decode (`Health Decode`) + Zumba Fitness (`Zumba Fitness`) | `script-system/rules/health.md` | `health` / `zumba` |
- Pick the channel first: the sheet's Category (column H) if set; else Zumba / dance-fitness topics → Zumba Fitness; health / body / disease / medicine → Health Decode; everything else → Dark World. The user can force it with `dark`, `health` or `zumba` anywhere in the request.
- Writing: load ONLY that category's rule file. Never read or apply the other file.
- Inside a rule file, each rule lives in one place; when two lines seem to conflict, the more specific one (channel-specific, topic-specific) wins. Report a real conflict to the user instead of guessing.
- New rule (user correction, Mode D, Mode F, a pasted instruction): decide the category from the channel it is about (Health Decode or Zumba → `health.md`; Dark World → `dark-world.md`; "all channels" → both files). Put it in the right section of the file and **delete or rewrite the older line it replaces in the same edit** (never stack old + new). Word-level swaps go into the language section of that file.

## Reading the user's update: sentence formation first, words second (user rule 2026-11-19, MAIN)
When the user gives updated content (Mode D, Mode F, a pasted rewrite in chat), do NOT stop at word swaps. For every changed sentence ask how it was BUILT and what the user did to it:
- order: what moved to the front or the end; reasons / source / number placed where;
- merging and splitting: sentences joined into one or one broken into two; length and rhythm;
- linking: the connectors and pattern (e.g. claim → "ఎందుకంటే" reason → "కానీ" risk), question vs statement;
- verb and ending forms, tense, politeness; commas and pause points; how the subject is named.
Then write the rule about the PATTERN ("state the myth, give the reason with ఎందుకంటే, then the risk in one sentence"), with one sentence of the user's as a model (tone example, not text to copy), plus the word-level swaps only as secondary items. The Changes Made text must include a "sentence formation" line whenever sentences were restructured. A rule built from words alone is incomplete - check the structure before `add-rule`.

## Mode A: write a script

### 1. Research (English sources)
**Cost rule - steps 1-2 are delegated whenever the Agent tool exists (always in unattended `/script run`).** Start ONE subagent with the Agent tool (`subagent_type: general-purpose`, `model: sonnet`). Its prompt must contain: the topic; the target duration (research depth below); the channel (Health: at least one WHO/NIH/CDC/ICMR/NIN/NHS/Mayo source + one why-it-matters number + the study's limits; Dark World news: official reports / primary sources); the exact output path `output/YYYY-MM-DD-<english-slug>/facts.md`; the fact-sheet format of step 2; the rule "confirm recent-event facts in 2 independent sources"; and "reply in 3 lines: path written, number of sources, any disputed claims". When it returns, Read facts.md once and continue from step 3 - do NOT repeat the research yourself. Writing the Telugu stays with you. If the Agent tool is not available, do steps 1-2 yourself.
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
- limits / caveats of the main study or report
```
Health adds the sections listed in `health.md` §11. English bullets, short. From here on, write from these notes only — never from the article text — so the Telugu is re-told, not translated.

### 3. Load rules
Read the ONE rule file of this category (table above), whole. Do NOT open `sample script/` or the other rule file. Then:
- `python script-system/learning_db.py history-last dark|health|zumba` (this channel; shows the last 20 scripts' hook type, codes, first and last lines) instead of reading `history.json`.
- `python script-system/learning_db.py rules "Dark World"` or `rules Health` - prints only approved rules NOT yet merged into the rule file (usually none). Apply them; where one conflicts with the file, the rule printed here is newer and wins (skip `[TOPIC]` rules that don't fit this topic).

### 4. Plan
- Target words from the file's Length section for the duration.
- Pick the hook type (A–E) not used by the previous 4 scripts of this channel, an opening, a structure / flow and an ending that `history-last` does not show; the first sentence, closing line (and Health disclaimer) must not reuse its wording. Example sentences in the rule file and in Learning DB rules are tone only - rephrase for this topic.
- Health: plan the 6-step flow (`health.md` §2) and, for Health Decode disease topics, all 8 parts.
- Every major point = fact → Indian real-world context / study limit → grounded analysis.
- Pick 1 everyday analogy and 1 concrete example to carry through (if the topic allows).
- Durations ≥10 min: outline chapters first (each ~400–600 words, each opening with a bridge question).

### 5. Write
- Title line first — it is file metadata for the Learning DB / word count, not narrated — then start directly with the fresh, topic-specific hook (no fixed intro paragraph), then connected paragraphs (blank line between), then the ending. Apply the rule file's language, numbers and TTS sections while writing.
- Explain in your own Telugu, as if telling a friend at home — understand the fact first, then say it. Never translate a sentence from the sources.
- ≤8 min: write in one pass into `output/.../script.txt`.
- ≥10 min: write chapter by chapter, appending to `script.txt`; re-read only the previous chapter's last ~10 lines before writing the next, to keep continuity without bloating context.
- Narration text only. No headings inside, no b-roll / visual cues, no timestamps, no notes.

### 6. Human narration refinement (apply WHILE writing step 5; afterwards only targeted Edits, never rewrite the whole file)
Go paragraph by paragraph and ask "would a Telugu person say this out loud to a friend?". Rewrite anything that fails: spoken word choice per the rule file's language section; jargon labels → plain descriptions; choppy one-liners → flowing paragraphs with mixed sentence length; connectors and the filler blacklist within budget; drama the facts don't support removed; certainty words match `facts.md`; nothing that trips the tongue. Changing words must never change facts — if a natural phrasing would distort a fact, keep the accurate phrasing.

### 7. Final validation (one check, targeted Edits only; token cost: never Write script.txt a second time, one `words` run + one Grep for digits `[0-9]`)
- Run the rule file's **Final check** section; fix until every point is ✅. Health: show it after the script as one ✅ line (interactive).
- Every number, name, date matches `facts.md`; disputed claims hedged or omitted; nothing added that isn't in `facts.md`.
- No digits in the narration (only inside names / codes like GPT-5).
- Word count (`python script-system/learning_db.py words <file>`, title excluded) near the target; the duration is a rough guide — never cut an explanation, step, reason, fact or safety line to hit it; trim only repetition and filler.

### 8. Deliver
- Append to `history.json`: `{"date": "YYYY-MM-DD", "channel": "dark" | "health" | "zumba", "topic": "...", "duration": "...", "opening": "O#" | "-", "structure": "S#" | "6-step", "ending": "E#" | "short note", "file": "output/.../script.txt", "hook_type": "A-E", "opening_line": "<exact first sentence>", "closing_line": "<exact last sentence>", "flagged_words_avoided": "0 banned / repeated words"}`. Repeat checks compare only within the same channel. Interactive: also show the 4 audit fields as a JSON block after the script; never inside script.txt.
- Save the untouched original to the Script Learning Database: `python script-system/learning_db.py add-original output/.../script.txt` (do this BEFORE any user edits; it syncs to Google Sheets or reports PENDING — never claim it synced unless it printed SYNCED). It also prints the **Script ID** (S001, S002, ...) and stores the Title (first line) - keep the ID for the delivery line and for Mode E.
- Interactive: show the full script in chat. Unattended (watcher / `claude -p`): do NOT print the script (it is in script.txt and the sheet) — only one line. That line: Script ID, word count and file path. Nothing else unless something was uncertain in the facts — then one line naming it.

### 9. Learning from feedback
When the user corrects style ("ఇలా రాయను", "this word is wrong", "too formal"), decide the category (the script being discussed), then edit that category's rule file per "Rule files" above: the rule goes into its section, the line it replaces is removed. Present the change as a side-by-side table (old | new | reason). If they supply a full rewritten script, it may replace that file's gold sample. If they report a real recorded duration, recompute words/min in the Length section of both files.

---

## Mode E: `/script run` (requests from the Google Sheet)
Tab "Script Requests": row 1 = headers (G1 = the RUN ALL control; its hover note = last run summary), data from row 2.
Columns: Script ID (filled when the row is done) | Topic / Script | Extra Data | Minutes | ON/OFF | Status (⏳ RUNNING / ✅ done / ❌ Failed: reason; colour-coded) | RUN (column G: per-row ▶ RUN / ▶ START / ⏳ RUNNING; G2 = RUN ALL). Rows picked by a START click or RUN ALL are claimed by the watcher (G = ⏳ RUNNING) and `requests` lists exactly those; with no claimed rows (manual `/script run`) it lists the ON rows. Re-running a ✅ row writes a new script with a new Script ID.
- ON/OFF: only `ON` rows are written. Blank counts as OFF. A ✅ Status (or legacy `Done`) is always skipped (never regenerated; to redo a row the user clears its Status). Blank / Running / Failed are retried.
- Minutes dropdown: `Up to N min` (maximum, never pad), `Exact N min` (add real related angles if material is thin), ranges like `10-15 min`, `N+ min` (at least N). A typed plain number counts as `Up to`.
1. `python script-system/learning_db.py requests` -> prints every ON row still to write (sheet row, TOPIC or SCRIPT, extra data, LENGTH) and the skipped counts. "0 ON row(s)" -> tell the user and stop.
2. Process rows ONE AT A TIME, top to bottom; finish one completely before starting the next:
   a. `python script-system/learning_db.py request-start <row>` (Status and RUN cell = ⏳ RUNNING).
   b. Run Mode A: topic = Topic/Script, extra data = the user's own notes to include (still fact-check numbers), duration = the `LENGTH:` line (words target, ~150 words/min, what to do if material is short). Channel = the row's Category (column H of Script Requests; empty -> `category_of` guess: Zumba -> Zumba Fitness, health -> Health Decode, else Dark World); the rule file follows from the channel (table above). If the kind is SCRIPT (full script pasted): keep its facts and flow, rewrite in our style with the rule file, research only to verify numbers. Mode A step 8 saves the original to the Learning Database; use the Script ID it printed (S###).
   c. `python script-system/learning_db.py request-done <row> <id>`; add `--note "6 min, material for 10 min not enough"` when the length differs from the request or related angles were added (Status becomes ✅, or `✅ (note)`; the Script ID goes into column A of that row). On any failure: `python script-system/learning_db.py request-fail <row> "<reason>"`, then go on to the next row.
3. After the last row: `python script-system/learning_db.py run-finish "3 done, 1 failed"` (resets the RUN ALL cell G1 and stores the summary as its hover note).
4. Interactive run: show every script in chat as in Mode A. Unattended: one line per row (Script ID, words, path), no script text.
Triggers: the user types `/script run` in Claude Code (runs regardless of the RUN cell), or `script-system/watcher.py` starts an unattended run when RUN ALL (G1) = START ALL or a row's RUN cell = START. In an unattended run you cannot ask questions: decide with defaults, never wait for input, and only touch output/, history.json and learning_db.py.

## Other modes
Mode F (`/script revise`), Mode G (`/script topics`), Mode D (user sends a revised script), Mode B (`/script update`) and Mode C (`/script reanalyze`) are in `.claude/skills/script/modes-other.md` - Read that file ONLY when running one of those modes. Mode A (write) and Mode E (`/script run`) are fully above.
