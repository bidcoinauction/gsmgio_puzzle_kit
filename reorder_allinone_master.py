import math
import itertools
from mnemonic import Mnemonic
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes

# --- Known 18 BIP39 words (alphabetized)
BIP39_WORDS = [
    "forward", "bright", "argue", "capital", "chest", "miracle",
    "charge", "juice", "memory", "grant", "mountain", "initial",
    "guilt", "frost", "either", "because", "foam", "lumber"
]

# --- Decoded pair coordinates (base36 converted)
PAIR_VALUES = [
    "kr", "4E", "68", "8f", "J1", "FY", "b0", "dE", "c5",
    "M7", "sU", "TW", "NH", "Aa", "98", "vD", "rm", "Xe"
]

TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
LOG_FILE = "valid_mnemonics.log"

mnemo = Mnemonic("english")

def base36_char(c):
    return int(c) if c.isdigit() else 10 + ord(c.upper()) - ord('A')

# Convert pairs to (r, c, i)
coords = []
for i, p in enumerate(PAIR_VALUES):
    r = base36_char(p[0])
    c = base36_char(p[1])
    coords.append((r, c, i))

def spiral_order():
    center = (18, 18)
    def dist_angle(pt):
        dx, dy = pt[0] - center[0], pt[1] - center[1]
        return (abs(dx) + abs(dy), math.atan2(dy, dx))
    return [x[2] for x in sorted(coords, key=lambda x: dist_angle((x[0], x[1])))]

def mirrored_y_order():
    return [x[2] for x in sorted(coords, key=lambda x: (-x[1], x[0]))]

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

def diagonal_order():
    return [x[2] for x in sorted(coords, key=lambda x: (x[0] + x[1], x[0]))]

strategies = {
    "Spiral": spiral_order,
    "Mirrored-Y": mirrored_y_order,
    "Zigzag": zigzag_order,
    "Diagonal": diagonal_order,
}

def derive_btc_address(mnemonic):
    seed = Bip39SeedGenerator(mnemonic).Generate()
    addr = Bip44.FromSeed(seed, Bip44Coins.BITCOIN).Purpose().Coin().Account(0)        .Change(Bip44Changes.CHAIN_EXT).AddressIndex(0).PublicKey().ToAddress()
    return addr

def log_valid(strategy, phrase, addr, match):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{strategy}]{' 🎯' if match else ''}\n{phrase}\n{addr}\n\n")

# --- MAIN EXECUTION
open(LOG_FILE, "w").close()  # clear log
for label, func in strategies.items():
    print(f"\n[Testing Strategy] {label}")
    order = func()
    reordered = [BIP39_WORDS[i] for i in order]
    phrase = " ".join(reordered)

    if mnemo.check(phrase):
        addr = derive_btc_address(phrase)
        print("✅ Valid:", phrase)
        print("→", addr)
        log_valid(label, phrase, addr, addr == TARGET_ADDRESS)
        continue

    # Fuzzy: Try all 2-word swaps (153 combos)
    found = False
    for i, j in itertools.combinations(range(18), 2):
        swapped = reordered[:]
        swapped[i], swapped[j] = swapped[j], swapped[i]
        test_phrase = " ".join(swapped)
        if mnemo.check(test_phrase):
            addr = derive_btc_address(test_phrase)
            print(f"🛠️  Fix [{label}] Swap ({i},{j})")
            print("✅", test_phrase)
            print("→", addr)
            log_valid(f"{label} (swap {i},{j})", test_phrase, addr, addr == TARGET_ADDRESS)
            found = True
            break
    if not found:
        print("❌ No valid phrase found.")
