# GSMG.IO 5 BTC PUZZLE - INSTRUCTIONAL REORDERING SOLVER
# This script implements the theory that "ksmhse:rfdfuesa.:" is a direct
# reordering command for the coordinate-sorted base mnemonic.

import collections
from itertools import permutations

# Define a simple data structure for our points
Point = collections.namedtuple("Point", ["pair", "row", "col", "char", "word"])

def get_bip39_words():
    """
    Returns the 18 BIP39 words extracted from the puzzle.
    """
    return [
        "frost", "argue", "mountain", "chest", "guilt", "memory",
        "bright", "juice", "initial", "because", "lumber", "grant",
        "foam", "charge", "either", "forward", "capital", "miracle"
    ]

def get_puzzle_data():
    """
    Returns the list of all 18 decoded data points from the puzzle.
    """
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
    Example: 'r' -> 17, 'f' -> 5, etc.
    """
    try:
        instruction_part = key_string.split(':')[1]
        # Ensure we only parse the alphabetic part
        alpha_part = "".join(filter(str.isalpha, instruction_part))
        # The spec indicates 8 positions from 'rfdfuesa'
        target_indices = [ord(c) - ord('a') for c in alpha_part]
        # Cap indices at 17 for an 18-word list (0-17)
        return [min(idx, 17) for idx in target_indices]
    except (IndexError, TypeError):
        print("[!] Error: Could not parse the instruction key.")
        return []

def solve_with_instructional_reorder(base_words, target_positions):
    """
    Applies the reordering instruction and attempts to find the final mnemonic.
    """
    if not target_positions or len(target_positions) > len(base_words):
        print("[!] Invalid target positions list.")
        return

    print(f"[*] Applying reordering to the first {len(target_positions)} base words.")

    # Words to be placed at specific positions
    words_to_place = base_words[:len(target_positions)]
    # Words that need to fill the remaining slots
    remaining_words = base_words[len(target_positions):]

    # Create the template for the final mnemonic
    final_template = [None] * 18
    used_indices = set()

    # Place the fixed words into the template, handling duplicates
    for i, word in enumerate(words_to_place):
        pos = target_positions[i]
        # If the target position is already taken, find the next available one
        while pos in used_indices:
            pos = (pos + 1) % 18
        final_template[pos] = word
        used_indices.add(pos)

    print(f"[*] Template after placing fixed words: {final_template}")
    print(f"[*] Remaining words to permute: {remaining_words}")

    # Find the empty slots in the template
    empty_slots = [i for i, val in enumerate(final_template) if val is None]

    # Iterate through all permutations of the remaining words
    # NOTE: 10! is 3,628,800, which is computationally feasible.
    print("[*] Starting permutations for remaining words...")
    count = 0
    for perm in permutations(remaining_words):
        # Create a copy of the template to fill
        current_attempt = final_template[:]
        for i, word in enumerate(perm):
            current_attempt[empty_slots[i]] = word
        
        mnemonic_str = " ".join(current_attempt)
        
        # NOTE: A full BIP39 check requires the wordlist and checksum logic.
        # This is a placeholder for where you would validate the mnemonic.
        # For now, we print potential candidates for external validation.
        # A simple check is to ensure all words are present.
        if len(set(current_attempt)) == 18:
            count += 1
            if count <= 20: # Print first 20 valid permutations as examples
                 print(f"    -> Potential Mnemonic #{count}: {mnemonic_str}")

    print(f"\n[+] Completed. Found {count} potential mnemonics.")
    print("[!] ACTION: Test these mnemonics in a BIP39 tool to derive the address.")


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
