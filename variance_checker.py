import hashlib, hmac, ecdsa, base58, csv, itertools
from mnemonic import Mnemonic
from bip32utils import BIP32Key

# ===============================
# Config
# ===============================

TARGET_ADDRESS = "1KfZGvwZxsvSmemoCmEV75uqcNzYBHjkHZ"
OUTPUT_FILE = "seed_results.csv"

# Expanded word pool
CANDIDATE_WORDS = [
    "moon","tower","food","real","black","subject","this","order",
    "proof","time","liberty","day","future","hope","find","seed",
    "picture","eye","mask","pyramid","vote","police","world","brave",
    "welcome","only"
]

# Structured slots: pre-fill strong clues
base_slots = [
    "tower", "moon", "order", "black", None, None,
    "day", "time", "proof", "real", "this", "liberty"
]

# Slot candidates
slot5_candidates = ["food", "hope", "find"]
slot6_candidates = ["subject", "breathe", "find", "hope", "real"]

# Words allowed to swap if they appear
swap_words = ["tower", "food", "vote", "stop"]

# Passphrases and salts
passphrases = ["", "this", "breathe", "stop", "future"]
salts = [b"", b"80501", b"20200510", b"BTC80501"]

mnemo = Mnemonic("english")

# ===============================
# Helpers
# ===============================

def hash160(b):
    return hashlib.new('ripemd160', hashlib.sha256(b).digest()).digest()

def base58check(prefix, payload):
    data = prefix + payload
    checksum = hashlib.sha256(hashlib.sha256(data).digest()).digest()[:4]
    return base58.b58encode(data + checksum).decode()

def convertbits(data, frombits, tobits, pad=True):
    acc = 0; bits = 0; ret = []
    maxv = (1 << tobits) - 1
    for value in data:
        acc = (acc << frombits) | value
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)
    if pad and bits:
        ret.append((acc << (tobits - bits)) & maxv)
    return ret

def bech32_polymod(values):
    generator = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa,
                 0x3d4233dd, 0x2a1462b3]
    chk = 1
    for v in values:
        b = (chk >> 25)
        chk = ((chk & 0x1ffffff) << 5) ^ v
        for i in range(5):
            chk ^= generator[i] if ((b >> i) & 1) else 0
    return chk

def bech32_hrp_expand(s):
    return [ord(x) >> 5 for x in s] + [0] + [ord(x) & 31 for x in s]

def bech32_create_checksum(hrp, data):
    values = bech32_hrp_expand(hrp) + data
    polymod = bech32_polymod(values + [0, 0, 0, 0, 0, 0]) ^ 1
    return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]

def bech32_encode(hrp, data):
    charset = 'qpzry9x8gf2tvdw0s3jn54khce6mua7l'
    combined = data + bech32_create_checksum(hrp, data)
    return hrp + '1' + ''.join([charset[d] for d in combined])

def derive_addresses_from_bytes(seed_bytes):
    priv = seed_bytes[:32]
    sk = ecdsa.SigningKey.from_string(priv, curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    pubkey = b'\x04' + vk.to_string()
    pubkey_hash = hash160(pubkey)
    legacy = base58check(b'\x00', pubkey_hash)
    redeem = b'\x00\x14' + pubkey_hash
    redeem_hash = hash160(redeem)
    p2sh = base58check(b'\x05', redeem_hash)
    converted = convertbits(pubkey_hash, 8, 5)
    bech32 = bech32_encode('bc', [0] + converted)
    return legacy, p2sh, bech32

def pbkdf2_seed(passphrase, salt, iterations=2048):
    return hashlib.pbkdf2_hmac('sha512', passphrase.encode(), salt, iterations, dklen=64)

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

# ===============================
# Generator
# ===============================
def generate_variants():
    """
    Generates structured word lists:
    - Uses base_slots with slot5 and slot6 candidates
    - Adds swapping logic for specific words
    - Expands with additional candidate words beyond slot positions
    """
    base = base_slots[:]
    for w5 in slot5_candidates:
        for w6 in slot6_candidates:
            filled = base[:]
            filled[4] = w5
            filled[5] = w6

            swaps = [filled]
            for i, j in itertools.combinations(range(len(filled)), 2):
                if filled[i] in swap_words and filled[j] in swap_words:
                    new_list = filled[:]
                    new_list[i], new_list[j] = new_list[j], new_list[i]
                    swaps.append(new_list)

            seen = set()
            for variant in swaps:
                # Optionally mix in random unused words from expanded pool
                missing_words = [w for w in CANDIDATE_WORDS if w not in variant]
                # Only use first few extras to avoid infinite explosion
                extras = missing_words[:max(0, 12 - len(variant))]
                candidate = (variant + extras)[:12]
                tup = tuple(candidate)
                if tup not in seen:
                    seen.add(tup)
                    yield candidate

# ===============================
# Main
# ===============================
print("=== Expanded Seed Search (BIP44 / Electrum / PBKDF2) ===")
with open(OUTPUT_FILE, "w", newline="") as csvfile:
    fieldnames = ["phrase","salt","passphrase","addr_pdkf","addr_bip44","addr_electrum"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for variant in generate_variants():
        phrase = " ".join(variant)
        for salt in salts:
            for pphrase in passphrases:
                for phrase_case in [phrase, phrase.upper()]:
                    # PBKDF2-based legacy derivation
                    seed = pbkdf2_seed(phrase_case, salt)
                    legacy_pbkdf, _, _ = derive_addresses_from_bytes(seed)

                    # BIP44
                    try:
                        addr_bip44 = mnemonic_to_address_bip44(phrase_case, pphrase)
                    except:
                        addr_bip44 = ""

                    # Electrum
                    try:
                        addr_electrum = mnemonic_to_address_electrum(phrase_case, pphrase)
                    except:
                        addr_electrum = ""

                    match = (legacy_pbkdf == TARGET_ADDRESS or
                             addr_bip44 == TARGET_ADDRESS or
                             addr_electrum == TARGET_ADDRESS)

                    print(f"{phrase_case} | salt={salt} | passphrase={pphrase}")
                    print(f"  PBKDF: {legacy_pbkdf}")
                    print(f"  BIP44: {addr_bip44}")
                    print(f"  Electrum: {addr_electrum}")

                    writer.writerow({
                        "phrase": phrase_case,
                        "salt": salt.decode() if salt else "(none)",
                        "passphrase": pphrase,
                        "addr_pdkf": legacy_pbkdf,
                        "addr_bip44": addr_bip44,
                        "addr_electrum": addr_electrum
                    })

                    if match:
                        print(">>> MATCH FOUND!")
                        exit(0)
