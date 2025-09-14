import csv
import hashlib
import hmac
from mnemonic import Mnemonic
from bip32utils import BIP32Key
from ecdsa import SECP256k1, SigningKey

# =========================
# Config
# =========================
INPUT_CSV = "seedhunter_log.csv"
OUTPUT_CSV = "passphrasehunter_log.csv"
TARGET = "1KfZGvwZxsvSmemoCmEV75uqcNzYBHjkHZ"

PASSPHRASES = [
    "", "this", "breathe", "stop", "future",
    "password", "bitcoin", "wallet"
]

SALTS = [b"", b"80501", b"20200510", b"BTC80501"]

mnemo = Mnemonic("english")

# =========================
# Helper functions
# =========================
def ripemd160(x: bytes) -> bytes:
    return hashlib.new('ripemd160', x).digest()

def sha256(x: bytes):
    return hashlib.sha256(x)

def b58encode(b: bytes) -> str:
    B58_ALPHABET = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    n = int.from_bytes(b, 'big')
    res = bytearray()
    while n > 0:
        n, r = divmod(n, 58)
        res.insert(0, B58_ALPHABET[r])
    pad = 0
    for byte in b:
        if byte == 0:
            pad += 1
        else:
            break
    return (B58_ALPHABET[0:1] * pad + res).decode()

def pubkey_to_address(pubkey_bytes: bytes) -> str:
    h160 = ripemd160(sha256(pubkey_bytes).digest())
    prefix = b'\x00'
    data = prefix + h160
    checksum = sha256(sha256(data).digest()).digest()[:4]
    return b58encode(data + checksum)

def derive_bip32_root(seed_bytes: bytes):
    I = hmac.new(b"Bitcoin seed", seed_bytes, hashlib.sha512).digest()
    return I[:32]

def private_key_to_address(privkey: bytes) -> str:
    sk = SigningKey.from_string(privkey, curve=SECP256k1)
    vk = sk.get_verifying_key()
    pubkey_bytes = b'\x04' + vk.to_string()
    return pubkey_to_address(pubkey_bytes)

def derive_addresses_from_bytes(seed_bytes):
    priv = seed_bytes[:32]
    sk = SigningKey.from_string(priv, curve=SECP256k1)
    vk = sk.get_verifying_key()
    pubkey = b'\x04' + vk.to_string()
    pubkey_hash = ripemd160(sha256(pubkey).digest())
    legacy = pubkey_to_address(pubkey)
    return legacy, legacy, legacy

def mnemonic_to_address_bip44(mnemonic_phrase, passphrase=""):
    seed = mnemo.to_seed(mnemonic_phrase, passphrase)
    master = BIP32Key.fromEntropy(seed)
    child = master.ChildKey(44 + 0x80000000) \
                  .ChildKey(0 + 0x80000000) \
                  .ChildKey(0 + 0x80000000) \
                  .ChildKey(0).ChildKey(0)
    return child.Address()

def mnemonic_to_address_electrum(mnemonic_phrase, passphrase=""):
    seed = mnemo.to_seed(mnemonic_phrase, passphrase)
    I = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()
    master = BIP32Key.fromEntropy(I[:64])
    child = master.ChildKey(0).ChildKey(0)
    return child.Address()

# =========================
# Main
# =========================
with open(INPUT_CSV, newline="") as infile, open(OUTPUT_CSV, "w", newline="") as outfile:
    reader = csv.DictReader(infile)
    writer = csv.writer(outfile)
    writer.writerow(["phrase","passphrase","salt","addr_pbkdf","addr_bip44","addr_electrum"])

    total_tested = 0
    for row in reader:
        phrase_str = row["phrase"]

        for salt in SALTS:
            for pp in PASSPHRASES:
                for variant in [pp, pp.upper(), pp.capitalize()]:

                    # Derive seeds and addresses
                    seed_bytes = mnemo.to_seed(phrase_str, variant)

                    # PBKDF legacy
                    pbkdf_seed = hashlib.pbkdf2_hmac(
                        'sha512', phrase_str.encode(), salt, 2048, dklen=64
                    )
                    addr_pbkdf, _, _ = derive_addresses_from_bytes(pbkdf_seed)

                    # BIP44
                    try:
                        addr_bip44 = mnemonic_to_address_bip44(phrase_str, variant)
                    except Exception:
                        addr_bip44 = ""

                    # Electrum-style
                    try:
                        addr_electrum = mnemonic_to_address_electrum(phrase_str, variant)
                    except Exception:
                        addr_electrum = ""

                    writer.writerow([
                        phrase_str,
                        variant,
                        salt.decode() if salt else "",
                        addr_pbkdf,
                        addr_bip44,
                        addr_electrum
                    ])

                    # Show interesting results
                    if (addr_pbkdf.startswith("1K") or addr_bip44.startswith("1K") or addr_electrum.startswith("1K")):
                        print(f"{phrase_str} | passphrase={variant} | salt={salt}")
                        print(f"  PBKDF: {addr_pbkdf}")
                        print(f"  BIP44: {addr_bip44}")
                        print(f"  Electrum: {addr_electrum}")

                    # Match check
                    if (addr_pbkdf == TARGET or addr_bip44 == TARGET or addr_electrum == TARGET):
                        print(">>> MATCH FOUND!")
                        exit(0)

                    total_tested += 1
                    if total_tested % 50 == 0:
                        print(f"Tested {total_tested} combos; latest: {variant} for phrase {phrase_str}")
