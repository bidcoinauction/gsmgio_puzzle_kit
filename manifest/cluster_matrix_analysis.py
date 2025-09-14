from pathlib import Path
import itertools
import base64
import string

try:
    import base58
except ImportError:
    base58 = None
    print("[!] base58 module not found (pip install base58 to enable)")

SEQ_FILE = "stage2_results/ascii_sequences.txt"
OUTDIR = Path("matrix_results")
OUTDIR.mkdir(exist_ok=True)

# Load sequences
sequences = []
with open(SEQ_FILE) as f:
    for line in f:
        if ":" in line:
            seq = line.strip().split(":", 1)[1].strip()
            if seq:
                sequences.append(seq)

print(f"[+] Loaded {len(sequences)} sequences")
for s in sequences:
    print(s)

max_len = max(len(s) for s in sequences)
grid = [list(s.ljust(max_len)) for s in sequences]

print(f"[+] Grid size: {len(grid)} x {max_len}")

def save_variant(name, text):
    out_file = OUTDIR / f"{name}.txt"
    out_file.write_text(text)
    return out_file

def extract_columns(g):
    return [''.join(row[col] for row in g) for col in range(len(g[0]))]

def flip_horiz(g):
    return [list(reversed(row)) for row in g]

def flip_vert(g):
    return list(reversed(g))

def diagonals(g):
    diag_list = []
    rows = len(g)
    cols = len(g[0])
    for start_col in range(cols):
        diag = []
        r, c = 0, start_col
        while r < rows and c < cols:
            diag.append(g[r][c])
            r += 1
            c += 1
        diag_list.append(''.join(diag))
    for start_row in range(1, rows):
        diag = []
        r, c = start_row, 0
        while r < rows and c < cols:
            diag.append(g[r][c])
            r += 1
            c += 1
        diag_list.append(''.join(diag))
    return diag_list

# Build variants
variants = {}

# Rows (original)
variants["rows_concat"] = ''.join(''.join(row) for row in grid)

# Columns
cols = extract_columns(grid)
variants["columns_concat"] = ''.join(cols)

# Flips
for name, g in {
    "flip_horizontal": flip_horiz(grid),
    "flip_vertical": flip_vert(grid),
    "flip_both": flip_vert(flip_horiz(grid)),
}.items():
    variants[f"{name}_cols_concat"] = ''.join(extract_columns(g))

# Diagonals
variants["diagonals_concat"] = ''.join(diagonals(grid))

# Save all
for name, text in variants.items():
    save_variant(name, text)
    print(f"[+] Saved {name}")

# ------------------ Decoding Attempts ------------------
def printable_ratio(b: bytes) -> float:
    return sum(32 <= c < 127 for c in b) / len(b) if b else 0

def try_decodings(name, text):
    """Try multiple decoding methods and return promising outputs"""
    results = []
    enc = text.encode()
    # ROT13
    from codecs import encode as rot13
    rot = rot13(text, "rot_13").encode()
    if printable_ratio(rot) > 0.85:
        results.append(("rot13", rot))
    # Base64
    try:
        dec = base64.b64decode(enc, validate=True)
        if printable_ratio(dec) > 0.85:
            results.append(("base64", dec))
    except Exception:
        pass
    # Base85
    try:
        dec = base64.a85decode(enc)
        if printable_ratio(dec) > 0.85:
            results.append(("base85", dec))
    except Exception:
        pass
    # Base58
    if base58:
        try:
            dec = base58.b58decode(text)
            if printable_ratio(dec) > 0.85:
                results.append(("base58", dec))
        except Exception:
            pass
    # Hex
    try:
        dec = bytes.fromhex(text)
        if printable_ratio(dec) > 0.85:
            results.append(("hex", dec))
    except Exception:
        pass
    return results

# Run decoding attempts
decode_report = []
for name, text in variants.items():
    results = try_decodings(name, text)
    for method, decoded in results:
        out_file = OUTDIR / f"{name}_{method}_decoded.txt"
        try:
            out_file.write_bytes(decoded)
        except Exception:
            out_file.write_text(decoded.decode(errors='ignore'))
        ratio = printable_ratio(decoded)
        decode_report.append(f"{name} | {method} | ratio={ratio:.2f} | saved={out_file}")
        print(f"[!] {name} decoded with {method} (ratio={ratio:.2f}) -> {out_file}")

# Save a summary report
(OUTDIR / "decode_report.txt").write_text('\n'.join(decode_report))
print("[*] Decoding attempts complete. See decode_report.txt")
