import string

# === BIP39 Permutation Reference ===
# Alphabetical index of words (from parse_salphaseion.py output)
final_perm = [11, 1, 6, 3, 13, 17, 9, 15, 5, 16, 7, 2, 0, 14, 12, 10, 4, 8]

# === Decoding Functions ===
def base36_mod(pair): return int(pair, 36) % 18
def ascii_sum_mod(pair): return (ord(pair[0]) + ord(pair[1])) % 18
def rot13_ascii_sum_mod(pair):
    def rot13(c): return chr(((ord(c.lower()) - 97 + 13) % 26) + 97) if c.isalpha() else c
    return (ord(rot13(pair[0])) + ord(rot13(pair[1]))) % 18
def xor_sum_mod(pair): return (ord(pair[0]) ^ ord(pair[1])) % 18
def polybius_mod(pair):
    square = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    def idx(c): return square.index(c.upper().replace('J','I'))
    try: return (idx(pair[0]) + idx(pair[1])) % 18
    except: return -1
def mirrored_base58(pair):
    base58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    try: return (base58.index(pair[::-1])) % 18
    except: return -1
def bitwise_invert_ord(pair):
    return ((~ord(pair[0]) + ~ord(pair[1])) & 0xFF) % 18

# === Instruction Key Parsing ===
instruction_key = "rfdfuesa"
pairs = [instruction_key[i:i+2] for i in range(0, len(instruction_key), 2)]

# === Run all decoders ===
decoders = {
    "base36_mod": base36_mod,
    "ascii_sum_mod": ascii_sum_mod,
    "rot13_ascii_sum_mod": rot13_ascii_sum_mod,
    "xor_sum_mod": xor_sum_mod,
    "polybius_mod": polybius_mod,
    "bitwise_invert_ord": bitwise_invert_ord
}

print(f"\n🔑 Decoding instruction: {instruction_key} → Pairs: {pairs}\n")

# Collect output
for name, func in decoders.items():
    decoded = [func(p) for p in pairs]
    match = decoded == final_perm[:len(decoded)]
    print(f"[{name:<20}] → {decoded} {'✅ MATCH' if match else ''}")