#!/usr/bin/env python3

import base64
import hashlib
from Crypto.Cipher import AES
from bip_utils import (
    Bip39SeedGenerator, Bip39MnemonicValidator, Bip44, Bip44Coins, Bip39Languages
)
from typing import List, Tuple

# === CONFIGURATION ===

TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"

AES_PASSWORD_HEX = "a713554385283a3349635b3a32857161e3198845c4793f7521af72a15f026a27"
AES_BLOB_B64 = "U2FsdGVkX18tP2/gbclQ5tNZuD4shoV3axuUd8J8aycGCAMoYfhZK0JecHTDpTFe" \
"dGJh4SJIP66qRtXvo7PTpvsIjwO8prLiC/sNHthxiGMuqIrKoO224rOisFJZgARi" \
"c7PaJPne4nab8XCFuV3NbfxGX2BUjNkef5hg7nsoadZx08dNyU2b6eiciWiUvu7D" \
"SATSFO7IFBiAMz7dDqIETKuGlTAP4EmMQUZrQNtfbJsURATW6V5VSbtZB5RFk0O+" \
"IymhstzrQHsU0Bugjv2nndmOEhCxGi/lqK2rLNdOOLutYGnA6RDDbFJUattggELh" \
"2SZx+SBpCdbSGjxOap27l9FOyl02r0HU6UxFdcsbfZ1utTqVEyNs91emQxtpgt+6" \
"BPZisil74Jv4EmrpRDC3ufnkmWwR8NfqVPIKhUiGDu5QflYjczT6DrA9vLQZu3ko" \
"k+/ZurtRYnqqsj49UhwEF9GfUfl7uQYm0UunatW43C3Z1tyFRGAzAHQUFS6jRCd+" \
"vZGyoTlOsThjXDDCSAwoX2M+yM+oaEQoVvDwVkIqRhfDNuBmEfi+HpXuJLPBS1Pb" \
"UjrgoG/Uv7o8IeyST4HBv8+5KLx7IKQS8f1kPZ2YUME+8XJx0caFYs+JS2Jdm0oj" \
"Jm3JJEcYXdKEzOQvRzi4k+6dNlJ05TRZNTJvn0fPG5cM80aQb/ckUHsLsw9a4Wzh" \
"HsrzBQRTIhog9sTm+k+LkXzIJiFfSzRgf250pbviFGoQaIFl1CTQPT2w29DLP900" \
"6bSiliywwnxXOor03Hn+7MJL27YxeaGQn0sFGgP5X0X4jm3vEBkWvtF4PZl0bXWZ" \
"LvVL/zTn87+2Zi/u7LA6y6b2yt7YVMkpheeOL0japXaiAf3bSPeUPGz/eu8ZX/Nn"

GRID = [
    'KBKWBWKKKBWKYK',
    'WKBKWKKWBKKWKW',
    'KWKWKWKKKWKWKK',
    'BKWBKWKWKYKWKK',
    'KWKKKWYYWKKWKW',
    'WKBKWKWWWKWKKB',
    'KWKWBWKBWKWKKK',
    'KKKKKWKWYKWKWK',
    'WKWKYKYWKKKBWK',
    'KBKWKWKWWKKWKY',
    'WKWKBKKWKWKWKK',
    'KWKWKWKYWKBKWK',
    'WKYKWKWKKWKBKW',
    'KKBKWKWYKWKWKK'
]

COORD_TO_WORD = {
    (4, 6): "grant", (4, 7): "capital", (8, 6): "bright", (8, 4): "forward",
    (7, 9): "miracle", (11, 7): "because", (12, 2): "memory", (13, 8): "initial",
    (9, 13): "guilt", (6, 8): "foam", (6, 5): "charge", (5, 2): "lumber",
    (8, 10): "mountain", (9, 1): "chest", (10, 4): "argue", (11, 10): "either",
    (12, 11): "juice", (13, 3): "frost"
}

SPIRAL_PATH = [
    (6,6),(6,7),(5,7),(5,6),(5,5),(6,5),(7,5),(7,6),(7,7),(7,8),(6,8),(5,8),(4,8),(4,7),(4,6),(4,5),
    (4,4),(5,4),(6,4),(7,4),(8,4),(8,5),(8,6),(8,7),(8,8),(8,9),(7,9),(6,9),(5,9),(4,9),(3,9),(3,8),
    (3,7),(3,6),(3,5),(3,4),(3,3),(4,3),(5,3),(6,3),(7,3),(8,3),(9,3),(9,4),(9,5),(9,6),(9,7),(9,8),
    (9,9),(9,10),(8,10),(7,10),(6,10),(5,10),(4,10),(3,10),(2,10),(2,9),(2,8),(2,7),(2,6),(2,5),
    (2,4),(2,3),(2,2),(3,2),(4,2),(5,2),(6,2),(7,2),(8,2),(9,2),(10,2),(10,3),(10,4),(10,5),(10,6),
    (10,7),(10,8),(10,9),(10,10),(10,11),(9,11),(8,11),(7,11),(6,11),(5,11),(4,11),(3,11),(2,11),
    (1,11),(1,10),(1,9),(1,8),(1,7),(1,6),(1,5),(1,4),(1,3),(1,2),(1,1),(2,1),(3,1),(4,1),(5,1),
    (6,1),(7,1),(8,1),(9,1),(10,1),(11,1),(11,2),(11,3),(11,4),(11,5),(11,6),(11,7),(11,8),(11,9),
    (11,10),(11,11),(11,12),(10,12),(9,12),(8,12),(7,12),(6,12),(5,12),(4,12),(3,12),(2,12),
    (1,12),(0,12),(0,11),(0,10),(0,9),(0,8),(0,7),(0,6),(0,5),(0,4),(0,3),(0,2),(0,1),(0,0),
    (1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0),(8,0),(9,0),(10,0),(11,0),(12,0),(12,1),(12,2),
    (12,3),(12,4),(12,5),(12,6),(12,7),(12,8),(12,9),(12,10),(12,11),(12,12),(12,13),(11,13),
    (10,13),(9,13),(8,13),(7,13),(6,13),(5,13),(4,13),(3,13),(2,13),(1,13),(0,13)
]

# === UTILS ===

def decrypt_blob(password_hex: str, b64_data: str) -> bytes:
    blob = base64.b64decode(b64_data)
    salt_header = b"Salted__"
    if blob.startswith(salt_header):
        salt = blob[8:16]
        key_iv = hashlib.md5(bytes.fromhex(password_hex) + salt).digest()
        for _ in range(2):
            key_iv += hashlib.md5(key_iv[-16:] + bytes.fromhex(password_hex) + salt).digest()
        key = key_iv[:32]
        iv = key_iv[32:48]
        aes = AES.new(key, AES.MODE_CBC, iv)
        return aes.decrypt(blob[16:])
    raise ValueError("Invalid blob format")

def get_color_at(coord: Tuple[int, int]) -> str:
    row, col = coord
    return GRID[row][col]

def extract_ordered_words():
    yellow_coords = []
    blue_coords = []
    for coord in SPIRAL_PATH:
        color = get_color_at(coord)
        if color == "Y" and coord in COORD_TO_WORD:
            yellow_coords.append(coord)
        elif color == "B" and coord in COORD_TO_WORD:
            blue_coords.append(coord)
        if len(yellow_coords) == 9 and len(blue_coords) == 9:
            break
    return [COORD_TO_WORD[c] for c in yellow_coords + blue_coords]

def validate_mnemonic(words: List[str]):
    phrase = " ".join(words)
    if not Bip39MnemonicValidator(phrase, Bip39Languages.ENGLISH).Validate():
        return False, None
    seed = Bip39SeedGenerator(phrase, lang=Bip39Languages.ENGLISH).Generate()
    bip44 = Bip44.FromSeed(seed, Bip44Coins.BITCOIN)
    addr = bip44.PublicKey().ToAddress()
    return addr == TARGET_ADDRESS, addr

# === MAIN ===

if __name__ == "__main__":
    print("[+] Decrypting blob...")
    decrypted = decrypt_blob(AES_PASSWORD_HEX, AES_BLOB_B64)
    print(f"[✓] Decrypted {len(decrypted)} bytes.")

    print("[+] Extracting spiral-ordered mnemonic words...")
    words = extract_ordered_words()
    print("Mnemonic:", " ".join(words))

    print("[+] Validating mnemonic and deriving BTC address...")
    match, derived_addr = validate_mnemonic(words)
    if match:
        print(f"[🎯] Address MATCHES target: {derived_addr}")
    else:
        print(f"[❌] Address does NOT match. Derived: {derived_addr}")
