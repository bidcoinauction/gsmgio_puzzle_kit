from pathlib import Path
from collections import Counter
import string
import re
import itertools

decoded_files = list(Path("matrix_results").glob("*_rot13_decoded.txt"))

# Characters used in base91
BASE91_CHARS = ''.join([chr(c) for c in range(33, 127)])

def printable_ratio(b: bytes) -> float:
    return sum(32 <= c < 127 for c in b) / len(b) if b else 0

def chunker(seq, size):
    return [seq[i:i+size] for i in range(0, len(seq), size)]

def analyze_grid(text, width=13):
    # Build a grid
    clean = ''.join(c for c in text if c != '\n')
    grid = chunker(clean, width)
    grid = [row.ljust(width) for row in grid]

    print(f"[Grid {width}x{len(grid)}]")
    # Column frequencies
    col_freqs = []
    for col in range(width):
        chars = [row[col] for row in grid if col < len(row)]
        freq = Counter(chars)
        col_freqs.append(freq)

    for i, freq in enumerate(col_freqs):
        common = ' '.join([f"{c}:{n}" for c, n in freq.most_common(5)])
        print(f"Column {i}: {common}")

    return grid

def find_repeats(text):
    print("[Top 20 repeating bigrams/trigrams]")
    cleaned = re.sub(r'[^A-Za-z0-9\[\]\{\}@/<>]', '', text)
    bigrams = Counter([cleaned[i:i+2] for i in range(len(cleaned)-1)])
    trigrams = Counter([cleaned[i:i+3] for i in range(len(cleaned)-2)])
    for k,v in bigrams.most_common(10):
        print(f"2-gram {k}: {v}")
    for k,v in trigrams.most_common(10):
        print(f"3-gram {k}: {v}")

def try_exotic_decodes(text):
    print("[Exotic decoders]")
    # Attempt base91-like decoding
    try:
        import base91
    except ImportError:
        base91 = None
        print("base91 module not installed; skipping.")
    else:
        try:
            dec = base91.decode(text)
            if printable_ratio(dec) > 0.85:
                print("Base91 decode produced printable text!")
                Path("matrix_results/base91_attempt.txt").write_bytes(dec)
        except Exception:
            pass

    # Attempt simple polybius grouping (pairs of characters)
    pairs = chunker(''.join(c for c in text if c.isalnum()), 2)
    sample = pairs[:20]
    print(f"Sample polybius-style pairs: {sample}")

for file in decoded_files:
    print("\n=============================================")
    print(f"File: {file.name}")
    text = file.read_text()

    # Step 1: Grid frequency analysis
    analyze_grid(text, width=13)

    # Step 2: Find repeats
    find_repeats(text)

    # Step 3: Exotic decoding attempts
    try_exotic_decodes(text)

print("\n[*] Analysis complete. Review printed column frequencies and pattern data.")
