import itertools
from mnemonic import Mnemonic
from bip_utils import Bip44, Bip44Coins, Bip44Changes, Bip39SeedGenerator

TARGET_ADDR = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
LOG_FILE = "non_matching_valid_mnemonics.log"
mnemo = Mnemonic("english")

def derive_first_bip44_address(mnemonic):
    seed = Bip39SeedGenerator(mnemonic).Generate()
    bip44 = Bip44.FromSeed(seed, Bip44Coins.BITCOIN)
    account = bip44.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT)
    return account.AddressIndex(0).PublicKey().ToAddress()

def check_all_windows(base_words, strategy_name):
    print(f"\n=== Strategy: {strategy_name} ===")
    checked = 0
    found = False
    with open(LOG_FILE, "a") as log:
        log.write(f"\n--- {strategy_name} ---\n")
        for win_size in [3, 4, 5]:
            print(f"[+] Window size {win_size}...")
            for i in range(len(base_words) - win_size + 1):
                prefix = base_words[:i]
                window = base_words[i:i + win_size]
                suffix = base_words[i + win_size:]
                for perm in itertools.permutations(window):
                    candidate = prefix + list(perm) + suffix
                    mnemonic = " ".join(candidate)
                    if not mnemo.check(mnemonic):
                        continue
                    checked += 1
                    addr = derive_first_bip44_address(mnemonic)
                    if addr == TARGET_ADDR:
                        print(f"[FOUND] ✅ Address match!\nMnemonic: {mnemonic}")
                        return
                    else:
                        log.write(f"[{checked}] {mnemonic} → {addr}\n")
    print(f"[-] Checked {checked} valid permutations — no match found.")

# === Sequences to test ===
ascii_sorted = [
    "bright", "miracle", "argue", "because", "memory", "initial",
    "frost", "either", "guilt", "grant", "lumber", "charge",
    "foam", "juice", "mountain", "forward", "capital", "chest"
]

grid_sorted = [
    "argue", "charge", "mountain", "foam", "lumber", "capital",
    "frost", "juice", "grant", "initial", "guilt", "chest",
    "either", "forward", "memory", "miracle", "because", "bright"
]

spiral_sorted = [
    "frost", "initial", "bright", "capital", "juice", "chest",
    "grant", "either", "charge", "argue", "foam", "memory",
    "forward", "miracle", "because", "mountain", "lumber", "guilt"
]

# Run all
check_all_windows(ascii_sorted, "ASCII-SORTED")
check_all_windows(grid_sorted, "GRID-SORTED")
check_all_windows(spiral_sorted, "SPIRAL-SORTED")
