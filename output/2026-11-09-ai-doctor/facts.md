# AI Doctor (AI in healthcare) — Health Decode, 5 min + 1 min
Source draft = user-pasted Telugu script (≈10 min). Each claim in it re-checked 2026-11-09. Draft claims that failed are listed at the bottom.

## Verified claims used
- India doctor:population = 1:811 (govt estimate to Lok Sabha, 2024–25; NMC: 13,86,157 registered allopathic doctors; counts AYUSH too and assumes 80% availability) — https://www.etvbharat.com/en/!health/doctor-population-ratio-in-india-is-estimated-to-be-1-811-centre-enn25080105862 — high (it is the govt's own estimate; method is debated)
- Doctors concentrated in cities, rural access to specialists is weak — general/widely reported, not individually sourced — medium
- Google lung-cancer CT model: AUC 94.4% (6,716 NLST cases); vs 6 radiologists, no prior scan: −11% false positives, −5% false negatives; with prior scan: on par. Retrospective, not live use — Ardila et al., Nature Medicine, May 2019 — https://research.google/pubs/end-to-end-lung-cancer-screening-with-three-dimensional-deep-learning-on-low-dose-chest-computed-tomography/ — high
- MASAI trial (Sweden), Lancet Digital Health, Feb 2025: 105,934 women randomised; AI-supported mammography found 6.4 vs 5.0 cancers per 1,000 (~29% more); screen-reading workload ~44% lower; no increase in false positives per authors — https://pubmed.ncbi.nlm.nih.gov/39904652/ — high
- Microsoft MAI-DxO (June 2025 preprint): 85.5% of 304 NEJM cases solved vs mean 20% for 21 physicians (5–20 yrs experience, US/UK). Past, complex teaching cases; physicians worked without colleagues/references; not tested on real patients. Later peer-reviewed version reports ~83% vs 22–36% — https://microsoft.ai/news/the-path-to-medical-superintelligence/ — medium (numbers differ by version)
- Google/Verily diabetic-retinopathy AI tested at Aravind (Madurai) and Sankara Nethralaya; performed on par with general ophthalmologists; India has ~70 million people with diabetes and too few eye specialists to screen them — https://blog.verily.com/2019/02/launching-powerful-new-screening-tool.html , https://about.google/stories/seeingpotential — high
- AI-discovered molecules: Phase I success 80–90% (BCG-linked analysis, Drug Discovery Today 2024); sample only ~two dozen molecules; Phase II ~40% (similar to average); no AI-discovered drug fully approved yet at time of source — https://www.htworld.co.uk/news/ai/ai-discovered-drugs-achieved-higher-success-rate-than-those-by-humans-study/ — medium (small sample)
- India ≈ one-fifth of world's generic medicine supply by volume (IBEF/ORF, repeated; no primary dataset) — https://ibef.org/industry/indian-pharmaceuticals-industry-analysis-presentation — medium
- AI-in-healthcare market 2030 forecasts range ~US$110B to ~$346B (definitions differ) — https://marketsandmarkets.com/Market-Reports/artificial-intelligence-healthcaremarket-54679303.html — disputed → NOT used as a single number

## Imagined (labelled as imagination in script)
- Lakshmi, 58, village, chest discomfort → app advice → PHC ECG → referral. Hypothetical, not a real case or product.

## Draft claims REMOVED / CORRECTED
| Draft said | Problem | Now |
|---|---|---|
| 5,000 people per doctor in India | Govt estimate is 1:811 (contested but not 1:5000) | 1:811 + uneven distribution |
| WHO standard 1 doctor / 1,000 | WHO told The Hindu it does not recommend such a ratio; figure comes from MCI "Vision 2015" | dropped the "WHO standard" |
| Rural: 10,000 people, not even one doctor | no source | dropped |
| Lung cancer AI 94% vs radiologists 65% | 94.4% is AUC, not accuracy; radiologist 65% not in paper | replaced with real comparison above |
| Breast cancer AI 91% vs radiologists 74% | no source found | replaced with MASAI |
| AI cuts medical errors 85% | no source | dropped |
| AI detected lung cancer a year earlier than radiologists | not verified | dropped |
| Aidoc in 900+ hospitals | only "300+ medical centres" (Jan 2020) found | dropped the number |
| Drug time/cost down 30–50% | no primary source | replaced with BCG Phase I figure, hedged |
| Market $188B by 2030, $45.2B in 2026, 44.9% CAGR | forecasts conflict widely | dropped |
| US saves $200–360B | not verified in this pass | dropped |
| India AI health value $30B; 1.5M engineers; 1.8 lakh doctors/yr | no source | dropped |
| Healthcare = $650B economy | irrelevant to topic | dropped |
| "2030: everyone has AI doctor on phone" | prediction, overclaim | dropped |
| "Take dad to hospital before chest pain starts" | medically misleading | replaced with "don't wait for an app — go to hospital / call ambulance" |
| AI detects skin cancer from phone photo | not verified | dropped |

## Angle
- Core insight: AI doctor = software that gives doctors a second pair of eyes; real evidence is strong in screening (mammograms, CT, eye scans) but mostly from studies, not yet everywhere; it supports, never replaces, a doctor.
- Misconception: "AI doctor = robot" / "AI beats doctors".
