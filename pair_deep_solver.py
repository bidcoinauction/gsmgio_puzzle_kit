from pathlib import Path
import re
from collections import Counter
import string
import math
import random

# BIP39 English wordlist (2048 words)
# Download from: https://raw.githubusercontent.com/bitcoin/bips/master/bip-0039/english.txt
BIP39_FILE = "english.txt"
try:
    BIP39_WORDS = Path(BIP39_FILE).read_text().splitlines()
except Exception:
    BIP39_WORDS = []
    print("[!] BIP39 wordlist not found; skipping that step.")

decoded_files = list(Path("matrix_results").glob("*_rot13_decoded.txt"))

def base36_char(c):
    return int(c) if c.isdigit() else 10 + ord(c.upper()) - ord('A')

def pair_to_base36(p):
    return base36_char(p[0]) * 36 + base36_char(p[1])

def polybius6(p):
    try:
        r = base36_char(p[0]) % 6
        c = base36_char(p[1]) % 6
        return chr(r * 6 + c + ord('A'))
    except:
        return '?'

def extract_pairs(text):
    return re.findall(r'[A-Za-z0-9]{2}', text)

def fitness_frequency(text):
    text = re.sub(r'[^A-Z]', '', text.upper())
    counts = Counter(text)
    if not counts:
        return 0
    freq_order = ''.join([x for x, _ in counts.most_common()])
    target_order = "ETAOINSHRDLCUMWFGYPBVKJXQZ"
    return -sum(abs(target_order.index(c) - i) if c in target_order else 10 for i, c in enumerate(freq_order[:10]))

def swap_key(key):
    i, j = random.sample(range(26), 2)
    k = list(key)
    k[i], k[j] = k[j], k[i]
    return ''.join(k)

def substitution_solver(cipher, iterations=5000):
    cipher = cipher.upper()
    key = ''.join(string.ascii_uppercase)
    best_key = key
    best_score = fitness_frequency(apply_substitution(cipher, key))
    for _ in range(iterations):
        cand = swap_key(best_key)
        score = fitness_frequency(apply_substitution(cipher, cand))
        if score > best_score:
            best_key, best_score = cand, score
    return apply_substitution(cipher, best_key)

def apply_substitution(cipher, key):
    mapping = str.maketrans(string.ascii_uppercase, key)
    return cipher.translate(mapping)

def vigenere_bruteforce(cipher):
    # Simple brute with common keys
    keys = ["BITCOIN", "SEED", "KEY", "PASSWORD", "CRYPTO", "BLOCKCHAIN"]
    from itertools import cycle
    cipher = cipher.upper()
    results = []
    for k in keys:
        out = []
        for i, ch in enumerate(cipher):
            if ch.isalpha():
                shift = (ord(ch) - ord('A') - (ord(k[i % len(k)]) - ord('A'))) % 26
                out.append(chr(shift + ord('A')))
            else:
                out.append(ch)
        results.append((k, ''.join(out)))
    return results

for file in decoded_files:
    print(f"\n==== {file.name} ====")
    text = Path(file).read_text()
    pairs = extract_pairs(text)
    print(f"[+] {len(pairs)} pairs: {pairs[:15]}...")

    # Base36 values
    values = [pair_to_base36(p) for p in pairs]

    # 1. Base36 mod 26 letters
    mod26 = ''.join(chr((v % 26) + ord('A')) for v in values)
    print(f"[Base36 mod 26 → A-Z]: {mod26}")

    # 2. Polybius 6x6
    poly6 = ''.join(polybius6(p) for p in pairs)
    print(f"[Polybius 6x6]: {poly6}")

    # 3. BIP39 attempt
    if BIP39_WORDS:
        words = [BIP39_WORDS[v % len(BIP39_WORDS)] for v in values]
        print(f"[BIP39 words]: {' '.join(words[:12])} ...")

    # Try substitution solver on mod26
    candidate = substitution_solver(mod26)
    print(f"[Substitution solver candidate]: {candidate[:80]}")

    # Vigenère brute-force
    for key, plain in vigenere_bruteforce(mod26):
        print(f"[Vigenere key={key}]: {plain[:80]}")
