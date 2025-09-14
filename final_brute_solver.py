# final_brute_solver.py
#
# The definitive multi-process brute-force solver for the GSMG.IO puzzle.
# - Locks the 7 statistically stable words.
# - Permutes the remaining 11 words.
# - Loads all previously found mnemonics to avoid duplicate work.
#
# HOW TO RUN:
# 1. Install required libraries:
#    pip install bip_utils tqdm
#
# 2. Place this script in the same directory as your old log files.
#
# 3. Execute from the terminal:
#    python final_brute_solver.py

import itertools
import multiprocessing
import os
import csv
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
from bip_utils import (
    Bip39MnemonicValidator,
    Bip39SeedGenerator,
    Bip44,
    Bip44Coins,
    Bip44Changes,
)

# --- CONFIGURATION ---

TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"

LOCKED_WORDS = [
    "frost", "argue", "mountain", "chest", "guilt", "memory", "bright"
]

FUZZY_WORDS = [
    "initial", "because", "juice", "lumber", "grant", "forward", 
    "miracle", "foam", "charge", "capital", "either"
]

# --- Files containing mnemonics you've already found ---
# The script will read these to prevent re-checking old results.
EXISTING_LOG_FILES = [
    Path("valid_mnemonics.csv"),
    Path("valid_mnemonics_log.csv"),
    Path("valid_phrases_log.txt"),
    Path("NEW_valid_mnemonics.csv")  # <-- ADDED THIS FILE
]

# Generate unique, timestamped output filenames for this new run
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
MATCH_FILE = f"final_match_{TIMESTAMP}.txt"
VALID_LOG_FILE = f"final_valid_log_{TIMESTAMP}.txt"

# --- GLOBAL SET FOR WORKERS ---
# This set will hold all previously found mnemonics.
known_mnemonics = set()

# --- WORKER INITIALIZATION ---
def init_worker(existing_mnemonics_set):
    """Initializes each worker process with the set of known mnemonics."""
    global known_mnemonics
    known_mnemonics = existing_mnemonics_set

# --- HELPER FUNCTIONS ---

def load_existing_mnemonics(files_to_check):
    """Reads CSV and TXT files to create a set of already-found mnemonics."""
    found = set()
    print("Loading existing mnemonics to avoid duplicates...")
    for file_path in files_to_check:
        if not file_path.exists():
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                count_before = len(found)
                if file_path.suffix == '.csv':
                    reader = csv.reader(f)
                    next(reader, None)  # Skip header
                    for row in reader:
                        if row: found.add(row[0].strip())
                else: # .txt file
                    for line in f:
                        mnemonic = line.split('->')[0].split('|')[0].strip()
                        if mnemonic: found.add(mnemonic)
            print(f"  - Loaded {len(found) - count_before} unique mnemonics from {file_path}")
        except Exception as e:
            print(f"  - Error reading {file_path}: {e}")
            
    print(f"Total existing unique mnemonics loaded: {len(found)}\n")
    return found

def check_permutation(perm_tuple):
    """
    Worker function: takes a permutation, checks if it's new, validates it,
    and derives the BTC address.
    """
    global known_mnemonics
    
    full_mnemonic_list = LOCKED_WORDS + list(perm_tuple)
    mnemonic = " ".join(full_mnemonic_list)

    # 1. Skip if this mnemonic has been found in a previous run
    if mnemonic in known_mnemonics:
        return None

    # 2. Check for valid BIP39 checksum
    if not Bip39MnemonicValidator().IsValid(mnemonic):
        return None

    # 3. If valid, derive the address
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
    bip44_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)
    address_ctx = (
        bip44_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
    )
    derived_address = address_ctx.PublicKey().ToAddress()
    
    return (mnemonic, derived_address)

# --- MAIN EXECUTION ---

if __name__ == "__main__":
    
    # Load all previously found mnemonics
    already_found_set = load_existing_mnemonics(EXISTING_LOG_FILES)
    
    total_permutations = 39916800

    print("🚀 Starting Final Brute-Force Solver...")
    print(f"[*] Target Address: {TARGET_ADDRESS}")
    print(f"[*] Locked Words: {' '.join(LOCKED_WORDS)}")
    print(f"[*] Total Permutations to Check: {total_permutations:,}")
    print(f"[*] Skipping {len(already_found_set):,} already-found permutations.")
    print(f"[*] Logging NEW valid mnemonics to: {VALID_LOG_FILE}")
    print("-" * 60)
    
    perms_generator = itertools.permutations(FUZZY_WORDS)
    num_processes = os.cpu_count()
    
    with multiprocessing.Pool(processes=num_processes, initializer=init_worker, initargs=(already_found_set,)) as pool, \
         open(VALID_LOG_FILE, "w") as log_file:
        
        log_file.write("Mnemonic,Derived_Address\n")
        
        with tqdm(total=total_permutations, desc="Permutations Checked", unit="perm") as pbar:
            for result in pool.imap_unordered(check_permutation, perms_generator, chunksize=5000):
                pbar.update()
                
                if result:
                    mnemonic, address = result
                    log_file.write(f"{mnemonic},{address}\n")
                    log_file.flush()

                    if address == TARGET_ADDRESS:
                        print("\n" + "="*60)
                        print("🎯 MATCH FOUND! PUZZLE SOLVED! 🎯")
                        print(f"[*] Mnemonic: {mnemonic}")
                        print(f"[*] Address:  {address}")
                        print("="*60)
                        
                        with open(MATCH_FILE, "w") as match_f:
                            match_f.write(f"MATCH FOUND!\n\nMnemonic: {mnemonic}\nAddress: {address}\n")
                        
                        pool.terminate()
                        break
    
    print("\n✅ Search complete.")