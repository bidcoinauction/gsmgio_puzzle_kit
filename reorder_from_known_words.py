import math
from mnemonic import Mnemonic
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes

# --- Known alphabetized 18 BIP39 words (DO NOT REMAP)
BIP39_WORDS = [
    "forward", "bright", "argue", "capital", "chest", "miracle",
    "charge", "juice", "memory", "grant", "mountain", "initial",
    "guilt", "frost", "either", "because", "foam", "lumber"
]

# --- Pair values used only as coordinates/instructions
PAIR_VALUES = [
    "kr", "4E", "68", "8f", "J1", "FY", "b0", "dE", "c5",
    "M7", "sU", "TW", "NH", "Aa", "98", "vD", "rm", "Xe"
]

mnemo = Mnemonic("english")
TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"

# Utility
def base36_char(c):
    return int(c) if c.isdigit() else 10 + ord(c.upper()) - ord('A')

# Build grid coordinates for each pair
coords = []
for i, p in enumerate(PAIR_VALUES):
    r = base36_char(p[0])
    c = base36_char(p[1])
    coords.append((r, c, i))  # i is original word index

# --- Traversal Strategies (return reordered indices)
def spiral_order():
    center = (18, 18)
    def dist_angle(pt):
        dx, dy = pt[0] - center[0], pt[1] - center[1]
        return (abs(dx) + abs(dy), math.atan2(dy, dx))
    sorted_coords = sorted(coords, key=lambda x: dist_angle((x[0], x[1])))
    return [x[2] for x in sorted_coords]

def mirrored_y_order():
    sorted_coords = sorted(coords, key=lambda x: (-x[1], x[0]))
    return [x[2] for x in sorted_coords]

def zigzag_order():
    from collections import defaultdict
    row_dict = defaultdict(list)
    for item in coords:
        row_dict[item[0]].append(item)
    result = []
    for r in sorted(row_dict):
        row = sorted(row_dict[r], key=lambda x: x[1], reverse=(r % 2 == 1))
        result.extend([x[2] for x in row])
    return result

# Run strategies
strategies = {
    "Spiral": spiral_order,
    "Mirrored-Y": mirrored_y_order,
    "ZigZag": zigzag_order
}

for label, func in strategies.items():
    print(f"\n[Testing Strategy] {label}")
    order = func()
    reordered_words = [BIP39_WORDS[i] for i in order]
    phrase = " ".join(reordered_words)
    print("Mnemonic:", phrase)
    if mnemo.check(phrase):
        print("✅ Valid BIP39 checksum!")
        seed = Bip39SeedGenerator(phrase).Generate()
        bip44_addr = Bip44.FromSeed(seed, Bip44Coins.BITCOIN).Purpose().Coin().Account(0)\
                        .Change(Bip44Changes.CHAIN_EXT).AddressIndex(0).PublicKey().ToAddress()
        print("Derived Address:", bip44_addr)
        if bip44_addr == TARGET_ADDRESS:
            print("🎯 MATCHES TARGET ADDRESS!")
            break
    else:
        print("❌ Invalid BIP39 checksum")
