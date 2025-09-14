from mnemonic import Mnemonic
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes

mnemonics = {
    "Permutation Mapping": "either charge guilt initial miracle forward mountain frost bright argue juice lumber grant memory because capital chest foam",
    "Sorted by Base36 Value": "because bright capital lumber juice either forward foam chest charge argue frost initial miracle grant guilt memory mountain",
    "Mirrored Sorted": "mountain memory guilt grant miracle initial frost argue charge chest foam forward either juice lumber capital bright because",
    "Delta Path Heuristic": "guilt lumber forward bright capital foam chest miracle either mountain initial grant frost charge juice because argue memory"
}

target_address = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"

mnemo = Mnemonic("english")

for label, phrase in mnemonics.items():
    print(f"\n[Checking] {label}")
    if not mnemo.check(phrase):
        print("❌ Invalid BIP39 checksum")
        continue

    print("✅ Valid mnemonic!")
    seed = Bip39SeedGenerator(phrase).Generate()
    bip44_addr = Bip44.FromSeed(seed, Bip44Coins.BITCOIN).Purpose().Coin().Account(0)\
                    .Change(Bip44Changes.CHAIN_EXT).AddressIndex(0).PublicKey().ToAddress()

    print("Derived BIP44 Address:", bip44_addr)
    if bip44_addr == target_address:
        print("🎯 MATCHES TARGET ADDRESS!")
        break
