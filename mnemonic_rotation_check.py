from mnemonic import Mnemonic
from pathlib import Path

# The 18 words from your previous extraction:
words = [
    "frost", "because", "bright", "guilt", "grant", "lumber",
    "mountain", "either", "forward", "miracle", "charge", "foam",
    "capital", "argue", "initial", "juice", "chest", "memory"
]

mnemo = Mnemonic("english")

def is_valid(seq):
    phrase = " ".join(seq)
    return mnemo.check(phrase)

valid_combos = []

# 1. Check all circular rotations for full 18-word set
for shift in range(len(words)):
    rotated = words[shift:] + words[:shift]
    if is_valid(rotated):
        valid_combos.append(("18-word rotation", shift, rotated))

# 2. Check all 18 contiguous sequences (trivial: only one)
# Already covered above

# 3. Check all 12-word contiguous sequences
for i in range(len(words) - 12 + 1):
    subset = words[i:i+12]
    if is_valid(subset):
        valid_combos.append(("12-word segment", f"{i}-{i+11}", subset))

# Report results
if valid_combos:
    print("[+] Valid mnemonics found:")
    for kind, pos, seq in valid_combos:
        print(f"{kind} ({pos}): {' '.join(seq)}")
else:
    print("[-] No valid mnemonic found among rotations or contiguous segments.")
