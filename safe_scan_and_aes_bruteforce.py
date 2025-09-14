import base64, binascii, codecs, hashlib, subprocess
from pathlib import Path
import itertools
import os

TARGETS = ["salphaseion_decrypted.bin"]
OUTDIR = Path("decoded_attempts")
OUTDIR.mkdir(exist_ok=True)

PUZZLE_WORDS = [
    "tower","moon","order","black","matrixsumlist","archichoice",
    "thispassword","enter","lastwordsbeforearchichoice"
]

# -----------------------------------
# Helper: extract printable sequences
# -----------------------------------
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

# -----------------------------------
# Safe scan (no deep recursion)
# -----------------------------------
def safe_scan(fname):
    data = Path(fname).read_bytes()
    print(f"\n[>] Scanning {fname} ({len(data)} bytes)")
    seqs = printable_sequences(data)
    print(f"Found {len(seqs)} printable sequences. Preview:")
    for s in seqs[:13]:
        print(f"   {s}")

    # Save rot13
    rot13_content = codecs.decode(data.decode('latin-1', errors='ignore'), 'rot_13')
    rot13_path = OUTDIR / (Path(fname).name + ".rot13")
    rot13_path.write_text(rot13_content)
    print(f"[+] Saved: {rot13_path}")

    # Save base64 if decodable
    try:
        decoded = base64.b64decode(data, validate=False)
        base64_path = OUTDIR / (Path(fname).name + ".base64")
        base64_path.write_bytes(decoded)
        print(f"[+] Saved: {base64_path}")
    except Exception:
        pass

# -----------------------------------
# AES brute force helper
# -----------------------------------
def try_openssl(infile, passphrase, hashed=False):
    """Try to decrypt using OpenSSL with given passphrase."""
    tmp_out = OUTDIR / (Path(infile).stem + f".{passphrase}.out")
    cmd = ["openssl", "enc", "-aes-256-cbc", "-d", "-a",
           "-in", infile, "-out", str(tmp_out)]
    if hashed:
        hashed_pw = hashlib.sha256(passphrase.encode()).hexdigest()
        cmd += ["-pass", f"pass:{hashed_pw}"]
    else:
        cmd += ["-pass", f"pass:{passphrase}"]

    result = subprocess.run(cmd, capture_output=True)
    if result.returncode == 0 and tmp_out.exists() and tmp_out.stat().st_size > 0:
        print(f"[+] SUCCESS with passphrase: {passphrase} (hashed={hashed})")
        print(f"    Output saved to {tmp_out}")
        return True
    else:
        tmp_out.unlink(missing_ok=True)
    return False

# -----------------------------------
# Generate word combinations
# -----------------------------------
def generate_passphrases():
    for w in PUZZLE_WORDS:
        yield w
    for a, b in itertools.permutations(PUZZLE_WORDS, 2):
        yield f"{a}_{b}"
    for a, b, c in itertools.permutations(PUZZLE_WORDS, 3):
        yield f"{a}_{b}_{c}"

# -----------------------------------
# Run
# -----------------------------------
if __name__ == "__main__":
    # Step 1: Safe scan
    for t in TARGETS:
        if Path(t).exists():
            safe_scan(t)
        else:
            print(f"[!] Missing file {t}")

    # Step 2: AES brute force
    print("\n[+] Starting AES brute-force...")

    # Collect files to test: original, rot13, base64
    files_to_test = []
    for t in TARGETS:
        f = Path(t)
        if f.exists():
            files_to_test.append(str(f))
            rot = OUTDIR / (f.name + ".rot13")
            if rot.exists(): files_to_test.append(str(rot))
            b64 = OUTDIR / (f.name + ".base64")
            if b64.exists(): files_to_test.append(str(b64))

    # Deduplicate
    files_to_test = list(dict.fromkeys(files_to_test))

    for infile in files_to_test:
        print(f"\n--- Testing {infile} ---")
        for pw in generate_passphrases():
            if try_openssl(infile, pw, hashed=False):
                exit(0)
            if try_openssl(infile, pw, hashed=True):
                exit(0)

    print("[-] No valid AES passphrase found.")
