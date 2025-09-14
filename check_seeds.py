from mnemonic import Mnemonic
from bip32utils import BIP32Key
from itertools import permutations
from multiprocessing import Pool, cpu_count
import sys

# Target Bitcoin address
target = "1KfZGvwZxsvSmemoCmEV75uqcNzYBHjkHZ"

mnemo = Mnemonic("english")

# Fixed word positions in mnemonic
fixed_positions = {0: "subject", 3: "order", 9: "day"}
passphrase = "this"

# Remaining 8 words to permute
middle_words = ["real", "black", "breathe", "moon", "food", "only", "cover", "photo"]

# Priority candidate orders
priority_combos = [
    ["real", "black", "breathe", "moon", "food", "only", "cover", "photo"],
    ["real", "black", "breathe", "food", "moon", "only", "cover", "photo"],
    ["real", "black", "breathe", "only", "moon", "food", "cover", "photo"],
]

TOTAL = 40320  # 8!

def derive_address(seed_words, passphrase=""):
    """Derive first Bitcoin address (BIP44 m/44'/0'/0'/0/0)."""
    seed = mnemo.to_seed(seed_words, passphrase)
    master = BIP32Key.fromEntropy(seed)
    child = master.ChildKey(44 + 0x80000000) \
                  .ChildKey(0 + 0x80000000) \
                  .ChildKey(0 + 0x80000000) \
                  .ChildKey(0).ChildKey(0)
    return child.Address()

def build_phrase(combo, use_this_as_word):
    """Assemble a 12-word phrase with fixed positions and combo words."""
    phrase = [None] * 12
    for pos, word in fixed_positions.items():
        phrase[pos] = word

    free_positions = [i for i in range(12) if phrase[i] is None]

    # Fill 8 slots with combo words
    for i, word in enumerate(combo):
        phrase[free_positions[i]] = word

    # Handle the last open slot
    remaining_slots = [i for i in range(12) if phrase[i] is None]
    if use_this_as_word:
        # Fill any remaining slot with "this"
        for i in remaining_slots:
            phrase[i] = "this"
    else:
        # Replace remaining slot with an empty string (so join won't fail)
        for i in remaining_slots:
            phrase[i] = ""

    return " ".join(phrase).strip()

def test_combo(combo):
    """Test one word combo (with and without using 'this' as a word)."""

    # Case 1: Use passphrase = "this"
    phrase_str = build_phrase(combo, use_this_as_word=False)
    addr = derive_address(phrase_str, passphrase)
    if addr == target:
        return (phrase_str, passphrase)

    # Case 2: Use "this" as the 12th word
    phrase_str = build_phrase(combo, use_this_as_word=True)
    addr = derive_address(phrase_str, "")
    if addr == target:
        return (phrase_str, "")

    return None

def main():
    print("=== Testing priority combos first ===")
    for combo in priority_combos:
        res = test_combo(combo)
        if res:
            phrase, p = res
            print(f"\n*** MATCH FOUND ***\nSeed: {phrase}\nPassphrase: {p}")
            sys.exit(0)

    print("\nNo match in priority combos. Starting brute-force search...\n")

    all_perms = list(permutations(middle_words))
    total = len(all_perms)

    with Pool(cpu_count()) as pool:
        for idx, res in enumerate(pool.imap_unordered(test_combo, all_perms), 1):
            if idx % 500 == 0:
                pct = (idx / total) * 100
                print(f"Checked {idx}/{total} ({pct:.2f}%)")
            if res:
                phrase, p = res
                print(f"\n*** MATCH FOUND ***\nSeed: {phrase}\nPassphrase: {p}")
                pool.terminate()
                sys.exit(0)

    print("No match found in any permutation.")

if __name__ == "__main__":
    main()
