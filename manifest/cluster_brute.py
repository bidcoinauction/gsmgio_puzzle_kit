import itertools
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from mnemonic import Mnemonic

mnemo = Mnemonic("english")
TARGET = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"

CLUSTERS = [
    ["bright", "miracle", "memory", "initial", "lumber"],
    ["charge", "foam", "juice", "chest", "argue"],
    ["because", "frost", "either", "guilt"],
    ["grant", "mountain", "forward", "capital"],
]

def derive(words):
    phrase = " ".join(words)
    if not mnemo.check(phrase):
        return None
    seed = Bip39SeedGenerator(phrase).Generate()
    acct = Bip44.FromSeed(seed, Bip44Coins.BITCOIN).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT)
    return acct.AddressIndex(0).PublicKey().ToAddress()

for c1 in itertools.permutations(CLUSTERS[0]):
    for c2 in itertools.permutations(CLUSTERS[1]):
        for c3 in itertools.permutations(CLUSTERS[2]):
            for c4 in itertools.permutations(CLUSTERS[3]):
                words = list(c1 + c2 + c3 + c4)
                addr = derive(words)
                if addr == TARGET:
                    print("🎯 MATCH FOUND:", " ".join(words))
                    print("→", addr)
                    exit()
