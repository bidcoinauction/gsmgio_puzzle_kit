#!/usr/bin/env python3
import sys

# load the clean bit-stream
bits = open('bits196.txt').read().strip()
if len(bits) != 196:
    print("⚠️ bits196.txt length is", len(bits))
    sys.exit(1)

# two mappings to try:
for name, mapping in (("1→·,0→–",   {"1":"·","0":"–"}),
                      ("1→–,0→·",   {"1":"–","0":"·"})):
    morse = "".join(mapping[b] for b in bits)
    print(f"\n=== Mapping: {name} ===\n")
    # break into “words” at long runs of – (e.g. 7 or more)
    # then break each word at runs of 3 or more for letters
    import re
    chunks = re.split(r'(–{7,})', morse)
    for chunk in chunks:
        if chunk.startswith('–'*7):
            print(" [🏷 word-gap ] ")
        else:
            # split on letter-gaps of 3 or more
            letters = re.split(r'(–{3,})', chunk)
            line = []
            for l in letters:
                if l.startswith('–'*3):
                    line.append(" / ")
                else:
                    line.append(l)
            print("".join(line))
    print("\n" + "-"*60)
