from pathlib import Path
import string
import re

FILE = "matrix_results/columns_concat_rot13_decoded.txt"
text = Path(FILE).read_text()

# 1. Extract alphanumeric pairs
pairs = re.findall(r'[A-Za-z0-9]{2}', text)
print(f"[+] Extracted {len(pairs)} pairs, first 20: {pairs[:20]}")

# Helper to map base36 char
def base36_char(c):
    if c.isdigit():
        return int(c)
    return 10 + ord(c.upper()) - ord('A')

# Decode a pair to a base36 value
def pair_to_base36(p):
    return base36_char(p[0]) * 36 + base36_char(p[1])

# Try ASCII decoding from base36
decoded_ascii = ''.join(chr(pair_to_base36(p)) if 32 <= pair_to_base36(p) < 127 else '.' for p in pairs)
print("\n[Base36→ASCII]")
print(decoded_ascii[:200])

# Map to A-Z for 0–25
decoded_AZ = ''.join(chr((pair_to_base36(p) % 26) + ord('A')) for p in pairs)
print("\n[Base36 mod 26 → A-Z]")
print(decoded_AZ[:200])

# If BIP39-style indexes (0–2047)
decoded_idx = [pair_to_base36(p) for p in pairs]
print("\n[Base36 values]")
print(decoded_idx[:40])

# Polybius square attempt (6x6)
# Row: first char (0-5), Col: second char (0-5)
def polybius_decode(p):
    try:
        r = int(p[0], 36) % 6
        c = int(p[1], 36) % 6
        index = r * 6 + c
        return chr(index + ord('A'))
    except:
        return '?'

decoded_poly6 = ''.join(polybius_decode(p) for p in pairs)
print("\n[Polybius 6x6]")
print(decoded_poly6[:200])

# Save outputs
outdir = Path("pair_results")
outdir.mkdir(exist_ok=True)
(Path(outdir) / "decoded_base36_ascii.txt").write_text(decoded_ascii)
(Path(outdir) / "decoded_base36_mod26.txt").write_text(decoded_AZ)
(Path(outdir) / "decoded_polybius6.txt").write_text(decoded_poly6)

print("\n[*] Saved outputs to pair_results/. Inspect for patterns.")
