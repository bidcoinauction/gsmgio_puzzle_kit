import itertools
from bip_utils import (
    Bip39MnemonicValidator,
    Bip39SeedGenerator,
    Bip44,
    Bip44Coins,
    Bip44Changes,
)
from bip_utils.utils.mnemonic import MnemonicChecksumError
from tqdm import tqdm

# Target puzzle values
TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"

WORDS = [
    "frost", "because", "bright", "guilt", "grant", "lumber",
    "mountain", "either", "forward", "miracle", "charge",
    "foam", "capital", "argue", "initial", "juice", "chest", "memory"
]

# --------- Address derivation helper ----------
def derive_bip44_address(mnemonic: str) -> str:
    """
    Return first BIP44 legacy (m/44'/0'/0'/0/0) address.
    Uses Bip44Changes.CHAIN_EXT instead of raw 0 to be compatible with bip_utils 2.x
    """
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
    bip44_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)
    acct = (
        bip44_ctx
        .Purpose()
        .Coin()
        .Account(0)
        .Change(Bip44Changes.CHAIN_EXT)
        .AddressIndex(0)
    )
    return acct.PublicKey().ToAddress()

def is_valid_mnemonic(words_list):
    try:
        Bip39MnemonicValidator().Validate(" ".join(words_list))
        return True
    except MnemonicChecksumError:
        return False
    except Exception:
        return False

# --------- Heuristic permutations -------------
def heuristic_sequences(words):
    # 1. Rotations
    for i in range(len(words)):
        yield words[i:] + words[:i]
    # 2. Reverse full
    yield list(reversed(words))
    # 3. Reverse halves
    half = len(words)//2
    yield list(reversed(words[:half])) + list(reversed(words[half:]))
    # 4. Local 2,3,4,5-word reversals
    for size in [2, 3, 4, 5]:
        for i in range(len(words)-size+1):
            perm = words[:]
            perm[i:i+size] = reversed(perm[i:i+size])
            yield perm
    # 5. 6-6-6 block shuffle
    blocks = [words[:6], words[6:12], words[12:]]
    for block_perm in itertools.permutations(blocks):
        yield sum(block_perm, [])

# --------- Main Search ------------------------
def try_sequences(sequences, label):
    for seq in tqdm(sequences, desc=label):
        if not is_valid_mnemonic(seq):
            continue
        mnemonic = " ".join(seq)
        addr = derive_bip44_address(mnemonic)
        if addr == TARGET_ADDRESS:
            print("\n[+] MATCH FOUND!")
            print("Mnemonic:", mnemonic)
            print("Address:", addr)
            return True
    return False

def main():
    print(f"[+] Loaded {len(WORDS)} words.")
    # 1. Heuristic search
    if try_sequences(heuristic_sequences(WORDS), "Heuristic"):
        return
    print("[-] No match found with heuristics. Starting full brute force...")

    # 2. Full brute-force (very slow!)
    valid_perms = (p for p in itertools.permutations(WORDS) if is_valid_mnemonic(p))
    if try_sequences(valid_perms, "BruteForce"):
        return
    print("[-] No valid permutation produced the target address.")

if __name__ == "__main__":
    main()
