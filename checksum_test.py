import itertools
import csv
import hashlib
from pathlib import Path
from mnemonic import Mnemonic

# === CONFIG ===

TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
PAIR_LIST = [
    "kr", "4E", "68", "8f", "J1", "FY", "b0", "dE", "c5",
    "M7", "sU", "TW", "NH", "Aa", "98", "vD", "rm", "Xe"
]

WORDS = [
    "forward", "bright", "argue", "capital", "chest", "miracle", "charge", "juice", "memory",
    "grant", "mountain", "initial", "guilt", "frost", "either", "because", "foam", "lumber"
]

INDEX_LOCKS = {
    # Optional: lock words into certain positions
    # "miracle": 12,
}

EXPORT_PATH = "all_valid_mnemonics.csv"
mnemo = Mnemonic("english")

# === UTILITIES ===

def base36_pair_to_index(pair):
    def b36(c):
        return int(c) if c.isdigit() else 10 + ord(c.upper()) - ord('A')
    return (b36(pair[0]) * 36 + b36(pair[1])) % 18

def apply_instruction_permutation(words, pairs):
    indices = [base36_pair_to_index(p) for p in pairs]
    out = [None] * 18
    used = set()

    for i, idx in enumerate(indices):
        # Collision resolution: pick first unused slot from idx onward
        while idx in used:
            idx = (idx + 1) % 18
        out[idx] = words[i]
        used.add(idx)

    # Fill remaining empty spots in order
    unused_words = [w for w in words if w not in out]
    for i in range(18):
        if out[i] is None:
            out[i] = unused_words.pop(0)

    return out

def validate_and_export(mnemonic_words, strategy, log_writer):
    phrase = " ".join(mnemonic_words)
    if not mnemo.check(phrase):
        return False

    seed = mnemo.to_seed(phrase, passphrase="")
    entropy = hashlib.sha256(seed).digest()
    hashed = hashlib.new('ripemd160', hashlib.sha256(entropy).digest()).digest()
    prefix = b'\x00' + hashed
    checksum = hashlib.sha256(hashlib.sha256(prefix).digest()).digest()[:4]
    final = prefix + checksum
    import base58
    address = base58.b58encode(final).decode()

    log_writer.writerow([strategy, phrase, address])

    if address == TARGET_ADDRESS:
        print(f"\n🎯 MATCH! Strategy: {strategy}")
        print(f"[Mnemonic] {phrase}")
        print(f"[Address] {address}")
        return True

    print(f"[VALID] {strategy}: {address}")
    return False

def try_all_swaps(words, base_strategy, log_writer):
    # single swaps
    for i in range(18):
        for j in range(i + 1, 18):
            test = words[:]
            test[i], test[j] = test[j], test[i]
            strategy = f"{base_strategy} [swap {i},{j}]"
            validate_and_export(test, strategy, log_writer)

    # 3-cycles
    for i in range(18):
        for j in range(i + 1, 18):
            for k in range(j + 1, 18):
                test = words[:]
                test[i], test[j], test[k] = test[k], test[i], test[j]
                strategy = f"{base_strategy} [cycle {i},{j},{k}]"
                validate_and_export(test, strategy, log_writer)

def index_locked(words):
    for word, pos in INDEX_LOCKS.items():
        if pos >= len(words) or words[pos] != word:
            return False
    return True

# === MAIN ===

with open(EXPORT_PATH, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Strategy", "Mnemonic", "Address"])

    print(f"\n[🧠 Strategy] Instruction Pointer Mapping")
    reordered = apply_instruction_permutation(WORDS, PAIR_LIST)

    if index_locked(reordered):
        validate_and_export(reordered, "InstructionMap", writer)
        try_all_swaps(reordered, "InstructionMap", writer)
    else:
        print("❌ Does not satisfy index locks")

    print("\n[🔁 Strategy] Sorted by base36(pair)")
    sorted_by_val = [w for _, w in sorted(zip(PAIR_LIST, WORDS), key=lambda x: base36_pair_to_index(x[0]))]
    if index_locked(sorted_by_val):
        validate_and_export(sorted_by_val, "SortedBase36", writer)
        try_all_swaps(sorted_by_val, "SortedBase36", writer)

    print("\n[🔁 Strategy] Reverse Sorted")
    reversed_sorted = list(reversed(sorted_by_val))
    if index_locked(reversed_sorted):
        validate_and_export(reversed_sorted, "ReversedSorted", writer)
        try_all_swaps(reversed_sorted, "ReversedSorted", writer)

print(f"\n📝 Exported all valid mnemonics to: {EXPORT_PATH}")
