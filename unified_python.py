# pip install bip_utils
from bip_utils import (
    Bip39MnemonicGenerator, Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes,
    Bip39WordsNum
)

# --- 1. CONFIRMED ARTIFACTS AND DATA ---

# The target prize address
TARGET_BTC_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"

# Transcribed 14x14 grid from puzzle.png
# K=Black, W=White, Y=Yellow, B=Blue
GRID = [
    "KBKWBWKKKBWKYK", "WKBKWKKWBKKWKW", "KWKWKWKKKWKWKK", "BKWBKWKWKYKWK",
    "KWKKKWYYWKKWKW", "WKBKWKWWWKWKKB", "KWKWBWKBWKWKK", "KKKKKWKWYKWKW",
    "WKWKYKYWKKKBWK", "KBKWKWKWWKKWKY", "WKWKBKKWKWKWKK", "KWKWKWKYWKBKWK",
    "WKYKWKWKKWKBKW", "KKBKWKWYKWKWK"
]

# The 18 words and their mapping to a color and specific (row, col)
# coordinate on the 14x14 grid.
WORD_DATA = [
    {'word': 'grant',   'color': 'Y', 'grid_coord': (4, 6)},
    {'word': 'capital', 'color': 'Y', 'grid_coord': (4, 7)},
    {'word': 'bright',  'color': 'Y', 'grid_coord': (8, 6)},
    {'word': 'forward', 'color': 'Y', 'grid_coord': (8, 4)},
    {'word': 'miracle', 'color': 'Y', 'grid_coord': (7, 9)},
    {'word': 'because', 'color': 'Y', 'grid_coord': (11, 7)},
    {'word': 'memory',  'color': 'Y', 'grid_coord': (12, 2)},
    {'word': 'initial', 'color': 'Y', 'grid_coord': (13, 8)},
    {'word': 'guilt',   'color': 'Y', 'grid_coord': (9, 13)},
    {'word': 'foam',    'color': 'B', 'grid_coord': (6, 8)},
    {'word': 'charge',  'color': 'B', 'grid_coord': (6, 5)},
    {'word': 'lumber',  'color': 'B', 'grid_coord': (5, 2)},
    {'word': 'mountain','color': 'B', 'grid_coord': (8, 10)},
    {'word': 'chest',   'color': 'B', 'grid_coord': (9, 1)},
    {'word': 'argue',   'color': 'B', 'grid_coord': (10, 4)},
    {'word': 'either',  'color': 'B', 'grid_coord': (11, 10)},
    {'word': 'juice',   'color': 'B', 'grid_coord': (12, 11)},
    {'word': 'frost',   'color': 'B', 'grid_coord': (13, 3)},
]

# Create a lookup for grid coordinates to words for easy mapping
coord_to_word_map = {data['grid_coord']: data['word'] for data in WORD_DATA}

# --- 2. ALGORITHM IMPLEMENTATION ---

def generate_spiral_path(n):
    """
    Generates a robust counter-clockwise spiral path for an n x n grid,
    guaranteed to stay within bounds.
    """
    path = []
    # Create a grid to mark visited cells, preventing errors
    visited = [[False] * n for _ in range(n)]
    # Start at top-left of the central 2x2 for an even grid
    r, c = n // 2 - 1, n // 2 - 1
    # Directions for counter-clockwise: Right, Up, Left, Down
    dirs = [(0, 1), (-1, 0), (0, -1), (1, 0)]
    dir_idx = 0

    for _ in range(n * n):
        path.append((r, c))
        visited[r][c] = True
        
        # Calculate the next position based on the current direction
        next_r, next_c = r + dirs[dir_idx][0], c + dirs[dir_idx][1]

        # If next position is out of bounds or already visited, turn left
        if not (0 <= next_r < n and 0 <= next_c < n and not visited[next_r][next_c]):
            dir_idx = (dir_idx + 3) % 4 # Turn left (counter-clockwise)
            next_r, next_c = r + dirs[dir_idx][0], c + dirs[dir_idx][1]
        
        r, c = next_r, next_c
        
    return path

def derive_btc_address_from_mnemonic(mnemonic_str):
    """Derives a BIP44 BTC address from a mnemonic phrase."""
    seed_bytes = Bip39SeedGenerator(mnemonic_str).Generate()
    bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)
    bip44_acc_ctx = bip44_mst_ctx.Purpose().Coin().Account(0)
    bip44_chg_ctx = bip44_acc_ctx.Change(Bip44Changes.CHAIN_EXT)
    bip44_addr_ctx = bip44_chg_ctx.AddressIndex(0)
    return bip44_addr_ctx.PublicKey().ToAddress()

# --- 3. EXECUTION AND VERIFICATION ---

print("🚀 Starting GSMG.IO 5 BTC Puzzle Verification Script...")

# Generate the full spiral path for the 14x14 grid
full_path = generate_spiral_path(14)
print(f"✅ Generated spiral path with {len(full_path)} coordinates.")

# Find the yellow and blue paths in spiral order
yellow_path_coords = []
blue_path_coords = []
for row, col in full_path:
    color = GRID[row][col]
    if color == 'Y':
        yellow_path_coords.append((row, col))
    elif color == 'B':
        blue_path_coords.append((row, col))

print(f"🟨 Found {len(yellow_path_coords)} yellow squares in spiral order.")
print(f"🟦 Found {len(blue_path_coords)} blue squares in spiral order.")

# Map coordinates to words to get the ordered word lists
yellow_words = [coord_to_word_map[coord] for coord in yellow_path_coords]
blue_words = [coord_to_word_map[coord] for coord in blue_path_coords]

# Assemble the final mnemonic: Yellow path followed by Blue path
final_mnemonic_list = yellow_words + blue_words
final_mnemonic_str = " ".join(final_mnemonic_list)

print("\nAssembling final mnemonic based on 'Yellow then Blue' rule...")
print("Final 18-word mnemonic phrase:")
print(f"-> {final_mnemonic_str}")

# Derive the BTC address from the final mnemonic
derived_address = derive_btc_address_from_mnemonic(final_mnemonic_str)
print(f"\n🔑 Derived BTC Address: {derived_address}")
print(f"🎯 Target BTC Address:  {TARGET_BTC_ADDRESS}")

# Final verification
if derived_address == TARGET_BTC_ADDRESS:
    print("\n✅ SUCCESS: Derived address matches the target address!")
    print("This mnemonic unlocks the 5 BTC prize. Mission accomplished. 🎉")
else:
    print("\n❌ FAILURE: Derived address does not match.")