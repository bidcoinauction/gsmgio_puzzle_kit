import itertools
import os
import multiprocessing as mp
import csv
from tqdm import tqdm
from bip_utils import (
    Bip39MnemonicValidator,
    Bip39SeedGenerator,
    Bip44,
    Bip44Coins,
    Bip44Changes,
)
from bip_utils.utils.mnemonic import MnemonicChecksumError

TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
WORDS = [
    "frost", "because", "bright", "guilt", "grant", "lumber",
    "mountain", "either", "forward", "miracle", "charge",
    "foam", "capital", "argue", "initial", "juice", "chest", "memory"
]
CHECKPOINT_FILE = "checkpoint.txt"
CHUNK_SIZE = 1000
NUM_PROCESSES = max(mp.cpu_count() - 1, 1)
VALID_LOG_FILE = "valid_mnemonics_log.csv"
PROGRESS_LOG_FILE = "progress.log"

def derive_bip44_address(mnemonic: str) -> str:
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

def worker(task_chunk):
    matched = []
    logged = []
    for perm in task_chunk:
        if not is_valid_mnemonic(perm):
            continue
        mnemonic = " ".join(perm)
        try:
            addr = derive_bip44_address(mnemonic)
        except Exception:
            continue
        if addr == TARGET_ADDRESS:
            matched.append((mnemonic, addr))
        else:
            logged.append((mnemonic, addr))
    return matched, logged

def main():
    print(f"[+] Loaded {len(WORDS)} words.")
    if not os.path.exists(VALID_LOG_FILE):
        with open(VALID_LOG_FILE, "w") as f:
            writer = csv.writer(f)
            writer.writerow(["mnemonic", "address"])

    start_index = 0
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            start_index = int(f.read().strip())
        print(f"[+] Resuming from checkpoint index {start_index}")

    all_perms = itertools.islice(itertools.permutations(WORDS), start_index, None)

    batch = []
    index = start_index
    with mp.Pool(NUM_PROCESSES) as pool:
        with tqdm(total=None, desc="BruteForce", initial=start_index) as pbar:
            for perm in all_perms:
                batch.append(perm)
                index += 1
                if len(batch) >= CHUNK_SIZE:
                    results = pool.map(worker, [batch])
                    for matched, logged in results:
                        if matched:
                            for m in matched:
                                print("\n[+] MATCH FOUND!")
                                print("Mnemonic:", m[0])
                                print("Address:", m[1])
                                return
                        if logged:
                            with open(VALID_LOG_FILE, "a") as f:
                                writer = csv.writer(f)
                                writer.writerows(logged)

                    with open(CHECKPOINT_FILE, "w") as f:
                        f.write(str(index))
                    with open(PROGRESS_LOG_FILE, "w") as f:
                        f.write(f"Index: {index}\n")
                    pbar.update(CHUNK_SIZE)
                    batch = []

            if batch:
                results = pool.map(worker, [batch])
                for matched, logged in results:
                    if matched:
                        for m in matched:
                            print("\n[+] MATCH FOUND!")
                            print("Mnemonic:", m[0])
                            print("Address:", m[1])
                            return
                    if logged:
                        with open(VALID_LOG_FILE, "a") as f:
                            writer = csv.writer(f)
                            writer.writerows(logged)
                with open(CHECKPOINT_FILE, "w") as f:
                    f.write(str(index))
                with open(PROGRESS_LOG_FILE, "w") as f:
                    f.write(f"Index: {index}\n")
                pbar.update(len(batch))

    print("[-] No valid permutation produced the target address.")

if __name__ == "__main__":
    mp.set_start_method("fork")
    main()
