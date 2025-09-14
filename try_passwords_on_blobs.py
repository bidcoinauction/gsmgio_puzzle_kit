#!/usr/bin/env python3
import argparse, base64, binascii, hashlib, io, os, re, sys, textwrap
from pathlib import Path
from typing import Iterable, Tuple, Optional

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import MD5, SHA256

# ---------- helpers ----------
PRINTABLE = set(range(32,127)) | {9,10,13}

def b64_maybe_decode(data: bytes) -> bytes:
    s = data.strip()
    # quick heuristic: base64 alphabet and padded
    if re.fullmatch(rb"[A-Za-z0-9+/=\s]+", s) and len(s) % 4 == 0:
        try:
            return base64.b64decode(s, validate=True)
        except Exception:
            pass
    return data

def printable_sequences(b: bytes, min_len=8) -> list[str]:
    out, cur = [], bytearray()
    for ch in b:
        if ch in PRINTABLE:
            cur.append(ch)
        else:
            if len(cur) >= min_len:
                out.append(cur.decode('utf-8','replace'))
            cur = bytearray()
    if len(cur) >= min_len:
        out.append(cur.decode('utf-8','replace'))
    return out

def evp_bytes_to_key(password: bytes, key_len: int, iv_len: int) -> Tuple[bytes, bytes]:
    # OpenSSL EVP_BytesToKey with MD5, no salt
    d = b""
    prev = b""
    while len(d) < key_len + iv_len:
        prev = MD5.new(prev + password).digest()
        d += prev
    return d[:key_len], d[key_len:key_len+iv_len]

def aes_try(cipher: AES, blob: bytes) -> bytes:
    try:
        return cipher.decrypt(blob)
    except Exception:
        return b""

def sha256_key_iv(pwd: bytes, keylen=32, ivlen=16) -> Tuple[bytes,bytes]:
    h = hashlib.sha256(pwd).digest()
    key = (h * ((keylen+31)//32))[:keylen]
    iv = hashlib.md5(pwd).digest()[:ivlen]
    return key, iv

def variants(s: str) -> Iterable[str]:
    s = s.strip()
    base = s.strip('"').strip("'")
    us = base.replace(" ", "_")
    su = base.replace("_", " ")
    yield base
    yield base.lower()
    yield base.upper()
    yield base.title()
    yield us
    yield su
    yield su.lower()
    yield su.upper()
    yield us.lower()
    yield us.upper()
    # with quotes (sometimes used in clues)
    yield f'"{base}"'
    yield f"'{base}'"

# ---------- recipes to try ----------
def try_all(pwd: str, blob: bytes) -> Iterable[Tuple[str, bytes]]:
    p = pwd.encode()
    # 1) EVP_BytesToKey (MD5) → AES-256/128-CBC (no salt)
    for bits in (256, 128):
        klen = bits//8
        key, iv = evp_bytes_to_key(p, klen, 16)
        c = AES.new(key, AES.MODE_CBC, iv)
        out = aes_try(c, blob)
        if out:
            yield (f"EVP_MD5_AESCBC_{bits}", out)

    # 2) PBKDF2-HMAC-SHA256 → AES-256-CBC (common iters)
    for iters in (1000, 2048, 4096, 10000, 65536, 100000):
        key_iv = PBKDF2(p, b"", dkLen=48, count=iters, hmac_hash_module=SHA256)  # 32+16
        key, iv = key_iv[:32], key_iv[32:48]
        try:
            c = AES.new(key, AES.MODE_CBC, iv)
            out = aes_try(c, blob)
            if out:
                yield (f"PBKDF2_SHA256_{iters}_AESCBC_256", out)
        except Exception:
            pass

    # 3) Raw SHA256 → AES-256-CTR/ECB (Hail Marys)
    key, iv = sha256_key_iv(p, 32, 16)
    try:
        c = AES.new(key, AES.MODE_CTR, nonce=b"", initial_value=int.from_bytes(iv,'big'))
        out = aes_try(c, blob)
        if out:
            yield ("SHA256_KEY_AESCTR", out)
    except Exception:
        pass
    try:
        c = AES.new(key, AES.MODE_ECB)
        out = aes_try(c, blob)
        if out:
            yield ("SHA256_KEY_AESECB", out)
    except Exception:
        pass

def write_attempt(outdir: Path, name: str, payload: bytes):
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / f"{name}.bin").write_bytes(payload)
    # strings dump
    seqs = printable_sequences(payload, 12)
    if seqs:
        (outdir / f"{name}.strings.txt").write_text("\n".join(seqs), encoding="utf-8")
    # hex head
    (outdir / f"{name}.head.hex").write_text(binascii.hexlify(payload[:256]).decode(), encoding="utf-8")

# ---------- main ----------
def main():
    ap = argparse.ArgumentParser(description="Try password phrase(s) against encrypted blob(s).")
    ap.add_argument("--password", help="Single candidate password string")
    ap.add_argument("--password-file", help="File of candidate passwords (one per line)")
    ap.add_argument("--inline-b64", help="Blob as base64 string (instead of files)")
    ap.add_argument("files", nargs="*", help="Blob files (raw or base64)")
    ap.add_argument("--out", default="pwtest_out", help="Output directory")
    args = ap.parse_args()

    if not args.password and not args.password_file:
        print("Provide --password or --password-file", file=sys.stderr)
        sys.exit(1)

    blobs: list[Tuple[str, bytes]] = []
    if args.inline_b64:
        blobs.append(("inline_b64", base64.b64decode(args.inline_b64)))
    for f in args.files:
        p = Path(f)
        if not p.exists():
            print(f"[warn] missing file: {p}", file=sys.stderr)
            continue
        raw = p.read_bytes()
        blob = b64_maybe_decode(raw)
        blobs.append((p.name, blob))

    if not blobs:
        print("No blobs supplied.", file=sys.stderr)
        sys.exit(1)

    # collect passwords
    pwds = []
    if args.password:
        pwds.append(args.password)
    if args.password_file:
        for line in Path(args.password_file).read_text(encoding="utf-8", errors="ignore").splitlines():
            s = line.strip()
            if s: pwds.append(s)

    outroot = Path(args.out)
    attempts = 0
    hits = 0

    for pw in pwds:
        tried = set()
        for v in variants(pw):
            if v in tried: 
                continue
            tried.add(v)
            for blob_name, blob in blobs:
                attempts += 1
                outdir = outroot / f"{blob_name}__{re.sub('[^A-Za-z0-9]+','_', v)[:60]}"
                any_hit = False
                for tag, dec in try_all(v, blob):
                    # quick sanity: does it look like compressed/zip/png/text?
                    seqs = printable_sequences(dec, 16)
                    if seqs:
                        any_hit = True
                        write_attempt(outdir, f"{tag}", dec)
                if any_hit:
                    hits += 1
                    print(f"[+] Possible hit for '{v}' on {blob_name} → see {outdir}")
    print(f"\nDone. Attempts={attempts}, blobs={len(blobs)}, password_bases={len(pwds)}, hits={hits}")
    print(f"Outputs under: {outroot.resolve()}")

if __name__ == "__main__":
    main()
