from pathlib import Path
import re
from mnemonic import Mnemonic

# Stage2 offsets (from your analysis)
offsets = [
    0x2c, 0x45, 0xe6, 0x128, 0x193,
    0x226, 0x2a4, 0x2ed, 0x2f3,
    0x366, 0x3b8, 0x3c1, 0x4c6
]

# Compute deltas (might be useful later)
deltas = [j - i for i, j in zip(offsets, offsets[1:])]

# Load BIP39 wordlist
BIP39_FILE = "english.txt"
BIP39_WORDS = Path(BIP39_FILE).read_text().splitlines()
mnemo = Mnemonic("english")

# Extract 18 pairs
FILE = "matrix_results/columns_concat_rot13_decoded.txt"
text = Path(FILE).read_text()

def base36_char(c):
    return int(c) if c.isdigit() else 10 + ord(c.upper()) - ord('A')

pairs = re.findall(r'[A-Za-z0-9]{2}', text)
coords = []
for p in pairs:
    row = base36_char(p[0])
    col = base36_char(p[1])
    idx = row * 36 + col
    word = BIP39_WORDS[idx % 2048]
    coords.append((row, col, p, word))

print("[+] Loaded", len(coords), "pairs")
print("[+] Offsets:", offsets)
print("[+] Deltas:", deltas)

# Sort coordinates by offset rank first, then by (row,col)
# We'll just cycle offsets over the 18 coords
sorted_coords = sorted(
    coords,
    key=lambda x: (offsets[coords.index(x) % len(offsets)], x[0], x[1])
)

ordered_words = [w for _, _, _, w in sorted_coords]
phrase = " ".join(ordered_words)
print("\nCandidate mnemonic:")
print(phrase)

if mnemo.check(phrase):
    print("\n[VALID MNEMONIC FOUND!]")
else:
    print("\n[-] This offset-weighted order did not form a valid mnemonic yet.")
