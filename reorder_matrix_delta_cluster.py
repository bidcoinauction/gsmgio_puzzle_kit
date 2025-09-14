import csv
from bip_utils import (
    Bip39MnemonicValidator,
    Bip39SeedGenerator,
    Bip44,
    Bip44Coins,
)
import base36
from typing import List, Tuple


# === INPUTS ===
BIP39_WORDS = [
    "frost", "argue", "mountain", "chest", "guilt", "memory",
    "bright", "initial", "lumber", "foam", "juice", "charge",
    "because", "either", "miracle", "grant", "capital", "forward"
]

PAIR_KEYS = [
    "kr", "4E", "68", "8f", "J1", "FY", "b0", "dE", "c5",
    "M7", "sU", "TW", "NH", "Aa", "98", "vD", "rm", "Xe"
]

LOCKED_POSITIONS = {
    "miracle": 12  # Example locked constraint
}

TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
CSV_EXPORT_PATH = "reorder_matrix_delta_cluster_output.csv"


# === HELPERS ===
def is_valid_mnemonic(words: List[str]) -> bool:
    return Bip39MnemonicValidator().IsValid(" ".join(words))

def derive_btc_address(words: List[str]) -> str:
    seed = Bip39SeedGenerator(" ".join(words)).Generate()
    acct = Bip44.FromSeed(seed, Bip44Coins.BITCOIN).PublicKey()
    return acct.ToAddress()

def base36_mod(pair: str) -> Tuple[int, int]:
    try:
        return base36.loads(pair[0].lower()), base36.loads(pair[1].lower())
    except:
        return (0, 0)

def delta_walk_sort(pairs: List[str], words: List[str]) -> List[str]:
    vals = [sum(base36_mod(p)) for p in pairs]
    deltas = [abs(vals[i+1] - vals[i]) for i in range(len(vals)-1)]
    weighted = list(zip(deltas + [0], words))
    return [w for _, w in sorted(weighted)]

def matrix_grid_order(pairs: List[str], words: List[str], rows=6, cols=3) -> List[str]:
    grid = [[None]*cols for _ in range(rows)]
    mapped = [(base36_mod(p)[0] % rows, base36_mod(p)[1] % cols, w) for p, w in zip(pairs, words)]
    for r, c, w in mapped:
        grid[r][c] = w
    return [w for row in grid for w in row if w]

def apply_locks(words: List[str], locks: dict) -> bool:
    for word, pos in locks.items():
        if pos >= len(words) or words[pos] != word:
            return False
    return True


# === RUN ===
results = []

# 1. Delta-Walk
delta_order = delta_walk_sort(PAIR_KEYS, BIP39_WORDS)
if is_valid_mnemonic(delta_order) and apply_locks(delta_order, LOCKED_POSITIONS):
    results.append(("delta-walk", " ".join(delta_order), derive_btc_address(delta_order)))

# 2. Matrix-Grid
matrix_order = matrix_grid_order(PAIR_KEYS, BIP39_WORDS)
if is_valid_mnemonic(matrix_order) and apply_locks(matrix_order, LOCKED_POSITIONS):
    results.append(("matrix-map", " ".join(matrix_order), derive_btc_address(matrix_order)))

# === EXPORT ===
with open(CSV_EXPORT_PATH, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Strategy", "Mnemonic", "Address"])
    writer.writerows(results)

print(f"✅ Exported to {CSV_EXPORT_PATH} with {len(results)} valid candidates.")
