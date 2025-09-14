from pathlib import Path
import re
from mnemonic import Mnemonic

# Load BIP39 wordlist
BIP39_FILE = "english.txt"
BIP39_WORDS = Path(BIP39_FILE).read_text().splitlines()
mnemo = Mnemonic("english")

FILE = "matrix_results/columns_concat_rot13_decoded.txt"
text = Path(FILE).read_text()

def base36_char(c):
    return int(c) if c.isdigit() else 10 + ord(c.upper()) - ord('A')

def pair_to_base36(p):
    return base36_char(p[0]) * 36 + base36_char(p[1])

# Extract alphanumeric pairs
pairs = re.findall(r'[A-Za-z0-9]{2}', text)
if len(pairs) != 18:
    print(f"[!] Warning: Expected 18 pairs, found {len(pairs)}")
print("[+] Pairs:", pairs)

# Convert to base36 numeric values and words
values = [pair_to_base36(p) for p in pairs]
words = [BIP39_WORDS[v % 2048] for v in values]

print("\nExtracted words:")
print(" ".join(words))

def validate(seq, label):
    phrase = " ".join(seq)
    if mnemo.check(phrase):
        print(f"\n[VALID] {label}: {phrase}")
        return True
    return False

found = False

# 1. Ascending by base36 value
asc_words = [w for _, w in sorted(zip(values, words))]
found |= validate(asc_words, "ascending base36")

# 2. Descending
desc_words = [w for _, w in sorted(zip(values, words), reverse=True)]
found |= validate(desc_words, "descending base36")

# 3. Treat as coordinates in 3×6 grid
# Split the sorted list into 3 rows × 6 columns
if len(words) == 18:
    # Sort ascending by value first for coordinate mapping
    sorted_pairs = sorted(zip(values, words))
    sorted_words = [w for _, w in sorted_pairs]
    rows, cols = 3, 6
    grid = [sorted_words[i*cols:(i+1)*cols] for i in range(rows)]

    # Row-major
    flat_row = [w for r in grid for w in r]
    found |= validate(flat_row, "3x6 row-major")

    # Column-major
    flat_col = [grid[r][c] for c in range(cols) for r in range(rows)]
    found |= validate(flat_col, "3x6 column-major")

    # Diagonal order
    diag_order = []
    for s in range(rows + cols - 1):
        for r in range(rows):
            c = s - r
            if 0 <= c < cols:
                diag_order.append(grid[r][c])
    found |= validate(diag_order, "3x6 diagonal")

if not found:
    print("\n[-] No valid mnemonic found in these structured arrangements.")
