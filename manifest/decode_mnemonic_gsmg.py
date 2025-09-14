# decode_mnemonic_gsmg.py
# Full GSMG.IO Salphaseion decoder script

import itertools
import hashlib
import base64
from mnemonic import Mnemonic
from bip32utils import BIP32Key
import codecs

mnemo = Mnemonic("english")

# -----------------------------
# INPUTS
# -----------------------------

decoded_pairs = [
    "kr", "4E", "68", "n1", "ml", "Tj",
    "w4", "fs", "KE", "vf", "8k", "K0",
    "7K", "2K", "Pr", "QU", "8s", "uv"
]

bip39_words = [
    "frost", "argue", "mountain", "chest", "guilt", "memory",
    "bright", "juice", "initial", "because", "lumber", "grant",
    "foam", "charge", "either", "forward", "capital", "miracle"
]

TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"

# -----------------------------
# INTERPRETATION METHODS
# -----------------------------

def base58_index(pair):
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    try:
        val = sum(alphabet.index(c) * (58 ** i) for i, c in enumerate(reversed(pair)))
        return val % 18
    except ValueError:
        return -1

def polybius_index(pair):
    grid = "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # No 'J'
    try:
        row = grid.index(pair[0].upper()) // 5
        col = grid.index(pair[1].upper()) % 5
        return (row * 5 + col) % 18
    except ValueError:
        return -1

def ord_product(pair):
    try:
        return (ord(pair[0]) * ord(pair[1])) % 18
    except:
        return -1

def sorted_ascii(pair):
    return sum(sorted([ord(c) for c in pair])) % 18

def rot13_ascii_sum(pair):
    try:
        rot = codecs.encode(pair, 'rot_13')
        return sum(ord(c) for c in rot) % 18
    except:
        return -1

# -----------------------------
# WALLET VALIDATION
# -----------------------------

def derive_address(mnemonic_str):
    seed = mnemo.to_seed(mnemonic_str)
    key = BIP32Key.fromEntropy(seed)
    return key.Address()

def is_valid_index_array(indices):
    if len(indices) != 18:
        return False
    if any(i < 0 or i >= 18 for i in indices):
        return False
    if len(set(indices)) != 18:
        return False
    return True

def reorder_words(words, indices):
    ordered = [None] * 18
    for i, idx in enumerate(indices):
        ordered[idx] = words[i]
    return ordered

# -----------------------------
# FUZZY FALLBACK
# -----------------------------

def fuzzy_fill_indices(indices):
    missing = [i for i in range(18) if i not in indices]
    duplicates = [x for x in indices if indices.count(x) > 1]
    if len(missing) != len(duplicates):
        return []

    results = []
    for perm in itertools.permutations(missing):
        temp = indices[:]
        dup_idx = [i for i in range(len(temp)) if temp[i] in duplicates and duplicates.count(temp[i]) > 0]
        for j, pos in enumerate(dup_idx):
            temp[pos] = perm[j]
        if is_valid_index_array(temp):
            results.append(temp)
    return results

# -----------------------------
# RUN STRATEGY
# -----------------------------

def try_method(method_fn, name):
    indices = [method_fn(p) for p in decoded_pairs]
    if is_valid_index_array(indices):
        candidates = [indices]
    else:
        print(f"[!] {name} failed index validation. Attempting fuzzy correction...")
        candidates = fuzzy_fill_indices(indices)
        if not candidates:
            print(f"[!] No valid fuzzy permutations found for {name}.")
            return

    for idx_set in candidates:
        candidate = reorder_words(bip39_words, idx_set)
        mnemonic_str = " ".join(candidate)

        if not mnemo.check(mnemonic_str):
            continue

        address = derive_address(mnemonic_str)
        if address == TARGET_ADDRESS:
            print(f"\n[MATCH] {name} produced correct mnemonic!")
            print(mnemonic_str)
            with open("salphaseion_match.txt", "w") as f:
                f.write(mnemonic_str + "\n")
            return
        else:
            print(f"[x] {name} valid mnemonic → address: {address} (not target)")

# -----------------------------
# MAIN EXECUTION
# -----------------------------

METHODS = {
    "base58": base58_index,
    "polybius": polybius_index,
    "ord_product": ord_product,
    "sorted_ascii": sorted_ascii,
    "rot13_ascii_sum": rot13_ascii_sum
}

if __name__ == "__main__":
    for method_name, fn in METHODS.items():
        try_method(fn, method_name)

    print("\n[+] Completed decoding attempts.\n")
    print("Next Options:")
    print("- Integrate grid-walk reverse logic (spiral, diagonal, mirrored)")
    print("- Extend for batch mode via --input-dir")
