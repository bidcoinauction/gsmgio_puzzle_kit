#!/usr/bin/env python3
import sys
from PIL import Image

def load_bitgrid(path):
    im = Image.open(path).convert("L")
    w, h = im.size
    grid = []
    for y in range(h):
        row = []
        for x in range(w):
            row.append(1 if im.getpixel((x, y)) < 128 else 0)
        grid.append(row)
    return grid

def xor_grids(A, B):
    return [[A[r][c] ^ B[r][c] for c in range(len(A[0]))] for r in range(len(A))]

def spiral_ccw_coords(h, w):
    top, bottom, left, right = 0, h-1, 0, w-1
    coords = []
    while top <= bottom and left <= right:
        for r in range(top, bottom+1): coords.append((r, left))
        left += 1
        if left > right: break
        for c in range(left, right+1): coords.append((bottom, c))
        bottom -= 1
        if top > bottom: break
        for r in range(bottom, top-1, -1): coords.append((r, right))
        right -= 1
        if left > right: break
        for c in range(right, left-1, -1): coords.append((top, c))
        top += 1
    return coords

def main(img1, img2):
    A = load_bitgrid(img1)
    B = load_bitgrid(img2)
    if len(A)!=len(B) or len(A[0])!=len(B[0]):
        print("⚠️ Dimension mismatch"); sys.exit(1)
    G = xor_grids(A, B)
    coords = spiral_ccw_coords(len(G), len(G[0]))
    bits = [G[r][c] for r,c in coords[:196]]
    bitstr = ''.join(str(b) for b in bits)
    data = int(bitstr, 2).to_bytes((len(bitstr)+7)//8, 'big')
    print(data.hex())
    try:
        print(data.decode('ascii'))
    except:
        pass

if __name__=="__main__":
    if len(sys.argv)!=3:
        print("Usage: importimage_fixed.py puzzle.png puzzle_inv.png")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
