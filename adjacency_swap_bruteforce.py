#!/usr/bin/env python3
# adjacency_swap_bruteforce.py

from bip_utils import Bip39MnemonicValidator, Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from itertools import product

# --- Configuration ---
TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"

# These are your spiral‐extracted coords in CCW order:
yellow_coords = [(4,6), (4,7), (8,6), (8,4), (7,9), (6,8), (6,5), (5,2), (12,2)]
blue_coords   = [(8,10), (9,1), (10,4), (11,7), (11,10), (12,11), (13,3), (13,8), (9,13)]

# Map each coord to its word
coord_to_word = {
    (4,6): 'grant',    (4,7): 'capital',  (8,6): 'bright',
    (8,4): 'forward',  (7,9): 'miracle',  (6,8): 'foam',
    (6,5): 'charge',   (5,2): 'lumber',   (12,2): 'memory',
    (8,10): 'mountain',(9,1): 'chest',    (10,4): 'argue',
    (11,7): 'because', (11,10): 'either', (12,11): 'juice',
    (13,3): 'frost',   (13,8): 'initial', (9,13): 'guilt'
}

# Build the base word lists
yellow = [coord_to_word[c] for c in yellow_coords]
blue   = [coord_to_word[c] for c in blue_coords]

# Helpers
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

# Generate all single‐swap variants within distance 2
def generate_swapped(words, max_dist=2):
    out = set()
    n = len(words)
    for i in range(n):
        for j in range(i+1, min(n, i+1+max_dist)):
            w = list(words)
            w[i], w[j] = w[j], w[i]
            out.add(tuple(w))
    out.add(tuple(words))
    return [list(t) for t in out]

yellow_vars = generate_swapped(yellow)
blue_vars   = generate_swapped(blue)

print(f"Trying {len(yellow_vars)} yellow × {len(blue_vars)} blue ≈ {len(yellow_vars)*len(blue_vars)} combos")

for y_seq, b_seq in product(yellow_vars, blue_vars):
    for concat in (" ".join(y_seq + b_seq), " ".join(b_seq + y_seq)):
        if not is_valid(concat):
            continue
        addr = derive_address(concat)
        if addr == TARGET_ADDRESS:
            print("\n✅ MATCH FOUND!\n")
            print("Mnemonic:", concat)
            exit(0)

print("\n❌ No adjacency‐swap match found.")
