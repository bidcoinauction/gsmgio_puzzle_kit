#!/usr/bin/env python3
import sys
from bip_utils import Bip39MnemonicValidator, Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes

# --- CONFIGURATION ----------------------------------------------------

# Target address for validation
TARGET = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"

# Your 14×14 grid (K=black, W=white, Y=yellow, B=blue)
GRID = [
    list("KBKWBWKKKBWKYK"),
    list("WKBKWKKWBKKWKW"),
    list("KWKWKWKKKWKWKK"),
    list("BKWBKWKWKYKWK"),
    list("KWKKKWYYWKKWKW"),
    list("WKBKWKWWWKWKKB"),
    list("KWKWBWKBWKWKK"),
    list("KKKKKWKWYKWKW"),
    list("WKWKYKYWKKKBWK"),
    list("KBKWKWKWWKKWKY"),
    list("WKWKBKKWKWKWKK"),
    list("KWKWKWKYWKBKWK"),
    list("WKYKWKWKKWKBKW"),
    list("KKBKWKWYKWKWK"),
]
# (if any row is 13 long, you’ll see it immediately below)

# The 18 words and their grid coords
WORD_DATA = [
    ('grant',    (4, 6)),  ('capital',  (4, 7)),
    ('bright',   (8, 6)),  ('forward',  (8, 4)),
    ('miracle',  (7, 9)),  ('because',  (11, 7)),
    ('memory',   (12,2)),  ('initial',  (13,8)),
    ('guilt',    (9,13)),  ('foam',     (6,8)),
    ('charge',   (6,5)),   ('lumber',   (5,2)),
    ('mountain', (8,10)),  ('chest',    (9,1)),
    ('argue',    (10,4)),  ('either',   (11,10)),
    ('juice',    (12,11)), ('frost',    (13,3)),
]
coord_to_word = {coord: w for w, coord in WORD_DATA}

# CCW spiral path you verified (196 coords)
SPIRAL = [
    (6,6),(6,7),(5,7),(5,6),(5,5),(6,5),(7,5),(7,6),(7,7),(7,8),
    (6,8),(5,8),(4,8),(4,7),(4,6),(4,5),(4,4),(5,4),(6,4),(7,4),
    (8,4),(8,5),(8,6),(8,7),(8,8),(8,9),(7,9),(6,9),(5,9),(4,9),
    (3,9),(3,8),(3,7),(3,6),(3,5),(3,4),(3,3),(4,3),(5,3),(6,3),
    (7,3),(8,3),(9,3),(9,4),(9,5),(9,6),(9,7),(9,8),(9,9),(9,10),
    (8,10),(7,10),(6,10),(5,10),(4,10),(3,10),(2,10),(2,9),(2,8),
    (2,7),(2,6),(2,5),(2,4),(2,3),(2,2),(3,2),(4,2),(5,2),(6,2),
    (7,2),(8,2),(9,2),(10,2),(10,3),(10,4),(10,5),(10,6),(10,7),
    (10,8),(10,9),(10,10),(10,11),(9,11),(8,11),(7,11),(6,11),
    (5,11),(4,11),(3,11),(2,11),(1,11),(1,10),(1,9),(1,8),(1,7),
    (1,6),(1,5),(1,4),(1,3),(1,2),(1,1),(2,1),(3,1),(4,1),(5,1),
    (6,1),(7,1),(8,1),(9,1),(10,1),(11,1),(11,2),(11,3),(11,4),
    (11,5),(11,6),(11,7),(11,8),(11,9),(11,10),(11,11),(11,12),
    (10,12),(9,12),(8,12),(7,12),(6,12),(5,12),(4,12),(3,12),
    (2,12),(1,12),(0,12),(0,11),(0,10),(0,9),(0,8),(0,7),(0,6),
    (0,5),(0,4),(0,3),(0,2),(0,1),(0,0),(1,0),(2,0),(3,0),(4,0),
    (5,0),(6,0),(7,0),(8,0),(9,0),(10,0),(11,0),(12,0),(12,1),
    (12,2),(12,3),(12,4),(12,5),(12,6),(12,7),(12,8),(12,9),
    (12,10),(12,11),(12,12),(12,13),(11,13),(10,13),(9,13),(8,13),
    (7,13),(6,13),(5,13),(4,13),(3,13),(2,13),(1,13),(0,13),
]

# --- UTILS -----------------------------------------------------------

def derive_addr(mnemonic: str) -> str:
    seed = Bip39SeedGenerator(mnemonic).Generate()
    acct = Bip44.FromSeed(seed, Bip44Coins.BITCOIN).Purpose().Coin().Account(0)
    return acct.Change(Bip44Changes.CHAIN_EXT).AddressIndex(0).PublicKey().ToAddress()

def validate_mnemonic(mnemonic: str) -> bool:
    return Bip39MnemonicValidator().IsValid(mnemonic)

# --- RUN -------------------------------------------------------------

# 1) Quick grid consistency check
for idx,row in enumerate(GRID):
    if len(row)!=14:
        print(f"❌ GRID ROW {idx} is length {len(row)} (should be 14)")
        sys.exit(1)

print("\n🔍 Word‐coord color check:")
for w,(r,c) in WORD_DATA:
    if not (0<=r<14 and 0<=c<14):
        print(f"  ❌ {w} @({r},{c}) out of bounds")
        sys.exit(1)
    tile = GRID[r][c]
    if tile not in ('Y','B'):
        print(f"  ❌ {w} @({r},{c}) → grid[{r}][{c}] = {tile} (expected Y or B)")
        sys.exit(1)
    print(f"  ✅ {w:<8} @({r:2d},{c:2d}) → {tile}")

# 2) Collect in spiral order
yellow_coords = []
blue_coords   = []

for step,(r,c) in enumerate(SPIRAL, start=1):
    if (r,c) not in coord_to_word:
        continue
    color = GRID[r][c]
    if color=='Y' and len(yellow_coords)<9:
        yellow_coords.append((r,c,step))
    if color=='B' and len(blue_coords)<9:
        blue_coords.append((r,c,step))
    if len(yellow_coords)==9 and len(blue_coords)==9:
        break

print(f"\n🟨 Collected {len(yellow_coords)}/9 yellow squares")
print(f"🟦 Collected {len(blue_coords)}/9 blue squares")
if len(yellow_coords)!=9 or len(blue_coords)!=9:
    print("❌ Tile count wrong—double-check your GRID or SPIRAL.")
    sys.exit(1)

# 3) Build and test both orders
for order_name, seq in (("Y+B", yellow_coords+blue_coords),
                        ("B+Y", blue_coords+yellow_coords)):
    words = [ coord_to_word[(r,c)] for r,c,_ in seq ]
    mnem  = " ".join(words)
    ok    = validate_mnemonic(mnem)
    addr  = derive_addr(mnem) if ok else None

    print("\n" + "-"*50)
    print(f"🔑 Order: {order_name}")
    print("Mnemonic:", mnem)
    print("Checksum OK?" , "✅" if ok else "❌")
    if ok:
        print("Derived Address:", addr)
        print("MATCH!" if addr==TARGET else "no match")
print("\nAll done.\n")

