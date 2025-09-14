#!/usr/bin/env python3
from bip_utils import (
    Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
)

TARGET = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"

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
    (7,13),(6,13),(5,13),(4,13),(3,13),(2,13),(1,13),(0,13)
]

coord_to_word = {
    (4,6): 'grant',    (4,7): 'capital',
    (8,6): 'bright',   (8,4): 'forward',
    (7,9): 'miracle',  (11,7): 'because',
    (12,2): 'memory',  (13,8): 'initial',
    (9,13): 'guilt',   (6,8): 'foam',
    (6,5): 'charge',   (5,2): 'lumber',
    (8,10):'mountain',(9,1): 'chest',
    (10,4):'argue',    (11,10):'either',
    (12,11):'juice',   (13,3): 'frost'
}

# build spiral index
spiral_index = {c: i+1 for i,c in enumerate(SPIRAL)}

print("\nWord     | Coord   | Color | SpiralStep")
print("---------+---------+-------+-----------")
blue_count = yellow_count = 0
triples = []

for coord, w in coord_to_word.items():
    r,c = coord
    color = GRID[r][c]
    step  = spiral_index.get(coord, None)
    print(f"{w:<8} | {coord!s:<7} |  {color}    | {step}")
    if step is None:
        print("   ⚠️  no spiral entry for this coord!")
    if color=='B':   blue_count += 1
    elif color=='Y': yellow_count += 1
    else:
        print(f"   ❌  {w} is {color}, not B or Y—check GRID")

    # keep for later
    triples.append((w, color, step))

print(f"\n🟦 Blue tiles found:   {blue_count}")
print(f"🟨 Yellow tiles found: {yellow_count}\n")

# show partial table
print("Partial (word, step) for each color:")
print(" Blue words:")
for w,col,st in triples:
    if col=='B': print(f"  - {w:10s} @ step {st}")
print(" Yellow words:")
for w,col,st in triples:
    if col=='Y': print(f"  - {w:10s} @ step {st}")

# build full by matching each word to both
blue_map   = {w:st for w,col,st in triples if col=='B'}
yellow_map = {w:st for w,col,st in triples if col=='Y'}

combined = []
for w in sorted(coord_to_word.values()):
    b = blue_map.get(w)
    y = yellow_map.get(w)
    combined.append((w,b,y))

# two naive concatenations
names = ["Y→B","B→Y"]
orders = [
    [w for w,_,_ in combined if w in yellow_map] + [w for w,_,_ in combined if w in blue_map],
    [w for w,_,_ in combined if w in blue_map] + [w for w,_,_ in combined if w in yellow_map],
]

from bip_utils import Bip39MnemonicValidator
validator = Bip39MnemonicValidator()
from bip_utils import Bip39SeedGenerator, Bip44

print("\nTesting baseline mnemonics (alphabetical in each half):")
for name, order in zip(names, orders):
    phrase = " ".join(order)
    ok = validator.IsValid(phrase)
    addr = None
    if ok:
        seed = Bip39SeedGenerator(phrase).Generate()
        addr = (Bip44.FromSeed(seed, Bip44Coins.BITCOIN)
                     .Purpose().Coin().Account(0)
                     .Change(Bip44Changes.CHAIN_EXT)
                     .AddressIndex(0)
                     .PublicKey().ToAddress())
    print(f" [{name}]  checksum={'OK' if ok else '✗'}, derived addr={addr or '<invalid>'}")

print("\n➡️  Now you can see exactly which word/coord/color/step is missing or mis‐typed in your GRID.")
