import re

# Path to your local file
BIN_PATH = "salphaseion_decrypted.bin"
BIP39_PATH = "bip39_english.txt"

# EBCDIC-related encodings to try
encodings = ["cp037", "cp500", "latin1", "utf-8", "cp1140", "cp273"]

# Load binary
with open(BIN_PATH, "rb") as f:
    binary_data = f.read()

# Load BIP39 wordlist
with open(BIP39_PATH, "r") as f:
    bip39_words = set(word.strip() for word in f.readlines())

def extract_info(decoded_text):
    instruction_key = re.findall(r"ksmhse:[a-z]+", decoded_text)
    words = re.findall(r"\b[a-z]{3,}\b", decoded_text.lower())
    bip39_matches = sorted(set(w for w in words if w in bip39_words))
    numbers = re.findall(r"\b\d{2,}\b", decoded_text)
    base64ish = re.findall(r"[A-Za-z0-9+/=]{10,}", decoded_text)
    return instruction_key, bip39_matches, numbers, base64ish, decoded_text[:1000]

# Try each encoding and print results
for enc in encodings:
    try:
        print(f"\n=== Decoding with: {enc} ===")
        decoded = binary_data.decode(enc, errors="ignore")
        key, bip39s, nums, b64s, preview = extract_info(decoded)

        print(f"[🔑] Instruction Key(s): {key}")
        print(f"[🧠] BIP39 Matches ({len(bip39s)}): {bip39s}")
        print(f"[🔢] Numbers: {nums[:5]}")
        print(f"[🔐] Base64-like: {b64s[:5]}")
        print(f"[📄] Preview:\n{preview}\n")

    except Exception as e:
        print(f"[!] Failed on {enc}: {e}")
