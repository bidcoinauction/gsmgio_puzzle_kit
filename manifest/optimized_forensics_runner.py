# optimized_forensics_runner.py
#
# A high-speed version of the forensics script that uses batch API calls
# to check hundreds of addresses at once, dramatically improving performance.
#
# HOW TO RUN:
# 1. Install required libraries:
#    pip install bip_utils pandas tqdm
#
# 2. Place this script in the same directory as your log files.
#
# 3. Execute from the terminal:
#    python optimized_forensics_runner.py

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
OUTPUT_CSV_FILE = Path("forensics_report_optimized.csv")
BATCH_SIZE = 150 # Number of addresses to check per API call

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
        analysis_result["seed_hex"] = seed_bytes.hex()
        
        bip44_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)
        private_key = bip44_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0).PrivateKey()
        
        analysis_result["addr_legacy_p2pkh"] = private_key.PublicKey().ToAddress()
        analysis_result["addr_nested_segwit"] = Bip49.FromSeed(seed_bytes, Bip44Coins.BITCOIN).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0).PublicKey().ToAddress()
        analysis_result["addr_native_segwit"] = Bip84.FromSeed(seed_bytes, Bip44Coins.BITCOIN).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0).PublicKey().ToAddress()
        analysis_result["addr_taproot"] = Bip86.FromSeed(seed_bytes, Bip44Coins.BITCOIN).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0).PublicKey().ToAddress()
    except Exception:
        pass
    return analysis_result

def check_activity_batch(addresses: list):
    """Checks a batch of addresses using the blockchain.info/multiaddr API."""
    if not addresses:
        return {}
    
    address_str = "|".join(addresses)
    url = f"https://blockchain.info/multiaddr?active={address_str}"
    activity_map = {}
    
    try:
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            data = r.json()
            for addr_data in data.get("addresses", []):
                if addr_data.get("n_tx", 0) > 0:
                    activity_map[addr_data["address"]] = f"HIT: Balance={addr_data['final_balance']}, Txs={addr_data['n_tx']}"
        else:
            print(f"  - API Error: Status {r.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"  - API request failed: {e}")

    return activity_map

# --- MAIN EXECUTION ---

def main():
    mnemonics = load_all_mnemonics(ALL_LOG_FILES)
    all_results = []
    
    print("Starting optimized derivation and on-chain analysis with batching.")
    
    # First, derive all addresses for all mnemonics
    for mnemonic in tqdm(mnemonics, desc="Deriving Addresses"):
        all_results.append(derive_and_analyze(mnemonic))
        
    # Then, check all derived addresses in batches
    print(f"\nChecking all derived addresses in batches of {BATCH_SIZE}...")
    all_addresses = [
        addr for res in all_results 
        for key, addr in res.items() 
        if key.startswith("addr_") and addr
    ]
    
    activity_map = {}
    for i in tqdm(range(0, len(all_addresses), BATCH_SIZE), desc="Checking Batches"):
        batch = all_addresses[i:i + BATCH_SIZE]
        batch_activity = check_activity_batch(batch)
        activity_map.update(batch_activity)
        time.sleep(1) # Be polite to the API between large batches

    # Add the activity results to our main data
    for result in all_results:
        activity_found = []
        for key, addr in result.items():
            if key.startswith("addr_") and addr in activity_map:
                activity_found.append(f"{key}: {activity_map[addr]}")
        result["onchain_activity"] = "; ".join(activity_found) if activity_found else "None"

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