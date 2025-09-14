# block_solver_v2.py
#
# A dedicated solver to test the high-probability 5-word "CILBM block".
# It now loads all existing log files to avoid re-checking duplicates.
#
# HOW TO RUN:
# 1. Install required libraries:
#    pip install bip_utils
#
# 2. Place this script in the same directory as your log files.
#
# 3. Execute from the terminal (no arguments needed):
#    python block_solver_v2.py

import itertools
import csv
from pathlib import Path
from bip_utils import (
    Bip39MnemonicValidator,
    Bip39SeedGenerator,
    Bip44,
    Bip44Coins,
    Bip44Changes,
)

# --- CONFIGURATION ---
TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
LOCKED_PREFIX = ["frost", "argue", "mountain", "chest", "guilt", "memory", "bright"]
LOCKED_BLOCK = ["charge", "initial", "lumber", "because", "miracle"]
REMAINING_FUZZY = ["capital", "either", "foam", "forward", "grant", "juice"]

# All log files to be checked for duplicates
ALL_LOG_FILES = [
    Path("valid_mnemonics.csv"),
    Path("valid_mnemonics_log.csv"),
    Patxt"),
    Path("NEW_valid_mnemonics.csv"),
    Path("final_valid_log_20250808_165754.txt"),
    Path("miracle_last_valid_log_20250808_173127.txt")
]

def load_existing_mnemonics(file_list):
    """Loads mnemonics from all log files into a set to be skipped."""
    found = set()
    print("Loading existing mnemonics to avoid duplicates...")
    for file_path in file_list:
        if not file_path.exists():
            continue
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

def main():
    """
    Tests all permutations of the 6 remaining fuzzy words with the 5-word block
    placed at the beginning or end of the fuzzy section.
    """
    validator = Bip39MnemonicValidator()
    found = False
    
    # Load all previously found mnemonics to skip them
    skip_set = load_existing_mnemonics(ALL_LOG_FILES)

    print("🚀 Starting High-Probability Block Solver...")
    print(f"[*] Locking Prefix: {' '.join(LOCKED_PREFIX)}")
    print(f"[*] Locking Block: {' '.join(LOCKED_BLOCK)}")
    print(f"[*] Permuting Remaining 6 Words: {REMAINING_FUZZY}")
    print("-" * 60)

    # Test Case 1: Prefix + [6 Permuted Words] + 5-Word Block
    print("[*] Testing with 5-word block at the END...")
    for p in itertools.permutations(REMAINING_FUZZY):
        candidate_list = LOCKED_PREFIX + list(p) + LOCKED_BLOCK
        mnemonic = " ".join(candidate_list)
        
        if mnemonic in skip_set:
            continue
            
        if validator.IsValid(mnemonic):
            seed = Bip39SeedGenerator(mnemonic).Generate()
            addr_ctx = Bip44.FromSeed(seed, Bip44Coins.BITCOIN).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
            address = addr_ctx.PublicKey().ToAddress()
            
            print(f"  [VALID] {mnemonic} -> {address}")

            if address == TARGET_ADDRESS:
                found = True
                print("\n" + "="*60)
                print("🎯 MATCH FOUND! PUZZLE SOLVED!")
                print(f"[*] Mnemonic: {mnemonic}")
                print(f"[*] Address:  {address}")
                print("="*60)
                return

    # Test Case 2: Prefix + 5-Word Block + [6 Permuted Words]
    print("\n[*] Testing with 5-word block at the BEGINNING...")
    for p in itertools.permutations(REMAINING_FUZZY):
        candidate_list = LOCKED_PREFIX + LOCKED_BLOCK + list(p)
        mnemonic = " ".join(candidate_list)
        
        if mnemonic in skip_set:
            continue

        if validator.IsValid(mnemonic):
            seed = Bip39SeedGenerator(mnemonic).Generate()
            addr_ctx = Bip44.FromSeed(seed, Bip44Coins.BITCOIN).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
            address = addr_ctx.PublicKey().ToAddress()
            
            print(f"  [VALID] {mnemonic} -> {address}")

            if address == TARGET_ADDRESS:
                found = True
                print("\n" + "="*60)
                print("🎯 MATCH FOUND! PUZZLE SOLVED!")
                print(f"[*] Mnemonic: {mnemonic}")
                print(f"[*] Address:  {address}")
                print("="*60)
                return

    print("-" * 60)
    if not found:
        print("✅ Search complete for these block configurations. No match found.")

if __name__ == "__main__":
    main()