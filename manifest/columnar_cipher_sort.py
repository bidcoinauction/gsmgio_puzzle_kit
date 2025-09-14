from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from mnemonic import Mnemonic

CHARS = ['e', ':', 's', 'u', 'f', 'a', ' ', 'r', 'd', ':', 'h', 'f', 'm', 'k', 'e', 's', 's', '.']
WORDS = ["frost", "argue", "mountain", "chest", "guilt", "memory", "bright", "juice", "initial",
         "because", "lumber", "grant", "foam", "charge", "either", "forward", "capital", "miracle"]

TARGET = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
mnemo = Mnemonic("english")

# Sort words by ASCII of corresponding char
pairs = list(zip(CHARS, WORDS))
sorted_words = [w for _, w in sorted(pairs, key=lambda x: ord(x[0]))]
mnemonic = " ".join(sorted_words)

if mnemo.check(mnemonic):
    seed = Bip39SeedGenerator(mnemonic).Generate()
    acct = Bip44.FromSeed(seed, Bip44Coins.BITCOIN).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT)
    addr = acct.AddressIndex(0).PublicKey().ToAddress()
    print("✅ Valid:", addr)
    if addr == TARGET:
        print("🎯 MATCH FOUND!")
else:
    print("❌ Invalid mnemonic")
