#!/usr/bin/env python3
import sys
from PIL import Image

def image_to_bits(path):
    im = Image.open(path).convert("RGB")
    W, H = im.size
    # assume 14×14 grid centered (you may need to crop/mask to exactly the puzzle area)
    # here we just sample a 14×14 grid evenly across the image
    bx = W // 14
    by = H // 14
    bits = []
    for row in range(14):
        bits_row = []
        for col in range(14):
            x = col * bx + bx//2
            y = row * by + by//2
            r,g,b = im.getpixel((x,y))
            # treat “dark” as 1, else 0
            bits_row.append(1 if (r+g+b)/3 < 128 else 0)
        bits.append(bits_row)
    return bits

def spiral_ccw(n):
    seen = [[False]*n for _ in range(n)]
    dr = [0,1,0,-1]  # down, right, up, left → but we want start at (0,0) going right? adapt as needed
    dc = [1,0,-1,0]
    r = c = di = 0
    for _ in range(n*n):
        yield r,c
        seen[r][c] = True
        nr, nc = r+dr[di], c+dc[di]
        if 0 <= nr < n and 0 <= nc < n and not seen[nr][nc]:
            r, c = nr, nc
        else:
            di = (di+1) % 4
            r += dr[di]; c += dc[di]

def main(orig, inv):
    A = image_to_bits(orig)
    B = image_to_bits(inv)
    # XOR
    C = [[(A[r][c]^B[r][c]) for c in range(14)] for r in range(14)]
    # traverse spiral
    bits = [str(C[r][c]) for r,c in spiral_ccw(14)]
    bstr = "".join(bits)
    data = int(bstr,2).to_bytes((len(bstr)+7)//8, "big")
    print("hex:", data.hex())
    try:
        print("ascii:", data.decode("ascii"))
    except UnicodeDecodeError:
        pass

if __name__=="__main__":
    if len(sys.argv)!=3:
        print("Usage: importimage2.py puzzle.png puzzle_inv.png")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
