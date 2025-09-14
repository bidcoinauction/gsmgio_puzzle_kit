import math
import re
from pathlib import Path
from mnemonic import Mnemonic
import sys

# --- Data setup ---

offsets = [0x2c, 0x45, 0xe6, 0x128, 0x193, 0x226, 0x2a4,
           0x2ed, 0x2f3, 0x366, 0x3b8, 0x3c1, 0x4c6]
deltas = [j - i for i, j in zip(offsets, offsets[1:])]

BIP39_FILE = "english.txt"
BIP39_WORDS = Path(BIP39_FILE).read_text().splitlines()
mnemo = Mnemonic("english")

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

print(f"[+] {len(coords)} nodes, {len(deltas)} deltas")

# --- Distance functions ---

def manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def euclidean(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

# choose distance metric
distance_func = manhattan

# --- Backtracking search ---

N = len(coords)
best_path = None
found = False
threshold = 20  # tolerance for |distance - delta|

sys.setrecursionlimit(2000)

def dfs(path, used, delta_index):
    global found, best_path

    if found:  # stop if solution found
        return

    if len(path) == N:
        # Validate mnemonic
        words = [coords[i][3] for i in path]
        phrase = " ".join(words)
        if mnemo.check(phrase):
            print("\n[VALID MNEMONIC FOUND!]")
            print(" ".join(words))
            best_path = list(path)
            found = True
        return

    if delta_index >= len(deltas):
        # no more deltas, just append remaining in all orders
        remaining = [i for i in range(N) if i not in used]
        # try appending them directly
        full_path = path + remaining
        words = [coords[i][3] for i in full_path]
        phrase = " ".join(words)
        if mnemo.check(phrase):
            print("\n[VALID MNEMONIC FOUND!]")
            print(" ".join(words))
            best_path = list(full_path)
            found = True
        return

    current = coords[path[-1]]
    target_delta = deltas[delta_index]

    candidates = []
    for i in range(N):
        if i in used:
            continue
        dist = distance_func((current[0], current[1]), (coords[i][0], coords[i][1]))
        diff = abs(dist - target_delta)
        if diff <= threshold:
            candidates.append((diff, i))

    # sort candidates by how close their distance is to the delta
    candidates.sort(key=lambda x: x[0])

    for _, next_node in candidates:
        used.add(next_node)
        dfs(path + [next_node], used, delta_index + 1)
        used.remove(next_node)

# --- Try all starting nodes ---

for start in range(N):
    print(f"[i] Trying start node {start} ({coords[start][2]})")
    dfs([start], {start}, 0)
    if found:
        break

if not found:
    print("\n[-] No valid mnemonic found with delta-guided backtracking search.")
