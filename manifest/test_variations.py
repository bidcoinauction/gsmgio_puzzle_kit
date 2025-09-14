from mnemonic import Mnemonic
from bip32utils import BIP32Key
import itertools

mnemo = Mnemonic("english")
target = "1KfZGvwZxsvSmemoCmEV75uqcNzYBHjkHZ"

# Fixed starting words
base = ["tower", "moon", "order", "black", "food"]

slot5_options = ["subject", "breathe", "real", "hope"]
slot7to9_pool = ["day", "time", "proof", "real"]
last_two_options = ["this", "stop", "future", "liberty"]

passphrases = ["", "breathe", "stop", "this"]

def derive_bip44_address(seed_words, passphrase=""):
    seed = mnemo.to_seed(seed_words, passphrase)
    master = BIP32Key.fromEntropy(seed)
    child = master.ChildKey(44 + 0x80000000)\
                  .ChildKey(0 + 0x80000000)\
                  .ChildKey(0 + 0x80000000)\
                  .ChildKey(0).ChildKey(0)
    return child.Address()

def derive_electrum_address(seed_words, passphrase=""):
    seed = mnemo.to_seed(seed_words, passphrase)
    master = BIP32Key.fromEntropy(seed)
    child = master.ChildKey(0).ChildKey(0)
    return child.Address()

def test_phrase(words):
    phrase = " ".join(words)
    for p in passphrases:
        # BIP44
        if derive_bip44_address(phrase, p) == target:
            print(f"\nMATCH (BIP44): {phrase} | passphrase={p}")
            return True
        # Electrum
        if derive_electrum_address(phrase, p) == target:
            print(f"\nMATCH (Electrum): {phrase} | passphrase={p}")
            return True
    # 13-word Electrum (append "this")
    phrase13 = phrase + " this"
    for p in passphrases:
        if derive_electrum_address(phrase13, p) == target:
            print(f"\nMATCH (13-word Electrum): {phrase13} | passphrase={p}")
            return True
    return False

count = 0
tested = set()

# Generate combinations
for slot5 in slot5_options:
    for combo_7to9 in itertools.permutations(slot7to9_pool, 4):
        # combo_7to9 includes 4 words; ensure "day" is present
        if "day" not in combo_7to9:
            continue
        first9 = base + [slot5] + list(combo_7to9[:4])
        # last two positions
        for last_two in itertools.permutations(last_two_options, 2):
            words = first9 + list(last_two)
            phrase_str = " ".join(words)
            if phrase_str in tested:
                continue
            tested.add(phrase_str)
            count += 1
            if count % 500 == 0:
                print(f"Checked {count} phrases...")
            if test_phrase(words):
                exit(0)

print("No match found in expanded search.")
