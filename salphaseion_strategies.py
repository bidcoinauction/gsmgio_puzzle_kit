import csv
from collections import Counter
from bip_utils import Bip44, Bip44Coins, Bip44Changes, Bip39SeedGenerator
from mnemonic import Mnemonic

TARGET_ADDR = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
mnemo = Mnemonic("english")

# Each entry: (row, col), decoded char, BIP39 word
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

# === Address derivation ===
def derive_address(mnemonic):
    seed = Bip39SeedGenerator(mnemonic).Generate()
    bip44 = Bip44.FromSeed(seed, Bip44Coins.BITCOIN)
    acct = bip44.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT)
    return acct.AddressIndex(0).PublicKey().ToAddress()

# === Sorting strategies ===
def sort_by_linear(pairs):
    return sorted(pairs, key=lambda x: x[0][0] * 35 + x[0][1])

def sort_by_manhattan_topleft(pairs):
    return sorted(pairs, key=lambda x: abs(x[0][0]) + abs(x[0][1]))

def sort_by_manhattan_bottomright(pairs):
    return sorted(pairs, key=lambda x: abs(35 - x[0][0]) + abs(35 - x[0][1]))

def sort_by_char_rank(pairs):
    sequence = ":sfurad hmfkes.s"
    rank = {ch: i for i, ch in enumerate(sequence)}
    return sorted(pairs, key=lambda x: rank.get(x[1], 999))

def sort_by_char_frequency(pairs):
    counts = Counter([c for _, c, _ in pairs])
    return sorted(pairs, key=lambda x: (counts[x[1]], ord(x[1])))

# === Test and log ===
def test_strategy(name, sorted_pairs, csv_writer):
    words = [w for _, _, w in sorted_pairs]
    phrase = " ".join(words)
    if not mnemo.check(phrase):
        print(f"[-] {name}: Invalid BIP39 mnemonic.")
        return
    addr = derive_address(phrase)
    print(f"[{name}] → {addr}")
    csv_writer.writerow([name, phrase, addr])
    if addr == TARGET_ADDR:
        print(f"\n🎯 MATCH FOUND ✅\n{phrase}\n→ {addr}")
        exit(0)

# === Main ===
def main():
    strategies = {
        "Linear": sort_by_linear(PAIRS),
        "Manhattan_TopLeft": sort_by_manhattan_topleft(PAIRS),
        "Manhattan_BottomRight": sort_by_manhattan_bottomright(PAIRS),
        "Char_Rank": sort_by_char_rank(PAIRS),
        "Char_Frequency": sort_by_char_frequency(PAIRS),
    }

    with open("salphaseion_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Strategy", "Mnemonic", "BTC Address"])
        for name, sorted_list in strategies.items():
            test_strategy(name, sorted_list, writer)

if __name__ == "__main__":
    main()
