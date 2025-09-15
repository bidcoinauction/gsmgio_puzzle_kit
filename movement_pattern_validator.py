#!/usr/bin/env python3
"""
Movement Pattern Validator for GSMG Puzzle
Tests new movement patterns with mnemonic validation.
"""

import math
import hashlib
import csv
from pathlib import Path
from mnemonic import Mnemonic
from bip32utils import BIP32Key

# Configuration
TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
mnemo = Mnemonic("english")

# Puzzle data - 18 words with their coordinates and pairs
PUZZLE_DATA = [
    {'word': 'frost', 'pair': 'kr', 'coord': (10, 27)},
    {'word': 'argue', 'pair': '4E', 'coord': (11, 8)},
    {'word': 'mountain', 'pair': '68', 'coord': (6, 8)},
    {'word': 'chest', 'pair': 'n1', 'coord': (23, 1)},
    {'word': 'guilt', 'pair': 'ml', 'coord': (22, 21)},
    {'word': 'memory', 'pair': 'Tj', 'coord': (29, 19)},
    {'word': 'bright', 'pair': 'w4', 'coord': (32, 4)},
    {'word': 'juice', 'pair': 'fs', 'coord': (15, 28)},
    {'word': 'initial', 'pair': 'KE', 'coord': (20, 18)},
    {'word': 'because', 'pair': 'vf', 'coord': (31, 15)},
    {'word': 'lumber', 'pair': '8k', 'coord': (8, 20)},
    {'word': 'grant', 'pair': 'K0', 'coord': (20, 0)},
    {'word': 'foam', 'pair': '7K', 'coord': (7, 20)},
    {'word': 'charge', 'pair': '2K', 'coord': (2, 20)},
    {'word': 'either', 'pair': 'Pr', 'coord': (25, 27)},
    {'word': 'forward', 'pair': 'QU', 'coord': (26, 30)},
    {'word': 'capital', 'pair': '8s', 'coord': (8, 28)},
    {'word': 'miracle', 'pair': 'uv', 'coord': (30, 31)}
]

def derive_address(mnemonic_str: str) -> str:
    """Derive Bitcoin address from mnemonic."""
    seed = mnemo.to_seed(mnemonic_str)
    key = BIP32Key.fromEntropy(seed).ChildKey(44 | 0x80000000).ChildKey(0 | 0x80000000).ChildKey(0 | 0x80000000).ChildKey(0).ChildKey(0)
    return key.Address()

def validate_mnemonic(words: list, pattern_name: str, csv_writer=None) -> bool:
    """Validate mnemonic and check if it matches target address."""
    mnemonic_str = " ".join(words)
    if mnemo.check(mnemonic_str):
        address = derive_address(mnemonic_str)
        is_match = (address == TARGET_ADDRESS)
        
        print(f"✅ VALID MNEMONIC ({pattern_name}): {mnemonic_str}")
        print(f"   Address: {address}")
        
        if csv_writer:
            csv_writer.writerow([pattern_name, mnemonic_str, address, is_match])
        
        if is_match:
            print(f"🎯 MATCH FOUND! Pattern: {pattern_name}")
            return True
        else:
            print(f"   ❌ Wrong address")
    else:
        print(f"❌ Invalid mnemonic ({pattern_name}): {mnemonic_str}")
        if csv_writer:
            csv_writer.writerow([pattern_name, mnemonic_str, "INVALID", False])
    return False

def hash_based_order(coords: list) -> list:
    """Order coordinates based on hash values."""
    def coord_hash(coord):
        coord_str = f"{coord[0]},{coord[1]}"
        return int(hashlib.md5(coord_str.encode()).hexdigest(), 16)
    
    indexed_coords = [(i, coord) for i, coord in enumerate(coords)]
    sorted_coords = sorted(indexed_coords, key=lambda x: coord_hash(x[1]))
    return [i for i, _ in sorted_coords]

def sine_wave_order(coords: list, frequency: float = 1.0) -> list:
    """Order coordinates based on sine wave pattern."""
    def sine_score(coord):
        x, y = coord
        return math.sin(frequency * x) + math.cos(frequency * y)
    
    indexed_coords = [(i, coord) for i, coord in enumerate(coords)]
    sorted_coords = sorted(indexed_coords, key=lambda x: sine_score(x[1]))
    return [i for i, _ in sorted_coords]

def fibonacci_order(coords: list) -> list:
    """Order coordinates based on Fibonacci sequence."""
    def fibonacci(n):
        if n <= 1:
            return n
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b
    
    def fib_score(coord):
        x, y = coord
        return fibonacci(x % 20) + fibonacci(y % 20)
    
    indexed_coords = [(i, coord) for i, coord in enumerate(coords)]
    sorted_coords = sorted(indexed_coords, key=lambda x: fib_score(x[1]))
    return [i for i, _ in sorted_coords]

def prime_order(coords: list) -> list:
    """Order coordinates based on prime number sequence."""
    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                return False
        return True
    
    def prime_score(coord):
        x, y = coord
        score = 0
        for i in range(min(x, y) + 1):
            if is_prime(i):
                score += 1
        return score
    
    indexed_coords = [(i, coord) for i, coord in enumerate(coords)]
    sorted_coords = sorted(indexed_coords, key=lambda x: prime_score(x[1]))
    return [i for i, _ in sorted_coords]

def gravity_simulation_order(coords: list, center: tuple = (16, 16)) -> list:
    """Order coordinates based on gravitational attraction simulation."""
    def gravity_score(coord):
        x, y = coord
        cx, cy = center
        distance = math.sqrt((x - cx)**2 + (y - cy)**2)
        if distance == 0:
            return float('inf')
        return 1.0 / distance  # Gravitational potential
    
    indexed_coords = [(i, coord) for i, coord in enumerate(coords)]
    sorted_coords = sorted(indexed_coords, key=lambda x: gravity_score(x[1]), reverse=True)
    return [i for i, _ in sorted_coords]

def musical_scale_order(coords: list, scale: list = None) -> list:
    """Order coordinates based on musical scale intervals."""
    if scale is None:
        scale = [0, 2, 4, 5, 7, 9, 11]
    
    def musical_score(coord):
        x, y = coord
        # Use coordinates to determine scale position
        total = x + y
        scale_pos = total % len(scale)
        return scale[scale_pos]
    
    indexed_coords = [(i, coord) for i, coord in enumerate(coords)]
    sorted_coords = sorted(indexed_coords, key=lambda x: musical_score(x[1]))
    return [i for i, _ in sorted_coords]

def coordinate_based_order(coords: list, method: str = "row_col") -> list:
    """Order coordinates based on various coordinate methods."""
    indexed_coords = [(i, coord) for i, coord in enumerate(coords)]
    
    if method == "row_col":
        sorted_coords = sorted(indexed_coords, key=lambda x: (x[1][0], x[1][1]))
    elif method == "col_row":
        sorted_coords = sorted(indexed_coords, key=lambda x: (x[1][1], x[1][0]))
    elif method == "sum":
        sorted_coords = sorted(indexed_coords, key=lambda x: x[1][0] + x[1][1])
    elif method == "product":
        sorted_coords = sorted(indexed_coords, key=lambda x: x[1][0] * x[1][1])
    elif method == "distance_from_origin":
        sorted_coords = sorted(indexed_coords, key=lambda x: math.sqrt(x[1][0]**2 + x[1][1]**2))
    elif method == "distance_from_center":
        center = (16, 16)
        sorted_coords = sorted(indexed_coords, key=lambda x: math.sqrt((x[1][0] - center[0])**2 + (x[1][1] - center[1])**2))
    else:
        sorted_coords = indexed_coords
    
    return [i for i, _ in sorted_coords]

def test_movement_patterns():
    """Test all advanced movement patterns."""
    coords = [data['coord'] for data in PUZZLE_DATA]
    words = [data['word'] for data in PUZZLE_DATA]
    
    # Create CSV file for results
    csv_file = "movement_pattern_results.csv"
    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Pattern', 'Mnemonic', 'Address', 'Is_Match'])
        
        patterns = [
            ("Hash-based", lambda: hash_based_order(coords)),
            ("Sine Wave (f=1.0)", lambda: sine_wave_order(coords, 1.0)),
            ("Sine Wave (f=0.5)", lambda: sine_wave_order(coords, 0.5)),
            ("Sine Wave (f=2.0)", lambda: sine_wave_order(coords, 2.0)),
            ("Fibonacci", lambda: fibonacci_order(coords)),
            ("Prime-based", lambda: prime_order(coords)),
            ("Gravity Simulation", lambda: gravity_simulation_order(coords)),
            ("Musical Scale (Major)", lambda: musical_scale_order(coords, [0, 2, 4, 5, 7, 9, 11])),
            ("Musical Scale (Minor)", lambda: musical_scale_order(coords, [0, 2, 3, 5, 7, 8, 10])),
            ("Coordinate (row,col)", lambda: coordinate_based_order(coords, "row_col")),
            ("Coordinate (col,row)", lambda: coordinate_based_order(coords, "col_row")),
            ("Coordinate (sum)", lambda: coordinate_based_order(coords, "sum")),
            ("Coordinate (product)", lambda: coordinate_based_order(coords, "product")),
            ("Distance from origin", lambda: coordinate_based_order(coords, "distance_from_origin")),
            ("Distance from center", lambda: coordinate_based_order(coords, "distance_from_center")),
        ]
        
        print("Testing Advanced Movement Patterns...")
        print("=" * 60)
        
        for pattern_name, pattern_func in patterns:
            try:
                order = pattern_func()
                ordered_words = [words[i] for i in order]
                if validate_mnemonic(ordered_words, pattern_name, writer):
                    return True
                    
            except Exception as e:
                print(f"❌ Error in {pattern_name}: {e}")
                writer.writerow([pattern_name, f"ERROR: {e}", "ERROR", False])
        
        print("\n" + "=" * 60)
        print("All advanced patterns tested. No match found.")
        print(f"Results saved to {csv_file}")
        return False

def test_hybrid_patterns():
    """Test combinations of patterns."""
    coords = [data['coord'] for data in PUZZLE_DATA]
    words = [data['word'] for data in PUZZLE_DATA]
    
    print("\nTesting Hybrid Patterns...")
    print("=" * 60)
    
    # Create CSV file for hybrid results
    csv_file = "hybrid_pattern_results.csv"
    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Pattern', 'Mnemonic', 'Address', 'Is_Match'])
        
        # Combine hash-based with other patterns
        hash_order = hash_based_order(coords)
        
        # Try reversing hash order
        reversed_order = list(reversed(hash_order))
        ordered_words = [words[i] for i in reversed_order]
        if validate_mnemonic(ordered_words, "Hash-based (Reversed)", writer):
            return True
        
        # Try alternating hash and coordinate order
        coord_order = list(range(18))
        alternating_order = []
        for i in range(18):
            if i % 2 == 0:
                alternating_order.append(hash_order[i // 2])
            else:
                alternating_order.append(coord_order[i // 2])
        
        ordered_words = [words[i] for i in alternating_order]
        if validate_mnemonic(ordered_words, "Hash + Coordinate Alternating", writer):
            return True
        
        # Try combining with sine wave
        sine_order = sine_wave_order(coords, 1.0)
        combined_order = []
        for i in range(18):
            if i % 2 == 0:
                combined_order.append(hash_order[i // 2])
            else:
                combined_order.append(sine_order[i // 2])
        
        ordered_words = [words[i] for i in combined_order]
        if validate_mnemonic(ordered_words, "Hash + Sine Wave Alternating", writer):
            return True
        
        # Try combining with Fibonacci
        fib_order = fibonacci_order(coords)
        fib_combined_order = []
        for i in range(18):
            if i % 2 == 0:
                fib_combined_order.append(hash_order[i // 2])
            else:
                fib_combined_order.append(fib_order[i // 2])
        
        ordered_words = [words[i] for i in fib_combined_order]
        if validate_mnemonic(ordered_words, "Hash + Fibonacci Alternating", writer):
            return True
        
        print(f"Hybrid results saved to {csv_file}")
        return False

if __name__ == "__main__":
    print("GSMG Movement Pattern Validator")
    print("=" * 60)
    
    # Test basic patterns first
    success = test_movement_patterns()
    
    if not success:
        # Test hybrid patterns
        success = test_hybrid_patterns()
    
    if not success:
        print("\nNo solution found with movement patterns.")
        print("Consider implementing additional patterns or checking existing ones.")
