from bip_utils import (
    Bip39SeedGenerator,
    Bip44, Bip44Coins,
    Bip49, Bip49Coins,
    Bip84, Bip84Coins,
    Bip86, Bip86Coins,
    Bip44Changes,
)
import csv

# -------- CONFIG ---------
MNEMONIC = "frost argue mountain chest guilt memory bright juice initial because lumber grant foam charge either forward capital miracle"
OUTPUT_CSV = "btc_derived_addresses.csv"
NUM_ADDRS = 20
# -------------------------

# Generate seed
seed_bytes = Bip39SeedGenerator(MNEMONIC).Generate()
print("[+] Mnemonic:")
print(MNEMONIC)
print("\n[+] Seed (hex):", seed_bytes.hex())

# Derivers
schemes = [
    ("BIP44 Legacy (1...) P2PKH", Bip44, Bip44Coins.BITCOIN),
    ("BIP49 (3...) P2WPKH-in-P2SH", Bip49, Bip49Coins.BITCOIN),
    ("BIP84 (bc1q...) Native SegWit", Bip84, Bip84Coins.BITCOIN),
    ("BIP86 (bc1p...) Taproot", Bip86, Bip86Coins.BITCOIN),
]

rows = []
for title, deriver, coin in schemes:
    print(f"\n=== {title} ===")
    bip_ctx = deriver.FromSeed(seed_bytes, coin)

    # Collect account xpub/xprv
    acc_ctx = bip_ctx.Purpose().Coin().Account(0)
    xpub = acc_ctx.PublicKey().ToExtended()
    xprv = acc_ctx.PrivateKey().ToExtended()

    # External chain
    ext_ctx = acc_ctx.Change(Bip44Changes.CHAIN_EXT)
    for i in range(NUM_ADDRS):
        addr_ctx = ext_ctx.AddressIndex(i)
        addr = addr_ctx.PublicKey().ToAddress()
        wif = addr_ctx.PrivateKey().ToWif()
        path = addr_ctx.Path()

        print(f"{i:2d}: {addr} | WIF: {wif}")
        rows.append({
            "Scheme": title,
            "Index": i,
            "Path": path,
            "Address": addr,
            "WIF": wif,
            "xpub": xpub,
            "xprv": xprv,
        })

# Save to CSV
with open(OUTPUT_CSV, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["Scheme", "Index", "Path", "Address", "WIF", "xpub", "xprv"])
    writer.writeheader()
    writer.writerows(rows)

print(f"\n[+] Exported {len(rows)} entries to {OUTPUT_CSV}")
