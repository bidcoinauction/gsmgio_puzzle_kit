import csv
import requests
import time

API_URL = "https://blockstream.info/api/address/"

def check_btc_balance(address: str):
    url = f"{API_URL}{address}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            print(f"Error fetching data for {address}: {r.status_code}")
            return None
        data = r.json()
        chain_stats = data.get("chain_stats", {})
        mempool_stats = data.get("mempool_stats", {})

        confirmed = chain_stats.get("funded_txo_sum", 0) - chain_stats.get("spent_txo_sum", 0)
        mempool = mempool_stats.get("funded_txo_sum", 0) - mempool_stats.get("spent_txo_sum", 0)

        return confirmed, mempool, chain_stats.get("tx_count", 0)
    except Exception as e:
        print(f"Exception while checking {address}: {e}")
        return None

def main(input_csv, output_csv):
    with open(input_csv, newline="") as infile, open(output_csv, "w", newline="") as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + [
            "addr", "confirmed_sats", "mempool_sats", "tx_count"
        ]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            for key in ["addr_pbkdf", "addr_bip44", "addr_electrum"]:
                addr = row.get(key)
                if not addr:
                    continue

                result = check_btc_balance(addr)
                if result:
                    confirmed, mempool, tx_count = result
                    if confirmed > 0 or mempool > 0:
                        # Only log addresses with balance or tx
                        new_row = dict(row)
                        new_row["addr"] = addr
                        new_row["confirmed_sats"] = confirmed
                        new_row["mempool_sats"] = mempool
                        new_row["tx_count"] = tx_count
                        writer.writerow(new_row)
                        print(f"[+] {addr} | Confirmed: {confirmed/1e8:.8f} BTC | TXs: {tx_count}")
                time.sleep(0.2)  # small delay to avoid API throttling

if __name__ == "__main__":
    INPUT = "seedhunter_log.csv"
    OUTPUT = "seedhunter_balances.csv"
    main(INPUT, OUTPUT)
    print("Balance check complete. Results saved to", OUTPUT)
