import itertools
import os
import multiprocessing as mp
from tqdm import tqdm
from bip_utils import (
    Bip39MnemonicValidator,
    Bip39SeedGenerator,
    Bip44,
    Bip44Coins,
    Bip44Changes,
)
from bip_utils.utils.mnemonic import MnemonicChecksumError

# ---------------------------------------------
# CONFIGURATION
# ---------------------------------------------
TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
WORDS = [
    "frost", "because", "bright", "guilt", "grant", "lumber",
    "mountain", "either", "forward", "miracle", "charge",
    "foam", "capital", "argue", "initial", "juice", "chest", "memory"
]
CHECKPOINT_FILE = "checkpoint.txt"
SUCCESS_FILE = "success.txt"
CHUNK_SIZE = 1000
NUM_PROCESSES = max(mp.cpu_count() - 1, 1)

# ---------------------------------------------
# ADDRESS DERIVATION
# ---------------------------------------------
def derive_bip44_address(mnemonic: str) -> str:
    """Return first BIP44 legacy (m/44'/0'/0'/0/0) address."""
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

# ---------------------------------------------
# WORKER FUNCTION
# ---------------------------------------------
def worker(task_chunk):
    for perm in task_chunk:
        if not is_valid_mnemonic(perm):
            continue
        mnemonic = " ".join(perm)
        addr = derive_bip44_address(mnemonic)
        if addr == TARGET_ADDRESS:
            return mnemonic
    return None

# ---------------------------------------------
# LOGGING FUNCTION
# ---------------------------------------------
def log_success(mnemonic: str, address: str):
    with open(SUCCESS_FILE, "w") as f:
        f.write("MATCH FOUND!\n")
        f.write(f"Mnemonic: {mnemonic}\n")
        f.write(f"Address: {address}\n")
        f.write("Derivation path: m/44'/0'/0'/0/0\n")
    print(f"[+] Success logged to {SUCCESS_FILE}")

# ---------------------------------------------
# MAIN
# ---------------------------------------------
def main():
    print(f"[+] Loaded {len(WORDS)} words.")
    # Resume from checkpoint if available
    start_index = 0
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            start_index = int(f.read().strip())
        print(f"[+] Resuming from checkpoint index {start_index}")

    all_perms = itertools.islice(itertools.permutations(WORDS), start_index, None)

    # Batch processing
    batch = []
    index = start_index
    with mp.Pool(NUM_PROCESSES) as pool:
        with tqdm(total=None, desc="BruteForce", initial=start_index) as pbar:
            for perm in all_perms:
                batch.append(perm)
                index += 1
                if len(batch) >= CHUNK_SIZE:
                    results = pool.map(worker, [batch])
                    for res in results:
                        if res:
                            print("\n[+] MATCH FOUND!")
                            print("Mnemonic:", res)
                            print("Address:", TARGET_ADDRESS)
                            log_success(res, TARGET_ADDRESS)
                            return
                    with open(CHECKPOINT_FILE, "w") as f:
                        f.write(str(index))
                    pbar.update(CHUNK_SIZE)
                    batch = []

            # Final partial batch
            if batch:
                results = pool.map(worker, [batch])
                for res in results:
                    if res:
                        print("\n[+] MATCH FOUND!")
                        print("Mnemonic:", res)
                        print("Address:", TARGET_ADDRESS)
                        log_success(res, TARGET_ADDRESS)
                        return
                with open(CHECKPOINT_FILE, "w") as f:
                    f.write(str(index))
                pbar.update(len(batch))

    print("[-] No valid permutation produced the target address.")

if __name__ == "__main__":
    main()
