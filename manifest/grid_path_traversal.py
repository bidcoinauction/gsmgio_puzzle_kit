import math
import re
from mnemonic import Mnemonic
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes

# --- 18 extracted 2-character pairs from salphaseion ROT13 decoding
PAIR_VALUES = [
    "kr", "4E", "68", "8f", "J1", "FY", "b0", "dE", "c5",
    "M7", "sU", "TW", "NH", "Aa", "98", "vD", "rm", "Xe"
]

# Load BIP39 English wordlist
with open("english.txt") as f:
    BIP39_WORDS = f.read().splitlines()

mnemo = Mnemonic("english")
TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"

def base36_char(c):
    return int(c) if c.isdigit() else 10 + ord(c.upper()) - ord('A')

# Map pairs to grid coordinates and BIP39 words
coords = []
for p in PAIR_VALUES:
    r = base36_char(p[0])
    c = base36_char(p[1])
    idx = r * 36 + c
    word = BIP39_WORDS[idx % 2048]
    coords.append((r, c, p, word))

print(f"[+] Mapped {len(coords)} pairs to (r,c) and BIP39 words")

# --- Traversal Strategies ---
def spiral_traversal(coord_list):
    # Sort by Manhattan distance from center (18,18) and by angle
    center = (18, 18)
    def distance_and_angle(pt):
        dx, dy = pt[0] - center[0], pt[1] - center[1]
        dist = abs(dx) + abs(dy)
        angle = math.atan2(dy, dx)
        return (dist, angle)

    return sorted(coord_list, key=lambda x: distance_and_angle((x[0], x[1])))

def mirrored_y_traversal(coord_list):
    # Mirror over Y-axis (sort by col descending, then row)
    return sorted(coord_list, key=lambda x: (-x[1], x[0]))

def zigzag_traversal(coord_list):
    # Sort rows ascending; even rows → left to right, odd rows → right to left
    from collections import defaultdict
    row_dict = defaultdict(list)
    for item in coord_list:
        row_dict[item[0]].append(item)
    sorted_words = []
    for r in sorted(row_dict):
        row = sorted(row_dict[r], key=lambda x: x[1], reverse=(r % 2 == 1))
        sorted_words.extend(row)
    return sorted_words

# --- Try all strategies
strategies = {
    "Spiral": spiral_traversal,
    "Mirrored-Y": mirrored_y_traversal,
    "ZigZag": zigzag_traversal
}

for label, strategy in strategies.items():
    print(f"\n[Testing Strategy] {label}")
    ordered = strategy(coords)
    words = [x[3] for x in ordered]
    phrase = " ".join(words)
    print("Mnemonic:", phrase)
    if mnemo.check(phrase):
        print("✅ Valid BIP39 checksum!")
        seed = Bip39SeedGenerator(phrase).Generate()
        bip44_addr = Bip44.FromSeed(seed, Bip44Coins.BITCOIN).Purpose().Coin().Account(0)\
                        .Change(Bip44Changes.CHAIN_EXT).AddressIndex(0).PublicKey().ToAddress()
        print("Derived BIP44 Address:", bip44_addr)
        if bip44_addr == TARGET_ADDRESS:
            print("🎯 MATCHES TARGET ADDRESS!")
            break
    else:
        print("❌ Invalid BIP39 checksum")
