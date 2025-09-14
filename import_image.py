#!/usr/bin/env python3
from PIL import Image
import sys

def image_to_bitgrid(path, threshold=128):
    """Load image, convert to grayscale, then to a 0/1 grid."""
    im = Image.open(path).convert("L")  # Luma (0–255)
    w,h = im.size
    grid = [[0]*w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            grid[y][x] = 1 if im.getpixel((x,y)) < threshold else 0
    return grid

def xor_grids(A, B):
    h,w = len(A), len(A[0])
    assert h == len(B) and w == len(B[0]), "Image sizes must match!"
    return [[ A[y][x] ^ B[y][x] for x in range(w) ] for y in range(h)]

def spiral_ccw(grid, max_bits=None):
    """
    Counter-clockwise spiral from top-left inward.
    Yields (y,x) coordinates.
    """
    h,w = len(grid), len(grid[0])
    top, bottom = 0, h-1
    left,  right  = 0, w-1
    bits = 0
    while left <= right and top <= bottom:
        # bottom row: right → left
        for x in range(right, left-1, -1):
            yield bottom, x
            bits += 1
            if max_bits and bits>=max_bits: return
        bottom -= 1

        # left column: bottom → top
        for y in range(bottom, top-1, -1):
            yield y, left
            bits += 1
            if max_bits and bits>=max_bits: return
        left += 1

        # top row: left → right
        if top <= bottom:
            for x in range(left, right+1):
                yield top, x
                bits += 1
                if max_bits and bits>=max_bits: return
            top += 1

        # right column: top → bottom
        if left <= right:
            for y in range(top, bottom+1):
                yield y, right
                bits += 1
                if max_bits and bits>=max_bits: return
            right -= 1

def extract_and_decode(bitstr):
    # print the first 196 bits
    snippet = bitstr[:196]
    print("Bit-string (196 bits):", snippet)

    # as bytes:
    b = int(snippet, 2).to_bytes(len(snippet)//8, byteorder='big')
    print("Hex:", b.hex())
    try:
        print("ASCII:", b.decode('ascii'))
    except:
        print("ASCII: <non-ASCII bytes>")

if __name__=="__main__":
    if len(sys.argv)!=3:
        print("Usage: importimage.py puzzle.png puzzle_alt.jpg")
        sys.exit(1)

    A = image_to_bitgrid(sys.argv[1])
    B = image_to_bitgrid(sys.argv[2])

    C = xor_grids(A, B)

    # collect bits CCW spiral, cap at 196 if you want exactly that many
    bit_list = []
    for y,x in spiral_ccw(C, max_bits=196):
        bit_list.append(str(C[y][x]))

    bitstr = "".join(bit_list)
    extract_and_decode(bitstr)
