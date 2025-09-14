import base64
import string
import itertools
from mnemonic import Mnemonic
from bip32utils import BIP32Key
import hashlib

# --- INPUT DATA ---

bip39_words = [
    "frost", "because", "bright", "guilt", "grant", "lumber",
    "mountain", "either", "forward", "miracle", "charge",
    "foam", "capital", "argue", "initial", "juice", "chest", "memory"
]

decoded_pairs = [
    "kr", "4E", "68", "n1", "ml", "Tj", "w4", "fs", "KE",
    "vf", "8k", "K0", "7K", "2K", "Pr", "QU", "8s", "uv"
]

mnemo = Mnemonic("english")

# --- INTERPRETATION METHODS ---

def interpret_base36(pair):
    try:
        return int(pair, 36) % 18
    except:
        return None

def interpret_ascii_sum(pair):
    return sum(ord(c) for c in pair) % 18

def interpret_first_char(pair):
    return ord(pair[0]) % 18

def interpret_second_char(pair):
    return ord(pair[1]) % 18

# --- REORDERING ATTEMPTS ---

def generate_orderings(pairs):
    methods = [
        ("base36", interpret_base36),
        ("ascii_sum", interpret_ascii_sum),
        ("first_char", interpret_first_char),
        ("second_char", interpret_second_char)
    ]

    all_orders = []

    for name, func in methods:
        idx_order = [func(p) for p in pairs]
        if None in idx_order or len(set(idx_order)) != 18:
            print(f"[!] Skipping method {name} due to invalid or duplicate indices.")
            continue
        order = [None] * 18
        for i, pos in enumerate(idx_order):
            order[pos] = bip39_words[i]
        all_orders.append((name, order))

    return all_orders

# --- VALIDATION & DERIVATION ---

def derive_bip44_address(seed_bytes):
    master_key = BIP32Key.fromEntropy(seed_bytes)
    child_key = master_key.ChildKey(44 + BIP32Key.HARDEN).ChildKey(0 + BIP32Key.HARDEN).ChildKey(0 + BIP32Key.HARDEN).ChildKey(0).ChildKey(0)
    return child_key.Address()

def validate_mnemonic(order):
    phrase = " ".join(order)
    if mnemo.check(phrase):
        seed = mnemo.to_seed(phrase, passphrase="")
        addr = derive_bip44_address(seed)
        return addr
    return None

# --- MAIN LOOP ---

if __name__ == "__main__":
    orderings = generate_orderings(decoded_pairs)

    for method_name, words in orderings:
        print(f"\n[+] Trying method: {method_name}")
        print("Mnemonic:", " ".join(words))

        addr = validate_mnemonic(words)
        if addr:
            print(f"[\u2713] Valid BIP39 mnemonic! Derived address: {addr}")
        else:
            print("[-] Invalid mnemonic.")
