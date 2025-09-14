from pathlib import Path
import re
from mnemonic import Mnemonic

# BIP39 setup
BIP39_FILE = "english.txt"
BIP39_WORDS = Path(BIP39_FILE).read_text().splitlines()
mnemo = Mnemonic("english")

# Load decoded columns file
FILE = "matrix_results/columns_concat_rot13_decoded.txt"
text = Path(FILE).read_text()

def base36_char(c):
    return int(c) if c.isdigit() else 10 + ord(c.upper()) - ord('A')

# Extract pairs and compute coordinates
pairs = re.findall(r'[A-Za-z0-9]{2}', text)
coords = []
for p in pairs:
    row = base36_char(p[0])
    col = base36_char(p[1])
    idx = row * 36 + col
    word = BIP39_WORDS[idx % 2048]
    coords.append((row, col, p, word))

print("[+] Loaded", len(coords), "pairs")

def validate(seq, label):
    phrase = " ".join(seq)
    if mnemo.check(phrase):
        print(f"\n[VALID] {label}: {phrase}")
        return True
    return False

found = False

# Normalize coordinates
rows = [r for r, _, _, _ in coords]
cols = [c for _, c, _, _ in coords]
min_r, max_r = min(rows), max(rows)
min_c, max_c = min(cols), max(cols)

# Build a grid map
grid = {(r, c): w for r, c, _, w in coords}

# Utility: generate a list of positions for a spiral traversal
def spiral_positions():
    positions = []
    r1, r2 = min_r, max_r
    c1, c2 = min_c, max_c
    while r1 <= r2 and c1 <= c2:
        for c in range(c1, c2 + 1):
            positions.append((r1, c))
        for r in range(r1 + 1, r2 + 1):
            positions.append((r, c2))
        if r1 < r2 and c1 < c2:
            for c in range(c2 - 1, c1 - 1, -1):
                positions.append((r2, c))
            for r in range(r2 - 1, r1, -1):
                positions.append((r, c1))
        r1 += 1
        r2 -= 1
        c1 += 1
        c2 -= 1
    return positions

# Utility: snake (row-major but alternate directions)
def snake_positions():
    positions = []
    for r in range(min_r, max_r + 1):
        row_positions = [(r, c) for c in range(min_c, max_c + 1)]
        if (r - min_r) % 2 == 1:
            row_positions.reverse()
        positions.extend(row_positions)
    return positions

# Serpentine (column-major but alternate directions)
def serpentine_positions():
    positions = []
    for c in range(min_c, max_c + 1):
        col_positions = [(r, c) for r in range(min_r, max_r + 1)]
        if (c - min_c) % 2 == 1:
            col_positions.reverse()
        positions.extend(col_positions)
    return positions

# Diagonal sweep
def diagonal_positions():
    positions = []
    for s in range(min_r + min_c, max_r + max_c + 1):
        for r in range(min_r, max_r + 1):
            c = s - r
            if min_c <= c <= max_c:
                positions.append((r, c))
    return positions

# Function to build a sequence from a position list
def seq_from_positions(pos_list):
    return [grid[pos] for pos in pos_list if pos in grid]

# Generate sequences
paths = {
    "spiral": spiral_positions(),
    "snake": snake_positions(),
    "serpentine": serpentine_positions(),
    "diagonal": diagonal_positions(),
}

for label, positions in paths.items():
    seq = seq_from_positions(positions)
    if len(seq) == len(coords):  # All words used
        found |= validate(seq, label)

if not found:
    print("\n[-] No valid mnemonic found in spiral/snake/serpentine/diagonal paths.")
