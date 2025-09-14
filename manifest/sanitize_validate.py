#!/usr/bin/env python3
# sanitize_and_validate.py

from bip_utils import (
    Bip39MnemonicValidator,
    Bip39SeedGenerator,
    Bip44, Bip44Coins, Bip44Changes
)

# ——— YOUR CURRENT BEST‐GUESS PHRASE ———
BASE = (
    "mountain memory grant foam initial forward frost miracle "
    "lumber juice guilt chest charge capital either bright "
    "because argue"
)

TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"

def derive_addr(mnemonic: str) -> str:
    seed = Bip39SeedGenerator(mnemonic).Generate()
    acct = (
        Bip44.FromSeed(seed, Bip44Coins.BITCOIN)
        .Purpose()
        .Coin()
        .Account(0)
    )
    return acct.Change(Bip44Changes.CHAIN_EXT).AddressIndex(0).PublicKey().ToAddress()

def main():
    validator = Bip39MnemonicValidator()
    words = BASE.split()
    candidates = set()

    # 1) Base as‐is, lowercase, Titlecase
    candidates.add(" ".join(words))
    candidates.add(" ".join(w.lower() for w in words))
    candidates.add(" ".join(w.capitalize() for w in words))

    # 2) Swap every adjacent pair once
    for i in range(len(words) - 1):
        w2 = words.copy()
        w2[i], w2[i+1] = w2[i+1], w2[i]
        candidates.add(" ".join(w2))

    # 3) Two‐swap combinations (optional: if adjacent didn't work)
    # Uncomment if you want to try all 2-swap pairs (slow: ~153 combos)
    # from itertools import combinations
    # for i, j in combinations(range(len(words)), 2):
    #     w2 = words.copy()
    #     w2[i], w2[j] = w2[j], w2[i]
    #     candidates.add(" ".join(w2))

    print(f"🔍 Testing {len(candidates)} candidate mnemonics…\n")

    for mn in sorted(candidates):
        if not validator.IsValid(mn):
            continue
        addr = derive_addr(mn)
        print("✅ VALID CHECKSUM:", mn)
        print("   → Derived address:", addr)
        if addr == TARGET_ADDRESS:
            print("\n🎯 MATCH! This mnemonic unlocks the prize. 🎉")
            return

    print("\n❌ None of the sanitized variants matched your target address.")

if __name__ == "__main__":
    main()
