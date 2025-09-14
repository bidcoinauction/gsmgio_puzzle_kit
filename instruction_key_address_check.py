from bip_utils import Bip39MnemonicValidator, Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes

mnemonic = "grant argue lumber foam capital frost chest initial guilt either forward memory miracle because bright mountain juice charge"

# Validate mnemonic
validator = Bip39MnemonicValidator()
if not validator.IsValid(mnemonic):
    print("❌ Invalid BIP39 checksum!")
    exit(1)

# Generate seed from mnemonic
seed = Bip39SeedGenerator(mnemonic).Generate()

# Derive first BIP44 (legacy) Bitcoin address
addr = Bip44.FromSeed(seed, Bip44Coins.BITCOIN).Purpose().Coin().Account(0) \
       .Change(Bip44Changes.CHAIN_EXT).AddressIndex(0).PublicKey().ToAddress()

print("✅ Valid BIP39 mnemonic")
print("Derived BIP44 Address:", addr)
