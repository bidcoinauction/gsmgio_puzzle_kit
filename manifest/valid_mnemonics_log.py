import csv
import itertools
from collections import Counter
from bip_utils import Bip44, Bip44Coins, Bip44Changes, Bip39SeedGenerator
from mnemonic import Mnemonic

TARGET_ADDR = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
mnemo = Mnemonic("english")

# Each entry: (row, col), char, BIP39 word
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

def sort_linear(pairs):
    return sorted(pairs, key=lambda x: x[0][0] * 35 + x[0][1])

def sort_zigzag(pairs):
    return sorted(pairs, key=lambda x: (x[0][0], x[0][1] if x[0][0] % 2 == 0 else -x[0][1]))

def sort_ascii(pairs):
    return sorted(pairs, key=lambda x: ord(x[1]))

def brute_force_nearby_with_logging(words, strategy_name, csv_writer):
    print(f"\n🔍 Brute-forcing {strategy_name} ordering...")
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
                csv_writer.writerow([strategy_name, mnemonic, addr])
                if addr == TARGET_ADDR:
                    print("\n🎉 MATCH FOUND!")
                    print("Mnemonic:", mnemonic)
                    print("Derived:", addr)
                    return
    print(f"❌ No match in {checked} permutations.")

# Run and export
with open("valid_mnemonics_log.csv", "w", newline="") as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["Strategy", "Mnemonic", "Derived Address"])

    strategies = {
        "Polybius Linear": sort_linear(PAIRS),
        "Zigzag": sort_zigzag(PAIRS),
        "ASCII": sort_ascii(PAIRS),
    }

    for name, sorted_list in strategies.items():
        word_list = [w for _, _, w in sorted_list]
        brute_force_nearby_with_logging(word_list, name, csv_writer)
