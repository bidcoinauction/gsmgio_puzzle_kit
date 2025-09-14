#!/usr/bin/env python3
import string
from bip_utils import Bip39MnemonicValidator, Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes

# ── 1) Your base 18-word list (0-based positions) ───────────────────────────
base = [
    "charge",   #0
    "mountain", #1
    "foam",     #2
    "lumber",   #3
    "capital",  #4
    "frost",    #5
    "argue",    #6
    "juice",    #7
    "grant",    #8
    "initial",  #9
    "guilt",    #10
    "chest",    #11
    "either",   #12
    "forward",  #13
    "memory",   #14
    "miracle",  #15
    "because",  #16
    "bright"    #17
]

# ── 2) Parse the clue ──────────────────────────────────────────────────────
clue = "ksmhse:rfdfuesa"
from_str, to_str = clue.split(":")

def letters_to_indices(s):
    """ Convert letters→0–25 then mod 18 """
    return [ (string.ascii_lowercase.index(c) % 18) for c in s ]

from_idx = letters_to_indices(from_str)
to_idx   = letters_to_indices(to_str)

print("Parsed moves:")
for f,t in zip(from_idx, to_idx):
    print(f"  move base[{f}] → new[{t}]")

# ── 3) Apply the moves and fill remaining slots ─────────────────────────────
new = [None]*18
used = set()

# a) Move the specified words
for f, t in zip(from_idx, to_idx):
    new[t]    = base[f]
    used.add(f)

# b) Collect unused words in original order
remaining = [w for i,w in enumerate(base) if i not in used]

# c) Fill empty slots
ri = 0
for i in range(18):
    if new[i] is None:
        new[i] = remaining[ri]
        ri += 1

mnemonic = " ".join(new)
print("\n🗝 Final 18-word mnemonic:\n", mnemonic)

# ── 4) Validate & Derive BTC Address ────────────────────────────────────────
validator = Bip39MnemonicValidator()
if not validator.IsValid(mnemonic):
    print("\n❌ Checksum INVALID. Something went wrong.")
    exit(1)

seed = Bip39SeedGenerator(mnemonic).Generate()
acct = (
    Bip44.FromSeed(seed, Bip44Coins.BITCOIN)
         .Purpose().Coin().Account(0)
         .Change(Bip44Changes.CHAIN_EXT)
         .AddressIndex(0)
)
address = acct.PublicKey().ToAddress()

print("\n✅ Checksum valid.")
print("Derived address:", address)
if address == "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe":
    print("🎯 Bingo! This is the prize address.")
else:
    print("⚠️ Address does NOT match the target. Double-check your inputs.")
