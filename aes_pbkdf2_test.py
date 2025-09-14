import hashlib
import base64
import subprocess
from pathlib import Path

# Input variables
encrypted_file = "salphaseion_full.txt"  # base64-encoded file
password = "LASTWORDSBEFOREARCHICHOICE_MATRIXSUMLIST_ENTER_THISPASSWORD"
out_dir = Path("pbkdf2_attempts")
out_dir.mkdir(exist_ok=True)

# Convert password to SHA256 hex (same as you used on CLI)
sha256_pass = hashlib.sha256(password.encode()).hexdigest()

# Methods to test
methods = [
    # (description, args)
    ("legacy", ["openssl", "enc", "-aes-256-cbc", "-d", "-a",
                "-in", encrypted_file,
                "-pass", f"pass:{sha256_pass}"]),
    ("pbkdf2", ["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-d", "-a",
                "-in", encrypted_file,
                "-pass", f"pass:{sha256_pass}"]),
]

for name, cmd in methods:
    out_file = out_dir / f"decrypted_{name}.bin"
    try:
        print(f"[+] Trying method: {name}")
        with open(out_file, "wb") as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE)
        if result.returncode == 0:
            print(f"[SUCCESS] Output saved to {out_file}")
        else:
            print(f"[FAILED] {name} stderr:\n{result.stderr.decode()}")
    except Exception as e:
        print(f"[ERROR] Method {name} -> {e}")
