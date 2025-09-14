# final_forensics_runner.py
#
# A high-speed, reliable version of the forensics script. It uses the
# blockstream.info API, checks all derived address types, and includes
# resume-from-crash capability.
#
# HOW TO RUN:
# 1. Install required libraries:
#    pip install bip_utils pandas tqdm
#
# 2. Place this script in the same directory as your log files.
#
# 3. Execute from the terminal:
#    python final_forensics_runner.py
#    (If the script is stopped, just run it again to resume)

import csv
import requests
import time
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from bip_utils import (
    Bip39SeedGenerator, Bip44, Bip49, Bip84, Bip86, Bip44Coins, Bip44Changes
)

# --- CONFIGURATION ---
ALL_LOG_FILES = [
    Path("valid_mnemonics.csv"), Path("valid_mnemonics_log.csv"),
    Path("valid_phrases_log.txt"), Path("NEW_valid_mnemonics.csv"),
    Path("final_valid_log_20250808_165754.txt"),
    Path("miracle_last_valid_log_20250808_173127.txt"),
    Path("final_candidates.txt")
]
# --- NEW: Added a separate file for saving progress ---
PROGRESS_CSV_FILE = Path("progress_report.csv")
OUTPUT_CSV_FILE = Path("final_forensics_report.csv")


# --- HELPER FUNCTIONS ---

def load_all_mnemonics(file_list):
    """Loads a unique set of mnemonics from all specified log files."""
    found = set()
    print("Loading all unique mnemonics for forensic analysis...")
    for file_path in file_list:
        if not file_path.exists(): continue
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                mnemonic = line.split(',')[0].split('->')[0].split('|')[0].strip()
                if mnemonic.count(" ") >= 17:
                    found.add(mnemonic)
    print(f"Loaded {len(found)} unique mnemonics for processing.\n")
    return list(found)

def derive_and_analyze(mnemonic: str):
    """Derives all keys and addresses for a single mnemonic."""
    analysis_result = {"mnemonic": mnemonic}
    try:
        seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
        
        analysis_result["addr_legacy_p2pkh"] = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0).PublicKey().ToAddress()
        analysis_result["addr_nested_segwit"] = Bip49.FromSeed(seed_bytes, Bip44Coins.BITCOIN).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0).PublicKey().ToAddress()
        analysis_result["addr_native_segwit"] = Bip84.FromSeed(seed_bytes, Bip44Coins.BITCOIN).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0).PublicKey().ToAddress()
        analysis_result["addr_taproot"] = Bip86.FromSeed(seed_bytes, Bip44Coins.BITCOIN).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0).PublicKey().ToAddress()
    except Exception:
        # If derivation fails, the address fields will be missing
        pass
    return analysis_result

def check_activity(address: str):
    """Checks a single address using the blockstream.info API."""
    if not address or pd.isna(address): return None
    url = f"https://blockstream.info/api/address/{address}"
    try:
        # Increased timeout for more reliability on slow connections
        r = requests.get(url, timeout=20)
        if r.status_code == 200:
            data = r.json()
            tx_count = data.get("chain_stats", {}).get("tx_count", 0)
            if tx_count > 0:
                balance = data.get("chain_stats", {}).get("funded_txo_sum", 0) - data.get("chain_stats", {}).get("spent_txo_sum", 0)
                return f"HIT: Balance={balance}, Txs={tx_count}"
    except requests.exceptions.RequestException:
        # In case of network error, we'll just try again next time
        pass
    return None

# --- MAIN EXECUTION ---

def main():
    # --- NEW: Logic to load progress or start fresh ---
    if PROGRESS_CSV_FILE.exists():
        print(f"✅ Found existing progress file. Resuming from '{PROGRESS_CSV_FILE}'...")
        df = pd.read_csv(PROGRESS_CSV_FILE)
        # Ensure the activity column exists for resuming
        if 'onchain_activity' not in df.columns:
            df['onchain_activity'] = None
    else:
        print("No progress file found. Starting a new analysis...")
        mnemonics = load_all_mnemonics(ALL_LOG_FILES)
        all_results = []
        # First, derive all addresses locally. This is fast.
        for mnemonic in tqdm(mnemonics, desc="Deriving All Addresses"):
            all_results.append(derive_and_analyze(mnemonic))
        df = pd.DataFrame(all_results)
        # Add the placeholder column for on-chain activity results
        df['onchain_activity'] = None
        # Initial save so we don't have to derive again
        df.to_csv(PROGRESS_CSV_FILE, index=False)
        print("\nInitial address derivation complete. Progress is being saved.")

    print(f"\nChecking derived addresses for on-chain activity...")
    
    # Use tqdm to iterate over DataFrame rows with a progress bar
    pbar = tqdm(total=len(df), desc="Checking Addresses Online")
    
    for index, row in df.iterrows():
        # --- NEW: Skip rows that have already been processed ---
        if pd.notna(row.get('onchain_activity')) and row.get('onchain_activity') != "None":
            pbar.update(1) # Still update the progress bar
            continue

        activity_found = []
        # Check all address columns for this row
        for col_name, address in row.items():
            if col_name.startswith("addr_"):
                activity = check_activity(address)
                if activity:
                    # e.g., "addr_native_segwit: HIT: Balance=10000, Txs=1"
                    activity_found.append(f"{col_name}: {activity}")
                time.sleep(0.25) # Polite delay increased slightly

        # Update the DataFrame with the result
        activity_str = "; ".join(activity_found) if activity_found else "None"
        df.at[index, 'onchain_activity'] = activity_str
        
        # --- NEW: Save progress after every single mnemonic check ---
        df.to_csv(PROGRESS_CSV_FILE, index=False)
        pbar.update(1)

    pbar.close()

    # Final export to the desired output file
    df.to_csv(OUTPUT_CSV_FILE, index=False)
    
    print("\n" + "="*60)
    print("✅ Forensic analysis complete.")
    print(f"Full report has been saved to: {OUTPUT_CSV_FILE}")
    
    hits = df[df['onchain_activity'] != 'None']
    if not hits.empty:
        print("\n🚨 ATTENTION: Found one or more addresses with on-chain activity!")
        print(hits[['mnemonic', 'onchain_activity']].to_string())
    else:
        print("\nNo addresses with any balance or transaction history were found.")

if __name__ == "__main__":
    main()