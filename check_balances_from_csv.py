import csv
import requests
import time

INPUT_FILE = "seedhunter_log.csv"
OUTPUT_FILE = "address_balances.csv"

def check_btc_balance(address: str):
    url = f"https://blockstream.info/api/address/{address}"
    r = requests.get(url)
    if r.status_code != 200:
        print(f"Error fetching {address}: {r.status_code}")
        return None
    data = r.json()
    chain_stats = data.get("chain_stats", {})
    mempool_stats = data.get("mempool_stats", {})
    confirmed = chain_stats.get("funded_txo_sum", 0) - chain_stats.get("spent_txo_sum", 0)
    unconfirmed = mempool_stats.get("funded_txo_sum", 0) - mempool_stats.get("spent_txo_sum", 0)
    return confirmed / 1e8, unconfirmed / 1e8, chain_stats.get("tx_count", 0)

def main():
    # Collect all unique addresses from CSV
    addresses = set()
    with open(INPUT_FILE, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for col in ["addr_pdkf", "addr_bip44", "addr_electrum"]:
                addr = row.get(col, "")
                if addr:
                    addresses.add(addr)

    print(f"Found {len(addresses)} unique addresses to check.")

    # Open output CSV
    with open(OUTPUT_FILE, "w", newline="") as outcsv:
        fieldnames = ["address", "confirmed_balance", "unconfirmed_balance", "tx_count"]
        writer = csv.DictWriter(outcsv, fieldnames=fieldnames)
        writer.writeheader()

        for i, addr in enumerate(addresses, 1):
            print(f"[{i}/{len(addresses)}] Checking {addr}...")
            result = check_btc_balance(addr)
            if result:
                confirmed, unconfirmed, tx_count = result
                print(f"  Confirmed: {confirmed} BTC | Unconfirmed: {unconfirmed} BTC | TXs: {tx_count}")
                writer.writerow({
                    "address": addr,
                    "confirmed_balance": confirmed,
                    "unconfirmed_balance": unconfirmed,
                    "tx_count": tx_count
                })
            time.sleep(0.5)  # slow down to be polite to the API

    print(f"\nBalance check complete. Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
