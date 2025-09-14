from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from mnemonic import Mnemonic

PAIRS = [
    ((10, 27), 'e', "frost"),
    ((1, 18),  ':', "argue"),
    ((6, 8),   's', "mountain"),
    ((23, 1),  'u', "chest"),
    ((22, 21), 'f', "guilt"),
    ((29, 19), 'a', "memory"),
    ((32, 4),  ' ', "bright"),
    ((15, 28), 'r', "juice"),
    ((20, 18), 'd', "initial"),
    ((31, 15), ':', "because"),
    ((8, 20),  'h', "lumber"),
    ((20, 0),  'f', "grant"),
    ((7, 20),  'm', "foam"),
    ((2, 20),  'k', "charge"),
    ((25, 27), 'e', "either"),
    ((26, 30), 's', "forward"),
    ((8, 28),  's', "capital"),
    ((30, 31), '.', "miracle"),
]

mnemo = Mnemonic("english")
TARGET = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"

def derive_address(mnemonic):
    seed = Bip39SeedGenerator(mnemonic).Generate()
    acct = Bip44.FromSeed(seed, Bip44Coins.BITCOIN).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT)
    return acct.AddressIndex(0).PublicKey().ToAddress()

# Generate deltas and sort based on dx/dy movement
deltas = []
for i in range(len(PAIRS) - 1):
    (r1, c1), _, _ = PAIRS[i]
    (r2, c2), _, _ = PAIRS[i+1]
    dx, dy = r2 - r1, c2 - c1
    deltas.append((abs(dx) + abs(dy), PAIRS[i]))

# Fallback sort by delta-magnitude
sorted_words = [w for _, (_, _, w) in sorted(deltas + [(0, PAIRS[-1])])]
mnemonic = " ".join(sorted_words)
if mnemo.check(mnemonic):
    addr = derive_address(mnemonic)
    print(f"✅ Valid: {addr}")
    if addr == TARGET:
        print("🎯 MATCH FOUND!")
else:
    print("❌ Invalid mnemonic")
