from pathlib import Path
import math
import random
import re
from collections import Counter

# Config
decoded_files = list(Path("matrix_results").glob("*_rot13_decoded.txt"))

# English letter frequency (ETAOIN SHRDLU order)
english_freq = "ETAOINSHRDLCUMWFGYPBVKJXQZ"

def caesar_shift(text, n):
    result = []
    for c in text:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            result.append(chr((ord(c) - base + n) % 26 + base))
        else:
            result.append(c)
    return ''.join(result)

def rotN_bruteforce(text):
    results = []
    for n in range(1, 26):
        shifted = caesar_shift(text, n)
        if any(word in shifted.lower() for word in ["the", "and", "you", "bitcoin", "seed", "key", "flag"]):
            results.append((n, shifted))
    return results

# Frequency score for a candidate key
def fitness(text):
    text = re.sub(r'[^A-Za-z]', '', text).upper()
    if not text:
        return 0
    counts = Counter(text)
    freqs = [count / len(text) for _, count in counts.most_common()]
    # Score by comparing letter frequency order
    letters_by_freq = ''.join([x for x, _ in counts.most_common()])
    score = sum(abs(english_freq.index(letters_by_freq[i]) - i) for i in range(min(len(letters_by_freq), 10)))
    return -score  # lower is better, so return negative

def decrypt_substitution(ciphertext, key_map):
    table = str.maketrans(key_map)
    return ciphertext.translate(table)

def random_key():
    letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    random.shuffle(letters)
    return ''.join(letters)

def swap_letters(key):
    a, b = random.sample(range(26), 2)
    key_list = list(key)
    key_list[a], key_list[b] = key_list[b], key_list[a]
    return ''.join(key_list)

def substitution_solver(ciphertext, iterations=5000):
    ciphertext_up = ciphertext.upper()
    key = random_key()
    best_key = key
    best_score = fitness(decrypt_substitution(ciphertext_up, str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", key)))
    for i in range(iterations):
        candidate = swap_letters(best_key)
        candidate_text = decrypt_substitution(ciphertext_up, str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", candidate))
        candidate_score = fitness(candidate_text)
        if candidate_score > best_score or random.random() < math.exp((candidate_score-best_score)/5):
            best_key = candidate
            best_score = candidate_score
    return decrypt_substitution(ciphertext_up, str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", best_key))

for file in decoded_files:
    text = file.read_text()
    print(f"\n==== {file.name} ====")

    # Step 1: ROT-N brute force
    rot_hits = rotN_bruteforce(text)
    if rot_hits:
        print("ROT-N candidates found:")
        for n, shifted in rot_hits:
            print(f"[ROT{n}] {shifted[:200]}...")
        continue

    # Step 2: Substitution cipher solver
    print("No ROT-N hit; running frequency-based substitution solver...")
    result = substitution_solver(text, iterations=10000)
    print("Top candidate after substitution solving:")
    print(result[:500])
