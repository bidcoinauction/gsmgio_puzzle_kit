# final_solver.py
#
# The definitive solver for the GSMG.IO puzzle. This script combines:
#  - A high-confidence lock on the first 7 words.
#  - An intelligent backtracking generator that uses per-position statistical data.
#  - A robust, multi-process framework to check candidates in parallel.
#  - Cumulative duplicate checking against all previously generated log files.
#
# HOW TO RUN:
# 1. Install required libraries:
#    pip install bip_utils tqdm
#
# 2. Place this script in the same directory as all your log files.
#
# 3. Execute from the terminal (no arguments needed):
#    python final_solver.py

import itertools
import multiprocessing
import os
import csv
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
from typing import List, Dict, Set, Iterable
from bip_utils import (
    Bip39MnemonicValidator,
    Bip39SeedGenerator,
    Bip44,
    Bip44Coins,
    Bip44Changes,
)

# --- CONFIGURATION ---
TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"

# 7 words locked based on >99.97% statistical confidence
LOCKED_WORDS = ["frost", "argue", "mountain", "chest", "guilt", "memory", "bright"]

# The 11 fuzzy words that must be placed in the remaining slots
FUZZY_WORDS = {
    "initial", "because", "juice", "lumber", "grant", "forward", 
    "miracle", "foam", "charge", "capital", "either"
}

# Per-position candidate pools based on statistical analysis
CANDIDATE_POOLS = {
    7:  ["either", "foam", "because", "juice", "lumber", "initial"],
    8:  ["grant", "forward", "capital", "foam", "charge"],
    9:  ["lumber", "grant", "forward", "capital", "charge"],
    10: ["because", "forward", "either", "capital", "foam"],
    11: ["charge", "forward", "miracle", "capital", "grant", "either"],
    12: ["capital", "forward", "grant", "either", "foam"],
    13: ["initial", "because", "capital", "forward", "either"],
    14: ["lumber", "capital", "forward", "charge", "grant"],
    15: ["juice", "either", "capital", "forward", "foam"],
    16: ["either", "lumber", "capital", "forward", "charge"],
    17: ["miracle", "either", "grant", "capital", "forward"],
}

# All log files to be checked for duplicates
ALL_LOG_FILES = [
    Path("valid_mnemonics.csv"), Path("valid_mnemonics_log.csv"),
    Path("valid_phrases_log.txt"), Path("NEW_valid_mnemonics.csv"),
    Path("final_valid_log_20250808_165754.txt"), Path("miracle_last_valid_log_20250808_173127.txt")
]

# --- OUTPUT ---
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
MATCH_FILE = f"final_match_{TIMESTAMP}.txt"
VALID_LOG_FILE = f"final_valid_log_{TIMESTAMP}.txt"

known_mnemonics = set()

# --- WORKER & HELPERS ---

def init_worker(existing_mnemonics_set):
    global known_mnemonics
    known_mnemonics = existing_mnemonics_set

def load_existing_mnemonics(files_to_check):
    found = set()
    print("Loading existing mnemonics to avoid duplicates...")
    for file_path in files_to_check:
        if not file_path.exists(): continue
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                count_before = len(found)
                # Universal parser for both .txt and .csv
                for line in f:
                    mnemonic = line.split(',')[0].split('->')[0].split('|')[0].strip()
                    if mnemonic.count(" ") >= 17:
                        found.add(mnemonic)
            print(f"  - Loaded {len(found) - count_before} unique mnemonics from {file_path}")
        except Exception as e:
            print(f"  - Error reading {file_path}: {e}")
    print(f"Total existing unique mnemonics loaded: {len(found)}\n")
    return found

def check_candidate(mnemonic: str):
    """
    Worker function: takes a single mnemonic string, checks if it's new,
    validates it, and derives the address.
    """
    global known_mnemonics
    
    if mnemonic in known_mnemonics:
        return None

    try:
        if not Bip39MnemonicValidator().IsValid(mnemonic):
            return None
    except Exception: # Catches checksum errors
        return None

    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
    bip44_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)
    address_ctx = (bip44_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0))
    derived_address = address_ctx.PublicKey().ToAddress()
    
    return (mnemonic, derived_address)

def backtrack_generator(pools: Dict[int, List[str]], pos_list: List[int]):
    """
    A generator that yields full 18-word mnemonic candidates using backtracking.
    """
    phrase = [""] * 18
    for i, word in enumerate(LOCKED_WORDS):
        phrase[i] = word

    used_fuzzy_words = set()

    def solve(pos_idx):
        if pos_idx == len(pos_list):
            yield " ".join(phrase)
            return

        current_pos = pos_list[pos_idx]
        for word in pools[current_pos]:
            if word in used_fuzzy_words:
                continue
            
            phrase[current_pos] = word
            used_fuzzy_words.add(word)
            yield from solve(pos_idx + 1)
            used_fuzzy_words.remove(word) # Backtrack

    yield from solve(0)

# --- MAIN EXECUTION ---

if __name__ == "__main__":
    already_found_set = load_existing_mnemonics(ALL_LOG_FILES)
    
    # The positions that need to be filled by the backtracking solver (7-17)
    fuzzy_positions = sorted(list(FUZZY_WORDS))
    
    print("🚀 Starting Final Intelligent Solver...")
    print(f"[*] Target Address: {TARGET_ADDRESS}")
    print(f"[*] Locked Words (0-6): {' '.join(LOCKED_WORDS)}")
    print("[*] Generating candidates via backtracking on statistical pools...")
    print(f"[*] Skipping {len(already_found_set):,} already-found permutations.")
    print(f"[*] Logging NEW valid mnemonics to: {VALID_LOG_FILE}")
    print("-" * 60)

    # The backtracking generator will produce candidates for the pool
    candidate_generator = backtrack_generator(CANDIDATE_POOLS, pos_list=sorted(CANDIDATE_POOLS.keys()))
    num_processes = os.cpu_count()
    
    with multiprocessing.Pool(processes=num_processes, initializer=init_worker, initargs=(already_found_set,)) as pool, \
         open(VALID_LOG_FILE, "w") as log_file:
        
        log_file.write("Mnemonic,Derived_Address\n")
        
        # tqdm here won't have a total, as the generator size is unknown, but it will show progress rate
        with tqdm(desc="Candidates Checked", unit="cand") as pbar:
            for result in pool.imap_unordered(check_candidate, candidate_generator, chunksize=1000):
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