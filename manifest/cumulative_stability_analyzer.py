# cumulative_stability_analyzer.py
#
# Analyzes the COMBINED data from ALL log files to provide the most
# accurate positional stability report.
#
# HOW TO RUN:
# 1. Install required library:
#    pip install pandas
#
# 2. Place this script in the same directory as your log files.
#
# 3. Execute from the terminal (no arguments needed):
#    python cumulative_stability_analyzer.py

import pandas as pd
import csv
from pathlib import Path

# --- CONFIGURATION ---

# All log files to be combined for a full analysis
ALL_LOG_FILES = [
    Path("valid_mnemonics.csv"),
    Path("valid_mnemonics_log.csv"),
    Path("valid_phrases_log.txt"),
    Path("NEW_valid_mnemonics.csv"),
    Path("final_valid_log_20250808_165754.txt"),
    Path("miracle_last_valid_log_20250808_173127.txt"),
    Path("final_candidates.txt") # <-- Added the latest log file
]

CONFIDENCE_THRESHOLD = 0.95  # Confidence level to consider a position "locked"

def load_all_mnemonics(file_list):
    """
    Reads all specified log files and consolidates the mnemonics into a single list.
    """
    all_mnemonics_list = []
    print("Loading all mnemonics for cumulative analysis...")
    
    for file_path in file_list:
        if not file_path.exists():
            print(f"  - Skipping (not found): {file_path}")
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                count_before = len(all_mnemonics_list)
                # Handle CSV files by reading the first column
                if file_path.suffix == '.csv':
                    reader = csv.reader(f)
                    next(reader, None)  # Skip header row
                    for row in reader:
                        if row: all_mnemonics_list.append(row[0].strip())
                # Handle TXT files by parsing lines
                else:
                    for line in f:
                        # Handles formats like "mnemonic,address" or "mnemonic -> address"
                        mnemonic = line.split(',')[0].split('->')[0].split('|')[0].strip()
                        if mnemonic: all_mnemonics_list.append(mnemonic)

            print(f"  - Loaded {len(all_mnemonics_list) - count_before} mnemonics from {file_path}")
        except Exception as e:
            print(f"  - Error reading {file_path}: {e}")
            
    print(f"\nTotal mnemonics for analysis: {len(all_mnemonics_list)}\n")
    return pd.DataFrame(all_mnemonics_list, columns=['Mnemonic'])

def analyze_stability(df: pd.DataFrame):
    """
    Performs and prints the positional stability analysis on the combined DataFrame.
    """
    if df.empty:
        print("No data loaded. Nothing to analyze.")
        return
        
    # Split the mnemonic string into a list of 18 words
    words_df = df['Mnemonic'].str.split(' ', expand=True)

    locked_positions = {}

    print("--- Cumulative Positional Stability Report ---")
    print(f"{'Position':<10} {'Top Word':<12} {'Confidence':<20} {'Status'}")
    print("-" * 60)

    for i in range(18):  # For each position (0-17)
        pos_counts = words_df[i].value_counts()
        top_word = pos_counts.index[0]
        top_word_count = pos_counts.iloc[0]
        confidence = top_word_count / len(words_df)

        status = "LOCKED" if confidence >= CONFIDENCE_THRESHOLD else "Fuzzy"
        if status == "LOCKED":
            locked_positions[i] = (top_word, confidence)

        print(f"{i:<10} {top_word:<12} {confidence:<20.4%} {status}")
        
    print("\n--- Analysis Summary ---")
    if not locked_positions:
        print("No positions met the confidence threshold to be considered locked.")
    else:
        print(f"Found {len(locked_positions)} positions with >= {CONFIDENCE_THRESHOLD:.0%} confidence:")
        for pos, (word, conf) in sorted(locked_positions.items()):
            print(f"  - Position {pos}: '{word}' ({conf:.2%})")

if __name__ == "__main__":
    combined_df = load_all_mnemonics(ALL_LOG_FILES)
    if not combined_df.empty:
        analyze_stability(combined_df)