#!/usr/bin/env python3
from bip_utils import (
    Bip39MnemonicValidator, Bip39SeedGenerator,
    Bip44, Bip44Coins, Bip44Changes
)

TARGET = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"

# 1) Your 14×14 grid transcription (K=black, B=blue, Y=yellow, W=white)
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

# 2) Verified 196-entry CCW spiral (start at center (6,6))
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

# 3) Map coords → word
coord_to_word = {
    (4,6): 'grant',    (4,7): 'capital',
    (8,6): 'bright',   (8,4): 'forward',
    (7,9): 'miracle',  (11,7): 'because',
    (12,2): 'memory',  (13,8): 'initial',
    (9,13): 'guilt',   (6,8): 'foam',
    (6,5): 'charge',   (5,2): 'lumber',
    (8,10): 'mountain',(9,1): 'chest',
    (10,4): 'argue',   (11,10): 'either',
    (12,11): 'juice',  (13,3): 'frost'
}

# Build step‐lookup: coord → index (1–196)
spiral_index = {coord: idx+1 for idx, coord in enumerate(SPIRAL)}

# 4) Collect triples
triples = []
for coord, w in coord_to_word.items():
    step = spiral_index.get(coord)
    color = GRID[coord[0]][coord[1]]
    if color not in ('B','Y'):
        raise RuntimeError(f"{w} at {coord} is neither B nor Y")
    if color == 'B':
        bstep = step; ystep = None
    else:
        bstep = None; ystep = step
    triples.append([w, bstep, ystep])

# Now we need to fill in the missing side:
# there should be exactly 9 Y-step and 9 B-step entries.
# Let's split the two lists, then re-assign by matching words.
blue_words  = [t for t in triples if t[1] is not None]
yellow_words= [t for t in triples if t[2] is not None]

# Sanity
assert len(blue_words)==9 and len(yellow_words)==9, \
       f"Expected 9/9 colors, got {len(yellow_words)}/{len(blue_words)}"

# Re‐merge each word gets both B & Y:
full = []
for w,_,_ in triples:
    b = next(t[1] for t in blue_words  if t[0]==w)
    y = next(t[2] for t in yellow_words if t[0]==w)
    full.append((w, b, y))

# 5) Print the table
print("\nWord            BlueStep   YellowStep")
print("----            --------   ----------")
for w,b,y in sorted(full, key=lambda t: t[0]):
    print(f"{w:<15}{b:<11}{y}")

# 6) Try your two simple concat orders (alphabetical)
mnemo = [w for w,_,_ in sorted(full, key=lambda t:t[0])]
YplusB = mnemo[:9] + mnemo[9:]
BplusY = mnemo[9:] + mnemo[:9]

validator = Bip39MnemonicValidator()
def derive_btc(mn:str)->str:
    seed = Bip39SeedGenerator(mn).Generate()
    addr = (Bip44.FromSeed(seed, Bip44Coins.BITCOIN)
                 .Purpose().Coin().Account(0)
                 .Change(Bip44Changes.CHAIN_EXT)
                 .AddressIndex(0)
                 .PublicKey().ToAddress())
    return addr

for name, order in [("Y→B", YplusB), ("B→Y", BplusY)]:
    phrase = " ".join(order)
    ok   = validator.IsValid(phrase)
    addr = derive_btc(phrase) if ok else "<bad checksum>"
    print(f"\n[{name}] checksum={'OK' if ok else '✗'}, addr={addr}")

print("\n\nNow you have:")
print(" • the exact (word,blue,yellow) table")
print(" • the two simplest candidate mnemonics")
print("\nNext step: apply your refined sort/permutation to `full` until you hit one whose")
print("BIP39 checksum is OK and derives your target address.")
