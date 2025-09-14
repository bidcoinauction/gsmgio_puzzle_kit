# salphaseion_batch_decoder.py

import os
import itertools
import codecs
import hashlib
from tqdm import tqdm
from mnemonic import Mnemonic
from bip32utils import BIP32Key
from collections import Counter

mnemo = Mnemonic("english")

# -----------------------------
# Config
# -----------------------------
TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
VALID_LOG_FILE = "salphaseion_valid_log.txt"
MATCH_FILE = "salphaseion_match.txt"

# -----------------------------
# New Interpretation Methods
# -----------------------------
def base36_index(pair):
    try:
        return int(pair, 36) % 18
    except:
        return -1

def ascii_sum(pair):
    return sum(ord(c) for c in pair) % 18

def base58_index(pair):
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    try:
        val = sum(alphabet.index(c) * (58 ** i) for i, c in enumerate(reversed(pair)))
        return val % 18
    except ValueError:
        return -1

def polybius_index(pair):
    grid = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    try:
        row = grid.index(pair[0].upper()) // 5
        col = grid.index(pair[1].upper()) % 5
        return (row * 5 + col) % 18
    except ValueError:
        return -1

def rot13_ascii_sum(pair):
    try:
        rot = codecs.encode(pair, 'rot_13')
        return sum(ord(c) for c in rot) % 18
    except:
        return -1

def ascii_xor_sum(pair):
    try:
        return (ord(pair[0]) ^ ord(pair[1])) % 18
    except:
        return -1

def mirrored_base58(pair):
    try:
        reversed_pair = pair[::-1]
        return base58_index(reversed_pair)
    except:
        return -1

def bitwise_invert_ord(pair):
    try:
        return ((~ord(pair[0]) & 0xFF) + (~ord(pair[1]) & 0xFF)) % 18
    except:
        return -1

# -----------------------------
# Helpers
# -----------------------------
def reorder_words(wordlist, indices):
    ordered = [None] * 18
    for i, idx in enumerate(indices):
        ordered[idx] = wordlist[i]
    return ordered

def is_valid_index_array(indices):
    return len(indices) == 18 and len(set(indices)) == 18 and all(0 <= i < 18 for i in indices)

def derive_address(mnemonic_str):
    seed = mnemo.to_seed(mnemonic_str)
    key = BIP32Key.fromEntropy(seed)
    return key.Address()

def fuzzy_fill_indices(indices):
    missing = [i for i in range(18) if i not in indices]
    counts = Counter(indices)
    duplicates = [i for i in indices if counts[i] > 1]
    if len(duplicates) != len(missing):
        return []
    results = []
    for perm in itertools.permutations(missing):
        temp = indices[:]
        d_idx = [i for i, x in enumerate(temp) if temp.count(x) > 1]
        for j, pos in enumerate(d_idx):
            temp[pos] = perm[j]
        if is_valid_index_array(temp):
            results.append(temp)
    return results

# -----------------------------
# Main decode per pair set
# -----------------------------
METHODS = {
    "base36": base36_index,
    "ascii_sum": ascii_sum,
    "base58": base58_index,
    "polybius": polybius_index,
    "rot13_sum": rot13_ascii_sum,
    "ascii_xor": ascii_xor_sum,
    "mirrored_b58": mirrored_base58,
    "bitwise_invert": bitwise_invert_ord
}

def decode_pair_file(pair_path, wordlist):
    with open(pair_path) as f:
        pairs = [x.strip() for x in f.readlines() if len(x.strip()) == 2]
    if len(pairs) != 18:
        print(f"[!] Skipping {pair_path}, wrong number of pairs.")
        return

    for method_name, fn in METHODS.items():
        raw_idx = [fn(p) for p in pairs]
        candidates = [raw_idx] if is_valid_index_array(raw_idx) else fuzzy_fill_indices(raw_idx)
        for idx_set in candidates:
            ordered = reorder_words(wordlist, idx_set)
            mnemonic = " ".join(ordered)
            if not mnemo.check(mnemonic):
                continue
            addr = derive_address(mnemonic)
            if addr == TARGET_ADDRESS:
                print(f"[MATCH] {method_name} on {os.path.basename(pair_path)} → {addr}")
                with open(MATCH_FILE, "w") as f:
                    f.write(mnemonic + "\n")
                return
            else:
                with open(VALID_LOG_FILE, "a") as log:
                    log.write(f"{method_name}|{pair_path}|{addr}|{mnemonic}\n")

# -----------------------------
# Entrypoint
# -----------------------------

def run_decoder(pair_dir, wordlist_path):
    with open(wordlist_path) as f:
        words = f.read().replace("\n", " ").split()
    if len(words) != 18:
        print("[!] BIP39 word list must have 18 words.")
        return

    files = [os.path.join(pair_dir, x) for x in os.listdir(pair_dir) if x.endswith(".txt")]
    for path in tqdm(files, desc="Decoding pair files"):
        decode_pair_file(path, words)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Batch decode salphaseion pair sets")
    parser.add_argument("--pair-dir", required=True, help="Directory of decoded pair .txt files")
    parser.add_argument("--wordlist", required=True, help="Path to base 18-word BIP39 mnemonic")
    args = parser.parse_args()
    run_decoder(args.pair_dir, args.wordlist)
