import itertools
import csv
from bip_utils import (
    Bip39MnemonicValidator, Bip39SeedGenerator, Bip44, Bip44Coins,
    Bip39Languages
)
from multiprocessing import Pool, cpu_count

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

# === Address Derivation ===
def derive_btc_address(mnemonic: str) -> str:
    if not Bip39MnemonicValidator(mnemonic, lang=Bip39Languages.ENGLISH).Validate():
        return None
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
    bip44_mst = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)
    addr = bip44_mst.Purpose().Coin().Account(0).Change(0).AddressIndex(0).PublicKey().ToAddress()
    return addr

# === Strategies ===
def strategy_ascii_sum(pairs):
    def ascii_sum(pair): return sum(ord(c) for c in pair)
    indexed = sorted(enumerate(pairs), key=lambda x: ascii_sum(x[1]))
    return [BIP39_WORDS[i] for i, _ in indexed]

def strategy_base36(pairs):
    def b36(pair): return int(pair.encode().hex(), 16) % 18
    indexed = sorted(enumerate(pairs), key=lambda x: b36(x[1]))
    return [BIP39_WORDS[i] for i, _ in indexed]

def strategy_columnar_transposition(pairs):
    sorted_indices = sorted(range(len(pairs)), key=lambda i: pairs[i])
    return [BIP39_WORDS[i] for i in sorted_indices]

def strategy_char_rank(pairs):
    rank_map = {char: i for i, char in enumerate(sorted(set("".join(pairs))))}
    ranked = sorted(enumerate(pairs), key=lambda x: rank_map[x[1][0]] + rank_map.get(x[1][1], 0))
    return [BIP39_WORDS[i] for i, _ in ranked]

def strategy_weighted_hybrid(pairs):
    s1 = strategy_ascii_sum(pairs)
    s2 = strategy_columnar_transposition(pairs)
    s3 = strategy_char_rank(pairs)
    s4 = strategy_base36(pairs)
    position_score = {}
    for strategy in [s1, s2, s3, s4]:
        for pos, word in enumerate(strategy):
            position_score[word] = position_score.get(word, 0) + pos
    final = sorted(BIP39_WORDS, key=lambda w: position_score.get(w, 999))
    return final

# === Mnemonic Test ===
def test_mnemonic(word_list):
    mnemonic = " ".join(word_list)
    address = derive_btc_address(mnemonic)
    if address:
        print(f"✅ {mnemonic} → {address}")
        return mnemonic, address
    return None

# === CSV Export ===
def export_to_csv(results):
    with open(CSV_EXPORT_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Mnemonic", "Address"])
        for m, a in results:
            writer.writerow([m, a])
    print(f"\n✅ Exported {len(results)} valid mnemonics to: {CSV_EXPORT_PATH}")

# === Main Runner ===
if __name__ == "__main__":
    strategies = {
        "ASCII Sum": strategy_ascii_sum,
        "Base36 Mod": strategy_base36,
        "Columnar": strategy_columnar_transposition,
        "Char Rank": strategy_char_rank,
        "Weighted Hybrid": strategy_weighted_hybrid
    }

    valid_results = []
    for name, func in strategies.items():
        print(f"\n🔍 Testing strategy: {name}")
        try:
            mnemonic = " ".join(func(PAIR_KEYS))
            addr = derive_btc_address(mnemonic)
            if addr:
                print(f"✅ {name} matched → {addr}")
                valid_results.append((mnemonic, addr))
            else:
                print("❌ Invalid mnemonic")
        except Exception as e:
            print(f"⚠️ Error in {name}: {e}")

    if valid_results:
        export_to_csv(valid_results)
    else:
        print("❌ No valid mnemonics found.")

    # ✅ Optional next steps
    print("\n🔁 Let me know if you want to:")
    print("- Chain multiple strategies together (like CharRank + Columnar)")
    print("- Score positional agreement across methods")
    print("- Use fuzzy reordering from close match clusters (e.g., Levenshtein)")
