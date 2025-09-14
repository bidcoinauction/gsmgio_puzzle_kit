# pattern_solver.py
#
# An advanced solver that first analyzes word-pair frequencies (n-grams) from
# existing logs and then uses that data to run an intelligent, pattern-based
# backtracking search for the solution.
#
# HOW TO USE:
#
# 1. First, run in 'analyze' mode to see the most common patterns:
#    python pattern_solver.py --mode analyze
#
# 2. Then, run in 'solve' mode to use those patterns to find the solution:
#    python pattern_solver.py --mode solve --out final_candidates.txt

import pandas as pd
import argparse
import csv
from pathlib import Path
from collections import Counter
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
FUZZY_WORDS = {
    "initial", "because", "juice", "lumber", "grant", "forward", 
    "miracle", "foam", "charge", "capital", "either"
}
ALL_LOG_FILES = [
    Path("valid_mnemonics.csv"), Path("valid_mnemonics_log.csv"),
    Path("valid_phrases_log.txt"), Path("NEW_valid_mnemonics.csv"),
    Path("final_valid_log_20250808_165754.txt"), 
    Path("miracle_last_valid_log_20250808_173127.txt")
]

# --- HELPER FUNCTIONS ---

def load_all_mnemonics(file_list):
    """Loads mnemonics from all log files into a pandas DataFrame."""
    all_mnemonics_list = []
    print("Loading all mnemonics for cumulative analysis...")
    for file_path in file_list:
        if not file_path.exists(): continue
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            # Universal parser for both .txt and .csv
            for line in f:
                mnemonic = line.split(',')[0].split('->')[0].split('|')[0].strip()
                if mnemonic.count(" ") == 17:
                    all_mnemonics_list.append(mnemonic)
    print(f"Total mnemonics loaded for analysis: {len(all_mnemonics_list)}\n")
    return pd.DataFrame(all_mnemonics_list, columns=['Mnemonic'])

def run_analysis(df: pd.DataFrame):
    """Analyzes and prints the most common word pairs (bigrams) and triplets (trigrams)."""
    if df.empty:
        print("No data to analyze.")
        return

    words_df = df['Mnemonic'].str.split(' ', expand=True)
    fuzzy_df = words_df.iloc[:, 7:] # Get columns 7 through 17

    bigrams = Counter()
    trigrams = Counter()

    for row in fuzzy_df.itertuples(index=False, name=None):
        for i in range(len(row) - 1):
            bigrams[(row[i], row[i+1])] += 1
        for i in range(len(row) - 2):
            trigrams[(row[i], row[i+1], row[i+2])] += 1
    
    print("--- N-Gram Analysis Report ---")
    print("\nMost Common Word Pairs (Bigrams):")
    for (w1, w2), count in bigrams.most_common(15):
        print(f"  - ('{w1}', '{w2}'): {count} times")
        
    print("\nMost Common Word Triplets (Trigrams):")
    for (w1, w2, w3), count in trigrams.most_common(15):
        print(f"  - ('{w1}', '{w2}', '{w3}'): {count} times")

def run_solver(df: pd.DataFrame, out_file: str):
    """Runs a backtracking solver guided by n-gram frequencies."""
    if df.empty:
        print("Cannot run solver without data for n-gram analysis.")
        return

    # --- Build scoring model from analysis ---
    bigrams = Counter()
    for row in df['Mnemonic'].str.split(' ', expand=True).iloc[:, 7:].itertuples(index=False, name=None):
        for i in range(len(row) - 1):
            bigrams[(row[i], row[i+1])] += 1

    # --- Backtracking Search ---
    validator = Bip39MnemonicValidator()
    solution = None

    def solve(path):
        nonlocal solution
        if solution: return

        if len(path) == len(FUZZY_WORDS):
            mnemonic_list = LOCKED_PREFIX + path
            mnemonic_str = " ".join(mnemonic_list)
            
            if validator.IsValid(mnemonic_str):
                # If valid, derive address and check for match
                seed = Bip39SeedGenerator(mnemonic_str).Generate()
                addr_ctx = Bip44.FromSeed(seed, Bip44Coins.BITCOIN).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
                address = addr_ctx.PublicKey().ToAddress()
                
                with open(out_file, "a") as f:
                    f.write(f"{mnemonic_str},{address}\n")

                if address == TARGET_ADDRESS:
                    solution = mnemonic_str
            return

        # Score next possible words based on bigram frequency with the last word in the path
        last_word = path[-1]
        remaining_words = FUZZY_WORDS - set(path)
        
        # Sort remaining words by how often they follow the last word
        sorted_candidates = sorted(remaining_words, key=lambda word: bigrams.get((last_word, word), 0), reverse=True)

        for word in sorted_candidates:
            solve(path + [word])

    print("\n--- Starting Pattern-Based Solver ---")
    print(f"[*] Locking prefix: {' '.join(LOCKED_PREFIX)}")
    print(f"[*] Using n-gram frequencies to guide search.")
    print(f"[*] Writing all valid candidates to '{out_file}'")

    with open(out_file, "w") as f:
        f.write("Mnemonic,Derived_Address\n")

    # Start the backtracking search from each possible first fuzzy word
    for start_word in sorted(list(FUZZY_WORDS)):
        if solution: break
        print(f"[*] Starting search path with '{start_word}'...")
        solve([start_word])
        
    print("-" * 60)
    if solution:
        print("🎯 MATCH FOUND! PUZZLE SOLVED!")
        print(f"[*] Mnemonic: {solution}")
    else:
        print("Search complete for all paths. No match found.")

def main():
    parser = argparse.ArgumentParser(description="Advanced pattern analysis and solver for the GSMG puzzle.")
    parser.add_argument("--mode", choices=['analyze', 'solve'], required=True, help="Mode of operation.")
    parser.add_argument("--out", help="Output file for the solver.")
    args = parser.parse_args()

    if args.mode == 'solve' and not args.out:
        parser.error("--out is required when using --mode solve")

    df = load_all_mnemonics(ALL_LOG_FILES)

    if args.mode == 'analyze':
        run_analysis(df)
    elif args.mode == 'solve':
        run_solver(df, args.out)

if __name__ == "__main__":
    main()