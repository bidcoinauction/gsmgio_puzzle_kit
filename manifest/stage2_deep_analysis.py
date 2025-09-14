import itertools
import base64
import string
from pathlib import Path

try:
    import base58
except ImportError:
    base58 = None
    print("[!] base58 module not found (pip install base58 to enable)")

FILE = "pbkdf2_attempts/decrypted_legacy.bin"
OUTDIR = Path("stage2_results")
OUTDIR.mkdir(exist_ok=True)

data = Path(FILE).read_bytes()

print(f"[+] Loaded {FILE} ({len(data)} bytes)")

# ----------------------------------------------------
# 1. Extract printable ASCII sequences with offsets
# ----------------------------------------------------
print("[+] Printable ASCII sequences (len >= 4):")
seqs = []
cur = []
start = None

for i, b in enumerate(data):
    if 32 <= b < 127:
        if start is None:
            start = i
        cur.append(chr(b))
    else:
        if cur and len(cur) >= 4:
            s = "".join(cur)
            seqs.append((start, s))
        cur = []
        start = None
# Final check for trailing printable
if cur and len(cur) >= 4:
    seqs.append((start, "".join(cur)))

seq_file = OUTDIR / "ascii_sequences.txt"
with seq_file.open("w") as f:
    for offset, s in seqs:
        line = f"{offset:08x}: {s}"
        print(line)
        f.write(line + "\n")
print(f"[+] Saved ASCII sequences to {seq_file}")

# ----------------------------------------------------
# 2. Compute offset deltas
# ----------------------------------------------------
offsets = [o for o, _ in seqs]
deltas = [offsets[i+1] - offsets[i] for i in range(len(offsets)-1)]
print("[+] Offset deltas:", deltas)

# ----------------------------------------------------
# 3. Concatenate all sequences and save
# ----------------------------------------------------
all_seq = "".join(s for _, s in seqs)
seq_concat_file = OUTDIR / "ascii_sequences_concat.txt"
seq_concat_file.write_text(all_seq)
print(f"[+] Concatenated sequence: {all_seq}")
print(f"[+] Saved to {seq_concat_file}")

# ----------------------------------------------------
# 4. Try decoding concatenated sequences
# ----------------------------------------------------
def safe_decode(name, func):
    try:
        out = func(all_seq)
        outfile = OUTDIR / f"concat_decoded_{name}.bin"
        if isinstance(out, bytes):
            outfile.write_bytes(out)
        else:
            outfile.write_text(str(out))
        print(f"[+] {name} decode succeeded -> {outfile}")
    except Exception:
        print(f"[-] {name} decode failed")

# ROT13
from codecs import encode as rot13
safe_decode("rot13", lambda s: rot13(s, "rot_13"))

# Base64
safe_decode("base64", lambda s: base64.b64decode(s, validate=True))

# Base85 (ascii85)
safe_decode("base85", lambda s: base64.a85decode(s))

# Base58
if base58:
    safe_decode("base58", lambda s: base58.b58decode(s))

# ----------------------------------------------------
# 5. Stride-based transposition analysis
# ----------------------------------------------------
def deinterleave(buf, stride):
    return bytes(buf[i::stride] for i in range(stride))

# Try stride lengths from 2 up to 16
stride_dir = OUTDIR / "stride_attempts"
stride_dir.mkdir(exist_ok=True)

for stride in range(2, 17):
    reordered = b"".join(data[i::stride] for i in range(stride))
    outfile = stride_dir / f"stride_{stride}.bin"
    outfile.write_bytes(reordered)

print(f"[+] Generated deinterleaved files in {stride_dir}")
print("[*] Next step: run deep_scan_and_decode.py on these stride files.")
