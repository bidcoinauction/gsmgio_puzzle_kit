import hashlib
import hmac
import random
import csv
from mnemonic import Mnemonic
from bip32utils import BIP32Key
from ecdsa import SECP256k1, SigningKey

# ==========================================
# Target BTC address
# ==========================================
TARGET = "1KfZGvwZxsvSmemoCmEV75uqcNzYBHjkHZ"
mnemo = Mnemonic("english")

# ==========================================
# Candidate word pools
# ==========================================
CANDIDATE_WORDS = [
    "moon","tower","food","real","black","subject","this","order",
    "proof","time","liberty","day","future","hope","find","seed",
    "picture","eye","mask","pyramid","vote","police","world","brave",
    "welcome","only","stop","breathe"
]

# Only first 4 slots are locked
base_slots = [
    "tower", "moon", "order", "black",
    None, None, None, None, None, None, None, None
]

slot5_candidates = ["food", "hope", "find"]
slot6_candidates = ["subject", "breathe", "find", "hope", "real"]

# Passphrases and salts
passphrases = ["", "this", "breathe", "stop", "future"]
salts = [b"", b"80501", b"20200510", b"BTC80501"]

# Load BIP39 wordlist and combine
with open("english.txt") as f:
    BIP39_WORDS = [w.strip() for w in f]
FULL_POOL = list(set(CANDIDATE_WORDS + BIP39_WORDS))
flex_indices = range(6, 12)

# ==========================================
# Helper functions
# ==========================================
def ripemd160(x: bytes) -> bytes:
    return hashlib.new('ripemd160', x).digest()

def sha256(x: bytes) -> hashlib.sha256:
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
    prefix = b'\x00'
    data = prefix + pubkey_hash
    checksum = sha256(sha256(data).digest()).digest()[:4]
    addr = b58encode(data + checksum)
    return addr, None, None  # Only legacy for now

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

def looks_promising(addr: str) -> bool:
    return addr.startswith("1K")

# ==========================================
# Main loop
# ==========================================
MAX_RANDOM = 100000
total_tested = 0

with open("seedhunter_log.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["phrase", "passphrase", "salt"])

    for word5 in slot5_candidates:
        for word6 in slot6_candidates:
            for _ in range(MAX_RANDOM):
                slots = base_slots.copy()
                slots[4] = word5
                slots[5] = word6

                # Fill slots 6–11 with random mix
                for idx in flex_indices:
                    if random.random() < 0.7:
                        slots[idx] = random.choice(CANDIDATE_WORDS)
                    else:
                        slots[idx] = random.choice(FULL_POOL)

                # Avoid all identical
                if len(set(slots[6:12])) == 1:
                    continue

                phrase_str = " ".join(slots)

                for pp in passphrases:
                    for salt in salts:
                        for v in [pp, pp.upper(), pp.capitalize()]:
                            # Save log
                            writer.writerow([phrase_str, v, salt.decode() if salt else ""])

                            # Derive seeds and addresses
                            pbkdf_seed = hashlib.pbkdf2_hmac(
                                'sha512', phrase_str.encode(), salt, 2048, dklen=64)
                            addr_pbkdf, _, _ = derive_addresses_from_bytes(pbkdf_seed)

                            try:
                                addr_bip44 = mnemonic_to_address_bip44(phrase_str, v)
                            except Exception:
                                addr_bip44 = ""

                            try:
                                addr_electrum = mnemonic_to_address_electrum(phrase_str, v)
                            except Exception:
                                addr_electrum = ""

                            # Print detailed info if promising
                            if (looks_promising(addr_pbkdf) or
                                looks_promising(addr_bip44) or
                                looks_promising(addr_electrum)):
                                print(f"{phrase_str} | salt={salt} | passphrase={v}")
                                print(f"  PBKDF: {addr_pbkdf}")
                                print(f"  BIP44: {addr_bip44}")
                                print(f"  Electrum: {addr_electrum}")

                            # Match check
                            if (addr_pbkdf == TARGET or
                                addr_bip44 == TARGET or
                                addr_electrum == TARGET):
                                print(">>> MATCH FOUND!")
                                exit(0)

                            total_tested += 1
                            if total_tested % 1000 == 0:
                                print(f"Tested {total_tested} phrases; latest: {phrase_str}")
