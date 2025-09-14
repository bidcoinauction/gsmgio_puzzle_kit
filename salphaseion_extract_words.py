import struct
from typing import List

BIP39_WORDLIST_PATH = "bip39_english.txt"
BINARY_PATH = "salphaseion_decrypted.bin"

def load_bip39_words(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [w.strip() for w in f.readlines()]

def extract_ascii_candidates(binary: bytes, min_length: int = 4) -> List[str]:
    results = []
    current = b""
    for byte in binary:
        if 32 <= byte <= 126:
            current += bytes([byte])
        else:
            if len(current) >= min_length:
                results.append(current.decode("utf-8", errors="ignore"))
            current = b""
    if len(current) >= min_length:
        results.append(current.decode("utf-8", errors="ignore"))
    return results

def match_bip39_words(candidates: List[str], wordlist: List[str]) -> List[str]:
    return [word for word in candidates if word in wordlist]

def main():
    print("[+] Loading files...")
    with open(BINARY_PATH, "rb") as f:
        binary_data = f.read()

    bip39_words = load_bip39_words(BIP39_WORDLIST_PATH)

    print("[+] Extracting ASCII strings...")
    ascii_candidates = extract_ascii_candidates(binary_data)

    print(f"[+] Found {len(ascii_candidates)} ASCII strings.")
    for s in ascii_candidates:
        print("   ", s)

    print("[+] Matching BIP39 words...")
    bip39_matches = match_bip39_words(ascii_candidates, bip39_words)

    print(f"[+] Found {len(bip39_matches)} valid BIP39 words:")
    for word in bip39_matches:
        print(" -", word)

if __name__ == "__main__":
    main()
