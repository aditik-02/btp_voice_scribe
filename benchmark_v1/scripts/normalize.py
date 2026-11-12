"""Shared text normalisation for Voice Scribe ASR scoring (apply to BOTH reference and hypothesis).
Rules (v1, fixed 2026-10-25):
  - drop transcriber tags (<UNIN/>, <UNSURE>..</UNSURE> keeps inner words), bracketed sound tags
  - lowercase; unify apostrophes; strip punctuation except intra-word ' and -  ; hyphens -> space
  - remove fillers: um, uh, erm, er, hmm, mm, mhm, ah, uhm, hm
  - numbers are kept as written (no digit<->word conversion yet; revisit when scoring Eka dosages)
"""
import re
FILLERS = {"um","uh","erm","er","hmm","mm","mhm","ah","uhm","hm","mmm","umm","uhh"}
def clean_tags(t: str) -> str:
    t = re.sub(r"<UNIN\s*/>", " ", t)
    t = re.sub(r"</?UNSURE>", " ", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\[[^\]]*\]", " ", t)
    return re.sub(r"\s+", " ", t).strip()
def normalize(t: str) -> str:
    t = clean_tags(t).lower().replace("’", "'").replace("‘", "'")
    t = re.sub(r"(?<=\w)-(?=\w)", " ", t)
    t = re.sub(r"[^\w\s']", " ", t)
    t = re.sub(r"(^|\s)'|'(\s|$)", " ", t)
    return " ".join(w for w in t.split() if w not in FILLERS)


# ---------------------------------------------------------------------------------------------
# Scoring rule v2 (proposed after the EDA, decided on the dev split). Opt-in: score.py --norm v2
#   1. split numbers from units:          "40Mg" -> "40 mg"
#   2. one form per unit:                 milligram(s) -> mg, millilitre/milliliter(s) -> ml,
#                                         microgram(s) -> mcg, gram(s) -> g
#   3. number words -> digits:            "five hundred" -> "500", "two point five" -> "2.5"
#   4. once / twice / thrice and dosing abbreviations (OD, BD, TDS...) are left unchanged
# ---------------------------------------------------------------------------------------------
_UNITS = {"milligram": "mg", "milligrams": "mg", "mgs": "mg", "millilitre": "ml", "millilitres": "ml",
          "milliliter": "ml", "milliliters": "ml", "mls": "ml", "microgram": "mcg", "micrograms": "mcg",
          "gram": "g", "grams": "g", "gm": "g", "gms": "g"}
_ONES = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
         "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
         "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19}
_TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
_SCALES = {"hundred": 100, "thousand": 1000, "lakh": 100000, "lakhs": 100000}
_NUMWORDS = set(_ONES) | set(_TENS) | set(_SCALES)

def _words_to_number(ws):
    """['five','hundred','and','twenty'] -> 520; returns None if not a clean number phrase."""
    total, cur = 0, 0
    for w in ws:
        if w in _ONES: cur += _ONES[w]
        elif w in _TENS: cur += _TENS[w]
        elif w == "hundred": cur = max(cur, 1) * 100
        elif w in _SCALES: total += max(cur, 1) * _SCALES[w]; cur = 0
        elif w == "and": continue
        else: return None
    return total + cur

def _numbers_to_digits(words):
    out, i = [], 0
    while i < len(words):
        if words[i] in _NUMWORDS:
            j = i
            while j < len(words) and (words[j] in _NUMWORDS or (words[j] == "and" and j + 1 < len(words) and words[j + 1] in _NUMWORDS and j > i)):
                j += 1
            n = _words_to_number(words[i:j])
            # "point five" decimals: "two point five" -> 2.5
            if n is not None and j + 1 < len(words) and words[j] == "point" and words[j + 1] in _ONES:
                k = j + 1; dec = ""
                while k < len(words) and words[k] in _ONES and _ONES[words[k]] < 10: dec += str(_ONES[words[k]]); k += 1
                out.append(f"{n}.{dec}"); i = k; continue
            if n is not None: out.append(str(n)); i = j; continue
        out.append(words[i]); i += 1
    return out

def normalize_v2(t: str) -> str:
    t = clean_tags(t).lower().replace("’", "'").replace("‘", "'")
    t = re.sub(r"(\d)\s*(mg|mcg|ml|gm|g|iu)\b", r"\1 \2", t)          # 40mg -> 40 mg (before punctuation strip)
    t = re.sub(r"(?<=\d)\.(?=\d)", "DECIMALPOINT", t)                   # keep 12.5 intact
    t = re.sub(r"(?<=\w)-(?=\w)", " ", t)
    t = re.sub(r"[^\w\s']", " ", t).replace("DECIMALPOINT".lower(), ".").replace("DECIMALPOINT", ".")
    t = re.sub(r"(^|\s)'|'(\s|$)", " ", t)
    words = [_UNITS.get(w, w) for w in t.split() if w not in FILLERS]
    return " ".join(_numbers_to_digits(words))

NORMALIZERS = {"v1": normalize, "v2": normalize_v2}
