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

## Categories - rules never mix (user rule 2026-11-19)
Three separate categories: **Dark World**, **Health Decode**, **Zumba Fitness**. Every script, Learning DB row and Script Requests row has one (Category column H in both tabs; a value the user picked there is final, otherwise `category_of` guesses from the title). Before writing a script OR saving a rule, decide the category first:
- Writing: apply DNA §1-13 + `[ALL]` bullets + only the bullets tagged with THIS category (§11 tags `[DW]` `[HD]` `[ZF]`; Health also §14, Zumba also §15; Health AND Zumba both also §16 blueprint, 100% mandatory) and `learning_db.py rules "<category>"`. Never apply another category's rules.
- Saving a rule from a sheet update or a user correction: it goes ONLY to that row's category - `add-rule` stores the row's category automatically; the DNA §11 bullet gets that category's tag (`[ALL]` only if the user says it is for every channel). A rule from a Health row never changes how Dark World or Zumba scripts are written, and vice versa.

## Reading the user's update: sentence formation first, words second (user rule 2026-11-19, MAIN)
When the user gives updated content (Mode D, Mode F, a pasted rewrite in chat), do NOT stop at word swaps. For every changed sentence ask how it was BUILT and what the user did to it:
- order: what moved to the front or the end; reasons / source / number placed where;
- merging and splitting: sentences joined into one or one broken into two; length and rhythm;
- linking: the connectors and pattern (e.g. claim → "ఎందుకంటే" reason → "కానీ" risk), question vs statement;
- verb and ending forms, tense, politeness; commas and pause points; how the subject is named.
Then write the rule about the PATTERN ("state the myth, give the reason with ఎందుకంటే, then the risk in one sentence"), with one sentence of the user's as a model (tone example, not text to copy), plus the word-level swaps only as secondary rows (DNA §12). The Changes Made text must include a "sentence formation" line whenever sentences were restructured. A rule built from words alone is incomplete - check the structure before `add-rule`.

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
Health Decode adds three sections to facts.md: `## Myths vs facts` (✅/❌ lines), `## Hook ideas` (5, accurate, not scary, no cure claim), `## Description sources` (approved bodies only, with URLs). English bullets, short. From here on, write from these notes only — never from the article text — so the Telugu is re-told, not translated.

### 3. Load style
Read `script-system/writing-dna.md`: Health Decode → whole file except §15; Zumba Fitness → §1-13 + §15 (stop before `## 14`, then Read `## 15`); The Dark World → only up to the line before `## 14` (Grep `^## 14` / `^## 15` for the line numbers, then Read with limits). Every channel ALSO reads `## 17` (analytical educator + anti-repetition, all channels; Grep `^## 17`). In §11/§12 skip every bullet tagged for another category. Run `python script-system/learning_db.py history-last dark|health|zumba` instead of reading `history.json`. Do NOT open `sample script/`. Section 11 "Learned corrections" overrides everything else. Also run `python script-system/learning_db.py rules "<Dark World|Health Decode|Zumba Fitness>"` (this script's category only) and apply every APPROVED rule (only approved ones; skip `[TOPIC]` rules that don't fit this topic). Rules are listed oldest → newest; if two conflict, the newer one (later Script ID) wins. §13 gold reference = target quality (style only — never reuse its facts).

### 4. Plan
- Target words from DNA §8 for the duration.
- Health Decode: research must include at least one authoritative health source (only WHO, CDC, NIH, NHS, ICMR, NIN, AIIMS, GINA, Mayo Clinic or similar top bodies; never invent a study or number; unsure = "ధృవీకరించుకోవాలి" in facts.md, left out of the script), the study's limits, and one why-it-matters number for rubric point 5. Cover all 8 parts of the §14 Health content checklist.
- Health Decode AND Zumba Fitness: follow the §16 blueprint 100% (6-step flow, must-haves incl. the exact spoken disclaimer, strict red lines, ❌→✅ examples). §16 wins over any conflicting line. Use §14 openings (H1–H6), "normal body first, then what goes wrong" structure, §14 CTAs and safety rules.
- Pick a hook type A-E (§17) not used by the previous 4 scripts of this channel; every major point = fact → Indian real-world context / study limit → grounded analysis (§17).
- Pick one opening (§4), one structure (§5), one ending (§6). None of them may match the entries `history-last` printed, and the new first sentence, CTA lines and last line must not reuse the wording it shows (DNA §11 "No fixed template"). Exact sentences in rules are tone examples: rephrase them for this topic. Choose what fits the topic, not at random.
- Pick 1 everyday analogy and 1 concrete example to carry through (if the topic allows).
- Durations ≥10 min: outline chapters first (each ~400–600 words, each opening with a bridge question).

### 5. Write
- Telugu narration following DNA §2 (fixed voice) and §3 (signature moves). Title line first (§7) — it is file metadata for the Learning DB / word count, not narrated, so keep it even though rules say "no title inside the spoken script" — then start directly with the fresh, topic-specific hook (DNA §4 / §11, 2026-11-18: no fixed intro paragraph; never "తెలుసుకోబోతున్నాం"), then the narration in connected paragraphs (blank line between paragraphs), then CTA (§6). Apply the TTS rules while writing: commas after transition words / dramatic turns, no stacked suffixes (DNA §2.8, §2.9, §12 contractions).
- Explain in your own Telugu, as if telling a friend at home — understand the fact first, then say it. Never translate a sentence from the sources.
- ≤8 min: write in one pass into `output/.../script.txt`.
- ≥10 min: write chapter by chapter, appending to `script.txt`; re-read only the previous chapter's last ~10 lines before writing the next, to keep continuity without bloating context.
- Narration text only. No headings inside, no b-roll / visual cues, no timestamps, no notes.

### 6. Human narration refinement (apply WHILE writing step 5; afterwards only targeted Edits, never rewrite the whole file)
Go paragraph by paragraph and ask "would a Telugu person say this out loud to a friend?". Rewrite anything that fails:
- **Spoken word choice (DNA §2.3, §12):** use the word people actually say. English words people say → Latin script, never Telugu script. Bookish Telugu → spoken Telugu or the everyday English word. Channel-specific word lists in the rules win.
- **Labels → descriptions:** jargon labels ("chain reaction", "self-defense system") become plain explanations ("ఒకదాని తర్వాత ఒకటి మార్పులు జరుగుతూ", "తనను తాను కాపాడుకునే పద్ధతి").
- **Rhythm:** merge choppy one-liners into flowing paragraphs; vary sentence length; no two consecutive sentences with the same opening word.
- **Connector budget:** అయితే / దాంతో / అందుకే / మరి — at most ~2 each per 300 words; §17 blacklist (అసలు…?, అంతేకాకుండా, నిజానికి, ఇక్కడ ముఖ్యమైన విషయం ఏంటంటే) at most once each per script.
- **Viewer questions + light CTA (DNA §11):** a direct question to the viewer only at natural story turning points (roughly every 300–400 words, never mechanically), fitting that moment; mid subscribe = one short line in the flow, never a pitch that stops the story.
- **Tone:** remove drama the facts don't support (ఆయుధం, షాక్, ఏకంగా); keep suspense only where the content really turns.
- **Hedging:** certainty words match `facts.md` confidence ("తగ్గవచ్చు" vs "తగ్గుతాయి").
- **Speakability:** no sentence that needs a breath in an awkward place; no stacked suffixes that trip the tongue.
- Changing words must never change facts. If a natural phrasing would distort a fact, keep the accurate phrasing.

### 7. Final validation (one check, targeted Edits only, don't report the checklist; token cost: never Write script.txt a second time, one `words` run + one Grep for digits `[0-9]`)
- No digits in the narration (DNA §11 numbers rule): whole numbers in Telugu words (యాభై, పది కోట్లు, పది గంటలు), decimals in English words (zero point zero five); digits only inside names/codes (GPT-5, T3).
- Every number, name, date matches `facts.md`. Disputed claims are hedged or omitted. Nothing added that isn't in `facts.md`.
- No calques, no గ్రాంథిక / newsreader phrasing, §9 "Never" list clean.
- Paragraphs, not one-liners; no stretch of ~4 sentences of dry exposition without a question / example / turn.
- Word count near the target (`python script-system/learning_db.py words <file>` counts the narration, title excluded). The duration is only a rough guide (user rule 2026-11-19, all categories, every time frame): the viewer must understand the topic in detail, so never cut an explanation, step, reason, fact or flow to hit the number — longer is fine; trim only repetition and filler.
- Opening / structure / ending are not repeats from history, and the first sentence, CTAs and last line are not copies of the `history-last` wording or of a rule's example sentence.
- Health Decode only: run the §14 9-point rubric (point 9 = Health content checklist: 8 parts with reasons, separate danger-signs paragraph, spoken 2-sentence disclaimer; point 8 = HEALTHCARE CONTENT SAFETY RULE: no medicines/doses/treatment instructions/cure claims, warning signs + "Doctor decides treatment" included; this rule beats any research finding or older sample); fix until every point is ✅. After the script, show the rubric as a one-line ✅ list (the user wants to see it).
- All channels (§17): hook type differs from the last 4; first 10 words / sentence structure and the ending differ from all 20 `history-last` scripts; no generic Like/Subscribe/Comment closing; zero §17 banned words; blacklist fillers ≤1 each.
- Health Decode AND Zumba Fitness: run the §16 blueprint check (6 steps in order, all must-haves, no red line); fix until all ✅; show it as a one-line ✅ list.

### 8. Deliver
- Append to `history.json`: `{"date": "YYYY-MM-DD", "channel": "dark" | "health", "topic": "...", "duration": "...", "opening": "O#" | "H#", "structure": "S#", "ending": "E#", "file": "output/.../script.txt", "hook_type": "A-E", "opening_line": "<exact first sentence>", "closing_line": "<exact last sentence>", "flagged_words_avoided": "0 banned / repeated words"}` (channel "zumba" for Zumba Fitness). Opening-repeat checks compare only within the same channel. Interactive: also show these 4 audit fields as a JSON block after the script (§17); never inside script.txt.
- Save the untouched original to the Script Learning Database: `python script-system/learning_db.py add-original output/.../script.txt` (do this BEFORE any user edits; it syncs to Google Sheets or reports PENDING — never claim it synced unless it printed SYNCED). It also prints the **Script ID** (S001, S002, ...) and stores the Title (first line) - keep the ID for the delivery line and for Mode E.
- Interactive: show the full script in chat. Unattended (watcher / `claude -p`): do NOT print the script (it is in script.txt and the sheet) — only one line. That line: Script ID, word count and file path. Nothing else unless something was uncertain in the facts — then one line naming it.

### 9. Learning from feedback
When the user corrects style ("ఇలా రాయను", "this word is wrong", "too formal"), append a dated bullet to DNA §11 with the rule in one line, starting with the category tag (`[DW]` / `[HD]` / `[ZF]`, or `[ALL]` only if the user says it is for every channel) - decide the category first (the script being discussed); if they give word-level swaps, add rows to DNA §12 (keep it ≤ ~30 rows — merge or drop the least useful). If they supply a full rewritten script, it may replace §13 as the gold reference. If they report a real recorded duration, recompute words/min in §8.

---

## Mode E: `/script run` (requests from the Google Sheet)
Tab "Script Requests": row 1 = headers (G1 = the RUN ALL control; its hover note = last run summary), data from row 2.
Columns: Script ID (filled when the row is done) | Topic / Script | Extra Data | Minutes | ON/OFF | Status (⏳ RUNNING / ✅ done / ❌ Failed: reason; colour-coded) | RUN (column G: per-row ▶ RUN / ▶ START / ⏳ RUNNING; G2 = RUN ALL). Rows picked by a START click or RUN ALL are claimed by the watcher (G = ⏳ RUNNING) and `requests` lists exactly those; with no claimed rows (manual `/script run`) it lists the ON rows. Re-running a ✅ row writes a new script with a new Script ID.
- ON/OFF: only `ON` rows are written. Blank counts as OFF. A ✅ Status (or legacy `Done`) is always skipped (never regenerated; to redo a row the user clears its Status). Blank / Running / Failed are retried.
- Minutes dropdown: `Up to N min` (maximum, never pad), `Exact N min` (add real related angles if material is thin), ranges like `10-15 min`, `N+ min` (at least N). A typed plain number counts as `Up to`.
1. `python script-system/learning_db.py requests` -> prints every ON row still to write (sheet row, TOPIC or SCRIPT, extra data, LENGTH) and the skipped counts. "0 ON row(s)" -> tell the user and stop.
2. Process rows ONE AT A TIME, top to bottom; finish one completely before starting the next:
   a. `python script-system/learning_db.py request-start <row>` (Status and RUN cell = ⏳ RUNNING).
   b. Run Mode A: topic = Topic/Script, extra data = the user's own notes to include (still fact-check numbers), duration = the `LENGTH:` line (words target, ~150 words/min, what to do if material is short). Channel = the row's Category (column H of Script Requests; empty -> `category_of` guess: Zumba -> Zumba Fitness, health -> Health Decode, else Dark World). If the kind is SCRIPT (full script pasted): keep its facts and flow, rewrite in our style with the approved rules, research only to verify numbers. Mode A step 8 saves the original to the Learning Database; use the Script ID it printed (S###).
   c. `python script-system/learning_db.py request-done <row> <id>`; add `--note "6 min, material for 10 min not enough"` when the length differs from the request or related angles were added (Status becomes ✅, or `✅ (note)`; the Script ID goes into column A of that row). On any failure: `python script-system/learning_db.py request-fail <row> "<reason>"`, then go on to the next row.
3. After the last row: `python script-system/learning_db.py run-finish "3 done, 1 failed"` (resets the RUN ALL cell G1 and stores the summary as its hover note).
4. Interactive run: show every script in chat as in Mode A. Unattended: one line per row (Script ID, words, path), no script text.
Triggers: the user types `/script run` in Claude Code (runs regardless of the RUN cell), or `script-system/watcher.py` starts an unattended run when RUN ALL (G1) = START ALL or a row's RUN cell = START. In an unattended run you cannot ask questions: decide with defaults, never wait for input, and only touch output/, history.json and learning_db.py.

## Other modes
Mode F (`/script revise`), Mode G (`/script topics`), Mode D (user sends a revised script), Mode B (`/script update`) and Mode C (`/script reanalyze`) are in `.claude/skills/script/modes-other.md` - Read that file ONLY when running one of those modes. Mode A (write) and Mode E (`/script run`) are fully above.
