import base64, binascii, codecs, subprocess, itertools, os
from pathlib import Path
import string

# === CONFIG ===
INPUTS = [
    "salphaseion_decrypted.bin",
    "stage2.bin",
    "decoded_attempts/base64.out",
    "decoded_attempts/rot13.out",
]
OUTPUT_DIR = Path("decoded_attempts")
OUTPUT_DIR.mkdir(exist_ok=True)

PUZZLE_WORDS = [
    "tower","moon","order","black","archi","matrix",
    "sumlist","lastwords","enter","password","choice",
    "thispassword","lastwordsbeforearchichoice"
]

# --- utilities ---
def save_output(base_name, content):
    out = OUTPUT_DIR / base_name
    out.write_bytes(content)
    print(f"[+] Saved: {out}")
    return out

def printable_sequences(b, minlen=4):
    seqs, cur = [], []
    for c in b:
        if 32 <= c <= 126:
            cur.append(chr(c))
        else:
            if len(cur) >= minlen:
                seqs.append("".join(cur))
            cur = []
    if len(cur) >= minlen:
        seqs.append("".join(cur))
    return seqs

def xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def try_aes_decrypt(data_file: Path, password: str):
    out_file = OUTPUT_DIR / f"aes_{password}.bin"
    cmd = [
        "openssl","enc","-aes-256-cbc","-d","-a",
        "-in",str(data_file),
        "-pass",f"pass:{password}"
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0 and result.stdout:
            if any(x in result.stdout for x in [b"btc", b"bitcoin", b"bc1"]):
                save_output(out_file.name, result.stdout)
                print(f"[!] AES candidate passphrase: {password}")
    except Exception:
        pass

# --- scanning ---
def deep_scan(file_path: Path, depth=0, visited=None):
    if visited is None:
        visited = set()
    if file_path in visited:
        return
    visited.add(file_path)

    try:
        data = file_path.read_bytes()
    except FileNotFoundError:
        return
    print(f"\n[{'='*depth}>] Scanning {file_path} ({len(data)} bytes)")

    # strings preview
    seqs = printable_sequences(data)
    print(f"Found {len(seqs)} printable sequences. Preview:")
    for s in seqs[:20]:
        print("  ", s)

    # base encodings
    for enc, func in [
        ("base32", base64.b32decode),
        ("base64", base64.b64decode),
        ("base85", base64.b85decode),
    ]:
        try:
            decoded = func(data, validate=False)
            out_file = save_output(f"{file_path.name}.{enc}", decoded)
            deep_scan(out_file, depth + 1, visited)
        except Exception:
            pass

    # ROT13
    try:
        rot = codecs.decode(data.decode("latin-1", "ignore"), "rot_13")
        if rot and rot.encode() != data:
            out_file = save_output(f"{file_path.name}.rot13", rot.encode())
            deep_scan(out_file, depth + 1, visited)
    except Exception:
        pass

    # single-byte XOR
    for key in range(256):
        xored = bytes([b ^ key for b in data])
        if b"btc" in xored.lower() or b"bc1" in xored or b"seed" in xored.lower():
            out_file = save_output(f"{file_path.name}.xor_{key:02x}", xored)
            deep_scan(out_file, depth + 1, visited)

    # multi-byte XOR with all 1-3 word combinations
    all_keys = PUZZLE_WORDS[:]
    all_keys += ["".join(p) for p in itertools.permutations(PUZZLE_WORDS, 2)]
    all_keys += ["".join(p) for p in itertools.permutations(PUZZLE_WORDS, 3)]
    for key in all_keys:
        kb = key.encode()
        xored = xor_bytes(data, kb)
        ascii_ratio = sum(c in bytes(string.printable, "ascii") for c in xored) / len(xored)
        if ascii_ratio > 0.85:
            out_file = save_output(f"{file_path.name}.multi_xor_{key}", xored)
            deep_scan(out_file, depth + 1, visited)

    # try AES decrypt using each key (no sha256 hash – OpenSSL handles)
    for key in PUZZLE_WORDS:
        try_aes_decrypt(file_path, key)

# --- main ---
for fname in INPUTS:
    deep_scan(Path(fname))
