---
name: script
description: Research a topic in English and write a natural, human-sounding Telugu narration script in "The Dark World" channel's voice. Use when the user gives a topic (and optionally a duration like 40s, 1, 1.30, 5, 30) or asks to update the writing profile from new sample scripts.
---

# Telugu Narration Script Writer

Usage:
- `/script <topic> <duration>` — e.g. `/script why is the sky blue 1.30`. Duration in minutes (`1.30` = 1 min 30 s) or seconds (`40s`). No duration → ask once, default 1 min.
- Channel: health / body / disease / medicine topics → **Health Decode** (DNA §14). Everything else → **The Dark World**. User can force with `health` or `dark` anywhere in the request.
- `/script update` — analyze only new sample files and update the profile.
- `/script reanalyze` — full re-analysis of every sample (only when the user explicitly asks).

All system files live in `script-system/` (project root). Samples live in `sample script/`.

---

## Mode A: write a script

### 1. Research (English sources)
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
Read `script-system/writing-dna.md` (whole file) and `script-system/history.json`. Do NOT open `sample script/`. Section 11 "Learned corrections" overrides everything else. §13 gold reference = target quality (style only — never reuse its facts).

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
- Word count within ±10% of target (count by whitespace split).
- Opening / structure / ending are not repeats from history.
- Health Decode only: run the §14 7-point rubric; fix until every point is ✅. After the script, show the rubric as a one-line ✅ list (the user wants to see it).

### 8. Deliver
- Append to `history.json`: `{"date": "YYYY-MM-DD", "channel": "dark" | "health", "topic": "...", "duration": "...", "opening": "O#" | "H#", "structure": "S#", "ending": "E#", "file": "output/.../script.txt"}`. Opening-repeat checks compare only within the same channel.
- Show the full script in chat. One line after it: word count and file path. Nothing else unless something was uncertain in the facts — then one line naming it.

### 9. Learning from feedback
When the user corrects style ("ఇలా రాయను", "this word is wrong", "too formal"), append a dated bullet to DNA §11 with the rule in one line; if they give word-level swaps, add rows to DNA §12 (keep it ≤ ~30 rows — merge or drop the least useful). If they supply a full rewritten script, it may replace §13 as the gold reference. If they report a real recorded duration, recompute words/min in §8.

---

## Mode B: `/script update`
1. List `sample script/` with byte sizes. Compare to `script-system/manifest.json`.
2. New or changed files only (name not in manifest, or bytes differ): read them.
3. Merge new findings into `writing-dna.md` — add new openings/structures/endings/phrases, adjust ratios. Keep the file compact; don't duplicate existing entries.
4. Update `manifest.json` (status `analyzed` / `skipped` with note for duplicates, empty, or non-script files).
5. Report in 2–3 lines what changed in the profile.

## Mode C: `/script reanalyze`
Only on explicit request. Read all samples, rebuild `writing-dna.md` from scratch but KEEP §11 Learned corrections, rebuild `manifest.json`.
