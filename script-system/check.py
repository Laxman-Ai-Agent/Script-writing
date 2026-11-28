"""Rule checker for finished scripts. Banned words are read live from the channel's 06-banned-words.md,
so a word added there is enforced at once (no second list to keep in sync).

Usage:  python script-system/check.py <health|zumba|dark> <script.txt> [...]   exit 1 on any problem
        python script-system/check.py selftest
"""
import re, sys
from pathlib import Path

RULES = Path(__file__).parent / "rules"
FOLDER = {"health": "health-decode", "zumba": "zumba-fitness", "dark": "dark-world"}
CITE = {"health": r"W-H-O|I-C-M-R|C-D-C|N-I-H", "zumba": r"W-H-O|I-C-M-R|C-D-C|N-I-H|A-C-S-M"}
RAW_ACRONYMS = r"\b(WHO|ICMR|CDC|NIH|ACSM|NASA|ISRO|ESA|CERN|NOAA|IMD)\b"


def banned(ch):
    """(hard_ban_terms, limited_terms) from 06-banned-words.md."""
    hard, limited = set(), set()
    for line in (RULES / FOLDER[ch] / "06-banned-words.md").read_text(encoding="utf-8").splitlines():
        if not line.startswith("- ") and not line.startswith("  `"):
            continue
        if "Limited Frames" in line:
            limited.update(t.strip(". ") for t in re.findall(r"`([^`]+)`", line))
            continue
        if "→" in line:
            left = line[2:].split("→")[0]
            if "వద్దు" in left:                       # Part A2: - `X` వద్దు → ...
                hard.update(re.findall(r"`([^`]+)`", left))
            elif "`" not in left:                      # sections 1..: - X / Y → ...
                hard.update(w.strip() for w in left.split("/") if w.strip() and "(" not in w)
            continue
        if "`" in line:                                # Part A1 NEVER USE lists
            hard.update(t for t in re.findall(r"`([^`]+)`", line) if "..." not in t)
    return {t for t in hard if len(t) > 1}, limited


def check(ch, text):
    hard, limited = banned(ch)
    bad = []
    if re.search(r"\d", text):
        bad.append("digits: " + ", ".join(sorted(set(re.findall(r"\S*\d\S*", text)))[:6]))
    for t in sorted(hard):
        if t.isascii():
            hit = re.search(rf"\b{re.escape(t)}\b", text, re.I)
        elif len(t) <= 3:  # short Telugu word (అంట, వల) must stand alone, not inside అంటే / వల్ల
            hit = re.search(rf"(?<![ఀ-౿]){re.escape(t)}(?![ఀ-౿])", text)
        else:
            hit = t in text
        if hit:
            bad.append(f"banned: {t}")
    bad += [f"limited x{text.count(t.strip('.'))}: {t}" for t in limited if text.count(t.strip(".")) > 1]
    glued = re.findall(r"[A-Za-z]+‌?[ఀ-౿]+", text)
    if glued:
        bad.append("no space after English: " + ", ".join(sorted(set(glued))[:6]))
    if re.search(RAW_ACRONYMS, text):
        bad.append("acronym without hyphens")
    if ch in CITE and not re.search(CITE[ch], text):
        bad.append("no voice citation")
    if re.search(r"[\[\]#*•]|[\U0001F300-\U0001FAFF☀-➿]", text):
        bad.append("markdown/emoji")
    return bad


def selftest():
    for ch in FOLDER:
        hard, _ = banned(ch)
        assert len(hard) > 30, (ch, len(hard))
    assert any("banned" in b for b in check("health", "ఛాతీ లో W-H-O")), "06 word not enforced"
    assert check("health", "Cellsలో 37 WHO") and not check("health", "Cells లో W-H-O ప్రకారం ముప్పై ఏడు.")
    assert any("హత్య" in b for b in check("dark", "అక్కడ హత్య జరిగింది."))
    assert not any("banned" in b for b in check("dark", "అంటే దాని వల్ల ఇలా జరుగుతుంది."))
    lim = check("health", "ఇప్పుడు తెలుసుకుందాం. ఇప్పుడు తెలుసుకుందాం. W-H-O")
    assert any("limited" in b for b in lim) and not any("banned" in b for b in lim), lim
    assert not check("dark", "సింపుల్‌గా చెప్పాలంటే ఇదే.")  # Limited Frame once = OK
    print("selftest OK", {ch: len(banned(ch)[0]) for ch in FOLDER})


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["selftest"]:
        selftest(); sys.exit(0)
    if len(a) < 2 or a[0] not in FOLDER:
        sys.exit(__doc__)
    rc = 0
    for f in a[1:]:
        b = check(a[0], Path(f).read_text(encoding="utf-8"))
        print(f, "OK" if not b else b)
        rc |= bool(b)
    sys.exit(rc)
