import math
import re
from pathlib import Path
from mnemonic import Mnemonic

# Offsets (from ASCII sequence analysis)
offsets = [0x2c, 0x45, 0xe6, 0x128, 0x193, 0x226, 0x2a4,
           0x2ed, 0x2f3, 0x366, 0x3b8, 0x3c1, 0x4c6]
deltas = [j - i for i, j in zip(offsets, offsets[1:])]

# BIP39
BIP39_FILE = "english.txt"
BIP39_WORDS = Path(BIP39_FILE).read_text().splitlines()
mnemo = Mnemonic("english")

# Extract pairs
FILE = "matrix_results/columns_concat_rot13_decoded.txt"
text = Path(FILE).read_text()

def base36_char(c):
    return int(c) if c.isdigit() else 10 + ord(c.upper()) - ord('A')

pairs = re.findall(r'[A-Za-z0-9]{2}', text)
coords = []
for p in pairs:
    r = base36_char(p[0])
    c = base36_char(p[1])
    idx = r * 36 + c
    word = BIP39_WORDS[idx % 2048]
    coords.append((r, c, p, word))

print("[+] Starting delta-walk path solver with", len(coords), "nodes")
print("[+] Deltas:", deltas)

# Distance functions
def manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def euclidean(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def build_path(start_index):
    """Construct a path using deltas as a heuristic for nearest distances."""
    unused = list(range(len(coords)))
    path = [start_index]
    unused.remove(start_index)

    for d in deltas:
        if not unused:
            break
        current = coords[path[-1]]
        current_pos = (current[0], current[1])
        # Compute distances from current to all unused
        distances = [(abs(manhattan(current_pos, (coords[u][0], coords[u][1])) - d), u)
                     for u in unused]
        # Pick closest match
        distances.sort(key=lambda x: x[0])
        next_node = distances[0][1]
        path.append(next_node)
        unused.remove(next_node)

    # Append any remaining nodes arbitrarily
    path.extend(unused)
    return path

found = False

# Try all starting nodes
for start in range(len(coords)):
    order = build_path(start)
    words = [coords[i][3] for i in order]
    phrase = " ".join(words)
    if mnemo.check(phrase):
        print("\n[VALID] Path found starting at index", start)
        print(phrase)
        found = True
        break

if not found:
    print("\n[-] No valid mnemonic found using delta-walk heuristic.")
