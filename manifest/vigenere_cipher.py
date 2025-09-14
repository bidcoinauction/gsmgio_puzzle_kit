# GSMG.IO 5 BTC PUZZLE - FINAL SOLVER SCRIPT
# This script takes the 18 decoded data points, sorts them by their
# grid coordinates, and deciphers the hidden final command using
# multiple cipher techniques.

import collections

# Define a simple data structure for our points
Point = collections.namedtuple("Point", ["pair", "row", "col", "char", "word"])

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

def decipher_instruction(instruction_key):
    """
    Runs multiple cipher checks on the instruction key to find the command.
    """
    print("[*] Stage 2: Deciphering the instruction key...")
    print(f"    Input Key: '{instruction_key}'")
    
    # --- Test 1: Vigenère Cipher ---
    print("\n--- Testing Vigenère Cipher ---")
    potential_keys = ["matrix", "causality", "gsmg", "bip39", "neo", "oracle"]
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    
    for key in potential_keys:
        deciphered_text = ""
        key_index = 0
        for char in instruction_key:
            if char in alphabet:
                # Find the position of the character and the key character
                char_pos = alphabet.find(char)
                key_char = key[key_index % len(key)]
                key_pos = alphabet.find(key_char)
                
                # Decrypt by subtracting the key shift
                shifted_pos = (char_pos - key_pos + 26) % 26
                deciphered_text += alphabet[shifted_pos]
                key_index += 1
            else:
                # Keep non-alphabetic characters as they are
                deciphered_text += char
        print(f"Result for key '{key}': {deciphered_text}")

    # --- Test 2: Atbash Cipher ---
    print("\n--- Testing Atbash Cipher ---")
    reverse_alphabet = alphabet[::-1]
    atbash_result = ""
    for char in instruction_key:
        if char in alphabet:
            original_pos = alphabet.find(char)
            atbash_result += reverse_alphabet[original_pos]
        else:
            atbash_result += char
    print(f"Atbash Result: {atbash_result}")
    
    print("-" * 40)
    print("[!] ACTION: Inspect the Vigenère results to find the command.")


def main():
    """
    Main function to run the solver logic.
    """
    # --- Stage 1: Sort data to get the base mnemonic and instruction key ---
    print("[*] Stage 1: Sorting puzzle data by grid coordinates...")
    all_points = get_puzzle_data()
    
    # Sort points lexicographically by row, then column
    sorted_points = sorted(all_points, key=lambda p: (p.row, p.col))
    
    # The "base mnemonic" is the word list in this new sorted order
    base_mnemonic = [p.word for p in sorted_points]
    
    # The instruction key is the character list from the sorted data
    instruction_key = "".join([p.char for p in sorted_points])
    
    print(f"[*] Base Mnemonic (pre-instruction): \n    {' '.join(base_mnemonic)}\n")
    
    # --- Stage 2: Decipher the instruction key ---
    decipher_instruction(instruction_key)

    # --- Stage 3: Apply the command (Manual Step) ---
    print("\n[*] Stage 3: Apply the deciphered command.")
    print("    Once you identify the command (e.g., 'swap words 5 and 10'),")
    print("    you will need to apply it to the 'Base Mnemonic' list.")
    print("\n    Example of how to apply a command:")
    print("    # final_mnemonic = base_mnemonic[:]")
    print("    # final_mnemonic[4], final_mnemonic[9] = final_mnemonic[9], final_mnemonic[4]")
    print("    # print(' '.join(final_mnemonic))")
    print("\nGood luck!")


if __name__ == "__main__":
    main()
