from mnemonic import Mnemonic

mnemonic = "forward bright argue capital chest miracle charge juice memory grant mountain initial guilt frost either because foam lumber"
mnemo = Mnemonic("english")

if mnemo.check(mnemonic):
    print("✅ Valid mnemonic!")
else:
    print("❌ Invalid checksum.")
