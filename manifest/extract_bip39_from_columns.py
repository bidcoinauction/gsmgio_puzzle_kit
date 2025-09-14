from pathlib import Path
import re
import sys

# Requires: pip install mnemonic
try:
    from mnemonic import Mnemonic
except ImportError:
    print("Install the 'mnemonic' library: pip install mnemonic")
    sys.exit(1)

BIP39_FILE = "english.txt"
BIP39_WORDS = Path(BIP39_FILE).read_text().splitlines()

FILE = "matrix_results/columns_concat_rot13_decoded.txt"
text = Path(FILE).read_text()

# Extract alphanumeric pairs
pairs = re.findall(r'[A-Za-z0-9]{2}', text)
print(f"[+] Found {len(pairs)} pairs in {FILE}")

def base36_char(c):
    return int(c) if c.isdigit() else 10 + ord(c.upper()) - ord('A')

def pair_to_base36(p):
    return base36_char(p[0]) * 36 + base36_char(p[1])

# Convert all pairs to base36 values
indexes = [pair_to_base36(p) for p in pairs]

# Map indexes to BIP39 words (using modulo 2048 for safety)
words = [BIP39_WORDS[i % 2048] for i in indexes]

print("\n[BIP39 Word Sequence]:")
print(" ".join(words))

# Validate the sequence
mnemo = Mnemonic("english")
phrase = " ".join(words)
is_valid = mnemo.check(phrase)

if is_valid:
    print("\n[+] This is a valid BIP39 mnemonic!")
else:
    print("\n[-] This sequence does not pass BIP39 checksum validation (might be partial or transposed).")
