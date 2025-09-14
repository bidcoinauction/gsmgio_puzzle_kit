# gsmg.py
from bip_utils import Bip39MnemonicValidator, Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from itertools import product

TARGET = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"

# 14×14 puzzle grid (auto-extracted)
GRID = [
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
    ['K','K','K','B','K','W','K','W','Y','K','W','K','W','K'],
]

# Original WORD_DATA (word, (row, col)), now transposed to (col, row)
WORD_DATA = [
    ('grant',    (6,4)),   ('capital',  (7,4)),
    ('bright',   (6,8)),   ('forward',  (4,8)),
    ('miracle',  (9,7)),   ('because',  (7,11)),
    ('memory',   (2,12)),  ('initial',  (8,13)),
    ('guilt',    (13,9)),  ('foam',     (8,6)),
    ('charge',   (5,6)),   ('lumber',   (2,5)),
    ('mountain',(10,8)),   ('chest',    (1,9)),
    ('argue',    (4,10)),  ('either',   (10,11)),
    ('juice',    (11,12)), ('frost',    (3,13)),
]

# Build mapping from transposed coordinates → word
coord_to_word = {coord: w for w, coord in WORD_DATA}

def gen_spiral(n=14, clockwise=False):
    """
    Build a spiral of all n*n coords from the center, in CW or CCW order.
    CCW dirs: Up, Left, Down, Right
    CW  dirs: Right, Down, Left, Up
    """
    if clockwise:
        dx, dy = [0, 1, 0, -1], [1, 0, -1, 0]
    else:
        dx, dy = [0, -1, 0, 1], [1, 0, -1, 0]

    x = y = n // 2
    direction = 0
    steps = 1
    coords = [(x, y)]

    while len(coords) < n*n:
        for _ in range(2):
            for _ in range(steps):
                x += dx[direction]
                y += dy[direction]
                if 0 <= x < n and 0 <= y < n:
                    coords.append((x, y))
            direction = (direction + 1) % 4
        steps += 1

    return coords

def is_valid_mnemonic(mn: str) -> bool:
    try:
        Bip39MnemonicValidator().Validate(mn)
        return True
    except:
        return False

def derive_addr(mn: str) -> str:
    seed = Bip39SeedGenerator(mn).Generate()
    acct = Bip44.FromSeed(seed, Bip44Coins.BITCOIN).Purpose().Coin().Account(0)
    return acct.Change(Bip44Changes.CHAIN_EXT).AddressIndex(0).PublicKey().ToAddress()

print("\n🚀 Batch Testing Spiral Variants (with transposed coords)…\n")

for clockwise, order in product([False, True], ['Y+B','B+Y']):
    spiral = gen_spiral(14, clockwise=clockwise)
    yellow, blue = [], []

    # Collect first 9 of each color per spiral
    for r,c in spiral:
        if (r, c) not in coord_to_word:
            continue
        if GRID[r][c] == 'Y' and len(yellow) < 9:
            yellow.append((r,c))
        if GRID[r][c] == 'B' and len(blue) < 9:
            blue.append((r,c))
        if len(yellow) == 9 and len(blue) == 9:
            break

    # Report if incomplete
    if len(yellow) != 9 or len(blue) != 9:
        print(f"{'CW' if clockwise else 'CCW'} {order}: ✗ collected {len(yellow)}/9 Y, {len(blue)}/9 B")
        continue

    # Build mnemonic in chosen order
    if order == 'Y+B':
        seq = yellow + blue
    else:
        seq = blue + yellow
    words = [coord_to_word[c] for c in seq]
    mnemonic = " ".join(words)

    # Validate & derive
    valid = is_valid_mnemonic(mnemonic)
    addr = derive_addr(mnemonic) if valid else None
    match = (valid and addr == TARGET)

    print(
        f"{'CW' if clockwise else 'CCW'} {order}: "
        + ("✓ checksum" if valid else "✗ checksum")
        + (f", Derived={addr}" if valid else "")
        + ("  ✅ MATCH!" if match else "")
    )

print("\nBatch complete.\n")
