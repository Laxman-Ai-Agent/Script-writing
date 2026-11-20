# Dark World rules — the ONLY rule file for "The Dark World" scripts

Category **Dark World** (science, tech, history, AI, news explainers). Completely separate from Health (`health.md`): never use a Health rule here, never use a rule from here in a Health script.

**How this file stays clean (maintenance contract):**
- This file is the single source of truth. Each rule lives in exactly ONE place (its section). No dated "corrections" list that stacks old and new.
- A new user rule → put it in its section, and **delete or edit the older line it replaces in the same edit**. Never keep both.
- Example sentences show tone only; never copy them into a script (anti-repetition, §9).
- Learning DB rules: `learning_db.py rules "Dark World"` prints only rules not yet merged here. Fold each into its section, then `learning_db.py mark-merged "Dark World"`.
- Built from `sample script/01–35` (21 = 22 duplicate; 34, 35 = vocabulary lists; 36 empty) + user corrections to 2026-11-20. Do not re-read the samples.

---

## 1. Identity and role
- One narrator, Telugu explainer channel. Topics: how-things-work tech, everyday science, nature/body, deep-time history, disasters, AI/tech news.
- Audience: general Telugu viewers, mobile-first, zero background assumed; never talk down.
- Role: an **analytical educator and researcher**, a curious friend explaining something cool. Calm, objective, grounded, insightful, with calm suspense. Not a lecturer, not a sensational news anchor.
- Priority: natural human narration > fancy vocabulary > artificial storytelling. Understanding first: never drop a fact, number, step or reason to hit a length or to simplify; simplify the words only.

## 2. Language (Tanglish)
1. **Spoken Telugu (వ్యావహారికం)**, never గ్రాంథికం or heavy passive ("చేయబడినది"). "చేస్తారు", "వస్తుంది", "అనుకోండి".
2. **English words people say stay English, in Latin script:** simple, double, price, strict rules, experts, powerful, daily, weak spots, reason, announce, start, lead, money, deals, drop, first, use చేయడం, build చేయడం, work, safe గా, big, small, total, roughly, estimate. Never an English word in Telugu script. Telugu for grammar, verb endings, idioms and words people really say in Telugu (పల్లెటూళ్లు, ఆడవాళ్లు, అలుపు, అలసట, అర్ధరాత్రి, చంద్రుడు).
3. **News / disaster / government topics** use standard news Telugu for official actions and core terms: జారీ చేశారు, హెచ్చరించారు, ఆదేశించారు, ఏర్పాటు చేసి, పరిశీలిస్తున్నారు, అప్రమత్తంగా, మినహా, ముందస్తు, ప్రభావం, వేగం, దశ, సమయం, నష్టం, సిద్ధంగా, మొదలవుతుంది. Science / tech explainers keep the everyday English word (speed, time, effect).
4. Andhra / Telugu-region and neighbour-state places and Telugu leaders' names in Telugu script (నెల్లూరు, విశాఖపట్నం (not Vizag), కాకినాడ, ఒడిశా, తమిళనాడు, తెలంగాణ, చంద్రబాబు నాయుడు).
5. Shorter, lighter forms: చేసే (not చేయగలిగే), ఆపడం (not అడ్డుకోవడం), ఏళ్లుగా (not ఏళ్ల పాటు), "అందరూ వాడుకునేలా" (not అందరికీ). Refer back to the thing just named with దీన్ని (not దాన్ని); use a key noun (వ్యవస్థ) only where needed, then అది / ఇదే or the specific thing.
6. Describe, don't label jargon: "chain reaction" → "ఒకదాని తర్వాత ఒకటి మార్పులు జరుగుతూ". Define every term at first use: "X అంటే simple గా చెప్పాలంటే …".
7. **"మనం"** when exploring together ("ఇప్పుడు చూద్దాం"), **"మీరు"** to address the viewer.
8. No calques (English order in Telugu words), no newsreader / textbook phrasing in normal narration (ఈ నేపథ్యంలో, గణనీయంగా, పేర్కొన్నారు).

## 3. Numbers
- Every whole number in Telugu words, never digits: 50 → యాభై, 1970 → పంతొమ్మిది వందల డెబ్బై, 2005 → రెండు వేల ఐదు, 25% → ఇరవై ఐదు శాతం, 10 crores → పది కోట్లు.
- Number and unit in the SAME language, never mixed: "పది గంటల్లో" (default; same for నిమిషాలు, మీటర్లు, కిలోమీటర్లు, కిలోలు) or "ten hours లో" (inside English-heavy wording). Never "పది hours లో", never "10 hours", never abbreviations (km).
- Decimals in English words, Latin script: zero point zero five, one point five.
- A number inside a name or code stays as it is: GPT-5, T3, Falcon 9.

## 4. Sentences, paragraphs and TTS (ElevenLabs)
- **Connected paragraphs**, 3–6 sentences per beat, blank line between paragraphs; one person talking continuously, never a list of one-liners.
- Mix sentence lengths: crisp ~6-word sentences with ~18-word explanations. No two consecutive sentences starting with the same word.
- Every sentence complete (no fragments like "background." → "background చూద్దాం."). State analogies fully: "Bike నడవడానికి Petrol ఎంత అవసరమో, తుఫాను బలపడడానికి వేడిగా ఉన్న సముద్రం అంత అవసరం."
- **No "…" anywhere.** A pause = comma or full stop.
- **Breath commas:** a comma after a transition word or a dramatic turn ("కానీ, ఇక్కడే ఒక twist ఉంది."). No comma after the subject, and none around a list of names ("seven companies Nvidia, AMD, TSMC కలిసి").
- No tongue-twisters: break heavy compounds and stacked suffixes ("విడుదలవుతుండటంతో" → "విడుదల అవ్వడం వల్ల").
- Spoken contractions: ఏంటంటే (not ఏమిటి అంటే), జరుగుతుందని (not జరుగుతుంది అని), కదూ (not అవును కదా), చేయడానికే.
- Hedge to match the evidence: "కొంతవరకు తగ్గవచ్చు" (not "చాలా వరకు తగ్గుతాయి"), "scientists భావిస్తున్నారు", "science దగ్గర ఇప్పటికీ పూర్తి answer లేదు".
- Cite sources in the voice, never as footnotes: "Hugging Face investigation ప్రకారం", "scientists అంచనా ప్రకారం".

## 5. Content method (no parroting)
- Every major point = **Fact → real-world context → grounded analysis**: the fact, then the practical Indian context (daily life, budget, real usability) or the study's limit / hidden caveat, then a calm view ("ఈ report లో ఈ number ఆకర్షణీయంగా కనిపించినా, ground reality లో సామాన్యులకు ఇది ఎంతవరకు ఉపయోగపడుతుందో చూడాలి"). The view comes from facts.md, never from invented facts.
- Tech / news: no unverified guesses about disasters, stock crashes or emergencies; cite official reports, benchmarks or primary sources (in facts.md).
- Pull the viewer in: voice the viewer's own thought ("ఏదో robot వచ్చి చేస్తుందేమో అనుకుంటారు"), a direct question only at natural turning points (roughly every 300–400 words, never mechanically), then carry on with the answer. A question that opens a new beat starts its own paragraph.
- No stretch of ~4 sentences of dry exposition without a question, example, analogy or turn.
- Carry 1 everyday analogy and 1 concrete example through the script when the topic allows.
- Always give the fair correction when popular belief is wrong.

## 6. Signature moves (copy the MOVE, never the sample wording)
| Move | Pattern |
|---|---|
| Bridge question | "మరి … ఎలా?" / "మరి అలా ఎందుకు జరుగుతుంది?" |
| Myth → reality | "చాలామంది … అనుకుంటారు. కానీ అసలు విషయం అది కాదు." |
| Reframe | "ఇది కేవలం … కాదు." |
| Everyday analogy | household / cricket / school image (steel ball vs steel bowl; cricket ground paper folded to a ball = black hole) |
| One example carried through | "మన దగ్గర ఒక cat photo ఉందనుకుందాం" and follow it to the end |
| Causal chain | దాంతో / అందుకే / ఎందుకంటే / ఫలితంగా |
| Mid twist (only where the content really turns) | "కానీ, ఇక్కడే ఒక interesting విషయం ఉంది." |
| Escalation | "కానీ, కథ అక్కడితో ముగియలేదు." |
| Fair correction | "… అని చెప్పడం correct కాదు." |
| Human scale | "మనుషులు Pyramids కడుతున్న కాలంలో కూడా Mammoths ఇంకా తిరుగుతూ ఉండేవి." |
| Recap before the end | "ఇప్పటివరకు జరిగినదంతా ఒక్క line లో చెప్పాలంటే" |

## 7. Openings (hook)
- **No fixed intro.** Start directly with a fresh, topic-specific hook (its own scene, number, question or image). Never "ఈ video లో మనం … చూద్దాం / తెలుసుకుందాం" intro lines, never "తెలుసుకోబోతున్నాం", never "ఒక్కసారి ఊహించుకోండి".
- The hook teases the most surprising fact of the script in plain words; name the main entities early.
- **Hook type** (rotate; never the type of the previous 4 Dark World scripts): **A** surprising data point / study result, **B** relatable everyday Indian habit / scenario, **C** misconception vs reality, **D** "what happens inside…" mechanism preview, **E** short real-world case / comparison.
- **Opening shape** (rotate; never one of the last 3): O2 Paradox ("ఇంత బరువున్న ship ఎందుకు మునగదు?"), O3 Imagine scenario (built from the scene, without "ఊహించుకోండి"), O4 Cold open (the outcome first), O5 Myth-first, O6 Stacked questions (news / long-form; 2–4 quick questions), O7 Deep-time scene, O8 Hidden in plain sight ("రైలు పట్టాల మధ్య ఈ gap ఎందుకు?"), O1 Playful curiosity and O9 Casual greeting (shorts only, rare).

## 8. Body structures (pick by topic, not the last used)
- **S1 Process walk-through:** ముందుగా → ఆ తర్వాత → ఇప్పుడు → చివరికి, one example end to end.
- **S2 Why-mystery → cause stack:** observation → wrong guess → real cause → second cause → modern twist.
- **S3 Two sides:** reputation → why → "కానీ ఈ story కి మరో side ఉంది" → fair verdict.
- **S4 Timeline milestones**, closing insight.
- **S5 Disaster / event chronology:** calm before → trigger → escalation → human cost → aftermath. Safety tips as short one-action sentences in duty form ("IMD Updates మాత్రమే నమ్మాలి"); no filler.
- **S6 What-if cascade** → reality check → meaning.
- **S7 Investigation reconstruction** (long-form): teaser → setup + definitions → step-by-step escalation with recaps → misconception → lesson.
- **S8 Deep-time journey** → open question.
- **S9 Analogy → real example** with numbers.

## 9. Endings, CTA and anti-repetition
- **Ending** (rotate): E1 core-insight reframe, E2 poetic zoom-out, E3 lesson, E4 practical tip, E5 open mystery, E6 wonder line. The last line is a topic-specific closing reflection or ONE sharp question tied to this topic.
- **No generic closings:** no "Like కొట్టండి", "Subscribe చేయండి", "Comment లో చెప్పండి", "Share చేయండి" formulas. Serious / tragic topics may end with no question.
- **Mid-video subscribe:** at most one short line slipped into the flow at a natural turn, worded fresh each time, never a pitch that stops the story.
- **Never repeat** (`learning_db.py history-last dark` shows the last 20): the hook type of the last 4; the first-sentence structure or first 10 words of the last 20; the ending of the last 20; the wording of any example sentence in this file or a Learning DB rule.
- **Filler blacklist, at most once each per script:** "అసలు…?", "అంతేకాకుండా", "నిజానికి", "ఇక్కడ ముఖ్యమైన విషయం ఏంటంటే". Other connectors (అయితే, దాంతో, అందుకే, మరి) at most ~2 each per 300 words.

## 10. Never (zero tolerance)
- Fear / panic / clickbait words: Silent killer, ప్రమాదకరం, చనిపోతారు, Red alert, రాక్షసుడు, నిజమా?, అసలు నిజం, షాక్ అవుతారు, షాకింగ్, ఆయుధం, ఏకంగా (unless the fact is genuinely that dramatic).
- Stronger certainty than the facts; anything not in facts.md.
- Bullets, headings, labels, stage directions, visual / b-roll cues, timestamps or emojis inside the narration.
- Digits, "…", English words in Telugu script, stacked suffixes.

## 11. Phrase direction (user's own corrections — understand the why, don't search-and-replace)
| Machine-ish | Human | Why |
|---|---|---|
| అసలు ముట్టుకోదు | తాకనే తాకదు | spoken emphasis by doubling |
| మరి ఇది ఎలా జరుగుతుంది? | మరి అలా ఎందుకు జరుగుతుంది? | natural question shape |
| అసలు విషయం వేరే ఉంది | కానీ, ఇక్కడే అసలు విషయం ఉంది | spoken reveal + breath comma |
| ఇది దాని self-defense system | ఇది ఉల్లిపాయ తనను తాను కాపాడుకునే పద్ధతి | explain instead of jargon |
| ప్రకృతి ఇచ్చిన ఒక ఆయుధం | ప్రకృతి దానికి ఇచ్చిన రక్షణ | calmer, accurate |
| గుర్తించారు | గమనించారు | observation, not detection |
| ఏకంగా సెకనుకు 40 మీటర్ల వేగం వరకు | సెకనుకు నలభై మీటర్ల speed తో కూడా | less hype; Telugu number |
| దాగి ఉన్న ఒక చిన్న ఏర్పాటు ఉంది | ఒక చిన్న వ్యవస్థ పనిచేస్తుంది | active verb over static "ఉంది" |
| ప్రభుత్వం అంచనా | government లెక్కల ప్రకారం | the way people say it |
| Bike కి petrol ఎలాగో, తుఫానుకి వేడి సముద్రం అలా | (full analogy, §4) | no shorthand |

## 12. Title line
First line of script.txt = metadata (not narrated). Short: plain question ("Ship అంత బరువుగా ఉన్నా ఎందుకు మునగదు?"). Long: emoji + question + "| keywords Explained". Emojis only in the title.

## 13. Length (ESTIMATE ~150 words/min; recalibrate when the user reports a real recorded duration)
| Duration | Words | Shape |
|---|---|---|
| 40s | ~100 | hook + 1 core idea + reframe |
| 50s | ~125 | hook + 1–2 beats + reframe |
| 1 min | ~150 | hook + 2–3 beats + reframe + closing question |
| 1.5 min | ~225 | + one analogy or twist |
| 2 min | ~300 | + example carried through |
| 3 min | ~450 | full structure, 1 twist, recap |
| 5 min | ~750 | 3–4 sections, definitions |
| 7–8 min | ~1,050–1,200 | 4–6 sections, mid recap |
| 10–12 min | ~1,500–1,800 | chapters, 2 twists, recap every ~3 min |
| 15–20 min | ~2,250–3,000 | chapters, written chapter by chapter |
| 30 min | ~4,500 | chapters, recap every chapter |
The duration is a rough guide: longer is fine if the topic needs it; trim only repetition and filler. Long-form: each section opens with a bridge question or "ఇక ఇప్పుడు"; periodic "ఇప్పటివరకు … ఇప్పుడు మాత్రం" recaps.

## 14. Gold reference (user-written; style only, never a fact source; its last line is the OLD comment-CTA style — do not copy it, §9)
Notice: paragraphs, varied sentence length, "ఎలా అంటే," to open an explanation, "చూశారా," to open the closing reframe, English in Latin script, numbers in Telugu words, calm hedging.
```
ఉల్లిపాయ కోస్తే కళ్లలో నీళ్లు ఎందుకు వస్తాయి?

ఉల్లిపాయ మన కంటికి చాలా దూరంలోనే ఉంటుంది. కత్తి కూడా కంటికి చాలా దూరంలోనే ఉంటుంది. కానీ ఉల్లిపాయ కోయడం మొదలుపెట్టగానే కాసేపట్లోనే కళ్లు మండటం, నీళ్లు రావడం మొదలవుతుంది. మరి అసలు ఉల్లిపాయలో ఏం జరుగుతుంది? మన కళ్ల నుంచి నీళ్లు వచ్చేలా అది ఎలా చేస్తుంది?

చాలామంది ఉల్లిపాయ రసం కళ్లలో పడటం వల్లే ఇలా జరుగుతుందని అనుకుంటారు. కానీ అసలు విషయం అది కాదు. మనం ఉల్లిపాయను కోయకముందు కళ్లను మండించే ఆ పదార్థం అందులో ఉండదు. ఉల్లిపాయను కోసినప్పుడే అది తయారవుతుంది.

ఎలా అంటే, ఉల్లిపాయలోని కణాల్లో sulfur ఉన్న కొన్ని పదార్థాలు, వాటితో చర్య జరిపే enzymes విడివిడిగా ఉంటాయి. మనం కత్తితో ఉల్లిపాయను కోసినప్పుడు ఆ కణాలు పగిలిపోతాయి. అప్పుడు ఈ పదార్థాలన్నీ ఒకదానితో ఒకటి కలుస్తాయి. దాంతో కొన్ని రసాయన మార్పులు జరిగి, చివరికి Syn-Propanethial-S-oxide అనే వాయువు తయారవుతుంది.

ఈ వాయువు గాల్లోకి వ్యాపించి మన కళ్ల దగ్గరికి చేరుతుంది. మన కంటిపై ఉండే cornea అనే భాగంలో చాలా సున్నితమైన నరాలు ఉంటాయి. ఈ వాయువు వాటిని తాకగానే అవి వెంటనే స్పందిస్తాయి. వెంటనే మన కంటిలోని కన్నీటి గ్రంథులకు ఒక సంకేతం వెళ్తుంది. కంటికి ఇబ్బంది కలిగిస్తున్న ఈ పదార్థాన్ని బయటకు పంపించడానికి అవి ఎక్కువగా కన్నీళ్లను విడుదల చేస్తాయి. అందుకే ఉల్లిపాయ కోస్తున్నప్పుడు మనకు తెలియకుండానే కళ్లు నీళ్లతో నిండిపోతాయి.

మరి ఉల్లిపాయ ఇలా ఎందుకు చేస్తుంది? నిజానికి ఇది తనను తాను కాపాడుకునే ఒక పద్ధతి. ఉల్లిపాయను తినడానికి వచ్చే కొన్ని పురుగులు, జంతువుల నుంచి రక్షించుకోవడానికి ఈ రసాయన ప్రక్రియ ఉపయోగపడుతుంది.

ఇక్కడ ఇంకో ఆసక్తికరమైన విషయం ఉంది. రెండు వేల ఇరవై ఐదులో Cornell University పరిశోధకులు high-speed camera తో ఉల్లిపాయను కోసినప్పుడు ఏం జరుగుతుందో పరిశీలించారు. కత్తి ఉల్లిపాయను తాకిన ప్రతిసారీ, దాని నుంచి చాలా చిన్న చిన్న ద్రవ బిందువులు బయటకు ఎగురుతున్నట్లు గమనించారు. వాటిలో కొన్ని సెకనుకు నలభై మీటర్ల speed తో కూడా ప్రయాణించాయి.

ముఖ్యంగా మొద్దుబారిన కత్తితో ఉల్లిపాయను కోసినప్పుడు ఇలాంటి బిందువులు ఎక్కువగా బయటకు వస్తాయి. అందుకే పదునైన కత్తితో నెమ్మదిగా కోస్తే, ఉల్లిపాయ నుంచి బయటకు వచ్చే ఈ బిందువుల పరిమాణం తగ్గి, కళ్లలో నీళ్లు రావడం కూడా కొంతవరకు తగ్గవచ్చు.

చూశారా, మనం ఉల్లిపాయను కోస్తుంటే అది మనల్ని ఏడిపిస్తున్నట్లు అనిపిస్తుంది. కానీ అది తనను తాను కాపాడుకునే ప్రయత్నం చేస్తోంది. మనం మాత్రం మధ్యలో ఇరుక్కుపోతున్నాం అంతే!

మరి ఉల్లిపాయ కోసేటప్పుడు పదునైన కత్తి ఉపయోగిస్తే కళ్లలో నీళ్లు తగ్గుతాయని మీకు ముందే తెలుసా? తెలిసుంటే YES, తెలియకపోతే NO అని comment చేయండి!
```

## 15. Final check (before delivering; fix with targeted edits until all ✅)
Language (§2), numbers (§3), TTS (§4), fact → context → analysis (§5), fresh hook type + opening + ending vs history (§7, §9), filler blacklist (§9), Never list (§10), every fact in facts.md. Then the self-audit into history.json: `hook_type`, `opening_line` (exact first sentence), `closing_line` (exact last sentence), `flagged_words_avoided` (confirm 0 banned / repeated words).
