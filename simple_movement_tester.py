#!/usr/bin/env python3
"""
Simple Movement Pattern Tester for GSMG Puzzle
Tests new movement patterns without external dependencies.
"""

import math
import hashlib
from pathlib import Path
from typing import List, Tuple

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

def print_pattern_result(pattern_name: str, words: List[str], order: List[int]):
    """Print the result of a movement pattern test."""
    print(f"\n{pattern_name}:")
    print(f"  Order: {order}")
    print(f"  Words: {' '.join(words)}")
    print(f"  Length: {len(words)}")

def hilbert_curve_order(n: int) -> List[Tuple[int, int]]:
    """Generate Hilbert curve traversal order for n×n grid."""
    def hilbert_coords(d, n):
        """Convert distance d to (x,y) coordinates on Hilbert curve."""
        x, y = 0, 0
        for s in range(n-1, -1, -1):
            rx = 1 & (d >> 2*s)
            ry = 1 & (d >> 2*s + 1)
            if ry == 0:
                if rx == 1:
                    x = (1 << s) - 1 - x
                    y = (1 << s) - 1 - y
                x, y = y, x
            x += (1 << s) * rx
            y += (1 << s) * ry
        return (x, y)
    
    coords = []
    for d in range(n * n):
        coords.append(hilbert_coords(d, n))
    return coords

def hash_based_order(coords: List[Tuple[int, int]]) -> List[int]:
    """Order coordinates based on hash values."""
    def coord_hash(coord):
        coord_str = f"{coord[0]},{coord[1]}"
        return int(hashlib.md5(coord_str.encode()).hexdigest(), 16)
    
    indexed_coords = [(i, coord) for i, coord in enumerate(coords)]
    sorted_coords = sorted(indexed_coords, key=lambda x: coord_hash(x[1]))
    return [i for i, _ in sorted_coords]

def sine_wave_order(coords: List[Tuple[int, int]], frequency: float = 1.0) -> List[int]:
    """Order coordinates based on sine wave pattern."""
    def sine_score(coord):
        x, y = coord
        return math.sin(frequency * x) + math.cos(frequency * y)
    
    indexed_coords = [(i, coord) for i, coord in enumerate(coords)]
    sorted_coords = sorted(indexed_coords, key=lambda x: sine_score(x[1]))
    return [i for i, _ in sorted_coords]

def fibonacci_order(coords: List[Tuple[int, int]]) -> List[int]:
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

def prime_order(coords: List[Tuple[int, int]]) -> List[int]:
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

def gravity_simulation_order(coords: List[Tuple[int, int]], center: Tuple[int, int] = (16, 16)) -> List[int]:
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

def musical_scale_order(coords: List[Tuple[int, int]], scale: List[int] = [0, 2, 4, 5, 7, 9, 11]) -> List[int]:
    """Order coordinates based on musical scale intervals."""
    def musical_score(coord):
        x, y = coord
        # Use coordinates to determine scale position
        total = x + y
        scale_pos = total % len(scale)
        return scale[scale_pos]
    
    indexed_coords = [(i, coord) for i, coord in enumerate(coords)]
    sorted_coords = sorted(indexed_coords, key=lambda x: musical_score(x[1]))
    return [i for i, _ in sorted_coords]

def test_movement_patterns():
    """Test all advanced movement patterns."""
    coords = [data['coord'] for data in PUZZLE_DATA]
    words = [data['word'] for data in PUZZLE_DATA]
    
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
    ]
    
    print("Testing Advanced Movement Patterns...")
    print("=" * 60)
    
    for pattern_name, pattern_func in patterns:
        try:
            order = pattern_func()
            ordered_words = [words[i] for i in order]
            print_pattern_result(pattern_name, ordered_words, order)
                
        except Exception as e:
            print(f"\n❌ Error in {pattern_name}: {e}")
    
    print("\n" + "=" * 60)
    print("All advanced patterns tested.")

def test_hybrid_patterns():
    """Test combinations of patterns."""
    coords = [data['coord'] for data in PUZZLE_DATA]
    words = [data['word'] for data in PUZZLE_DATA]
    
    print("\nTesting Hybrid Patterns...")
    print("=" * 60)
    
    # Combine hash-based with other patterns
    hash_order = hash_based_order(coords)
    
    # Try reversing hash order
    reversed_order = list(reversed(hash_order))
    ordered_words = [words[i] for i in reversed_order]
    print_pattern_result("Hash-based (Reversed)", ordered_words, reversed_order)
    
    # Try alternating hash and coordinate order
    coord_order = list(range(18))
    alternating_order = []
    for i in range(18):
        if i % 2 == 0:
            alternating_order.append(hash_order[i // 2])
        else:
            alternating_order.append(coord_order[i // 2])
    
    ordered_words = [words[i] for i in alternating_order]
    print_pattern_result("Hash + Coordinate Alternating", ordered_words, alternating_order)
    
    # Try combining with sine wave
    sine_order = sine_wave_order(coords, 1.0)
    combined_order = []
    for i in range(18):
        if i % 2 == 0:
            combined_order.append(hash_order[i // 2])
        else:
            combined_order.append(sine_order[i // 2])
    
    ordered_words = [words[i] for i in combined_order]
    print_pattern_result("Hash + Sine Wave Alternating", ordered_words, combined_order)

if __name__ == "__main__":
    print("GSMG Simple Movement Pattern Tester")
    print("=" * 60)
    
    # Test basic patterns first
    test_movement_patterns()
    
    # Test hybrid patterns
    test_hybrid_patterns()
    
    print("\nPattern testing complete.")
    print("These patterns can now be tested with mnemonic validation.")
