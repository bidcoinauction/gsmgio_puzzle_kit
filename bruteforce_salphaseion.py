 #!/usr/bin/env python3
import itertools
import hashlib
import subprocess
from pathlib import Path

# ====== CONFIGURATION ======
OUTPUT_FILE = "salphaseion_decrypted.txt"
CIPHERTEXT_FILE = "salphaseion_full.txt"

# AES base64 blob copied directly from Salphaseion
AES_BLOB = """U2FsdGVkX18tP2/gbclQ5tNZuD4shoV3axuUd8J8aycGCAMoYfhZK0JecHTDpTFe
dGJh4SJIP66qRtXvo7PTpvsIjwO8prLiC/sNHthxiGMuqIrKoO224rOisFJZgARi
c7PaJPne4nab8XCFuV3NbfxGX2BUjNkef5hg7nsoadZx08dNyU2b6eiciWiUvu7D
SATSFO7IFBiAMz7dDqIETKuGlTAP4EmMQUZrQNtfbJsURATW6V5VSbtZB5RFk0O+
IymhstzrQHsU0Bugjv2nndmOEhCxGi/lqK2rLNdOOLutYGnA6RDDbFJUattggELh
2SZx+SBpCdbSGjxOap27l9FOyl02r0HU6UxFdcsbfZ1utTqVEyNs91emQxtpgt+6
BPZisil74Jv4EmrpRDC3ufnkmWwR8NfqVPIKhUiGDu5QflYjczT6DrA9vLQZu3ko
k+/ZurtRYnqqsj49UhwEF9GfUfl7uQYm0UunatW43C3Z1tyFRGAzAHQUFS6jRCd+
vZGyoTlOsThjXDDCSAwoX2M+yM+oaEQoVvDwVkIqRhfDNuBmEfi+HpXuJLPBS1Pb
UjrgoG/Uv7o8IeyST4HBv8+5KLx7IKQS8f1kPZ2YUME+8XJx0caFYs+JS2Jdm0oj
Jm3JJEcYXdKEzOQvRzi4k+6dNlJ05TRZNTJvn0fPG5cM80aQb/ckUHsLsw9a4Wzh
HsrzBQRTIhog9sTm+k+LkXzIJiFfSzRgf250pbviFGoQaIFl1CTQPT2w29DLP900
6bSiliywwnxXOor03Hn+7MJL27YxeaGQn0sFGgP5X0X4jm3vEBkWvtF4PZl0bXWZ
LvVL/zTn87+2Zi/u7LA6y6b2yt7YVMkpheeOL0japXaiAf3bSPeUPGz/eu8ZX/Nn
O3259hG1XwoEVcGdDBV0Nh0A4/phPCR0x5BG04U0OeWAT/5Udc/gGM0TT2FrEzs/
AJKtmsnj31OSsqWb9wD+CoduYY2JrkzJYihE3ZcgcvqqffZXqxQkaI/83ro6JZ4P
ubml0PUnAnkdmnBCpbClbZMzmo3ELZ0EQwsvkJFDMQmiRhda4nBooUW7zXOIb7Wx
bE9THrt3cdZP5uAgVfgguUNE4fZMN8ATEDhdSsLklJe2GvihKuZVA6uuSkWAsK6u
MGo76xpPwYs3eUdLjtANS83a6/F/fhkX1GXs7zbQjh+Inzk8jhEdEogl9jPs/oDj
KjbkUpFlsCWwAZGoeKlmX7c4OGuD5c+FEH+2nYHvYl8y1E/K5SDt9Uocio8XuxbD
ZOzhw7LMSGkD1MZxpDzsCZY1emkSNd88NFj+9U8VssIDDVMYwKMsHKfjc0x5OlzQ
1f6ST0xCkwydDHHGRKKxFC4y6H6fV9sgf9OPK/65z94Rx72+mfvTyizShjxYSRpl
sH9otU4parl8roD0KsVTfXZoYrYXzK6cXBn1BO/OEqWlu++Dd9MiGaUGKd22fXER
qNWoRAKlNn2b6EehD2D8WaAoliPURjkB0Lb/FpP9unI93Twg6NxBXAj734nctukR
b3kE08RydJV70eJsvEftF5hbED4HacGx9pzisaSz6t9AKiuSoF6uoCtlTIYatyfZ
kQA4wg50hAJqTynOQ09ArRHEchtB/7uvWZSBGJ7+zlzRGKx99P3oDZD+Y5D8bmUs
3PV6FnAp+IRSlnsQ6hChkwBoQUcngcfGSkBRvmGjsGercCetRRwBOfh9fbX2ruw4
mzRYrGnz9eBtepkJXDRjD6yvhNfQMCSkm6l9zMWxKvFbv5g2ae2SLrEt/x3MP2/G"""

# The parts of the password from the riddle
PARTS = [
    "enter",
    "lastwordsbeforearchichoice",
    "matrixsumlist",
    "thispassword"
]

# The possible separators between the parts
SEPARATORS = ["", "_", "-"]

# ====== Generate permutations and case variations ======
def generate_variants(parts):
    variants = set()
    for combo in itertools.permutations(parts):
        for sep in SEPARATORS:
            base = sep.join(combo)

            # Apply different capitalization patterns
            variants.add(base)
            variants.add(base.lower())
            variants.add(base.upper())
            variants.add(base.title())

            # CamelCase (capitalize first segment only)
            camel = combo[0].capitalize() + sep + sep.join(combo[1:])
            variants.add(camel)

    return list(variants)

# ====== Compute SHA256 digest ======
def sha256_digest(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()

# ====== Test password with OpenSSL (byte-safe) ======
def try_password(passphrase: str) -> bool:
    digest = sha256_digest(passphrase)
    # The openssl command that was used in the puzzle
    cmd = [
        "openssl", "enc", "-aes-256-cbc", "-d", "-a",
        "-in", CIPHERTEXT_FILE,
        "-pass", f"pass:{digest}"
    ]
    try:
        # Use a more robust way to handle subprocess output
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stderr_text = result.stderr.decode(errors="ignore")
        stdout_bytes = result.stdout
        
        # Check for a successful decryption
        if result.returncode == 0 and "bad decrypt" not in stderr_text.lower():
            try:
                stdout_text = stdout_bytes.decode(errors="ignore")
            except Exception:
                stdout_text = "<binary output>"

            print(f"[+] SUCCESS with password: {passphrase}\n")
            print(stdout_text)
            Path(OUTPUT_FILE).write_bytes(stdout_bytes)
            print(f"\nDecrypted text saved to {OUTPUT_FILE}")
            return True
    except FileNotFoundError:
        print("Error: OpenSSL command not found. Please ensure it is installed and in your PATH.")
    except Exception as e:
        print(f"Error: {e}")
    return False

# ====== MAIN ======
if __name__ == "__main__":
    # Write the blob to a file for OpenSSL to read
    Path(CIPHERTEXT_FILE).write_text(AES_BLOB.strip())

    candidates = generate_variants(PARTS)
    print(f"Generated {len(candidates)} password candidates to try...\n")

    for pwd in candidates:
        print(f"Trying: {pwd}")
        if try_password(pwd):
            break
