#!/usr/bin/env python3
import sys
from bip_utils import (
    Bip39MnemonicValidator, Bip39SeedGenerator,
    Bip44, Bip44Coins, Bip44Changes,
    Bip49, Bip49Coins,
    Bip84, Bip84Coins,
    Bip86, Bip86Coins
)

def derive_and_print(wallet_cls, coin, label, seed_bytes):
    print(f"\n=== {label} ===")
    account = wallet_cls.FromSeed(seed_bytes, coin).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT)
    for idx in range(20):
        addr = account.AddressIndex(idx).PublicKey().ToAddress()
        wif  = account.AddressIndex(idx).PrivateKey().ToWif()
        print(f"{idx:2d}: {addr} | WIF: {wif}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python derive_keys.py \"<mnemonic>\"")
        sys.exit(1)

    mnemonic = sys.argv[1]
    validator = Bip39MnemonicValidator()
    if not validator.Validate(mnemonic):
        print("❌ Invalid mnemonic checksum.")
        sys.exit(1)

    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
    print("[+] Seed (hex):", seed_bytes.hex())

    derive_and_print(Bip44, Bip44Coins.BITCOIN, "BIP44 Legacy (1...) P2PKH",         seed_bytes)
    derive_and_print(Bip49, Bip49Coins.BITCOIN, "BIP49 (3...) P2WPKH-in-P2SH",       seed_bytes)
    derive_and_print(Bip84, Bip84Coins.BITCOIN, "BIP84 (bc1q...) Native SegWit",     seed_bytes)
    derive_and_print(Bip86, Bip86Coins.BITCOIN, "BIP86 (bc1p...) Taproot",           seed_bytes)

if __name__=="__main__":
    main()
