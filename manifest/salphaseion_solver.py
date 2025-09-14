# salphaseion_batch_solver.py

import os
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip39MnemonicValidator
from typing import List, Tuple

# === CONFIG ===
TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
VALID_LOG = "salphaseion_valid_log.txt"
MATCH_LOG = "salphaseion_match.txt"

# === Trusted Coordinate → Word Mapping (18 items) ===
coord_to_word = {
    (4, 6): "grant",     (4, 7): "capital",   (8, 6): "bright",
    (8, 4): "forward",   (7, 9): "miracle",   (11, 7): "because",
    (12, 2): "memory",   (13, 8): "initial",  (9, 13): "guilt",
    (6, 8): "foam",      (6, 5): "charge",    (5, 2): "lumber",
    (8, 10): "mountain", (9, 1): "chest",     (10, 4): "argue",
    (11, 10): "either",  (12, 11): "juice",   (13, 3): "frost"
}

# === Grid from puzzle.png (Y=yellow, B=blue) ===
grid = [
    ['K','B','K','W','K','B','W','K','K','B','W','K','Y','K'],
    ['W','K','B','K','W','K','K','W','B','K','K','W','K','W'],
    ['K','W','K','W','K','W','K','K','K','W','K','W','K','K'],
    ['B','K','W','K','B','K','W','K','W','K','Y','K','W','K'],
    ['K','W','K','K','K','W','Y','Y','W','K','K','W','K','W'],
    ['W','K','B','K','W','K','W','W','W','K','W','K','K','B'],
    ['K','W','K','W','K','B','W','K','B','W','K','W','K','K'],
    ['K','K','K','K','K','W','K','W','K','Y','K','W','K','W'],
    ['W','K','W','K','Y','K','Y','W','K','K','B','K','W','K'],
    ['K','B','K','W','K','W','W','K','W','K','K','W','K','Y'],
    ['W','K','W','K','B','K','K','W','K','W','K','W','K','K'],
    ['K','W','K','W','K','W','K','Y','W','K','B','K','W','K'],
    ['W','K','Y','K','W','K','W','K','K','W','K','B','K','W'],
    ['K','K','K','B','K','W','K','W','Y','K','W','K','W','K']
]

# === Spiral Path Generator ===
def spiral_coords(start_x, start_y, size=14, reverse=False):
    x, y = start_x, start_y
    dx, dy = [0, -1, 0, 1], [1, 0, -1, 0]
    direction = 0
    steps = 1
    coords = [(x, y)]
    while len(coords) < size * size:
        for _ in range(2):
            for _ in range(steps):
                x += dx[direction]
                y += dy[direction]
                if 0 <= x < size and 0 <= y < size:
                    coords.append((x, y))
            direction = (direction + 1) % 4
        steps += 1
    return coords[::-1] if reverse else coords

# === Extract Y and B squares from a spiral path ===
def get_color_coords(path: List[Tuple[int, int]]) -> Tuple[List[Tuple[int,int]], List[Tuple[int,int]]]:
    yellow, blue = [], []
    for r, c in path:
        if (r, c) in coord_to_word:
            if grid[r][c] == 'Y':
                yellow.append((r, c))
            elif grid[r][c] == 'B':
                blue.append((r, c))
        if len(yellow) == 9 and len(blue) == 9:
            break
    return yellow, blue

# === Validate mnemonic and derive BTC address ===
def validate_and_derive(words: List[str]) -> Tuple[bool, str]:
    mnemonic = " ".join(words)
    try:
        Bip39MnemonicValidator().Validate(mnemonic)
        seed = Bip39SeedGenerator(mnemonic).Generate()
        wallet = Bip44.FromSeed(seed, Bip44Coins.BITCOIN)
        address = wallet.Purpose().Coin().Account(0).Change(0).AddressIndex(0).PublicKey().ToAddress()
        return True, address
    except Exception:
        return False, ""

# === Run all spiral strategies ===
def run_all_variants():
    centers = [(7, 7), (6, 6), (7, 6), (6, 7)]
    variants_tested = 0
    matches_found = 0

    open(VALID_LOG, 'w').close()
    open(MATCH_LOG, 'w').close()

    for reverse in [False, True]:
        for (cx, cy) in centers:
            path = spiral_coords(cx, cy, reverse=reverse)
            yellow, blue = get_color_coords(path)

            for order in [('YB', yellow + blue), ('BY', blue + yellow)]:
                label, coords = order
                if len(coords) != 18:
                    continue
                try:
                    words = [coord_to_word[c] for c in coords]
                except KeyError:
                    continue

                is_valid, address = validate_and_derive(words)
                if is_valid:
                    mnemonic = " ".join(words)
                    with open(VALID_LOG, 'a') as vf:
                        vf.write(f"[{cx},{cy}] Rev={reverse} Order={label}\n{mnemonic}\nAddress: {address}\n\n")
                    if address == TARGET_ADDRESS:
                        with open(MATCH_LOG, 'a') as mf:
                            mf.write(f"🎯 MATCH FOUND!\nMnemonic: {mnemonic}\n")
                        matches_found += 1
                variants_tested += 1

    print(f"✅ Checked {variants_tested} variants.")
    print(f"🔑 Matches found: {matches_found}")
    print(f"📄 Valid mnemonics logged to: {VALID_LOG}")
    print(f"🎯 Matching mnemonics logged to: {MATCH_LOG}")

if __name__ == "__main__":
    run_all_variants()
