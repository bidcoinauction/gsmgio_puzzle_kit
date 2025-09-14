import itertools
from multiprocessing import Pool, cpu_count
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from mnemonic import Mnemonic

WORDS = ["frost", "argue", "mountain", "chest", "guilt", "memory", "bright", "juice", "initial",
         "because", "lumber", "grant", "foam", "charge", "either", "forward", "capital", "miracle"]
TARGET = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
mnemo = Mnemonic("english")

def check_perm(perm):
    phrase = " ".join(perm)
    if mnemo.check(phrase):
        seed = Bip39SeedGenerator(phrase).Generate()
        acct = Bip44.FromSeed(seed, Bip44Coins.BITCOIN).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT)
        addr = acct.AddressIndex(0).PublicKey().ToAddress()
        if addr == TARGET:
            return f"🎯 MATCH FOUND: {phrase} → {addr}"
    return None

if __name__ == "__main__":
    with Pool(cpu_count()) as pool:
        for result in pool.imap_unordered(check_perm, itertools.permutations(WORDS)):
            if result:
                print(result)
                break
