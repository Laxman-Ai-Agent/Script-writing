# Health rules — the ONLY rule file for Health Decode AND Zumba Fitness scripts

Category **Health** = two channels, one rulebook: **Health Decode** (body, disease, medicine) and **Zumba Fitness** (exercise, dance fitness). Completely separate from Dark World (`dark-world.md`): never use a Dark World rule here, never use a rule from here in a Dark World script. Everything below applies to both channels unless a line says "Health Decode only" or "Zumba only".

**How this file stays clean (maintenance contract):**
- This file is the single source of truth. Each rule lives in exactly ONE place (its section). No dated "corrections" list that stacks old and new.
- A new user rule for Health Decode or Zumba → put it in its section here, and **delete or edit the older line it replaces in the same edit**. Never keep both.
- Example sentences show tone only; never copy them into a script (anti-repetition, §9).
- Learning DB rules: `learning_db.py rules Health` prints only Health Decode + Zumba rules not yet merged here. Fold each into its section, then `learning_db.py mark-merged Health`.
- Built from `sample script/Health-decode.txt`, the user's blueprint (2026-11-20), the Zumba gold sample and user corrections to 2026-11-20. Do not re-read the samples.

---

## 1. Identity and role
- **Goal: EDUCATE, never prescribe.** What the condition (or exercise effect) is, why it happens, how it works inside the body, what to watch for, how it can generally be prevented or managed with safe lifestyle habits.
- Role: an **analytical educator and researcher**: "I read the research and explain it simply", friendly, calm, caring, objective. **Not a doctor** (no "AI డాక్టర్" persona, never present the voice as a doctor) and not a sensational news anchor. Never "నేను చెబుతున్నాను నమ్మండి".
- Audience: ordinary Telugu families, mobile-first, zero background assumed.
- Understanding first: never drop a fact, step, reason or safety line to hit a length; simplify the words only.

## 2. Script flow (6 steps, in this order, long and Short)
1. **Curiosity hook (first 5–10 seconds):** a daily-life question or a myth that makes people curious, never fear (§7).
2. **Simple explanation, "what is it really?":** the normal body first, then what goes wrong, step by step, in plain words. Health Decode: the organ affected and the process, causes and risk factors (with "దీనికి ఒక్క కారణం ఉండదు" balance and "risk factor ఉందంటే తప్పనిసరిగా వస్తుందని కాదు"; separate causes from triggers with a contrast sentence), early and severe symptoms, complications if ignored. Zumba: what happens in the body during the exercise.
3. **Science and official sources:** what WHO / ICMR / NIN / CDC / NIH / Mayo Clinic / a published study says, simply, AND that study's limits. At least one genuine why-it-matters number.
4. **Habits, myths vs facts:** safe everyday habits (నడక, నిద్ర, నీళ్ళు, Indian food: ఇడ్లీ, పప్పు, పెరుగు, చపాతీ, రాగులు, పల్లీలు), what to eat and what to avoid, prevention, myths (§6). Health Decode: the types of treatment that exist, general description only, "Doctor decides which one".
5. **Red flags, "when to see a Doctor?":** usually it's fine, but if these 2–3 danger signs appear, go to the hospital right away (Zumba: stop exercising and see a Doctor). Its own separate paragraph, the most valuable part.
6. **Safe outro:** the spoken disclaimer (§5), then one curiosity question or closing reflection tied to this topic (§9).
Health Decode disease scripts must also contain all 8 parts, each with its reason: causes and risk factors, organ + process, early and severe symptoms, prevention, lifestyle and food (general), treatment types + when to see a Doctor, complications if ignored, myths vs facts. In Shorts keep all 6 steps, shortened.

## 3. Language (Tanglish)
1. **Spoken Telugu (వ్యావహారికం)**, never గ్రాంథికం. Telugu words in Telugu script; English medical / technical terms in **Latin script** (ElevenLabs reads them right). Never an English word in Telugu script.
2. **Capitalise the first letter of every English word in Latin script**, also mid-sentence (Doctor, Treatment, Inhaler, Exercise, Heart Rate, Comments).
3. **English (Latin):** medical, device and body terms people say in English: Doctor, Hospital, Treatment, Control, Inhaler, Steroid, Immune System, Inflammation, Ambulance, Air Pollution, Cigarette, Smoking, Tumor, Tissue Sample, Thyroid, Acidity, Insulin, Metabolism, Symptoms, Research, Blood Sugar, Cholesterol; foods people say in English (Cabbage, Cauliflower); fitness words (Dance, Workout, Cardio, Study). Safe phrases from the blueprint: "Research ప్రకారం", "Help అవ్వొచ్చు".
4. **Telugu** where a common Telugu word exists: సమస్య (problem), సాధారణంగా (normal), ప్రయత్నిస్తే (try), మోతాదు (dose), అధ్యయనం (study), అపోహలు (myths), అవకాశం / ప్రమాదం పెరగొచ్చు (risk), ప్రేరేపించే (trigger), నయం చేసే చికిత్స (cure), నచ్చితే (useful అనిపిస్తే), బలహీనపడటం (weak), నిర్ణయించాలి (decide), వివరంగా (in detail), సుమారుగా (roughly), బిగుతుగా (tight), ఏకాగ్రత, మూత్రం, ప్రమాదాలు (accidents), మంచి నీళ్లు (not safe నీళ్లు), వాహనం నడుపుకుంటూ (drive). Stats and facts in clear standard Telugu: గణాంకాల ప్రకారం (లెక్కల ప్రకారం also fine), జీవించి ఉంటారు, గుర్తిస్తే, నిర్ధారించడానికి, ప్రయోజనం, సంవత్సరాల్లో, పురుషులు / మహిళలు, మరణించారు, తొలగించడం. A medical process word reads better explained in Telugu ("అసలు వ్యాధిని గుర్తించడంలో ఆలస్యం", not "diagnosis ఆలస్యమైంది"); the Telugu disease name where it reads naturally (మూర్ఛ వ్యాధి).
5. **Word forms:** "వీడియో" in Telugu script; "Doctor ను", "Heart కు", "Heart Rate ను" (ను / కు endings); ఆస్పత్రి (not ఆసుపత్రి) or Hospital; the helper takes the patient (తీసుకెళ్లాలి). Liquor = "alcohol" (never "మందు", which also means medicine). Spoken verbs: చెప్తారు / చెప్తుంది (not చెబుతారు), ఉండడం (not ఉండటం), అనుకొని (not అనుకుని), అవ్వగానే, ఇళ్లల్లో, చెయ్యి కదపాలన్నా, గాయమైనా, పక్కనున్న వాళ్ళు, కలిసే వాళ్లు. Separate words: పని చేయడం, సరి చేయడం, అంతే కాదు, చాలా మంది, అంటు వ్యాధి.
6. Acronyms letter by letter with spaces: W H O, G E R D, P P I s.
7. Use the full term ("Blood Sugar", not just "Sugar"); "లేదా" between options, not a comma list. Name the subject explicitly in section openers and key lines ("మరి lung cancer ఎందుకు వస్తుంది?").
8. Define every medical term right away: "X అంటే …". Everyday analogies (bone marrow = రక్తం తయారయ్యే factory, insulin = తాళం చెవి, clot = పైపులో గడ్డ). Replace metaphors like "రక్షణ కవచం" with the plain meaning.

## 4. Numbers
- Every whole number in Telugu words, never digits: యాభై, పంతొమ్మిది, ఎనభై శాతం, నాలుగు కోట్లు, రెండు వేల పంతొమ్మిది.
- Number and unit in the SAME language: "మూడు గంటలకు", "పది నిమిషాల్లో" (default) or "ten minutes లో" inside English-heavy wording. Never "మూడు hours", never digits.
- A number inside an English term = English word, Latin: "Type two Diabetes" (not Type 2, not టైప్ టూ). Decimals: zero point five.

## 5. Safety (strict red lines — zero tolerance)
- **No cure guarantee:** never "పూర్తిగా పోతుంది", "మూడు రోజుల్లో కరిగిపోతుంది", "Cancer cure", "మందులు అవసరం లేదు". Home tips, foods and supplements do not replace treatment; say so.
- **No medicine names or doses:** only the general category ("reliever inhaler", "controller inhaler"); never a tablet name, a dose, how much to take, "ఈ tablet వేసుకోండి" or "ఈ treatment తీసుకోండి".
- **No stop-medicine advice**, ever ("Tablets ఆపేయండి" = demonetization risk). Right: "మీరు ఇప్పటికే medicines వాడుతుంటే, వాటికి తోడుగా Doctor సలహాతో ఈ diet follow అవ్వొచ్చు."
- **No diagnosis:** never "ఈ symptoms ఉంటే మీకు X ఉన్నట్టే". Right: "ఇది X కి ఒక symptom అవ్వొచ్చు. Exact కారణం తెలియాలంటే Doctor ను కలవాలి." Correct over-generalising ("కాలు ఉబ్బింది కదా అని అది ఖచ్చితంగా ఫైలేరియానే అని అనుకోకూడదు").
- **No fear / hype / clickbait:** Silent Killer, ప్రమాదకరం, చనిపోతారు, Red Alert, రాక్షసుడు, నిజమా?, అసలు నిజం, షాకింగ్, "డాక్టర్లు దాచే నిజం", "మీరు danger లో ఉన్నారు". Soften drama ("గాలి కోసం పోరాడుతోంది" → "గాలి కోసం ఇబ్బంది పడుతోంది"). Right: "ఈ food ని ఎక్కువగా తీసుకోవడం వల్ల Cholesterol పెరిగే అవకాశం ఉందని I C M R guidelines చెప్తున్నాయి."
- **No unsourced numbers:** only WHO, CDC, NIH, NHS, ICMR, NIN, AIIMS, GINA, Mayo Clinic or similar top bodies / published studies. Never invent a study, statistic or organisation; unsure → "ధృవీకరించుకోవాలి" in facts.md and leave it out.
- **Hedge outcomes** with safe words: "Help అవ్వొచ్చు", "Research ప్రకారం", "సాధారణంగా", "చాలా మందిలో", "రావచ్చు", "ప్రమాదం పెరగొచ్చు". Certainty matches facts.md.
- **Advice and emergency steps in duty form**, short, one action each: "Ambulance కి Call చేయాలి", "వెంటనే ఆపి Doctor ను సంప్రదించాలి", "ఏ మాత్రం ఆలస్యం చేయకూడదు". Flag key safety advice ("ముఖ్యంగా గుర్తుంచుకోండి." / "అయితే ఒక విషయం గుర్తుంచుకోండి." — vary it).
- **Spoken disclaimer, always, at the end before the closing question:** two sentences with this meaning: educational / general awareness only + see your Doctor before any health decision. Base wording: "ఈ వీడియో educational purpose కి మాత్రమే. మీ health గురించి ఎలాంటి నిర్ణయాలు తీసుకున్నా ముందుగా మీ Doctor ను సంప్రదించండి." Rephrase it each script (Zumba e.g. "మీ ఆరోగ్య పరిస్థితికి ఏ Exercise సరైనదో Doctor మాత్రమే సూచించగలరు.") so no two recent scripts share the same disclaimer sentence.
- Sensitive topics (periods, reproduction, sexual health): factual, respectful, normalising ("ఇది వ్యాధి కాదు, సహజమైన ప్రక్రియ"). No jokes.

## 6. Explanation moves
- **Fact → real-world context → grounded analysis** for every major point: the fact, then the Indian context (diet, budget, daily routine, real usability) or the study's limit, then a calm view ("ఈ number ఆకర్షణీయంగా కనిపించినా, సామాన్యులకు ఇది ఎంతవరకు ఉపయోగపడుతుందో చూడాలి"). The view comes from facts.md only.
- Stat paragraph: who / what study, then the number, then the verdict ("CDC గణాంకాల ప్రకారం, ఈ స్థాయి శ్రమ Vigorous Exercise కిందకు వస్తుంది.").
- **Myths, flowing, never "అపోహ: / వాస్తవం:" labels** (two shapes, rotate): (a) "…అని అనుకోవడం పొరపాటు. ఎందుకంటే … కానీ ఈ పరిస్థితిని నిర్లక్ష్యం చేస్తే, భవిష్యత్తులో … వచ్చే అవకాశం ఉంటుంది." + a source line; (b) "అయితే X ని అచ్చంగా Y అని అనుకోకూడదు. ఎందుకంటే … అంటే ఇది …".
- Inner dialogue of the body ("Brain కి ఇప్పుడు నాకు ముప్పై తొమ్మిది డిగ్రీలు కావాలి అనిపిస్తుంది"); pre-empt the viewer's doubt ("మరి మీకు ఒక doubt రావొచ్చు"); voice the viewer's own picture.
- Explain fully, no shorthand: after a list of body changes add one result line; give each consequence its effect.
- A direct question to the viewer only at natural turning points (roughly every 300–400 words), then carry on with the answer.
- Scenario character = an unnamed relatable person. 5-minute shape ≈ 8 fuller paragraphs of 5–7 sentences; related proofs merged, side topics cut.

## 7. Openings (hook)
- **No fixed intro.** Start directly with a fresh, topic-specific hook. Never "ఈ video లో మనం … తెలుసుకుందాం / చూద్దాం" intro lines, never "తెలుసుకోబోతున్నాం", never "ఒక్కసారి ఊహించుకోండి".
- Curious, accurate, never scary; science-first questions about what happens in the body, never superstition guesses (దెయ్యం పట్టిందా?).
- **Hook type** (rotate; never the type of the previous 4 scripts of this channel): **A** surprising data point / study result, **B** relatable everyday Indian habit / scenario ("మీలో చాలా మంది తిన్న వెంటనే నీళ్ళు తాగుతుంటారు"), **C** misconception vs reality, **D** "what happens inside the body when…" preview, **E** short real-world case / comparison.
- Shapes to draw from (vary): everyday sighting ("ఎవరికైనా ఒక్క కాలు మాత్రమే ఉబ్బిపోయి ఉండటం చూశారా?"), fear → understanding, known-but-unknown, series continuation (Part 2), topic question + "లేక …?" alternative + "బయటకు చూస్తే … కానీ …" (Zumba). The old signature "తెలీదు కదూ, ఐతే నేను చెప్తా" at most once in 20 scripts.

## 8. Sentences and TTS (ElevenLabs)
- Connected paragraphs, blank line between; full flowing sentences joined by connectors (అంతే కాదు, అయితే, ఎందుకంటే, అంటే, కానీ). Mix crisp ~6-word sentences with ~18-word explanations; split long comma-joined statements.
- Every sentence complete with its verb: no "అదే పొగ." / "అంతే." fragments; explicit section transitions as full sentences ("ఇక దీని లక్షణాల గురించి చూద్దాం", worded fresh).
- **No "…" anywhere**, no quote marks around reported speech.
- **Commas:** a breath comma after a transition word, a dramatic turn and "X ప్రకారం," ("CDC గణాంకాల ప్రకారం, …"). No comma after the subject, none around a list of names, none before the main clause after a short condition.
- No stacked suffixes or heavy compounds; spoken contractions (ఏంటంటే, జరుగుతుందని, కదూ).

## 9. Endings, CTA and anti-repetition
- The last line = a topic-specific closing reflection or ONE sharp question tied to this topic (Zumba: also fine to end on one payoff line, "చూడటానికి Dance లా కనిపించినా, …").
- **No generic closings:** no "Like కొట్టండి", "Subscribe చేయండి", "Comment లో చెప్పండి", "Share చేయండి" formulas, no keyword-to-DM line.
- **Mid-video subscribe:** Health Decode only, at most one short line at a natural turn (e.g. just before a key reveal), worded fresh. **Zumba: no subscribe, no share line.** Each channel names only itself, never the other.
- A series may end with a next-part teaser ("… అదే Part 2 లో చూద్దాం").
- **Never repeat** (`learning_db.py history-last health` / `zumba` shows the last 20): the hook type of the last 4; the first-sentence structure or first 10 words of the last 20; the ending or disclaimer sentence of the last 20; the wording of any example sentence in this file or a Learning DB rule.
- **Filler blacklist, at most once each per script:** "అసలు…?", "అంతేకాకుండా", "నిజానికి", "ఇక్కడ ముఖ్యమైన విషయం ఏంటంటే". Other connectors at most ~2 each per 300 words.

## 10. Never
- Everything in §5. Bullets, headings, labels, emoji, timestamps, "Visual" / "Text on screen" lines, captions or b-roll cues inside the narration (if visuals are ever mentioned: 2D/3D organ animation only, no blood, surgery or scary scenes — never in script.txt).
- Digits, "…", English in Telugu script, stacked suffixes, stronger certainty than the facts, anything not in facts.md.

## 11. facts.md extras (research step)
`## Myths vs facts` (✅/❌ lines), `## Hook ideas` (5, curious but accurate, not scary, no cure claim), `## Description sources` (approved bodies only, with URLs), plus the study limits found.

## 12. Gold samples (style only, never a fact source)
- Myth paragraph (Health Decode, user-written): "Sugar Report Normal గా ఉంటే ఎలాంటి సమస్యా లేనట్టే అని అనుకోవడం పొరపాటు. ఎందుకంటే Pancreas ఎక్కువ కష్టపడి పనిచేస్తున్నంత కాలం Blood Sugar Normal గానే కనిపించవచ్చు. కానీ ఈ పరిస్థితిని నిర్లక్ష్యం చేస్తే, భవిష్యత్తులో Prediabetes లేదా Type two Diabetes వచ్చే అవకాశం ఉంటుంది. CDC గణాంకాల ప్రకారం, అమెరికాలోనే సుమారు నాలుగు కోట్ల మందికి Diabetes ఉంది."
- Zumba full script (user-written): `output/2026-11-19-zumba-hiit-cardio/script-reel.txt` — its ending formula is the OLD style (§9).
- Blueprint pairs (❌ → ✅): "పసుపు నీళ్ళు తాగితే diabetes cure అవుతుంది." → "Research ప్రకారం Turmeric లో ఉండే Curcumin Blood Sugar Control కి కొంత Help అవ్వొచ్చు. కానీ ఇది Tablets కి replacement మాత్రం కాదు." / "నిద్ర పట్టకపోతే మీకు Sleep Apnea ఉన్నట్టే." → "మీకు regular గా నిద్రలో ఇబ్బంది ఉంటే, ఇది Sleep Apnea కి ఒక Symptom అవ్వొచ్చు. Exact కారణం తెలియాలంటే Doctor ను కలవాలి."

## 13. Title line
First line of script.txt = metadata (not narrated): the topic as a plain curiosity question, optional "| keywords". Emojis only in the title.

## 14. Length (ESTIMATE ~150 words/min; recalibrate when the user reports a real recorded duration)
40s ~100 · 50s ~125 · 1 min ~150 · 1.5 min ~225 · 2 min ~300 · 3 min ~450 · 5 min ~750 · 7–8 min ~1,050–1,200 · 10–12 min ~1,500–1,800 (chapters) · 15–20 min ~2,250–3,000 · 30 min ~4,500 (chapter by chapter). A rough guide only: longer is fine when the topic needs it (all 6 steps, all 8 parts); trim only repetition and filler.

## 15. Final check (run before delivering; fix with targeted edits until all ✅; interactive: show it as one ✅ line)
1. Hook — curious, accurate, fresh hook type and wording (§7, §9). 2. Flow — 6 steps in order; red flags in their own paragraph (§2). 3. Health Decode content — all 8 parts with reasons. 4. Simplicity — everyday words, every term explained (§3). 5. TTS — numbers in words, no "…", commas, no stacked suffixes (§4, §8). 6. Sources — at least one approved source + its limit + one why-it-matters number, all in facts.md (§5). 7. Safety — no cure, medicine name, dose, stop-medicine, diagnosis, fear word or unsourced number; Doctor decides treatment (§5). 8. Disclaimer — spoken, two sentences, not a repeat. 9. Ending — topic-specific, no generic CTA, not a repeat; filler blacklist ≤ 1 each (§9).
Then the self-audit into history.json: `hook_type`, `opening_line` (exact first sentence), `closing_line` (exact last sentence), `flagged_words_avoided` (confirm 0 banned / repeated words).
