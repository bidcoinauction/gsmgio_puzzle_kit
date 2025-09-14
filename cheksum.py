from bip_utils import (
    Bip39MnemonicValidator, Bip39SeedGenerator,
    Bip44, Bip44Coins, Bip39WordsNum, Bip39WordsList
)

TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"

original_words = [
    "grant", "capital", "bright", "forward", "miracle",
    "because", "memory", "initial", "guilt",
    "foam", "charge", "lumber", "mountain",
    "chest", "argue", "either", "juice", "frost"
]

# Load full BIP39 English wordlist
bip39_wordlist = Bip39WordsList(Bip39WordsNum.WORDS_NUM_12).GetAll()

def is_valid_mnemonic(words):
    return Bip39MnemonicValidator().IsValid(" ".join(words))

def derive_address(words):
    seed = Bip39SeedGenerator(" ".join(words)).Generate()
    return Bip44.FromSeed(seed, Bip44Coins.BITCOIN).Purpose().Coin().Account(0).Change(0).AddressIndex(0).PublicKey().ToAddress()

# Main test loop
for idx in range(len(original_words)):
    for replacement in bip39_wordlist:
        if replacement == original_words[idx]:
            continue  # skip same word

        candidate = original_words[:]
        candidate[idx] = replacement

        if is_valid_mnemonic(candidate):
            address = derive_address(candidate)
            if address == TARGET_ADDRESS:
                print(f"[MATCH] Word #{idx+1} replaced with '{replacement}'")
                print("Mnemonic:", " ".join(candidate))
                print("Address:", address)
                exit(0)

print("❌ No match found with 1-word replacements.")
