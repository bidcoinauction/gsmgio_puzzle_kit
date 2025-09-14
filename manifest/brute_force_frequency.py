import itertools
from bip_utils import Bip44, Bip44Coins, Bip44Changes, Bip39SeedGenerator
from mnemonic import Mnemonic

TARGET_ADDR = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
mnemo = Mnemonic("english")

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

def derive_address(mnemonic):
    seed = Bip39SeedGenerator(mnemonic).Generate()
    bip44 = Bip44.FromSeed(seed, Bip44Coins.BITCOIN)
    acct = bip44.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT)
    return acct.AddressIndex(0).PublicKey().ToAddress()

# Sort by character frequency
from collections import Counter
def get_freq_base():
    chars = [char for _, char, _ in PAIRS]
    counts = Counter(chars)
    sorted_pairs = sorted(PAIRS, key=lambda x: (counts[x[1]], ord(x[1])))
    return [w for _, _, w in sorted_pairs]

# Brute-force nearby permutations
def brute_force_nearby(words):
    print("\n🔁 Brute-forcing around Char_Frequency ordering...")
    checked = 0
    for win_size in [3, 4, 5]:
        for i in range(len(words) - win_size + 1):
            prefix = words[:i]
            window = words[i:i + win_size]
            suffix = words[i + win_size:]
            for perm in itertools.permutations(window):
                candidate = prefix + list(perm) + suffix
                mnemonic = " ".join(candidate)
                if not mnemo.check(mnemonic):
                    continue
                addr = derive_address(mnemonic)
                checked += 1
                print(f"[{checked}] {addr}")
                if addr == TARGET_ADDR:
                    print("\n✅ MATCH FOUND!")
                    print("Mnemonic:", mnemonic)
                    print("Derived:", addr)
                    return
                # Log valid but non-matching
                with open("valid_phrases_log.txt", "a") as f:
                    f.write(f"{mnemonic} → {addr}\n")
    print(f"❌ No match in {checked} permutations.")

if __name__ == "__main__":
    base_words = get_freq_base()
    brute_force_nearby(base_words)
