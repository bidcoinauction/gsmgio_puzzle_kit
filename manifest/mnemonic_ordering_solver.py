from mnemonic import Mnemonic
from pathlib import Path
import re

# Load English BIP39 wordlist
BIP39_FILE = "english.txt"
BIP39_WORDS = Path(BIP39_FILE).read_text().splitlines()
mnemo = Mnemonic("english")

# File with column variant (rot13 decoded)
FILE = "matrix_results/columns_concat_rot13_decoded.txt"
text = Path(FILE).read_text()

def base36_char(c):
    return int(c) if c.isdigit() else 10 + ord(c.upper()) - ord('A')
def pair_to_base36(p):
    return base36_char(p[0]) * 36 + base36_char(p[1])

# Extract pairs and convert
pairs = re.findall(r'[A-Za-z0-9]{2}', text)
indices = [pair_to_base36(p) for p in pairs]
words = [BIP39_WORDS[i % 2048] for i in indices]

print(f"[+] Extracted {len(words)} words:")
print(" ".join(words))

def check_sequence(seq, label):
    phrase = " ".join(seq)
    if mnemo.check(phrase):
        print(f"[VALID] {label}: {phrase}")
        return True
    return False

found = False

# 1. Original order
print("\n[Testing original order]")
found |= check_sequence(words, "original")

# 2. Sort by index ascending
sorted_by_index = [w for _, w in sorted(zip(indices, words))]
print("\n[Testing index-sorted order]")
found |= check_sequence(sorted_by_index, "sorted by index")

# 3. Reverse sort
reverse_sorted = [w for _, w in sorted(zip(indices, words), reverse=True)]
print("\n[Testing reverse index-sorted order]")
found |= check_sequence(reverse_sorted, "reverse sorted")

# 4. Attempt simple 3-row grid (6 words per row)
# Try row-major and column-major orders
if len(words) in (12, 18, 24):
    cols = 6
    rows = len(words) // cols
    grid = [words[i*cols:(i+1)*cols] for i in range(rows)]

    # Row-major
    flat_row = [w for r in grid for w in r]
    print("\n[Testing 3x6 row-major]")
    found |= check_sequence(flat_row, "3x6 row-major")

    # Column-major
    flat_col = [grid[r][c] for c in range(cols) for r in range(rows)]
    print("\n[Testing 3x6 column-major]")
    found |= check_sequence(flat_col, "3x6 column-major")

    # Diagonal (simple top-left to bottom-right)
    diag_order = []
    for s in range(rows+cols-1):
        for r in range(rows):
            c = s - r
            if 0 <= c < cols:
                diag_order.append(grid[r][c])
    print("\n[Testing 3x6 diagonal]")
    found |= check_sequence(diag_order, "3x6 diagonal")

if not found:
    print("\n[-] No valid mnemonic found in these structured arrangements.")
