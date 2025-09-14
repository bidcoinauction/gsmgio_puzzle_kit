#!/usr/bin/env python3
from PIL import Image
import numpy as np
import sys

GRID_SIZE = 14

def img_to_bits(path, invert=False, crop_box=None):
    """Load, (optionally) crop, resize to 14×14, map black/blue→1, white/yellow→0."""
    im = Image.open(path).convert("RGB")
    if crop_box:
        im = im.crop(crop_box)
    im = im.resize((GRID_SIZE, GRID_SIZE), Image.NEAREST)
    arr = np.array(im)
    is_black_or_blue = (
        (arr[:,:,0]==0) & (arr[:,:,1]==0) & (arr[:,:,2]==0)
    ) | (
        (arr[:,:,0]==0) & (arr[:,:,1]==0) & (arr[:,:,2]==255)
    )
    bits = is_black_or_blue.astype(int)
    if invert:
        bits = 1 - bits
    return bits

def show(grid, name):
    print(f"\n{name}:")
    for row in grid:
        print("".join("█" if b else " " for b in row))

def spiral_ccw(n):
    """
    Generate (r,c) coordinates for an n×n counter-clockwise spiral,
    starting at (0,0), moving right first.
    """
    seen = [[False]*n for _ in range(n)]
    # directions in CCW order: right → down → left → up
    drc = [(0,1),(1,0),(0,-1),(-1,0)]
    r = c = di = 0
    for _ in range(n*n):
        yield r,c
        seen[r][c] = True
        # try turning left (CCW), i.e. di+1 mod4
        ndi = (di+1) % 4
        nr, nc = r + drc[ndi][0], c + drc[ndi][1]
        if 0 <= nr < n and 0 <= nc < n and not seen[nr][nc]:
            di = ndi
        else:
            nr, nc = r + drc[di][0], c + drc[di][1]
        r, c = nr, nc

def bits_to_bytes(bits):
    b = bytearray()
    for i in range(0, len(bits), 8):
        byte = 0
        for bit in bits[i:i+8]:
            byte = (byte<<1) | bit
        b.append(byte)
    return bytes(b)

def try_mapping(invert):
    A = img_to_bits("puzzle.png", invert=invert)
    B = img_to_bits("puzzle_alt.jpg", invert=invert)
    show(A,   f"Grid A (invert={invert})")
    show(B,   f"Grid B (invert={invert})")

    C = A ^ B
    show(C,   f"XOR A⊕B (invert={invert})")

    # read bits in CCW spiral
    spiral_coords = list(spiral_ccw(GRID_SIZE))
    # sanity check
    if len(spiral_coords) != GRID_SIZE*GRID_SIZE:
        print("❌ Spiral generator length mismatch!")
        sys.exit(1)

    bits = []
    for (r,c) in spiral_coords:
        if not (0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE):
            print(f"❌ Out-of-bounds spiral idx {(r,c)}")
            sys.exit(1)
        bits.append(int(C[r,c]))

    data = bits_to_bytes(bits)
    text = data.decode("ascii", errors="ignore")
    print(f"\n→ invert={invert} → {len(bits)} bits → {len(data)} bytes → ASCII:\n")
    print(text)
    print("\n" + ("─"*60) + "\n")

if __name__ == "__main__":
    for inv in (False, True):
        try_mapping(inv)
