import itertools
from mnemonic import Mnemonic
from pathlib import Path

mnemo = Mnemonic("english")

# --- Load words ---
word_file = "words.txt"  # Replace with your file
raw = Path(word_file).read_text().strip().replace("\n", " ")
words = raw.split()
print(f"[+] Loaded {len(words)} words: {words}")

if len(words) != 18:
    print("[-] Expected 18 words!")
    exit()

# --- Helpers ---
def try_mnemonic(seq):
    phrase = " ".join(seq)
    if mnemo.check(phrase):
        print("\n[!!!] VALID MNEMONIC FOUND:\n", phrase)
        return True
    return False

# --- Heuristic orderings ---
candidates = []

# 1. Original order
candidates.append(words)

# 2. Reverse order
candidates.append(list(reversed(words)))

# 3. Sort alphabetically
candidates.append(sorted(words))

# 4. Sort by BIP39 index
bip39_idx = {w: mnemo.wordlist.index(w) for w in words}
candidates.append(sorted(words, key=lambda w: bip39_idx[w]))

# 5. Reverse index sort
candidates.append(sorted(words, key=lambda w: bip39_idx[w], reverse=True))

# 6. Generate column/row heuristics:
# Treat as 6x3 or 3x6 grid
for cols in [3, 6]:
    grid = [words[i:i+cols] for i in range(0, 18, cols)]
    # Row-major
    candidates.append(list(itertools.chain.from_iterable(grid)))
    # Column-major
    col_major = [grid[r][c] for c in range(cols) for r in range(len(grid))]
    candidates.append(col_major)
    # Snake pattern
    snake = []
    for i, row in enumerate(grid):
        snake.extend(row if i % 2 == 0 else reversed(row))
    candidates.append(snake)

# 7. Try all combinations of 12 contiguous words from sorted list
for base in [words, sorted(words), sorted(words, key=lambda w: bip39_idx[w])]:
    for i in range(len(base) - 11):
        subset = base[i:i+12]
        candidates.append(subset)

# --- Deduplicate candidates ---
unique_candidates = []
seen = set()
for cand in candidates:
    tup = tuple(cand)
    if tup not in seen:
        seen.add(tup)
        unique_candidates.append(cand)

print(f"[+] Generated {len(unique_candidates)} candidate sequences")

# --- Test all candidates ---
found = False
for cand in unique_candidates:
    if try_mnemonic(cand):
        found = True
        break

if not found:
    print("[-] No valid mnemonic found with these heuristics.")
