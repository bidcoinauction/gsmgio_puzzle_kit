# final_forensics_runner.py
#
# A high-speed, reliable version of the forensics script. It uses the
# blockstream.info API to avoid connection errors and checks all derived
# address types for on-chain activity.
#
# HOW TO RUN:
# 1. Install required libraries:
#    pip install bip_utils pandas tqdm
#
# 2. Place this script in the same directory as your log files.
#
# 3. Execute from the terminal:
#    python final_forensics_runner.py

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
        pass
    return analysis_result

def check_activity(address: str):
    """Checks a single address using the blockstream.info API."""
    if not address: return None
    url = f"https://blockstream.info/api/address/{address}"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            tx_count = data.get("chain_stats", {}).get("tx_count", 0)
            if tx_count > 0:
                balance = data.get("chain_stats", {}).get("funded_txo_sum", 0) - data.get("chain_stats", {}).get("spent_txo_sum", 0)
                return f"HIT: Balance={balance}, Txs={tx_count}"
    except requests.exceptions.RequestException:
        pass
    return None

# --- MAIN EXECUTION ---

def main():
    mnemonics = load_all_mnemonics(ALL_LOG_FILES)
    all_results = []
    
    print("Starting reliable on-chain analysis using blockstream.info.")
    
    # First, derive all addresses locally. This is fast.
    for mnemonic in tqdm(mnemonics, desc="Deriving All Addresses"):
        all_results.append(derive_and_analyze(mnemonic))
        
    # Second, check each address online. This is the slow part.
    print(f"\nChecking all derived addresses for on-chain activity...")
    for result_row in tqdm(all_results, desc="Checking Addresses Online"):
        activity_found = []
        for key, addr in result_row.items():
            if key.startswith("addr_"):
                activity = check_activity(addr)
                if activity:
                    activity_found.append(f"{key}: {activity}")
                time.sleep(0.2) # Polite delay between each request
        result_row["onchain_activity"] = "; ".join(activity_found) if activity_found else "None"

    # Export all data to a single CSV
    df = pd.DataFrame(all_results)
    df.to_csv(OUTPUT_CSV_FILE, index=False)
    
    print("\n" + "="*60)
    print("✅ Forensic analysis complete.")
    print(f"Full report has been saved to: {OUTPUT_CSV_FILE}")
    
    hits = df[df['onchain_activity'] != 'None']
    if not hits.empty:
        print("\n🚨 ATTENTION: Found one or more addresses with on-chain activity!")
        print(hits)
    else:
        print("\nNo addresses with any balance or transaction history were found.")

if __name__ == "__main__":
    main()