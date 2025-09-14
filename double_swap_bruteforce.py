# double_swap_bruteforce.py

from bip_utils import Bip39MnemonicValidator, Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from itertools import combinations

# --- Configuration ---

BASE_MNEMONIC = "initial guilt memory because forward miracle capital grant bright frost chest juice lumber either argue mountain charge foam"
TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"

words = BASE_MNEMONIC.split()
assert len(words) == 18

# --- Helpers ---

def is_valid(mn: str) -> bool:
    try:
        Bip39MnemonicValidator().Validate(mn)
        return True
    except:
        return False

def derive_addr(mn: str) -> str:
    seed = Bip39SeedGenerator(mn).Generate()
    acc = Bip44.FromSeed(seed, Bip44Coins.BITCOIN).Purpose().Coin().Account(0)
    return acc.Change(Bip44Changes.CHAIN_EXT).AddressIndex(0).PublicKey().ToAddress()

# --- Double-Swap Brute ---

print(f"🔍 Trying all double-swap combinations (~{(18*17//2)**2} cases)…")

found = False
pairs = list(combinations(range(18), 2))

for i, j in pairs:
    # first swap
    tmp1 = words.copy()
    tmp1[i], tmp1[j] = tmp1[j], tmp1[i]
    for k, l in pairs:
        # second swap
        tmp2 = tmp1.copy()
        tmp2[k], tmp2[l] = tmp2[l], tmp2[k]
        candidate = " ".join(tmp2)
        
        if not is_valid(candidate):
            continue
        
        addr = derive_addr(candidate)
        if addr == TARGET_ADDRESS:
            print("\n✅ MATCH FOUND!")
            print(f"Swapped pairs: ({i},{j}) and ({k},{l})")
            print("Mnemonic:", candidate)
            print("Derived Address:", addr)
            found = True
            break
    if found:
        break

if not found:
    print("❌ No double-swap produced the target address.")
