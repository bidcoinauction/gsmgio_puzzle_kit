#!/usr/bin/env python3
# GSMG.IO 5 BTC Puzzle - All-in-One Solver

import argparse
import csv
from typing import List
from bip_utils import Bip39MnemonicValidator, Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes, Bip39Languages

# ==============================================================================
# === CONFIGURATION & KNOWN DATA
# ==============================================================================

TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
LOG_FILE = "solver_log.csv"

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

# ==============================================================================
# === HELPER FUNCTIONS
# ==============================================================================

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

def spiral_coords(start_x, start_y, size=14, reverse=False):
    """Generates a spiral path from a starting point."""
    x, y = start_x, start_y
    # Directions for a counter-clockwise inward spiral
    dx, dy = [0, -1, 0, 1], [1, 0, -1, 0] 
    direction = 0
    steps = 1
    coords = [(x, y)]
    
    while len(coords) < size * size:
        for _ in range(2):
            for _ in range(steps):
                x += dx[direction]
                y += dy[direction]
                if 0 <= x < size and 0 <= y < size:
                    coords.append((x, y))
            direction = (direction + 1) % 4
        steps += 1
    
    # The puzzle solution uses a reversed version of a specific spiral
    return coords[::-1] if reverse else coords

def get_spiral_mnemonic():
    """Generates the base mnemonic from the spiral grid path."""
    # The known-correct path starts at (6,7) and is reversed
    path = spiral_coords(start_x=6, start_y=7, size=14, reverse=True)

    yellow_words, blue_words = [], []
    for r, c in path:
        if (r, c) in COORD_TO_WORD:
            word = COORD_TO_WORD.get((r, c))
            if GRID[r][c] == 'Y' and word not in yellow_words:
                yellow_words.append(word)
            elif GRID[r][c] == 'B' and word not in blue_words:
                blue_words.append(word)
    
    if len(yellow_words) != 9 or len(blue_words) != 9:
        raise ValueError(f"Error: Found {len(yellow_words)} yellow and {len(blue_words)} blue words. Expected 9 each.")
        
    # The base mnemonic is the yellow path followed by the blue path
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

    # --- 1. Get Base Mnemonic ---
    base_mnemonic_list = get_spiral_mnemonic()
    print("--- Base Mnemonic Generation ---")
    print("Base mnemonic from spiral grid path:")
    print(f"-> {' '.join(base_mnemonic_list)}\n")

    # --- 2. Open Log File ---
    with open(LOG_FILE, 'w', newline='') as csvfile:
        fieldnames = ['mnemonic', 'derived_address', 'is_match']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # --- 3. Run Solver Logic ---
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
            print("No instruction key provided. Testing simple permutations...")
            
            # Test original spiral
            addr = derive_btc_address(' '.join(base_mnemonic_list), writer)
            print(f"\nTesting original spiral order...")
            print(f"Derived Address: {addr or 'Invalid Checksum'}")
            if addr == TARGET_ADDRESS:
                print(f"🎉 SUCCESS! Original spiral order is correct.")
                return

            # Test reversed spiral
            rev_mnemonic = list(reversed(base_mnemonic_list))
            addr = derive_btc_address(' '.join(rev_mnemonic), writer)
            print(f"\nTesting reversed spiral order...")
            print(f"Derived Address: {addr or 'Invalid Checksum'}")
            if addr == TARGET_ADDRESS:
                print(f"🎉 SUCCESS! Reversed spiral order is correct.")
                return

            print("\nSimple variations did not match. Use --from_key and --to_key to test instructions.")

    print(f"\n✅ All operations complete. Log saved to '{LOG_FILE}'.")

if __name__ == "__main__":
    main()
