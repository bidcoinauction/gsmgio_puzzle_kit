#!/usr/bin/env python3
import sys
from PIL import Image

def load_bitgrid(path):
    """Load image, threshold to a 2D list of 0/1 bits (white→0, black→1)."""
    im = Image.open(path).convert("L")
    w, h = im.size
    grid = []
    for y in range(h):
        row = []
        for x in range(w):
            # threshold at 128: darker is "1"
            row.append(1 if im.getpixel((x, y)) < 128 else 0)
        grid.append(row)
    return grid

def xor_grids(A, B):
    h = len(A)
    w = len(A[0])
    return [[A[r][c] ^ B[r][c] for c in range(w)] for r in range(h)]

def spiral_ccw_coords(h, w):
    """Generate all (r,c) coords in a counter-clockwise inward spiral."""
    top, bottom, left, right = 0, h-1, 0, w-1
    coords = []
    while top <= bottom and left <= right:
        # go down along left
        for r in range(top, bottom+1):
            coords.append((r, left))
        left += 1
        if left > right: break
        # go right along bottom
        for c in range(left, right+1):
            coords.append((bottom, c))
        bottom -= 1
        if top > bottom: break
        # go up along right
        for r in range(bottom, top-1, -1):
            coords.append((r, right))
        right -= 1
        if left > right: break
        # go left along top
        for c in range(right, left-1, -1):
            coords.append((top, c))
        top += 1
    return coords

def main(img1_path, img2_path):
    A = load_bitgrid(img1_path)
    B = load_bitgrid(img2_path)
    if len(A)!=len(B) or len(A[0])!=len(B[0]):
        print("⚠️ Image dimensions differ!", len(A), len(A[0]), len(B), len(B[0]))
        sys.exit(1)

    G = xor_grids(A, B)
    h, w = len(G), len(G[0])
    coords = spiral_ccw_coords(h, w)
    bits = [ G[r][c] for (r,c) in coords[:196] ]  # take exactly 196 bits

    # pack bits to bytes
    bitstr = ''.join(str(b) for b in bits)
    data = int(bitstr, 2).to_bytes((len(bitstr)+7)//8, byteorder='big')

    print("▶ Hex (196 bits → 25 bytes):")
    print(data.hex())
    try:
        txt = data.decode('ascii')
        print("\n▶ ASCII:")
        print(txt)
    except UnicodeDecodeError:
        print("\n▶ ASCII: (non-printable bytes present)")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: importimage_fixed.py puzzle.png puzzle_inv.png")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
