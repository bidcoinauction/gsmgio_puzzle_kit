# GSMG.IO 5 BTC PUZZLE - FINAL AUTOMATED SOLVER
# This script applies the instructional reordering and automatically validates
# each generated mnemonic against the target BTC address, logging results to a CSV.

import collections
import csv
from itertools import permutations
# These libraries are required for the final validation step.
# Install them using: pip install mnemonic bip32utils
from mnemonic import Mnemonic
from bip32utils import BIP32Key

# --- CONFIGURATION ---
TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
CSV_OUTPUT_FILE = "results.csv"
mnemo = Mnemonic("english")

def get_puzzle_data():
    """
    Returns the list of all 18 decoded data points from the puzzle.
    """
    Point = collections.namedtuple("Point", ["pair", "row", "col", "char", "word"])
    return [
        Point(pair='kr', row=10, col=27, char='e', word='frost'),
        Point(pair='4E', row=11, col=8, char=':', word='argue'),
        Point(pair='68', row=6, col=8, char='s', word='mountain'),
        Point(pair='n1', row=23, col=1, char='u', word='chest'),
        Point(pair='ml', row=22, col=21, char='f', word='guilt'),
        Point(pair='Tj', row=29, col=19, char='a', word='memory'),
        Point(pair='w4', row=32, col=4, char=' ', word='bright'),
        Point(pair='fs', row=15, col=28, char='r', word='juice'),
        Point(pair='KE', row=20, col=18, char='d', word='initial'),
        Point(pair='vf', row=31, col=15, char=':', word='because'),
        Point(pair='8k', row=8, col=20, char='h', word='lumber'),
        Point(pair='K0', row=20, col=0, char='f', word='grant'),
        Point(pair='7K', row=7, col=20, char='m', word='foam'),
        Point(pair='2K', row=2, col=20, char='k', word='charge'),
        Point(pair='Pr', row=25, col=27, char='e', word='either'),
        Point(pair='QU', row=26, col=30, char='s', word='forward'),
        Point(pair='8s', row=8, col=28, char='s', word='capital'),
        Point(pair='uv', row=30, col=31, char='.', word='miracle')
    ]

def parse_instruction_key(key_string):
    """
    Parses the instruction key 'rfdfuesa' into a list of target indices.
    """
    try:
        instruction_part = key_string.split(':')[1]
        alpha_part = "".join(filter(str.isalpha, instruction_part))
        target_indices = [ord(c) - ord('a') for c in alpha_part]
        return [min(idx, 17) for idx in target_indices]
    except (IndexError, TypeError):
        return []

def derive_address_from_mnemonic(mnemonic_str):
    """
    Derives the first legacy BIP44 address from a mnemonic string.
    """
    seed = mnemo.to_seed(mnemonic_str)
    # Derivation path for the first legacy address
    key = BIP32Key.fromEntropy(seed).ChildKey(44 | 0x80000000).ChildKey(0 | 0x80000000).ChildKey(0 | 0x80000000).ChildKey(0).ChildKey(0)
    return key.Address()

def solve_with_instructional_reorder(base_words, target_positions):
    """
    Applies the reordering instruction and automatically finds the final mnemonic.
    """
    if not target_positions or len(target_positions) > len(base_words):
        print("[!] Invalid target positions list.")
        return

    words_to_place = base_words[:len(target_positions)]
    remaining_words = base_words[len(target_positions):]
    
    final_template = [None] * 18
    used_indices = set()

    for i, word in enumerate(words_to_place):
        pos = target_positions[i]
        while pos in used_indices:
            pos = (pos + 1) % 18
        final_template[pos] = word
        used_indices.add(pos)

    empty_slots = [i for i, val in enumerate(final_template) if val is None]

    print(f"[*] Starting automated validation... Logging valid mnemonics to {CSV_OUTPUT_FILE}")
    
    with open(CSV_OUTPUT_FILE, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Mnemonic', 'Derived Address', 'Is Match'])

        for i, perm in enumerate(permutations(remaining_words)):
            current_attempt = final_template[:]
            for j, word in enumerate(perm):
                current_attempt[empty_slots[j]] = word
            
            mnemonic_str = " ".join(current_attempt)
            
            # Fast checksum validation first
            if mnemo.check(mnemonic_str):
                # If checksum is valid, derive the address
                derived_address = derive_address_from_mnemonic(mnemonic_str)
                is_match = (derived_address == TARGET_ADDRESS)
                
                # Log to CSV
                writer.writerow([mnemonic_str, derived_address, is_match])
                
                if is_match:
                    print("\n" + "="*50)
                    print("  ✅✅✅  MATCH FOUND! PUZZLE SOLVED!  ✅✅✅")
                    print(f"  Final Mnemonic: {mnemonic_str}")
                    print(f"  Results have been saved to {CSV_OUTPUT_FILE}")
                    print("="*50 + "\n")
                    return mnemonic_str
            
            if (i + 1) % 100000 == 0:
                print(f"    ...checked {i + 1} permutations...")

    print(f"\n[x] Completed all permutations. No match found. See {CSV_OUTPUT_FILE} for all valid candidates.")
    return None

def main():
    """
    Main function to run the solver logic.
    """
    print("[*] Stage 1: Sorting puzzle data by grid coordinates...")
    all_points = get_puzzle_data()
    sorted_points = sorted(all_points, key=lambda p: (p.row, p.col))
    base_mnemonic_words = [p.word for p in sorted_points]
    instruction_key = "".join([p.char for p in sorted_points])
    
    print(f"[*] Base Mnemonic (pre-instruction): \n    {' '.join(base_mnemonic_words)}\n")
    print(f"[*] Instruction Key: '{instruction_key}'")

    target_indices = parse_instruction_key(instruction_key)
    print(f"[*] Parsed Target Indices: {target_indices}\n")

    solve_with_instructional_reorder(base_mnemonic_words, target_indices)

if __name__ == "__main__":
    main()
