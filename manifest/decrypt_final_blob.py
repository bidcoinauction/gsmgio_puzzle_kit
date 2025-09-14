#!/usr/bin/env python3
import base64
from Crypto.Cipher import AES
from Crypto.Hash import MD5
# OpenSSL’s EVP_BytesToKey (MD5-based) implementation:
def evp_bytes_to_key(password: bytes, key_len: int, iv_len: int, salt: bytes = b"") -> tuple[bytes, bytes]:
    """
    Derives key and IV exactly like `openssl enc -pass pass:...` (no pbkdf2, 1 iteration).
    """
    dt = b""
    key_iv = b""
    while len(key_iv) < key_len + iv_len:
        dt = MD5.new(dt + password + salt).digest()
        key_iv += dt
    return key_iv[:key_len], key_iv[key_len:key_len+iv_len]

# 1. Read the Base64‐wrapped blob
with open('final_blob.txt', 'r') as f:
    b64 = f.read().strip()
raw = base64.b64decode(b64)

# 2. Derive key+iv
password_hex = "a713554385283a3349635b3a32857161e3198845c4793f7521af72a15f026a27"
password = bytes.fromhex(password_hex)
key, iv = evp_bytes_to_key(password, key_len=32, iv_len=16)

# 3. Decrypt and strip PKCS#7 padding
cipher = AES.new(key, AES.MODE_CBC, iv)
pt = cipher.decrypt(raw)
pad_len = pt[-1]
pt = pt[:-pad_len]

# 4. Write the result
with open('salphaseion_decrypted.bin', 'wb') as out:
    out.write(pt)

print("✅ salphaseion_decrypted.bin written")
