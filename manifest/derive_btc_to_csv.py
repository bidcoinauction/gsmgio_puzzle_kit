import csv
from bip_utils import (
    Bip39SeedGenerator,
    Bip44, Bip44Coins,
    Bip49, Bip49Coins,
    Bip84, Bip84Coins,
    Bip86, Bip86Coins,
    Bip44Changes,
)

MNEMONIC = (
    "frost argue mountain chest guilt memory bright juice initial because "
    "lumber grant foam charge either forward capital miracle"
)

OUTPUT_FILE = "btc_addresses.csv"

seed_bytes = Bip39SeedGenerator(MNEMONIC).Generate()
print("[+] Mnemonic:\n", MNEMONIC)
print("\n[+] Seed (hex):", seed_bytes.hex())

csv_file = open(OUTPUT_FILE, "w", newline="")
csv_writer = csv.writer(csv_file)
csv_writer.writerow([
    "Standard", "Index", "Derivation Path", "Address", "WIF",
    "Root xprv", "Root xpub"
])

def export_addresses(deriver, coin_enum, title, derivation_base):
    print(f"\n=== {title} ===")
    bip_root = deriver.FromSeed(seed_bytes, coin_enum)
    xprv = bip_root.PrivateKey().ToExtended()
    xpub = bip_root.PublicKey().ToExtended()

    addr_ctx = bip_root.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT)

    for i in range(20):
        child = addr_ctx.AddressIndex(i)
        addr = child.PublicKey().ToAddress()
        wif = child.PrivateKey().ToWif()
        path = f"{derivation_base}/{i}"

        print(f"{i:2d}: {addr} | WIF: {wif}")
        csv_writer.writerow([title, i, path, addr, wif, xprv, xpub])

export_addresses(Bip44, Bip44Coins.BITCOIN, "BIP44 Legacy (1...)", "m/44'/0'/0'/0")
export_addresses(Bip49, Bip49Coins.BITCOIN, "BIP49 (3...)", "m/49'/0'/0'/0")
export_addresses(Bip84, Bip84Coins.BITCOIN, "BIP84 (bc1q...)", "m/84'/0'/0'/0")
export_addresses(Bip86, Bip86Coins.BITCOIN, "BIP86 (bc1p...)", "m/86'/0'/0'/0")

csv_file.close()
print(f"\n[+] Results saved to {OUTPUT_FILE}")
