import string, glob, re
from collections import Counter, defaultdict
from typing import List

# === BIP39 Permutation Reference ===
# Alphabetical index of words (from parse_salphaseion.py output)
# This is our target sequence.
final_perm = [11, 1, 6, 3, 13, 17, 9, 15, 5, 16, 7, 2, 0, 14, 12, 10, 4, 8]

# === Decoding Functions ===
# These are the same functions we've tested before. If a new instruction
# key works, it will be with one of these.
def base36_mod(pair):
    """Decodes a Base36 pair and takes modulo 18."""
    try: return int(pair, 36) % 18
    except ValueError: return -1
    
def ascii_sum_mod(pair):
    """Sums the ASCII values of a pair and takes modulo 18."""
    return (ord(pair[0]) + ord(pair[1])) % 18
    
def rot13_ascii_sum_mod(pair):
    """Applies ROT13, sums ASCII values, and takes modulo 18."""
    def rot13(c): return chr(((ord(c.lower()) - 97 + 13) % 26) + 97) if c.isalpha() else c
    return (ord(rot13(pair[0])) + ord(rot13(pair[1])) ) % 18
    
def xor_sum_mod(pair):
    """XORs the ASCII values of a pair and takes modulo 18."""
    return (ord(pair[0]) ^ ord(pair[1])) % 18

def polybius_mod(pair):
    """Decodes a Polybius square pair and takes modulo 18."""
    square = {
        (1, 1): 'a', (1, 2): 'b', (1, 3): 'c', (1, 4): 'd', (1, 5): 'e',
        (2, 1): 'f', (2, 2): 'g', (2, 3): 'h', (2, 4): 'i', (2, 5): 'k',
        (3, 1): 'l', (3, 2): 'm', (3, 3): 'n', (3, 4): 'o', (3, 5): 'p',
        (4, 1): 'q', (4, 2): 'r', (4, 3): 's', (4, 4): 't', (4, 5): 'u',
        (5, 1): 'v', (5, 2): 'w', (5, 3): 'x', (5, 4): 'y', (5, 5): 'z'
    }
    try:
        val1 = int(pair[0])
        val2 = int(pair[1])
        if 1 <= val1 <= 5 and 1 <= val2 <= 5:
            decoded_char = square[(val1, val2)]
            instruction_keys_alphabet = string.ascii_lowercase.replace('j', '')
            return (instruction_keys_alphabet.find(decoded_char) + 1) % 18
        else:
            return -1
    except (ValueError, KeyError):
        return -1

def mirrored_base58(pair):
    """Decodes a mirrored Base58 pair and takes modulo 18."""
    b58_alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    reversed_b58 = b58_alphabet[::-1]
    try:
        val = reversed_b58.find(pair[0]) * 58 + reversed_b58.find(pair[1])
        return val % 18
    except ValueError:
        return -1

def bitwise_invert_ord(pair):
    """Performs bitwise inversion on the sum of ASCII values and takes modulo 18."""
    return (~(ord(pair[0]) + ord(pair[1]))) % 18

# The final instruction key to test
instruction_keys_to_test = [
    "9t9j86030d0h090f050g0702000e0c"
]

# === Run all decoders for all keys ===
decoders = {
    "base36_mod": base36_mod,
    "ascii_sum_mod": ascii_sum_mod,
    "rot13_ascii_sum_mod": rot13_ascii_sum_mod,
    "xor_sum_mod": xor_sum_mod,
    "polybius_mod": polybius_mod,
    "mirrored_base58": mirrored_base58,
    "bitwise_invert_ord": bitwise_invert_ord
}

print(f"\nSearching for a matching instruction key...")
print("-" * 50)

# Iterate through each key and each decoder to find a match.
for key in instruction_keys_to_test:
    if len(key) % 2 != 0:
        print(f"🔑 Skipping key: '{key}' - has an odd number of characters.")
        print("-" * 50)
        continue
    
    pairs = [key[i:i+2] for i in range(0, len(key), 2)]
    
    for name, func in decoders.items():
        if len(pairs) > 0:
            results = [func(pair) for pair in pairs]
            
            # Check for a match with the full target sequence
            if results == final_perm:
                print(f"🎉🎉🎉 Found the final solution! Key: '{key}' with decoder: '{name}'")
                print(f"Final sequence: {results}")
                # We found it, so we can exit.
                break
    else:
        continue
    break

print("\nSearch complete.")