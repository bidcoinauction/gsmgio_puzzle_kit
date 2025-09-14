import csv
import itertools
import hashlib
from bip_utils import (
    Bip39MnemonicValidator, Bip39SeedGenerator, Bip44, Bip44Coins,
    Bip44Changes
)
from multiprocessing import Pool, cpu_count
from typing import List

# --- CONFIG ---
TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
SCRAMBLED_WORDS = [
    "frost", "because", "bright", "guilt", "grant", "lumber",
    "mountain", "either", "forward", "miracle", "charge",
    "foam", "capital", "argue", "initial", "juice", "chest", "memory"
]
DECODED_PAIRS = [
    "kr", "4E", "68", "n1", "ml", "Tj",
    "w4", "fs", "KE", "vf", "8k", "K0",
    "7K", "2K", "Pr", "QU", "8s", "uv"
]
REFERENCE_ORDER = [
    "frost", "argue", "mountain", "chest", "guilt", "memory",
    "bright", "juice", "initial", "because", "lumber", "grant",
    "foam", "charge", "either", "forward", "capital", "miracle"
]
LOG_FILE = "valid_mnemonics_log.csv"

# --- HELPERS ---
def ascii_sum(pair: str) -> int:
    return sum(ord(c) for c in pair) % 18

def base36_mod(pair: str) -> int:
    try:
        return int(pair, 36) % 18
    except ValueError:
        return -1

def polybius(pair: str) -> int:
    table = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    pair = pair.upper()
    if len(pair) != 2:
        return -1
    try:
        row = table.index(pair[0]) // 5
        col = table.index(pair[1]) % 5
        return (row * 5 + col) % 18
    except ValueError:
        return -1

def generate_ordered_words(scrambled: List[str], method: str) -> List[str]:
    index_map = {
        "ascii": ascii_sum,
        "base36": base36_mod,
        "polybius": polybius
    }.get(method)

    if not index_map:
        raise ValueError("Invalid mapping method")

    ordered = [None] * 18
    for i, pair in enumerate(DECODED_PAIRS):
        idx = index_map(pair)
        if idx == -1 or idx >= len(scrambled) or ordered[idx] is not None:
            return []  # conflict or bad index
        ordered[idx] = scrambled[i]
    return ordered if None not in ordered else []

def mnemonic_entropy_distance(mnemonic: List[str], reference: List[str]) -> int:
    return sum(1 for a, b in zip(mnemonic, reference) if a != b)

def test_mnemonic(mnemonic: List[str]) -> tuple:
    phrase = " ".join(mnemonic)
    if not Bip39MnemonicValidator(phrase).Validate():
        return None

    seed_bytes = Bip39SeedGenerator(phrase).Generate()
    addr = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)\
        .Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT)\
        .AddressIndex(0).PublicKey().ToAddress()

    return (phrase, addr, seed_bytes.hex()) if addr == TARGET_ADDRESS else None

# --- MULTIPROCESS WORKER ---
def worker(permutation):
    result = test_mnemonic(permutation)
    if result:
        phrase, address, seed_hex = result
        with open(LOG_FILE, "a") as f:
            writer = csv.writer(f)
            writer.writerow([phrase, address, seed_hex])
        return result
    return None

# --- MAIN ---
def run_full_search():
    with open(LOG_FILE, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["mnemonic", "address", "seed"])

    print("[*] Trying decoded pair mappings...")
    for method in ["ascii", "base36", "polybius"]:
        ordered = generate_ordered_words(SCRAMBLED_WORDS, method)
        if ordered:
            print(f"[+] Testing mapped mnemonic using {method}: {' '.join(ordered)}")
            res = test_mnemonic(ordered)
            if res:
                phrase, addr, seed = res
                print(f"[!!!] MATCH FOUND via {method}: {phrase}")
                print(f"Address: {addr}\nSeed: {seed}")
                return

    print("[*] Launching brute-force permutation scan (prioritized by entropy distance)...")
    permutations = list(itertools.permutations(SCRAMBLED_WORDS))
    permutations.sort(key=lambda p: mnemonic_entropy_distance(p, REFERENCE_ORDER))

    with Pool(cpu_count()) as pool:
        for result in pool.imap_unordered(worker, permutations):
            if result:
                print(f"[!!!] BRUTE-FORCE MATCH FOUND:\nMnemonic: {result[0]}\nAddress: {result[1]}\nSeed: {result[2]}")
                break

if __name__ == "__main__":
    run_full_search()
