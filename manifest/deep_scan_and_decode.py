import base64, binascii, codecs
from pathlib import Path
import string

# ========== CONFIG ==========
fname = "salphaseion_decrypted.bin"
data = Path(fname).read_bytes()

decoded_dir = Path("decoded_attempts")
decoded_dir.mkdir(exist_ok=True)

print(f"[+] Loaded {fname} ({len(data)} bytes)")

# -------------------------
# 1. Deep signature scan
# -------------------------
signatures = {
    b'\x50\x4B\x03\x04': 'ZIP',
    b'\x89PNG\r\n\x1a\n': 'PNG',
    b'%PDF': 'PDF',
    b'\x1f\x8b\x08': 'GZIP',
    b'\x7fELF': 'ELF',
}

found = False
for sig, desc in signatures.items():
    idx = 0
    while True:
        idx = data.find(sig, idx)
        if idx == -1:
            break
        print(f"[!] Found possible {desc} signature at offset {idx}")
        found = True
        idx += 1

if not found:
    print("[+] No standard file signatures detected\n")

# -------------------------
# 2. Extract ASCII sequences
# -------------------------
def printable_sequences(b, minlen=4):
    out, seq = [], []
    for byte in b:
        if 32 <= byte <= 126:
            seq.append(chr(byte))
        else:
            if len(seq) >= minlen:
                out.append(''.join(seq))
            seq = []
    if len(seq) >= minlen:
        out.append(''.join(seq))
    return out

seqs = printable_sequences(data)
print("[+] Extracting printable ASCII sequences (>=4 chars)...")
for s in seqs[:40]:
    print(s)

# -------------------------
# Save helper
# -------------------------
def save_output(name, content):
    outname = decoded_dir / f"{name}.out"
    outname.write_bytes(content if isinstance(content, bytes) else content.encode())
    print(f"[+] Saved decoded output: {outname}")

# -------------------------
# 3. Try base encodings
# -------------------------
for enc, func in [
    ("base32", base64.b32decode),
    ("base64", base64.b64decode),
    ("base85", base64.b85decode),
]:
    try:
        out = func(data, validate=False)
        save_output(enc, out)
    except Exception:
        pass

# --- ROT13 ---
try:
    rot = codecs.decode(data.decode('latin-1', errors='ignore'), 'rot_13')
    if rot and rot != data.decode('latin-1', errors='ignore'):
        save_output("rot13", rot)
except Exception:
    pass

# -------------------------
# 4. Single-byte XOR brute force
# -------------------------
print("[+] Trying single-byte XOR keys...")
for key in range(256):
    xored = bytes([b ^ key for b in data])
    if b"bitcoin" in xored.lower() or b"bc1" in xored or b"seed" in xored.lower():
        name = f"xor_{key:02x}"
        save_output(name, xored)
        print(f"[!] Found likely hit with XOR key 0x{key:02x}")

# -------------------------
# 5. Multi-byte XOR brute force (puzzle keywords)
# -------------------------
keywords = [
    b"tower",
    b"matrix",
    b"enter",
    b"archi",
    b"lastwords",
    b"password",
    b"choice",
    b"sumlist",
]

def score_printable(b):
    # Score by ratio of printable ASCII
    return sum(c in range(32, 127) for c in b) / len(b)

print("[+] Trying multi-byte XOR with puzzle keywords...")
for key in keywords:
    xored = bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])
    score = score_printable(xored)
    if score > 0.85:  # mostly printable
        name = f"multi_xor_{key.decode('latin-1', errors='ignore')}"
        save_output(name, xored)
        print(f"[!] Candidate multi-byte XOR result with key '{key.decode()}', score={score:.2f}")
