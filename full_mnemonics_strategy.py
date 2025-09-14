import itertools
import csv
from bip_utils import (
    Bip39MnemonicValidator, Bip39SeedGenerator, Bip44, Bip44Coins, Bip39Languages
)
from typing import List, Tuple, Callable
from collections import defaultdict, Counter
from Levenshtein import distance as levenshtein_distance

# === Configuration ===
BIP39_WORDS = [
    "frost", "argue", "mountain", "chest", "guilt", "memory", "bright", "initial", "lumber",
    "foam", "juice", "charge", "because", "either", "miracle", "grant", "capital", "forward"
]

PAIR_KEYS = [
    "kr", "4E", "68", "8f", "J1", "FY", "b0", "dE", "c5",
    "M7", "sU", "TW", "NH", "Aa", "98", "vD", "rm", "Xe"
]

TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
CSV_EXPORT_PATH = "valid_mnemonics.csv"
FULL_LOG_CSV = "full_mnemonics.csv"

# === Address Derivation ===
def derive_btc_address(mnemonic: str) -> str:
    if not Bip39MnemonicValidator(mnemonic, Bip39Languages.ENGLISH).Validate():
        return None
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
    bip44_mst = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)
    return bip44_mst.Purpose().Coin().Account(0).Change(0).AddressIndex(0).PublicKey().ToAddress()

# === Strategies ===
def strategy_ascii_sum(pairs):
    return sorted(range(len(pairs)), key=lambda i: sum(ord(c) for c in pairs[i]))

def strategy_base36(pairs):
    return sorted(range(len(pairs)), key=lambda i: int(pairs[i].encode().hex(), 16) % 18)

def strategy_columnar_transposition(pairs):
    return sorted(range(len(pairs)), key=lambda i: pairs[i])

def strategy_char_rank(pairs):
    rank_map = {c: i for i, c in enumerate(sorted(set("".join(pairs))))}
    return sorted(range(len(pairs)), key=lambda i: rank_map[pairs[i][0]] + rank_map.get(pairs[i][1], 0))

def strategy_weighted_hybrid(pairs):
    strategies = [
        strategy_ascii_sum,
        strategy_columnar_transposition,
        strategy_char_rank,
        strategy_base36
    ]
    scores = defaultdict(int)
    for strat in strategies:
        for pos, idx in enumerate(strat(pairs)):
            scores[idx] += pos
    return sorted(range(len(pairs)), key=lambda i: scores[i])

# === Utilities ===
def apply_strategy(indices: List[int]) -> List[str]:
    return [BIP39_WORDS[i] for i in indices]

def test_mnemonic(words: List[str]) -> Tuple[str, str] or None:
    mnemonic = " ".join(words)
    address = derive_btc_address(mnemonic)
    if address:
        print(f"✅ {mnemonic} → {address}")
        return mnemonic, address
    return None

def export_to_csv(results: List[Tuple[str, str]], filename: str = CSV_EXPORT_PATH):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Mnemonic", "Address"])
        for row in results:
            writer.writerow(row)
    print(f"\n✅ Exported {len(results)} valid mnemonics to: {filename}")

def export_all_to_csv(candidates: List[str], filename: str = FULL_LOG_CSV):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Mnemonic"])
        for m in candidates:
            writer.writerow([m])
    print(f"📂 Exported {len(candidates)} permutations to: {filename}")

# === Fuzzy Agreement Example ===
def positional_agreement_score(strategies):
    position_counts = defaultdict(list)
    for strat in strategies:
        for pos, word in enumerate(strat):
            position_counts[word].append(pos)
    averaged = {word: sum(positions)/len(positions) for word, positions in position_counts.items()}
    return sorted(BIP39_WORDS, key=lambda w: averaged.get(w, 999))

# === Runner ===
if __name__ == "__main__":
    STRATEGIES: dict[str, Callable] = {
        "ASCII Sum": strategy_ascii_sum,
        "Base36 Mod": strategy_base36,
        "Columnar": strategy_columnar_transposition,
        "Char Rank": strategy_char_rank,
        "Weighted Hybrid": strategy_weighted_hybrid
    }

    valid_results = []
    all_mnemonics = []
    all_word_orders = []

    for name, strat_func in STRATEGIES.items():
        print(f"\n🔍 Testing strategy: {name}")
        try:
            idx_order = strat_func(PAIR_KEYS)
            words = apply_strategy(idx_order)
            all_word_orders.append(words)
            result = test_mnemonic(words)
            mnemonic = " ".join(words)
            all_mnemonics.append(mnemonic)
            if result:
                valid_results.append(result)
            else:
                print("❌ Invalid mnemonic")
        except Exception as e:
            print(f"⚠️ Error in {name}: {e}")

    # Positional Agreement Composite Strategy
    composite = positional_agreement_score(all_word_orders)
    print("\n📊 Composite Positional Agreement Strategy")
    result = test_mnemonic(composite)
    mnemonic = " ".join(composite)
    all_mnemonics.append(mnemonic)
    if result:
        valid_results.append(result)

    if valid_results:
        export_to_csv(valid_results)
    export_all_to_csv(all_mnemonics)

    # Next Steps Prompt
    print("""
🔁 Let me know if you want to:
- 🧬 Chain multiple strategies together (like CharRank → Columnar → ASCII)
- 📊 Score positional agreement across methods
- 🧪 Use fuzzy reordering from close match clusters (e.g., Levenshtein)
- 📜 Log all permutations to CSV for auditing, including invalid ones
    """)
