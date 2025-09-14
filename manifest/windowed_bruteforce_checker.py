import itertools
from mnemonic import Mnemonic
from bip_utils import Bip44, Bip44Coins, Bip44Changes, Bip39SeedGenerator
from multiprocessing import Pool, cpu_count
import os

TARGET_ADDR = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
CHECKPOINT_FILE = "checkpoint_index.txt"
CHUNK_SIZE = 10000

mnemo = Mnemonic("english")

BASE_SEQUENCE = [
    "argue", "charge", "mountain", "foam", "lumber", "capital",
    "frost", "juice", "grant", "initial", "guilt", "chest",
    "either", "forward", "memory", "miracle", "because", "bright"
]

def derive_first_bip44_address(mnemonic):
    seed = Bip39SeedGenerator(mnemonic).Generate()
    bip44 = Bip44.FromSeed(seed, Bip44Coins.BITCOIN)
    account = bip44.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT)
    return account.AddressIndex(0).PublicKey().ToAddress()

def check_permutation(index_perm):
    idx, perm = index_perm
    phrase = " ".join(perm)
    if not mnemo.check(phrase):
        return None
    addr = derive_first_bip44_address(phrase)
    if addr == TARGET_ADDR:
        return f"[FOUND] ✅ Mnemonic: {phrase}"
    return None

def run_bruteforce(start_idx=0):
    print(f"[+] Starting from checkpoint index {start_idx}")
    pool = Pool(cpu_count())
    all_perms = itertools.permutations(BASE_SEQUENCE)

    # Skip to checkpoint
    for _ in range(start_idx):
        next(all_perms)

    for batch_start in range(start_idx, 6_402_373_705_728_000, CHUNK_SIZE):
        batch = list(itertools.islice(all_perms, CHUNK_SIZE))
        indexed_batch = list(enumerate(batch, start=batch_start))
        results = pool.map(check_permutation, indexed_batch)

        for result in results:
            if result:
                print(result)
                with open("FOUND_MNEMONIC.txt", "w") as f:
                    f.write(result)
                pool.terminate()
                return

        with open(CHECKPOINT_FILE, "w") as f:
            f.write(str(batch_start + CHUNK_SIZE))
        print(f"[+] Checked {batch_start + CHUNK_SIZE} permutations...")

    pool.close()
    pool.join()

if __name__ == "__main__":
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE) as f:
            start = int(f.read())
    else:
        start = 0
    run_bruteforce(start)
