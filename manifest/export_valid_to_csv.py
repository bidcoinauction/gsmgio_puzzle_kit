import itertools
import csv
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from mnemonic import Mnemonic

mnemo = Mnemonic("english")
WORDS = ["frost", "argue", "mountain", "chest", "guilt", "memory", "bright", "juice", "initial",
         "because", "lumber", "grant", "foam", "charge", "either", "forward", "capital", "miracle"]

def derive_address(words):
    phrase = " ".join(words)
    if not mnemo.check(phrase):
        return None
    seed = Bip39SeedGenerator(phrase).Generate()
    acct = Bip44.FromSeed(seed, Bip44Coins.BITCOIN).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT)
    addr = acct.AddressIndex(0).PublicKey().ToAddress()
    return (phrase, addr)

with open("valid_mnemonics.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Mnemonic", "Address"])
    for perm in itertools.permutations(WORDS):
        result = derive_address(list(perm))
        if result:
            writer.writerow(result)
