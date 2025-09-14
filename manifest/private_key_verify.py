# You will need to install the 'ecdsa' library for this script to work.
# You can install it using pip:
# pip install ecdsa

import hashlib
import ecdsa

# --- CONFIGURATION ---

# This is the SHA256 hash we previously calculated, which we hypothesize
# is the raw 256-bit private key for the wallet.
RAW_PRIVATE_KEY_HEX = "96820056fe43c34ab04bb813a4fd6d919af92e9bb2618434b08fe54d40109da9"

# This is the known public address of the prize wallet.
TARGET_ADDRESS = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"


# --- CRYPTOGRAPHIC HELPER FUNCTIONS ---

BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def b58encode(b: bytes) -> str:
    """
    Base58 encodes a bytes object.
    """
    # Convert bytes to a large integer
    n = int.from_bytes(b, 'big')
    
    # Handle leading zero bytes
    leading_zeros = len(b) - len(b.lstrip(b'\0'))
    
    # Perform the conversion
    res = []
    while n > 0:
        n, r = divmod(n, 58)
        res.append(BASE58_ALPHABET[r])
    
    # Add '1' for each leading zero byte and reverse the result
    return (BASE58_ALPHABET[0] * leading_zeros) + ''.join(reversed(res))

def b58check_encode(payload: bytes) -> str:
    """
    Performs Base58Check encoding on a payload.
    This involves adding a checksum to the payload before Base58 encoding.
    """
    # 1. Calculate the checksum: first 4 bytes of a double SHA256 hash
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    
    # 2. Append the checksum to the payload
    checked_payload = payload + checksum
    
    # 3. Base58 encode the result
    return b58encode(checked_payload)

def hash160(b: bytes) -> bytes:
    """
    Computes the HASH160 of a bytes object (SHA256 followed by RIPEMD-160).
    """
    # SHA256 hash
    sha256_hash = hashlib.sha256(b).digest()
    
    # RIPEMD-160 hash
    ripemd160_hasher = hashlib.new('ripemd160')
    ripemd160_hasher.update(sha256_hash)
    return ripemd160_hasher.digest()


# --- BITCOIN-SPECIFIC FUNCTIONS ---

def encode_privkey(private_key_bytes: bytes, compressed: bool = True) -> str:
    """
    Encodes a raw private key into Wallet Import Format (WIF).
    """
    # 1. Add the mainnet prefix (0x80)
    prefix = b'\x80'
    payload = prefix + private_key_bytes
    
    # 2. If using a compressed public key, add the suffix (0x01)
    if compressed:
        payload += b'\x01'
        
    # 3. Base58Check encode the payload
    return b58check_encode(payload)

def public_key_to_address(public_key_bytes: bytes, version: int = 0) -> str:
    """
    Derives a standard Bitcoin address from a public key.
    """
    # 1. Prepend the version byte (0x00 for mainnet P2PKH addresses)
    version_byte = version.to_bytes(1, 'big')
    
    # 2. Perform HASH160 on the public key
    hashed_pub_key = hash160(public_key_bytes)
    
    # 3. Combine version byte and hashed public key
    payload = version_byte + hashed_pub_key
    
    # 4. Base58Check encode the result to get the final address
    return b58check_encode(payload)


# --- MAIN VERIFICATION LOGIC ---

def verify_key():
    """
    Verifies if the raw private key generates the target Bitcoin address.
    """
    print("--- Verifying Final Private Key ---")
    print(f"[*] Raw Key: {RAW_PRIVATE_KEY_HEX}")
    print(f"[*] Target:  {TARGET_ADDRESS}")

    try:
        # 1. Convert the hexadecimal private key string into bytes.
        private_key_bytes = bytes.fromhex(RAW_PRIVATE_KEY_HEX)

        # 2. Derive the Wallet Import Format (WIF) key.
        wif_key = encode_privkey(private_key_bytes, compressed=True)

        # 3. Derive the public key using elliptic curve multiplication.
        #    The 'ecdsa' library handles the complex math of SECP256k1.
        #    We create a signing key object from our private key bytes.
        signing_key = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1)
        
        #    Then, we get the corresponding verifying key (the public key).
        verifying_key = signing_key.verifying_key
        
        # 4. Generate the compressed version of the public key.
        #    Compressed keys are smaller and are the standard format used today.
        compressed_pub_key = verifying_key.to_string('compressed')

        # 5. Derive the final, human-readable Bitcoin address from the public key.
        #    The 'version=0' specifies the '1...' prefix for a standard Bitcoin address.
        derived_address = public_key_to_address(compressed_pub_key, version=0)

        print(f"\n[+] Derived WIF Key:   {wif_key}")
        print(f"[+] Derived Address:   {derived_address}")

        # 6. Compare the derived address to our target to confirm the solution.
        if derived_address == TARGET_ADDRESS:
            print("\n" + "="*50)
            print("✅ VERIFICATION SUCCESSFUL!")
            print("The hash is the correct private key for the target address.")
            print("="*50)
        else:
            print("\n" + "="*50)
            print("❌ VERIFICATION FAILED!")
            print("The derived address does not match the target.")
            print("="*50)

    except Exception as e:
        print(f"\n[!] An error occurred during verification: {e}")

if __name__ == "__main__":
    verify_key()
