#!/usr/bin/env python3
import string
from collections import Counter
from itertools import islice

# ——— CONFIG ———
VARIANTS = [
    "diagonals_concat.txt",
    "rows_concat.txt",
    "columns_concat.txt",
    "flip_horizontal_cols_concat.txt",
    "flip_vertical_cols_concat.txt",
    "flip_both_cols_concat.txt",
]
VIG_KEYS = ["rabbit","matrix","split","gibson","causality","thales","rabbitnest","salphaseion"]
TOP_K = 3  # show top 3 for each method

# ——— HELPERS ———
def load(name):
    try:
        return open(name, encoding="utf8").read().strip()
    except FileNotFoundError:
        return None

def score_text(t):
    # simple heuristic: count spaces + common trigrams
    sc = t.count(" ") + t.count("THE")*3 + t.count("AND")*2
    return sc

def rot_n(s, n):
    res = []
    for c in s:
        if c in string.ascii_uppercase:
            res.append(chr((ord(c)-ord('A')+n)%26 + ord('A')))
        else:
            res.append(c)
    return "".join(res)

def atbash(s):
    A = ord('A'); Z = ord('Z')
    res = []
    for c in s:
        if c in string.ascii_uppercase:
            res.append(chr(Z - (ord(c)-A)))
        else:
            res.append(c)
    return "".join(res)

def vigenere(s, key):
    s = s.upper()
    key = key.upper()
    res = []
    ki = 0
    for c in s:
        if c in string.ascii_uppercase:
            shift = ord(key[ki%len(key)])-ord('A')
            res.append(chr((ord(c)-ord('A')-shift)%26 + ord('A')))
            ki += 1
        else:
            res.append(c)
    return "".join(res)

# ——— MAIN ———
if __name__=="__main__":
    for fname in VARIANTS:
        text = load(fname)
        if not text:
            print(f"⚠️  Missing file {fname}, skipping.")
            continue

        print(f"\n\n=== Variant: {fname} ===\n")

        # normalize to uppercase letters and spaces only
        ct = "".join(c for c in text.upper() if c in string.ascii_uppercase+" ")

        # ROT-N
        rot_results = []
        for n in range(1,26):
            pt = rot_n(ct, n)
            rot_results.append((score_text(pt), f"ROT{n}", pt))
        for score, tag, pt in sorted(rot_results, reverse=True)[:TOP_K]:
            print(f"[{tag:5}] score={score:3} → {pt[:100]}…")

        # Atbash
        at = atbash(ct)
        print(f"\n[ATBASH] score={score_text(at):3} → {at[:100]}…")

        # Vigenère
        vig_results = []
        for key in VIG_KEYS:
            pt = vigenere(ct, key)
            vig_results.append((score_text(pt), f"VIG({key})", pt))
        for score, tag, pt in sorted(vig_results, reverse=True)[:TOP_K]:
            print(f"[{tag:12}] score={score:3} → {pt[:100]}…")
