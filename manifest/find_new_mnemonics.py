#!/usr/bin/env python3
"""
window_search.py

Lock positions 0..6 to the stable words, anchor slot 7 to one of a small set,
then sweep overlapping 3-word windows:
(7,8,9) (8,9,10) (9,10,11) (12,13,14) (15,16,17)

Generates candidate mnemonics, optionally filters to valid BIP39 and derives
addresses to search for a target.

Examples
--------
# Minimal: generate candidates only (no derivations), default anchors at pos 7
python window_search.py \
  --base "frost argue mountain chest guilt memory bright initial forward miracle foam charge capital either grant lumber juice because" \
  --out candidates.txt

# Also check BIP39 validity and derive P2PKH index 0 to hunt a match
python window_search.py \
  --base "frost argue mountain chest guilt memory bright initial forward miracle foam charge capital either grant lumber juice because" \
  --derive --target 1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe \
  --out candidates_valid.txt

# Try custom anchor set for slot 7
python window_search.py --base "...18 words..." --anchor7 initial,because,juice,lumber --out cands.txt

"""

import argparse
import itertools
from typing import List, Iterable, Tuple, Set

# Optional: derivation (needs bip-utils installed)
try:
    from bip_utils import (
        Bip39MnemonicValidator, Bip39SeedGenerator,
        Bip44, Bip44Coins, Bip44Changes
    )
    HAVE_BIP = True
except Exception:
    HAVE_BIP = False


LOCK_INDICES = [0,1,2,3,4,5,6]
LOCK_WORDS   = ["frost","argue","mountain","chest","guilt","memory","bright"]

DEFAULT_WINDOWS: List[Tuple[int,int,int]] = [
    (7,8,9),
    (8,9,10),
    (9,10,11),
    (12,13,14),
    (15,16,17),
]

DEFAULT_ANCHORS_7 = ["initial","because","juice","lumber"]


def enforce_locks(words: List[str]) -> List[str]:
    """Ensure LOCK_WORDS are at LOCK_INDICES by swapping as needed."""
    out = words[:]
    for idx, w in zip(LOCK_INDICES, LOCK_WORDS):
        if out[idx] == w:
            continue
        try:
            j = out.index(w)
        except ValueError:
            raise ValueError(f"Locked word '{w}' not found in base mnemonic.")
        out[idx], out[j] = out[j], out[idx]
    return out


def set_anchor_pos7(words: List[str], anchor: str) -> List[str]:
    """Move given anchor word to position 7 (swap with whatever is there)."""
    if words[7] == anchor:
        return words[:]
    try:
        j = words.index(anchor)
    except ValueError:
        raise ValueError(f"Anchor word '{anchor}' not in mnemonic.")
    out = words[:]
    out[7], out[j] = out[j], out[7]
    return out


def permute_window_once(words: List[str], triplet: Tuple[int,int,int]) -> Iterable[List[str]]:
    """Generate all 3! permutations for the 3 indices in 'triplet'."""
    i, j, k = triplet
    trio = [words[i], words[j], words[k]]
    for perm in itertools.permutations(trio):
        if list(perm) == trio:
            # include the original order as well
            yield words[:]
        out = words[:]
        out[i], out[j], out[k] = perm
        yield out


def chain_windows(base_words: List[str], windows: List[Tuple[int,int,int]]) -> Set[str]:
    """Apply each window to all current phrases; dedupe by string."""
    current = {" ".join(base_words)}
    for trip in windows:
        new_set: Set[str] = set()
        for phrase in current:
            ws = phrase.split()
            for w2 in permute_window_once(ws, trip):
                new_set.add(" ".join(w2))
        current = new_set
    return current


def filter_valid_bip39(cands: Iterable[str]) -> List[str]:
    if not HAVE_BIP:
        raise RuntimeError("bip-utils not available; install it or run without --derive/--filter-valid.")
    validator = Bip39MnemonicValidator()
    return [m for m in cands if validator.Validate(m)]


def derive_p2pkh_index0(mnemonic: str) -> str:
    seed = Bip39SeedGenerator(mnemonic).Generate()
    acct = (Bip44.FromSeed(seed, Bip44Coins.BITCOIN)
                .Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT))
    return acct.AddressIndex(0).PublicKey().ToAddress()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="Base 18-word mnemonic to start from.")
    ap.add_argument("--anchor7", default=",".join(DEFAULT_ANCHORS_7),
                    help="Comma-list of anchors to force at position 7.")
    ap.add_argument("--windows", default=";".join(",".join(map(str,w)) for w in DEFAULT_WINDOWS),
                    help="Semicolon-separated list of 3-index windows, e.g. '7,8,9;8,9,10;...'")
    ap.add_argument("--out", required=True, help="Write candidates here.")
    ap.add_argument("--filter-valid", action="store_true", help="Keep only valid BIP39 mnemonics.")
    ap.add_argument("--derive", action="store_true", help="Derive P2PKH index 0 (requires bip-utils).")
    ap.add_argument("--target", default=None, help="If set, stop when derived address equals this.")
    args = ap.parse_args()

    words = args.base.strip().split()
    if len(words) != 18:
        raise SystemExit("Base mnemonic must be exactly 18 words.")

    # Enforce locks 0..6
    words = enforce_locks(words)

    # Parse windows
    windows = []
    for chunk in args.windows.split(";"):
        idxs = [int(x) for x in chunk.split(",") if x.strip()!=""]
        if len(idxs) != 3:
            raise SystemExit(f"Bad window spec: {chunk!r}")
        windows.append(tuple(idxs))

    anchors = [w.strip() for w in args.anchor7.split(",") if w.strip()]
    all_candidates: Set[str] = set()

    for anc in anchors:
        try:
            anchored = set_anchor_pos7(words, anc)
        except ValueError:
            # anchor not in list; skip
            continue
        cset = chain_windows(anchored, windows)
        all_candidates.update(cset)

    # Optional filter to valid BIP39
    cands = sorted(all_candidates)
    if args.filter_valid:
        cands = filter_valid_bip39(cands)

    # Optional derivation / target check
    hit = None
    if args.derive and args.target:
        if not HAVE_BIP:
            raise SystemExit("bip-utils missing. Install it or run without --derive/--target.")
        for m in cands:
            addr = derive_p2pkh_index0(m)
            if addr == args.target:
                hit = m
                break

    # Write
    with open(args.out, "w") as f:
        for m in cands:
            f.write(m + "\n")

    print(f"Wrote {len(cands)} candidates to {args.out}")
    if args.filter_valid:
        print("Filtered to BIP39-valid mnemonics.")
    if args.derive and args.target:
        if hit:
            print(f"🎉 MATCH FOUND for target {args.target}:\n{hit}")
        else:
            print("No target match in this batch (index 0 path).")


if __name__ == "__main__":
    main()
