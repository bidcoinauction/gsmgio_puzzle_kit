import re
from pathlib import Path
from mnemonic import Mnemonic

# --- Setup ---
offsets = [0x2c, 0x45, 0xe6, 0x128, 0x193, 0x226, 0x2a4,
           0x2ed, 0x2f3, 0x366, 0x3b8, 0x3c1, 0x4c6]
deltas = [j - i for i, j in zip(offsets, offsets[1:])]
print("[+] Offsets:", offsets)
print("[+] Deltas:", deltas)

BIP39_FILE = "english.txt"
BIP39_WORDS = Path(BIP39_FILE).read_text().splitlines()
mnemo = Mnemonic("english")

# Extract pairs
FILE = "matrix_results/columns_concat_rot13_decoded.txt"
text = Path(FILE).read_text()

def base36_char(c):
    return int(c) if c.isdigit() else 10 + ord(c.upper()) - ord('A')

pairs = re.findall(r'[A-Za-z0-9]{2}', text)
coords = []
for p in pairs:
    r = base36_char(p[0])
    c = base36_char(p[1])
    idx = r * 36 + c
    word = BIP39_WORDS[idx % 2048]
    coords.append((p, word))

print(f"[+] Loaded {len(coords)} pairs")

# --- Josephus-style traversal ---
def josephus_path(start, deltas, clockwise=True):
    remaining = list(range(len(coords)))
    order = []
    pos = start
    for d in deltas:
        if not remaining:
            break
        step = d % len(remaining)
        if not clockwise:
            step = -step
        pos = (pos + step) % len(remaining)
        order.append(remaining.pop(pos))
    # Append remaining nodes
    order += remaining
    return order

def validate_order(order):
    words = [coords[i][1] for i in order]
    phrase = " ".join(words)
    return mnemo.check(phrase), phrase

found = False
for clockwise in [True, False]:
    for add in [0, 1]:  # try delta and delta+1
        modified_deltas = [d + add for d in deltas]
        for start in range(len(coords)):
            order = josephus_path(start, modified_deltas, clockwise)
            valid, phrase = validate_order(order)
            if valid:
                print(f"\n[VALID MNEMONIC] Found with start={start}, clockwise={clockwise}, +{add}")
                print(phrase)
                found = True
                break
        if found:
            break
    if found:
        break

if not found:
    print("\n[-] No valid mnemonic found with Josephus-style delta walking.")

# --- Part B: Dump raw bytes at offsets ---
bin_file = Path("salphaseion_decrypted.bin")
if bin_file.exists():
    data = bin_file.read_bytes()
    print("\n[+] Raw bytes at offsets:")
    for off in offsets:
        snippet = data[off:off+8]
        hex_snip = " ".join(f"{b:02x}" for b in snippet)
        ascii_snip = "".join(chr(b) if 32 <= b < 127 else "." for b in snippet)
        print(f"{off:04x}: {hex_snip} | {ascii_snip}")
else:
    print("[-] salphaseion_decrypted.bin not found for raw byte extraction.")
