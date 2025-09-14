import csv
import itertools
from bip_utils import (
    Bip39MnemonicValidator, Bip39SeedGenerator, Bip44, Bip44Coins, Bip39Languages
)
from typing import List, Dict

# === CONFIG ===
TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
BIP39_LANGUAGE = Bip39Languages.ENGLISH

WORDS = [
    "frost", "because", "bright", "guilt", "grant", "lumber",
    "mountain", "either", "forward", "miracle", "charge",
    "foam", "capital", "argue", "initial", "juice", "chest", "memory"
]

PAIR_KEYS = [
    "kr", "4E", "68", "8f", "J1", "FY", "b0", "dE", "c5",
    "M7", "sU", "TW", "NH", "Aa", "98", "vD", "rm", "Xe"
]

OUTPUT_FILE = "reorder_matrix_delta_cluster_output.csv"

# === FUNCTIONS ===
def to_base36(pair: str) -> int:
    try:
        return int(pair, 36)
    except ValueError:
        return sum(ord(c) for c in pair)

def matrix_layout(words: List[str], rows: int, cols: int) -> List[List[str]]:
    matrix = [["____" for _ in range(cols)] for _ in range(rows)]
    for i, word in enumerate(words):
        r, c = divmod(i, cols)
        if r < rows:
            matrix[r][c] = word
    return matrix

def spiral_traverse(matrix: List[List[str]]) -> List[str]:
    result = []
    top, left = 0, 0
    bottom, right = len(matrix), len(matrix[0])
    while top < bottom and left < right:
        for i in range(left, right):
            result.append(matrix[top][i])
        top += 1
        for i in range(top, bottom):
            result.append(matrix[i][right - 1])
        right -= 1
        if top < bottom:
            for i in range(right - 1, left - 1, -1):
                result.append(matrix[bottom - 1][i])
            bottom -= 1
        if left < right:
            for i in range(bottom - 1, top - 1, -1):
                result.append(matrix[i][left])
            left += 1
    return result

def check_mnemonic(words: List[str]) -> bool:
    mnemonic = " ".join(words)
    try:
        return Bip39MnemonicValidator(mnemonic, lang=BIP39_LANGUAGE).Validate()
    except Exception:
        return False

def derive_address(mnemonic: str) -> str:
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
    bip44_mst = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)
    return bip44_mst.PublicKey().ToAddress()

def run():
    tested = set()
    valid_results = []
    with open(OUTPUT_FILE, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Layout", "Mnemonic", "BTC Address"])

        for rows, cols in [(3, 6), (6, 3), (4, 5), (5, 4)]:
            layout_name = f"{rows}x{cols}"
            matrix = matrix_layout(WORDS, rows, cols)
            ordered = spiral_traverse(matrix)

            if len(ordered) != 18:
                continue
            if tuple(ordered) in tested:
                continue
            tested.add(tuple(ordered))

            if check_mnemonic(ordered):
                mnemonic = " ".join(ordered)
                address = derive_address(mnemonic)
                print(f"[VALID] {layout_name} → {address}")
                writer.writerow([layout_name, mnemonic, address])
                valid_results.append((layout_name, mnemonic, address))

    print(f"✅ Exported {len(valid_results)} valid mnemonics to {OUTPUT_FILE}")

if __name__ == "__main__":
    run()
