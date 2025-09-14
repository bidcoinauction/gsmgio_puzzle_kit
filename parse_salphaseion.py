#!/usr/bin/env python3
import re

# The encoding used in a previous stage of the puzzle
EBCDIC_ENCODING = 'cp1141' 

try:
    with open('salphaseion_decrypted.bin', 'rb') as f:
        data = f.read()

    print(f"--- Attempting to decode with {EBCDIC_ENCODING} ---")
    
    # Decode the binary data using the EBCDIC character set
    text = data.decode(EBCDIC_ENCODING, 'ignore')

    # --- Extraction Logic ---
    # Find all unique lowercase words that are at least 3 characters long.
    words = sorted(list(set(re.findall(r"\b[a-z]{3,}\b", text))))
    
    # Find the specific pattern for the instruction key.
    instruction_key_match = re.search(r"ksmhse:[\w.:]+", text)
    
    # --- Print Results ---
    if len(words) == 18 and instruction_key_match:
        instruction_key = instruction_key_match.group(0)
        
        print("\n✅ SUCCESS: Content Found!\n")
        print(f"--- Artifacts Extracted ---")
        
        print("\n[+] Instruction Key:")
        print(instruction_key)

        print("\n[+] BIP39 Words (alphabetized):")
        for i, word in enumerate(words, 1):
            print(f"{i}. {word}")
    else:
        print("\n--- ANALYSIS FAILED ---")
        print("Could not extract the expected content even with EBCDIC encoding.")
        print(f"Found {len(words)} words and key: {instruction_key_match}")

except FileNotFoundError:
    print("Error: 'salphaseion_decrypted.bin' not found.")
except Exception as e:
    print(f"An error occurred: {e}")