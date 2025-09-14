import csv
from itertools import product
from mnemonic import Mnemonic
from bip32utils import BIP32Key
import hmac, hashlib

# === CONFIG ===
target = "1KfZGvwZxsvSmemoCmEV75uqcNzYBHjkHZ"
mnemo = Mnemonic("english")
output_file = "seed_results.csv"

# Baseline 12-slot order
base_slots = [
    "tower","moon","order","black","food",None,
    "day","time","proof","real","this","liberty"
]

slot6_candidates = ["subject", "breathe", "find", "hope"]
passphrases = ["", "this", "breathe"]

# === DERIVATION FUNCTIONS ===
def mnemonic_to_address_bip44(mnemonic, passphrase=""):
    seed = mnemo.to_seed(mnemonic, passphrase)
    master = BIP32Key.fromEntropy(seed)
    child = (master.ChildKey(44 + 0x80000000)
                    .ChildKey(0 + 0x80000000)
                    .ChildKey(0 + 0x80000000)
                    .ChildKey(0).ChildKey(0))
    return child.Address()

def mnemonic_to_address_electrum(mnemonic):
    seed = mnemo.to_seed(mnemonic, "")
    I = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()
    master = BIP32Key.fromEntropy(I[:64])
    child = master.ChildKey(0).ChildKey(0)
    return child.Address()

# === TESTING FUNCTION ===
def test_seed(seed_words, passphrase):
    phrase_str = " ".join(seed_words)
    checksum_valid = mnemo.check(phrase_str)

    addr_bip44, addr_electrum = "", ""
    match_found = False
    match_type = ""

    if checksum_valid:
        addr_bip44 = mnemonic_to_address_bip44(phrase_str, passphrase)
        addr_electrum = mnemonic_to_address_electrum(phrase_str)

        if addr_bip44 == target:
            match_found = True
            match_type = "BIP44"
        elif addr_electrum == target:
            match_found = True
            match_type = "Electrum"

    return {
        "phrase": phrase_str,
        "passphrase": passphrase,
        "checksum_valid": checksum_valid,
        "addr_bip44": addr_bip44,
        "addr_electrum": addr_electrum,
        "match": match_found,
        "match_type": match_type,
    }

# === MAIN ===
if __name__ == "__main__":
    print("=== Structured Seed Search with CSV Export ===")
    results = []
    for word6, pphrase in product(slot6_candidates, passphrases):
        seed_words = list(base_slots)
        seed_words[5] = word6
        print(f"Testing slot6='{word6}', passphrase='{pphrase}' ...")

        res = test_seed(seed_words, pphrase)
        results.append(res)

        if res["match"]:
            print(f"\nMATCH FOUND!\nType: {res['match_type']}\nSeed: {res['phrase']}\nPassphrase: {res['passphrase']}")
            break

    # Export to CSV
    with open(output_file, "w", newline="") as csvfile:
        fieldnames = ["phrase","passphrase","checksum_valid","addr_bip44","addr_electrum","match","match_type"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nSearch finished. Results saved to {output_file}")
