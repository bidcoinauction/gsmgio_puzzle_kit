from pathlib import Path
import re
from mnemonic import Mnemonic

BIP39_FILE = "english.txt"
BIP39_WORDS = Path(BIP39_FILE).read_text().splitlines()
mnemo = Mnemonic("english")

FILE = "matrix_results/columns_concat_rot13_decoded.txt"
text = Path(FILE).read_text()

def base36_char(c):
    return int(c) if c.isdigit() else 10 + ord(c.upper()) - ord('A')

# Extract pairs
pairs = re.findall(r'[A-Za-z0-9]{2}', text)
if len(pairs) != 18:
    print(f"[!] Expected 18 pairs, found {len(pairs)}")

# Compute row/col and corresponding word
coords = []
for p in pairs:
    row = base36_char(p[0])
    col = base36_char(p[1])
    idx = row * 36 + col
    word = BIP39_WORDS[idx % 2048]
    coords.append((row, col, p, word))

print("[+] Pairs with coords:")
for r, c, p, w in coords:
    print(f"{p} -> row={r}, col={c}, word={w}")

def validate(seq, label):
    phrase = " ".join(seq)
    if mnemo.check(phrase):
        print(f"\n[VALID] {label}: {phrase}")
        return True
    return False

found = False

# 1. Row-major (sort by row, then col)
row_major = sorted(coords, key=lambda x: (x[0], x[1]))
row_words = [w for _, _, _, w in row_major]
found |= validate(row_words, "row-major (row,col)")

# 2. Column-major (sort by col, then row)
col_major = sorted(coords, key=lambda x: (x[1], x[0]))
col_words = [w for _, _, _, w in col_major]
found |= validate(col_words, "column-major (col,row)")

# 3. Diagonal order based on (row+col)
diag_major = sorted(coords, key=lambda x: (x[0] + x[1], x[0]))
diag_words = [w for _, _, _, w in diag_major]
found |= validate(diag_words, "diagonal (row+col)")

if not found:
    print("\n[-] No valid mnemonic found using coordinate-based orderings.")
