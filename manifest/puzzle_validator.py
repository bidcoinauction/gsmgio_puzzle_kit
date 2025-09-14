# GSMG.IO 5 BTC PUZZLE - DEFINITIVE GRID TRAVERSAL SOLVER
# This script solves the final word order by correctly traversing the puzzle grid,
# using the confirmed 9 blue and 9 yellow square locations.
# It now tests four different ways of combining the two color paths.

import csv
from mnemonic import Mnemonic
from bip32utils import BIP32Key

# --- CONFIGURATION ---
TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
CSV_OUTPUT_FILE = "final_solution_candidates.csv"
mnemo = Mnemonic("english")

# --- INPUT DATA ---
# This dictionary maps each word to its color based on the debug output.
WORD_TO_COLOR_MAP = {
    'grant': 'Y', 'capital': 'Y', 'bright': 'Y', 'forward': 'Y',
    'miracle': 'Y', 'because': 'Y', 'memory': 'Y', 'initial': 'Y',
    'guilt': 'Y', 'foam': 'B', 'charge': 'B', 'lumber': 'B',
    'mountain': 'B', 'chest': 'B', 'argue': 'B', 'either': 'B',
    'juice': 'B', 'frost': 'B'
}

# This dictionary maps each word to its coordinate pair from the puzzle artifacts.
# This is used to build the correct grid.
WORD_TO_COORD_MAP = {
    'grant': (4, 6), 'capital': (4, 7), 'bright': (8, 6), 'forward': (8, 4),
    'miracle': (7, 9), 'because': (11, 7), 'memory': (12, 2), 'initial': (13, 8),
    'guilt': (9, 13), 'foam': (6, 8), 'charge': (6, 5), 'lumber': (5, 2),
    'mountain': (8, 10), 'chest': (9, 1), 'argue': (10, 4), 'either': (11, 10),
    'juice': (12, 11), 'frost': (13, 3)
}

def get_color_grid():
    """
    Returns the correctly transcribed 14x14 color grid based on the 9 blue
    and 9 yellow square locations derived from the user's debug log.
    0=Other, 2=Yellow, 3=Blue
    """
    grid = [[0 for _ in range(14)] for _ in range(14)]
    for word, coord in WORD_TO_COORD_MAP.items():
        color_char = WORD_TO_COLOR_MAP.get(word)
        r, c = coord
        if color_char == 'Y':
            grid[r][c] = 2 # Yellow
        elif color_char == 'B':
            grid[r][c] = 3 # Blue
    return grid

def derive_address_from_mnemonic(mnemonic_str):
    """
    Derives the first legacy BIP44 address from a mnemonic string.
    Returns None if the mnemonic checksum is invalid.
    """
    if not mnemo.check(mnemonic_str):
        return None
    seed = mnemo.to_seed(mnemonic_str)
    key = BIP32Key.fromEntropy(seed).ChildKey(44 | 0x80000000).ChildKey(0 | 0x80000000).ChildKey(0 | 0x80000000).ChildKey(0).ChildKey(0)
    return key.Address()

def solve_by_grid_traversal():
    """
    Performs a correct counter-clockwise spiral traversal of the grid to find
    the final mnemonic order and validates the results.
    """
    grid = get_color_grid()
    n = len(grid)

    # Create a reverse map from coordinate to word for easy lookup
    coord_to_word_map = {v: k for k, v in WORD_TO_COORD_MAP.items()}

    path_coords = []
    
    print("[*] Starting counter-clockwise spiral traversal of the grid...")
    
    top, bottom, left, right = 0, n - 1, 0, n - 1
    
    while top <= bottom and left <= right:
        # Move Down
        for i in range(top, bottom + 1): path_coords.append((i, left))
        left += 1
        # Move Right
        if top <= bottom:
            for i in range(left, right + 1): path_coords.append((bottom, i))
            bottom -= 1
        # Move Up
        if left <= right:
            for i in range(bottom, top - 1, -1): path_coords.append((i, right))
            right -= 1
        # Move Left
        if top <= bottom:
            for i in range(right, left - 1, -1): path_coords.append((top, i))
            top += 1

    yellow_path_words = []
    blue_path_words = []

    for r, c in path_coords:
        word = coord_to_word_map.get((r, c))
        if word:
            color = WORD_TO_COLOR_MAP.get(word)
            if color == 'Y':
                yellow_path_words.append(word)
            elif color == 'B':
                blue_path_words.append(word)

    if len(blue_path_words) != 9 or len(yellow_path_words) != 9:
        print(f"\n[!] Error: Found {len(yellow_path_words)} yellow and {len(blue_path_words)} blue words. Expected 9 of each.")
        return

    print("\n[+] Found two ordered paths. Testing all combinations...")
    
    final_candidates = []
    
    # --- Theory 1: Yellow Path + Blue Path (Concatenated) ---
    theory1_mnemonic = yellow_path_words + blue_path_words
    theory1_str = " ".join(theory1_mnemonic)
    theory1_addr = derive_address_from_mnemonic(theory1_str)
    final_candidates.append({'path': 'Yellow + Blue', 'mnemonic': theory1_str, 'address': theory1_addr or "INVALID"})

    # --- Theory 2: Blue Path + Yellow Path (Concatenated) ---
    theory2_mnemonic = blue_path_words + yellow_path_words
    theory2_str = " ".join(theory2_mnemonic)
    theory2_addr = derive_address_from_mnemonic(theory2_str)
    final_candidates.append({'path': 'Blue + Yellow', 'mnemonic': theory2_str, 'address': theory2_addr or "INVALID"})

    # --- Theory 3: Yellow-Blue Interleaved (Stitched) ---
    theory3_mnemonic = []
    for i in range(9):
        theory3_mnemonic.append(yellow_path_words[i])
        theory3_mnemonic.append(blue_path_words[i])
    theory3_str = " ".join(theory3_mnemonic)
    theory3_addr = derive_address_from_mnemonic(theory3_str)
    final_candidates.append({'path': 'Yellow-Blue Interleaved', 'mnemonic': theory3_str, 'address': theory3_addr or "INVALID"})

    # --- Theory 4: Blue-Yellow Interleaved (Stitched) ---
    theory4_mnemonic = []
    for i in range(9):
        theory4_mnemonic.append(blue_path_words[i])
        theory4_mnemonic.append(yellow_path_words[i])
    theory4_str = " ".join(theory4_mnemonic)
    theory4_addr = derive_address_from_mnemonic(theory4_str)
    final_candidates.append({'path': 'Blue-Yellow Interleaved', 'mnemonic': theory4_str, 'address': theory4_addr or "INVALID"})

    # --- Print and Export Results ---
    with open(CSV_OUTPUT_FILE, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Path', 'Mnemonic', 'Derived Address', 'Is Match'])

        for candidate in final_candidates:
            is_match = (candidate['address'] == TARGET_ADDRESS)
            print("-" * 50)
            print(f"Testing Path: {candidate['path']}\nMnemonic: {candidate['mnemonic']}")
            print(f"Derived Address: {candidate['address']}")
            if is_match:
                print("✅✅✅ MATCH FOUND! PUZZLE SOLVED! ✅✅✅")
            writer.writerow([candidate['path'], candidate['mnemonic'], candidate['address'], is_match])

    print("-" * 50)
    print(f"\n[+] Results have been saved to {CSV_OUTPUT_FILE}")

if __name__ == "__main__":
    solve_by_grid_traversal()
