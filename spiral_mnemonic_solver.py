# spiral_mnemonic_solver.py

import os
from PIL import Image
import numpy as np
from mnemonic import Mnemonic
from bip32utils import BIP32Key

# --- CONFIG ---
TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
COLOR_BLUE = (63, 63, 255)   # RGB blue
COLOR_YELLOW = (255, 255, 0) # RGB yellow
GRID_SIZE = 14
USE_COLOR = 'blue'  # 'blue' or 'yellow'

mnemo = Mnemonic("english")

# --- INPUTS ---
WORDS = [
    "frost", "argue", "mountain", "chest", "guilt", "memory",
    "bright", "juice", "initial", "because", "lumber", "grant",
    "foam", "charge", "either", "forward", "capital", "miracle"
]

PAIRS = [
    "kr", "4E", "68", "n1", "ml", "Tj",
    "w4", "fs", "KE", "vf", "8k", "K0",
    "7K", "2K", "Pr", "QU", "8s", "uv"
]

COORDS = [
    (10, 27), (11, 8), (6, 8), (23, 1), (22, 21), (29, 19),
    (32, 4), (15, 28), (20, 18), (31, 15), (8, 20), (20, 0),
    (7, 20), (2, 20), (25, 27), (26, 30), (8, 28), (30, 31)
]

# --- UTILS ---
def spiral_indices(n):
    dx, dy = 1, 0
    x, y = 0, 0
    visited = set()
    order = []
    for _ in range(n * n):
        if 0 <= x < n and 0 <= y < n and (x, y) not in visited:
            order.append((y, x))  # (row, col)
            visited.add((x, y))
        else:
            x -= dx
            y -= dy
            dx, dy = -dy, dx  # rotate direction
        x += dx
        y += dy
    return order

def extract_coords(image_path, color):
    im = Image.open(image_path).convert('RGB')
    pixels = np.array(im)
    targets = []
    for r in range(pixels.shape[0]):
        for c in range(pixels.shape[1]):
            if tuple(pixels[r, c])[:3] == color:
                targets.append((r, c))
    return targets

def derive_address(mnemonic_str):
    seed = mnemo.to_seed(mnemonic_str)
    key = BIP32Key.fromEntropy(seed)
    return key.Address()

def get_final_order():
    # Step 1: Sort by (row, col)
    indexed = list(zip(range(18), PAIRS, COORDS, WORDS))
    sorted_by_coord = sorted(indexed, key=lambda x: (x[2][0], x[2][1]))

    # Step 2: Extract Char column — simulated
    fake_chars = [  # Replace with actual extraction from grid matrix if needed
        'k', 's', 'm', 'h', 's', 'e', ':', 'r', 'f', 'd', 'f', 'u', 'e', 's', 'a', '.', ':', ''
    ]
    print("[DEBUG] Character cipher:", ''.join(fake_chars))

    # Step 3: Base mnemonic from coord sort
    sorted_words = [x[3] for x in sorted_by_coord]

    # Step 4: (Optional) apply deciphered transformation to sorted_words
    # For now, just try it raw
    mnemonic = " ".join(sorted_words)
    if mnemo.check(mnemonic):
        addr = derive_address(mnemonic)
        print("[Mnemonic Valid]", mnemonic)
        print("[Address]", addr)
        if addr == TARGET_ADDRESS:
            print("✅ MATCH! Final mnemonic found.")
        else:
            print("❌ Valid mnemonic but wrong address.")
    else:
        print("❌ Invalid mnemonic checksum.")
        print("Mnemonic (coord-sorted):", mnemonic)

if __name__ == '__main__':
    get_final_order()