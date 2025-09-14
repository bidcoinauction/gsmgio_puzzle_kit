from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes

# The correct 18-word mnemonic (known good)
mnemonic = "frost argue mountain chest guilt memory bright juice initial because lumber grant foam charge either forward capital miracle"

# Step 1: Generate seed
seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
print("[+] Seed (hex):", seed_bytes.hex())

# Step 2: Derive address using BIP44 (Legacy P2PKH, m/44'/0'/0'/0/0)
bip44 = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)
addr = (
    bip44
    .Purpose()
    .Coin()
    .Account(0)
    .Change(Bip44Changes.CHAIN_EXT)
    .AddressIndex(0)
    .PublicKey()
    .ToAddress()
)

print("[+] Derived Address:", addr)