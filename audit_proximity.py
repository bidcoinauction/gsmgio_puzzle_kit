import csv
import sys
from Levenshtein import distance as levenshtein_distance

# === CONFIG ===
CSV_FILE = "all_valid_mnemonics.csv"
TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
TOP_N = 25

# === FUNCTIONS ===
def hamming_dist(a, b):
    if len(a) != len(b):
        return None
    return sum(x != y for x, y in zip(a, b))

# === LOAD CSV ===
with open(CSV_FILE, newline='') as f:
    reader = csv.DictReader(f)
    headers = reader.fieldnames
    print(f"📋 Detected CSV headers: {headers}")

    # Auto-detect address field
    addr_key = next((k for k in headers if "address" in k.lower()), None)
    if not addr_key:
        print("❌ Couldn't detect address column.")
        sys.exit(1)

    rows = list(reader)

# === COMPUTE DISTANCES ===
results = []
for row in rows:
    address = row[addr_key].strip()
    mnemonic = row["Mnemonic"]

    lev = levenshtein_distance(address, TARGET_ADDRESS)
    ham = hamming_dist(address, TARGET_ADDRESS)

    results.append({
        "levenshtein": lev,
        "hamming": ham if ham is not None else "N/A",
        "address": address,
        "mnemonic": mnemonic,
        "strategy": row["Strategy"]
    })

# === SORT + DISPLAY ===
sorted_results = sorted(results, key=lambda x: x["levenshtein"])

print(f"\n🎯 Top {TOP_N} Closest BTC Addresses to {TARGET_ADDRESS}\n")
for r in sorted_results[:TOP_N]:
    print(f"[{r['levenshtein']:>2}L / {r['hamming']}]  {r['address']}  ← {r['strategy']}")

# === SAVE TO FILE ===
with open("proximity_ranked_results.csv", "w", newline='') as f:
    fieldnames = ["levenshtein", "hamming", "address", "strategy", "mnemonic"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(sorted_results)

print("\n✅ Exported ranked results to proximity_ranked_results.csv")
