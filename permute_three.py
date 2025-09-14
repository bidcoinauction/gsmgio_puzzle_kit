#!/usr/bin/env python3
"""
permute_three.py

Given a single 18-word base mnemonic (or a file of them), lock any positions you
trust, then generate all 3-way permutations of the remaining slots.

Usage:
  # Single mnemonic on the command line, locking positions 0,5,12:
  python permute_three.py \
    --base "w1 w2 … w18" \
    --lock 0,5,12 \
    --out candidates.txt

  # Or process a file of base mnemonics (one per line):
  python permute_three.py \
    --input bases.txt \
    --lock 0,5,12 \
    --out candidates.txt

Each candidate will vary only three unlocked positions at a time, permuting their
words among themselves (6 arrangements per triplet).
"""

import argparse
import itertools
import sys

def load_bases(args):
    if args.base:
        return [args.base.split()]
    else:
        with open(args.input, 'r') as f:
            return [line.strip().split() for line in f if line.strip()]

def main():
    p = argparse.ArgumentParser()
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument('--base', help='One 18-word mnemonic in quotes')
    group.add_argument('--input', help='File of base mnemonics (one per line)')
    p.add_argument('--lock', required=True,
                   help='Comma-separated zero-based indices to lock in place')
    p.add_argument('--out', required=True, help='Write candidates here')
    args = p.parse_args()

    locked = sorted(int(i) for i in args.lock.split(','))
    bases = load_bases(args)

    with open(args.out, 'w') as fout:
        for words in bases:
            if len(words) != 18:
                print(f"Skipping (not 18 words): {' '.join(words)}", file=sys.stderr)
                continue

            # determine unlocked positions
            all_idx = set(range(18))
            free_idx = sorted(all_idx - set(locked))
            # for every triplet of free positions
            for triplet in itertools.combinations(free_idx, 3):
                # the three words currently at those positions
                original = [words[i] for i in triplet]
                # permute them
                for perm in itertools.permutations(original):
                    candidate = list(words)
                    # place permuted words back into those slots
                    for pos, w in zip(triplet, perm):
                        candidate[pos] = w
                    fout.write(" ".join(candidate) + "\n")

    print(f"Wrote {args.out} with all 3-swap variants "
          f"locking positions {locked}")

if __name__ == "__main__":
    main()
