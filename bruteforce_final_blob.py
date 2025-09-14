#!/usr/bin/env python3
import base64
import hashlib
from Crypto.Cipher import AES

BLOB_FILE      = "final_blob.txt"
CANDIDATES_FILE = "candidates.txt"

def evp_bytes_to_key(password: bytes, key_len: int, iv_len: int) -> (bytes, bytes):
    """
    Re-implements OpenSSL's EVP_BytesToKey with MD5, no salt.
    """
    dt = b""
    key_iv = b""
    while len(key_iv) < key_len + iv_len:
        dt = hashlib.md5(dt + password).digest()
        key_iv += dt
    return key_iv[:key_len], key_iv[key_len:key_len+iv_len]

def is_printable(b: bytes, threshold: float = 0.9) -> bool:
    """Rudimentary check: at least `threshold` fraction of bytes are in printable ASCII or newline."""
    printable = sum(1 for c in b if 32 <= c < 127 or c in (9,10,13))
    return printable / len(b) >= threshold

def try_decrypt(b64_blob: bytes, password: str):
    raw = base64.b64decode(b64_blob)
    # OpenSSL by default writes "Salted__" + 8-byte salt if salt was used.
    # If your blob begins with "Salted__", you need to skip 16 bytes and use the salt.
    # If not, EVP_BytesToKey is called with no salt.
    if raw.startswith(b"Salted__"):
        salt = raw[8:16]
        data = raw[16:]
        # TODO: if your blob really uses salt, you'd pass salt into EVP_BytesToKey.
        # For now we assume no salt => ignore.
    else:
        salt = None
        data = raw

    key, iv = evp_bytes_to_key(password.encode(), 32, 16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    try:
        pt = cipher.decrypt(data)
        # strip PKCS#7 padding
        padlen = pt[-1]
        if 1 <= padlen <= 16:
            pt = pt[:-padlen]
        return pt
    except Exception:
        return None

def main():
    with open(BLOB_FILE, "rb") as f:
        b64_blob = f.read().strip()
    with open(CANDIDATES_FILE) as f:
        candidates = [l.strip() for l in f if l.strip()]

    print(f"🔍 Trying {len(candidates)} candidate passwords…\n")
    for pwd in candidates:
        pt = try_decrypt(b64_blob, pwd)
        if not pt:
            continue
        if is_printable(pt):
            print(f"✅ Password: {pwd!r}")
            print("──── Decrypted snippet ────")
            print(pt[:512].decode('utf-8', 'replace'))
            print("───────────────────────────\n")

if __name__ == "__main__":
    main()
