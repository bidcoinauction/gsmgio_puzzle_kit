import math
import re
from pathlib import Path
from mnemonic import Mnemonic

# --- Config ---
FILE = "matrix_results/columns_concat_rot13_decoded.txt"
BIP39_FILE = "english.txt"

# Deltas from salphaseion offsets
offsets = [0x2c, 0x45, 0xe6, 0x128, 0x193, 0x226, 0x2a4,
           0x2ed, 0x2f3, 0x366, 0x3b8, 0x3c1, 0x4c6]
deltas = [j - i for i, j in zip(offsets, offsets[1:])]

mnemo = Mnemonic("english")
BIP39_WORDS = Path(BIP39_FILE).read_text().splitlines()

# --- Helpers ---
def base36_char(c):
    return int(c) if c.isdigit() else 10 + ord(c.upper()) - ord('A')

def manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def euclidean(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

# Load pairs
text = Path(FILE).read_text()
pairs = re.findall(r'[A-Za-z0-9]{2}', text)

coords = []
for p in pairs:
    r = base36_char(p[0])
    c = base36_char(p[1])
    idx = r * 36 + c
    word = BIP39_WORDS[idx % 2048]
    coords.append((p, (r, c), word))

print(f"[+] Loaded {len(coords)} pairs")
print("[+] Deltas:", deltas)

# --- Backtracking solver ---
best_path = None
best_score = float("inf")
found = False

def recurse(path, used, metric, score_so_far):
    global best_path, best_score, found

    step = len(path) - 1
    if len(path) == len(coords):
        # full path
        words = [coords[i][2] for i in path]
        phrase = " ".join(words)
        if mnemo.check(phrase):
            print(f"\n[VALID MNEMONIC FOUND] Metric={metric.__name__}")
            print(phrase)
            found = True
        # track best scoring
        if score_so_far < best_score:
            best_score = score_so_far
            best_path = path[:]
        return

    if found:
        return

    current = coords[path[-1]][1]
    if step < len(deltas):
        target = deltas[step]
    else:
        target = deltas[-1]  # repeat last delta for remaining steps

    # Compute distances
    candidates = []
    for i in range(len(coords)):
        if i in used:
            continue
        d = metric(current, coords[i][1])
        diff = abs(d - target)
        candidates.append((diff, d, i))

    # sort by closeness to target
    candidates.sort(key=lambda x: x[0])

    # try only top few candidates to prune search
    for diff, d, i in candidates[:5]:
        used.add(i)
        recurse(path+[i], used, metric, score_so_far+diff)
        used.remove(i)
        if found:
            return

def run_solver(metric):
    global best_path, best_score, found
    best_path = None
    best_score = float("inf")
    found = False

    for start in range(len(coords)):
        print(f"[i] Starting at node {start} ({coords[start][0]}) using {metric.__name__}")
        recurse([start], {start}, metric, 0)
        if found:
            break

    if not found:
        print(f"\n[-] No valid mnemonic found with {metric.__name__}.")
        if best_path:
            words = [coords[i][2] for i in best_path]
            print(f"[DEBUG] Closest path (total diff={best_score}):")
            print(" ".join(words))

# --- Run both metrics ---
run_solver(manhattan)
if not found:
    run_solver(euclidean)
