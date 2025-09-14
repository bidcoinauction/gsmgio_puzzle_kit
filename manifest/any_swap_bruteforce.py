#!/usr/bin/env python3
# any_swap_bruteforce.py

from bip_utils import Bip39MnemonicValidator, Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from itertools import combinations, product
import sys

# --- Configuration ---
TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"

# Your spiral‐extracted coords in CCW order:
yellow_coords = [(4,6), (4,7), (8,6), (8,4), (7,9), (6,8), (6,5), (5,2), (12,2)]
blue_coords   = [(8,10), (9,1), (10,4), (11,7), (11,10), (12,11), (13,3), (13,8), (9,13)]

# Map coords→word
coord_to_word = {
    (4,6): 'grant',    (4,7): 'capital',  (8,6): 'bright',
    (8,4): 'forward',  (7,9): 'miracle',  (6,8): 'foam',
    (6,5): 'charge',   (5,2): 'lumber',   (12,2): 'memory',
    (8,10): 'mountain',(9,1): 'chest',    (10,4): 'argue',
    (11,7): 'because', (11,10): 'either', (12,11): 'juice',
    (13,3): 'frost',   (13,8): 'initial', (9,13): 'guilt'
}

yellow = [coord_to_word[c] for c in yellow_coords]
blue   = [coord_to_word[c] for c in blue_coords]

def derive_address(mnemonic):
    seed = Bip39SeedGenerator(mnemonic).Generate()
    acct = Bip44.FromSeed(seed, Bip44Coins.BITCOIN).Purpose().Coin().Account(0)
    return acct.Change(Bip44Changes.CHAIN_EXT).AddressIndex(0).PublicKey().ToAddress()

def is_valid(mnemonic):
    try:
        Bip39MnemonicValidator().Validate(mnemonic)
        return True
    except:
        return False

# Generate **all** single‐swap variants for a block of 9 words
def all_single_swaps(words):
    variants = []
    for i, j in combinations(range(len(words)), 2):
        w = words.copy()
        w[i], w[j] = w[j], w[i]
        variants.append(w)
    variants.append(list(words))  # include the original
    return variants

yellow_variants = all_single_swaps(yellow)
blue_variants   = all_single_swaps(blue)

total = len(yellow_variants) * len(blue_variants) * 2
print(f"🔍 Testing ~{total:,} combinations (36×36×2)…\n")

for y_seq, b_seq in product(yellow_variants, blue_variants):
    for mnemonic in (" ".join(y_seq + b_seq), " ".join(b_seq + y_seq)):
        if not is_valid(mnemonic):
            continue
        addr = derive_address(mnemonic)
        if addr == TARGET_ADDRESS:
            print("✅ MATCH FOUND!\n")
            print("Mnemonic:", mnemonic, "\n")
            sys.exit(0)

print("❌ No single‐swap combo (anywhere in block) matched.")
