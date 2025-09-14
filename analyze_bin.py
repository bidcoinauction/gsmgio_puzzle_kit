import zlib, bz2, lzma
from pathlib import Path
import math

fname = "salphaseion_decrypted.bin"
data = Path(fname).read_bytes()
size = len(data)

# --- Entropy ---
counts = {b: data.count(b) for b in set(data)}
entropy = -sum((c/size)*math.log2(c/size) for c in counts.values())
print(f"File: {fname} ({size} bytes)")
print(f"Entropy: {entropy:.2f} bits/byte\n")

# --- Try common decompressors ---
for name, func in [
    ("zlib", lambda d: zlib.decompress(d)),
    ("bz2", lambda d: bz2.decompress(d)),
    ("lzma", lambda d: lzma.decompress(d))
]:
    try:
        out = func(data)
        outname = f"{fname}.{name}.out"
        Path(outname).write_bytes(out)
        print(f"[+] Successfully decompressed with {name}, saved to {outname}")
    except Exception as e:
        print(f"[-] {name} failed: {e}")
