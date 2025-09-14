from mnemonic import Mnemonic
from bip32utils import BIP32Key

target = "1KfZGvwZxsvSmemoCmEV75uqcNzYBHjkHZ"
mnemo = Mnemonic("english")

# fixed positions in the 12-word mnemonic
fixed_positions = {0: "subject", 3: "order", 9: "day"}
passphrase = "this"

# 3 priority candidate combinations
candidates = [
    ["real","black","breathe","moon","food","only","cover","photo"],
    ["real","black","breathe","food","moon","only","cover","photo"],
    ["real","black","breathe","only","moon","food","cover","photo"],
]

def derive_address(seed_words, passphrase=""):
    """
    Derive the first Bitcoin address from the mnemonic
    using BIP44: m/44'/0'/0'/0/0
    """
    seed = mnemo.to_seed(seed_words, passphrase)
    master = BIP32Key.fromEntropy(seed)
    # Path m/44'/0'/0'/0/0
    child = master.ChildKey(44 + 0x80000000) \
                  .ChildKey(0 + 0x80000000) \
                  .ChildKey(0 + 0x80000000) \
                  .ChildKey(0).ChildKey(0)
    return child.Address()

# test each candidate phrase
for combo in candidates:
    # build the 12-word phrase with fixed positions
    phrase = [None] * 12
    for pos, word in fixed_positions.items():
        phrase[pos] = word
    free_positions = [i for i in range(12) if phrase[i] is None]
    for i, word in enumerate(combo):
        phrase[free_positions[i]] = word
    phrase_str = " ".join(phrase)

    for p in [passphrase, ""]:
        addr = derive_address(phrase_str, p)
        print(f"Testing: {phrase_str} (passphrase='{p}') -> {addr}")
        if addr == target:
            print("\n*** MATCH FOUND! ***")
            print(f"Seed: {phrase_str}")
            print(f"Passphrase: {p}")
            exit(0)

print("No match found in the top 3 candidates.")
