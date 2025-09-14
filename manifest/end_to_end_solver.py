#!/usr/bin/env python3
# GSMG.IO 5 BTC Puzzle - All-in-One Solver

import argparse
import base64
import itertools
import csv
import re
from typing import List
from Crypto.Cipher import AES
from Crypto.Hash import MD5
from bip_utils import Bip39MnemonicValidator, Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes, Bip39Languages

# ==============================================================================
# === CONFIGURATION & KNOWN DATA
# ==============================================================================

TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
LOG_FILE = "solver_log.csv"

# --- Injected AES Data ---
# Correct SHA256 hash of the final password
AES_PASSWORD_HEX = "a713554385283a3349635b3a32857161e3198845c4793f7521af72a15f026a27"
# Correct and complete Base64 blob for "salphaseion_full.txt"
AES_BLOB_B64 = (
    "U2FsdGVkX18tP2/gbclQ5tNZuD4shoV3axuUd8J8aycGCAMoYfhZK0JecHTDpTFe"
    "dGJh4SJIP66qRtXvo7PTpvsIjwO8prLiC/sNHthxiGMuqIrKoO224rOisFJZgARi"
    "c7PaJPne4nab8XCFuV3NbfxGX2BUjNkef5hg7nsoadZx08dNyU2b6eiciWiUvu7D"
    "SATSFO7IFBiAMz7dDqIETKuGlTAP4EmMQUZrQNtfbJsURATW6V5VSbtZB5RFk0O+"
    "IymhstzrQHsU0Bugjv2nndmOEhCxGi/lqK2rLNdOOLutYGnA6RDDbFJUattggELh"
    "2SZx+SBpCdbSGjxOap27l9FOyl02r0HU6UxFdcsbfZ1utTqVEyNs91emQxtpgt+6"
    "BPZisil74Jv4EmrpRDC3ufnkmWwR8NfqVPIKhUiGDu5QflYjczT6DrA9vLQZu3ko"
    "k+/ZurtRYnqqsj49UhwEF9GfUfl7uQYm0UunatW43C3Z1tyFRGAzAHQUFS6jRCd+"
    "vZGyoTlOsThjXDDCSAwoX2M+yM+oaEQoVvDwVkIqRhfDNuBmEfi+HpXuJLPBS1Pb"
    "UjrgoG/Uv7o8IeyST4HBv8+5KLx7IKQS8f1kPZ2YUME+8XJx0caFYs+JS2Jdm0oj"
    "Jm3JJEcYXdKEzOQvRzi4k+6dNlJ05TRZNTJvn0fPG5cM80aQb/ckUHsLsw9a4Wzh"
    "HsrzBQRTIhog9sTm+k+LkXzIJiFfSzRgf250pbviFGoQaIFl1CTQPT2w29DLP900"
    "6bSiliywwnxXOor03Hn+7MJL27YxeaGQn0sFGgP5X0X4jm3vEBkWvtF4PZl0bXWZ"
    "LvVL/zTn87+2Zi/u7LA6y6b2yt7YVMkpheeOL0japXaiAf3bSPeUPGz/eu8ZX/Nn"
    "O3259hG1XwoEVcGdDBV0Nh0A4/phPCR0x5BG04U0OeWAT/5Udc/gGM0TT2FrEzs/"
    "AJKtmsnj31OSsqWb9wD+CoduYY2JrkzJYihE3ZcgcvqqffZXqxQkaI/83ro6JZ4P"
    "ubml0PUnAnkdmnBCpbClbZMzmo3ELZ0EQwsvkJFDMQmiRhda4nBooUW7zXOIb7Wx"
    "bE9THrt3cdZP5uAgVfgguUNE4fZMN8ATEDhdSsLklJe2GvihKuZVA6uuSkWAsK6u"
    "MGo76xpPwYs3eUdLjtANS83a6/F/fhkX1GXs7zbQjh+Inzk8jhEdEogl9jPs/oDj"
    "KjbkUpFlsCWwAZGoeKlmX7c4OGuD5c+FEH+2nYHvYl8y1E/K5SDt9Uocio8XuxbD"
    "ZOzhw7LMSGkD1MZxpDzsCZY1emkSNd88NFj+9U8VssIDDVMYwKMsHKfjc0x5OlzQ"
    "1f6ST0xCkwydDHHGRKKxFC4y6H6fV9sgf9OPK/65z94Rx72+mfvTyizShjxYSRpl"
    "sH9otU4parl8roD0KsVTfXZoYrYXzK6cXBn1BO/OEqWlu++Dd9MiGaUGKd22fXER"
    "qNWoRAKlNn2b6EehD2D8WaAoliPURjkB0Lb/FpP9unI93Twg6NxBXAj734nctukR"
    "b3kE08RydJV70eJsvEftF5hbED4HacGx9pzisaSz6t9AKiuSoF6uoCtlTIYatyfZ"
    "kQA4wg50hAJqTynOQ09ArRHEchtB/7uvWZSBGJ7+zlzRGKx99P3oDZD+Y5D8bmUs"
    "3PV6FnAp+IRSlnsQ6hChkwBoQUcngcfGSkBRvmGjsGercCetRRwBOfh9fbX2ruw4"
    "mzRYrGnz9eBtepkJXDRjD6yvhNfQMCSkm6l9zMWxKvFbv5g2ae2SLrEt/x3MP2/G"
)

# --- Known Puzzle Artifacts ---
GRID = [
    'KBKWBWKKKBWKYK', 'WKBKWKKWBKKWKW', 'KWKWKWKKKWKWKK', 'BKWBKWKWKYKWK',
    'KWKKKWYYWKKWKW', 'WKBKWKWWWKWKKB', 'KWKWBWKBWKWKK',  'KKKKKWKWYKWKW',
    'WKWKYKYWKKKBWK', 'KBKWKWKWWKKWKY', 'WKWKBKKWKWKWKK', 'KWKWKWKYWKBKWK',
    'WKYKWKWKKWKBKW', 'KKBKWKWYKWKWK'
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
    (9,9),(9,10),(8,10),(7,10),(6,10),(5,10),(4,10),(3,10),(2,10),(2,9),(2,8),(2,7),(2,6),(2,5),(2,4),
    (2,3),(2,2),(3,2),(4,2),(5,2),(6,2),(7,2),(8,2),(9,2),(10,2),(10,3),(10,4),(10,5),(10,6),(10,7),
    (10,8),(10,9),(10,10),(10,11),(9,11),(8,11),(7,11),(6,11),(5,11),(4,11),(3,11),(2,11),(1,11),
    (1,10),(1,9),(1,8),(1,7),(1,6),(1,5),(1,4),(1,3),(1,2),(1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(7,1),
    (8,1),(9,1),(10,1),(11,1),(11,2),(11,3),(11,4),(11,5),(11,6),(11,7),(11,8),(11,9),(11,10),
    (11,11),(11,12),(10,12),(9,12),(8,12),(7,12),(6,12),(5,12),(4,12),(3,12),(2,12),(1,12),(0,12),
    (0,11),(0,10),(0,9),(0,8),(0,7),(0,6),(0,5),(0,4),(0,3),(0,2),(0,1),(0,0),(1,0),(2,0),(3,0),(4,0),
    (5,0),(6,0),(7,0),(8,0),(9,0),(10,0),(11,0),(12,0),(12,1),(12,2),(12,3),(12,4),(12,5),(12,6),
    (12,7),(12,8),(12,9),(12,10),(12,11),(12,12),(12,13),(11,13),(10,13),(9,13),(8,13),(7,13),
    (6,13),(5,13),(4,13),(3,13),(2,13),(1,13),(0,13)
]

# ==============================================================================
# === HELPER FUNCTIONS
# ==============================================================================

def evp_bytes_to_key(password: bytes, key_len: int, iv_len: int) -> tuple[bytes, bytes]:
    """Implements OpenSSL's EVP_BytesToKey logic to derive an AES key and IV."""
    key_iv = b""
    prev_hash = b""
    while len(key_iv) < key_len + iv_len:
        prev_hash = MD5.new(prev_hash + password).digest()
        key_iv += prev_hash
    return key_iv[:key_len], key_iv[key_len:key_len + iv_len]

def printable_sequences(binary_data: bytes, min_len: int = 4) -> List[bytes]:
    """Extracts printable ASCII sequences from binary data."""
    return re.findall(b'[\x20-\x7e]{%d,}' % min_len, binary_data)

def derive_btc_address(mnemonic: str, log_writer):
    """Validates a mnemonic, derives the address, and logs the attempt."""
    validator = Bip39MnemonicValidator(Bip39Languages.ENGLISH)
    if not validator.Validate(mnemonic):
        return None
        
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
    bip44_acc = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN).Purpose().Coin().Account(0)
    address = bip44_acc.Change(Bip44Changes.CHAIN_EXT).AddressIndex(0).PublicKey().ToAddress()
    
    is_match = (address == TARGET_ADDRESS)
    log_writer.writerow({'mnemonic': mnemonic, 'derived_address': address, 'is_match': is_match})
    
    return address

def get_spiral_mnemonic():
    """Generates the base mnemonic from the spiral grid path."""
    yellow_words, blue_words = [], []
    for r, c in SPIRAL_PATH:
        if (r, c) in COORD_TO_WORD:
            word = COORD_TO_WORD.get((r, c))
            if GRID[r][c] == 'Y' and word not in yellow_words:
                yellow_words.append(word)
            elif GRID[r][c] == 'B' and word not in blue_words:
                blue_words.append(word)
    
    if len(yellow_words) != 9 or len(blue_words) != 9:
        raise ValueError(f"Error: Found {len(yellow_words)} yellow and {len(blue_words)} blue words. Expected 9 each.")
        
    return yellow_words + blue_words

def apply_instruction(from_key: str, to_key: str, base_words: List[str]) -> List[str]:
    """Applies a from-to mapping to a list of words."""
    if len(from_key) != len(to_key):
        raise ValueError("From and To keys must have the same length.")

    def letters_to_indices(s):
        return [(ord(c.lower()) - ord('a')) % 18 for c in s if c.isalpha()]

    from_idx = letters_to_indices(from_key)
    to_idx = letters_to_indices(to_key)
    
    print(f"\nApplying instruction: {from_key} -> {to_key}")
    print(f"FROM indices: {from_idx}")
    print(f"TO indices:   {to_idx}")

    new_order = [None] * 18
    used_from_indices = set()
    
    # Place specified words
    for f, t in zip(from_idx, to_idx):
        if new_order[t] is None:
            new_order[t] = base_words[f]
            used_from_indices.add(f)

    # Fill remaining slots
    remaining_words = [word for i, word in enumerate(base_words) if i not in used_from_indices]
    for i in range(18):
        if new_order[i] is None:
            new_order[i] = remaining_words.pop(0)
            
    return new_order

# ==============================================================================
# === MAIN SOLVER
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="GSMG.IO 5 BTC Puzzle All-in-One Solver")
    parser.add_argument("--from_key", type=str, help="The 'from' string for the instruction key (e.g., 'ksmhse').")
    parser.add_argument("--to_key", type=str, help="The 'to' string for the instruction key (e.g., 'rfdfuesa').")
    args = parser.parse_args()

    # --- 1. On-the-fly Decryption ---
    print("--- Phase 3: Decrypting Injected AES Blob ---")
    key, iv = evp_bytes_to_key(bytes.fromhex(AES_PASSWORD_HEX), 32, 16)
    # The b64decode function expects a single string without newlines
    ciphertext = base64.b64decode(AES_BLOB_B64.replace("\n", ""))
    plain = AES.new(key, AES.MODE_CBC, iv).decrypt(ciphertext)
    print("[🗝️] Raw plaintext sequences found:", printable_sequences(plain))
    print("✅ Decryption complete.\n")

    # --- 2. Get Base Mnemonic ---
    base_mnemonic_list = get_spiral_mnemonic()
    print("--- Base Mnemonic Generation ---")
    print("Base mnemonic from spiral grid path:")
    print(f"-> {' '.join(base_mnemonic_list)}\n")

    # --- 3. Open Log File ---
    with open(LOG_FILE, 'w', newline='') as csvfile:
        fieldnames = ['mnemonic', 'derived_address', 'is_match']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # --- 4. Run Solver Logic ---
        if args.from_key and args.to_key:
            # --- Instruction Key Mode ---
            try:
                final_words = apply_instruction(args.from_key, args.to_key, base_mnemonic_list)
                mnemonic_str = " ".join(final_words)
                address = derive_btc_address(mnemonic_str, writer)
                
                print(f"\nFinal mnemonic:\n-> {mnemonic_str}")
                if address:
                    print(f"Derived Address: {address}")
                    if address == TARGET_ADDRESS:
                        print("\n🎉 SUCCESS! The derived address matches the target!")
                    else:
                        print("\n❌ Address does not match target.")
                else:
                    print("\n❌ Final mnemonic has an invalid checksum.")

            except ValueError as e:
                print(f"Error: {e}")

        else:
            # --- Brute-Force Fallback Mode ---
            print("--- Brute-Force Mode ---")
            print("No instruction key provided. Testing permutations...")
            
            # Note: 18! is too large. This is a placeholder for a more intelligent brute-force.
            # A true brute-force would need significant pruning (e.g., locking words).
            # For this example, we will test a few simple variations.
            
            print("\nTesting simple variations (original, reversed)...")
            
            # Test original spiral
            addr = derive_btc_address(' '.join(base_mnemonic_list), writer)
            if addr == TARGET_ADDRESS:
                print(f"🎉 SUCCESS! Original spiral order is correct: {addr}")
                return

            # Test reversed spiral
            rev_mnemonic = list(reversed(base_mnemonic_list))
            addr = derive_btc_address(' '.join(rev_mnemonic), writer)
            if addr == TARGET_ADDRESS:
                print(f"🎉 SUCCESS! Reversed spiral order is correct: {addr}")
                return

            print("\nSimple variations did not match. A more advanced permutation strategy is needed.")

    print(f"\n✅ All operations complete. Log saved to '{LOG_FILE}'.")

if __name__ == "__main__":
    main()
