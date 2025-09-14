# GSMG.IO 5 BTC PUZZLE - FINAL AUTOMATED SOLVER
# This script tests the theory that 'ksmhse:rfdfuesa.:' is a "from-to"
# mapping to reorder the base mnemonic. It will test all permutations
# for the remaining words.

import collections
import csv
import os
from itertools import permutations, islice
import multiprocessing
import math
# These libraries are required for the final validation step.
# Install them using: pip install mnemonic bip32utils tqdm
from mnemonic import Mnemonic
from bip32utils import BIP32Key
from tqdm import tqdm

# --- CONFIGURATION ---
TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
CSV_OUTPUT_FILE = "results.csv"
CHUNK_SIZE = 10000

# --- GLOBAL INITIALIZATION ---
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
    Parses 'ksmhse:rfdfuesa.:' into 'from' and 'to' index lists.
    """
    try:
        parts = key_string.strip().split(':')
        if len(parts) >= 2:
            from_part = parts[0]
            to_part = parts[1]
            
            from_alpha = "".join(filter(str.isalpha, from_part))
            to_alpha = "".join(filter(str.isalpha, to_part))

            from_indices = [min(ord(c) - ord('a'), 17) for c in from_alpha]
            to_indices = [min(ord(c) - ord('a'), 17) for c in to_alpha]
            
            return from_indices, to_indices
        else:
            return [], []
    except (ValueError, IndexError, TypeError):
        print("[!] Error parsing instruction key.")
        return [], []

def derive_address_from_mnemonic(mnemonic_str):
    """
    Derives the first legacy BIP44 address from a mnemonic string.
    """
    seed = mnemo.to_seed(mnemonic_str)
    key = BIP32Key.fromEntropy(seed).ChildKey(44 | 0x80000000).ChildKey(0 | 0x80000000).ChildKey(0 | 0x80000000).ChildKey(0).ChildKey(0)
    return key.Address()

def check_permutation_chunk(args):
    """
    Worker function to check a chunk of permutations.
    """
    final_template, empty_slots, perm_chunk, target_address_ref = args
    results = []
    for perm in perm_chunk:
        current_attempt = final_template[:]
        for j, word in enumerate(perm):
            current_attempt[empty_slots[j]] = word
        mnemonic_str = " ".join(current_attempt)
        if mnemo.check(mnemonic_str):
            derived_address = derive_address_from_mnemonic(mnemonic_str)
            is_match = (derived_address == target_address_ref)
            results.append([mnemonic_str, derived_address, is_match])
            if is_match:
                return results
    return results

def solve_with_from_to_mapping(base_words, from_indices, to_indices):
    """
    Applies the "from-to" reordering and finds the final mnemonic via permutation.
    """
    print("\n--- Starting From-To Mapping Permutation Search ---")
    if not from_indices or not to_indices:
        print("[!] Invalid from/to index lists for permutation. Exiting.")
        return None

    words_to_place_map = {idx: base_words[idx] for idx in from_indices}
    words_to_place = list(words_to_place_map.values())
    
    remaining_words = [word for word in base_words if word not in words_to_place]
    
    final_template = [None] * 18
    used_indices = set()

    min_len = min(len(words_to_place), len(to_indices))
    for i in range(min_len):
        word = words_to_place[i]
        pos = to_indices[i]
        while pos in used_indices:
            pos = (pos + 1) % 18
        final_template[pos] = word
        used_indices.add(pos)

    empty_slots = [i for i, val in enumerate(final_template) if val is None]
    
    num_processes = os.cpu_count() or 1
    print(f"[*] Starting automated validation with {num_processes} processes...")
    
    file_exists = os.path.isfile(CSV_OUTPUT_FILE)
    
    total_permutations = math.factorial(len(remaining_words))
    perms_iterator = permutations(remaining_words)
    solution_found = None

    with open(CSV_OUTPUT_FILE, 'a', newline='') as csvfile, \
         multiprocessing.Pool(processes=num_processes) as pool, \
         tqdm(total=total_permutations, desc="Checking Permutations", unit="perm") as pbar:
        
        writer = csv.writer(csvfile)
        if not file_exists or os.path.getsize(CSV_OUTPUT_FILE) == 0:
            writer.writerow(['Mnemonic', 'Derived Address', 'Is Match'])
        
        while not solution_found:
            chunk = list(islice(perms_iterator, CHUNK_SIZE * num_processes))
            if not chunk: break

            process_chunks = [list(islice(iter(chunk), i, len(chunk), num_processes)) for i in range(num_processes)]
            process_args = [(final_template, empty_slots, p_chunk, TARGET_ADDRESS) for p_chunk in process_chunks if p_chunk]

            for results in pool.imap_unordered(check_permutation_chunk, process_args):
                for row in results:
                    writer.writerow(row)
                    if row[2]:
                        solution_found = row[0]
                        break
                if solution_found: break
            
            pbar.update(len(chunk))
    
    return solution_found

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

    from_indices, to_indices = parse_instruction_key(instruction_key)
    print(f"[*] Parsed 'From' Indices: {from_indices}")
    print(f"[*] Parsed 'To' Indices:   {to_indices}\n")

    solution = solve_with_from_to_mapping(base_mnemonic_words, from_indices, to_indices)

    if solution:
        print("\n" + "="*50)
        print("  ✅✅✅  MATCH FOUND! PUZZLE SOLVED!  ✅✅✅")
        print(f"  Final Mnemonic: {solution}")
        print(f"  Results have been saved to {CSV_OUTPUT_FILE}")
        print("="*50 + "\n")
    else:
        print(f"\n[x] Completed all permutations. No match found. See {CSV_OUTPUT_FILE} for all valid candidates.")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
