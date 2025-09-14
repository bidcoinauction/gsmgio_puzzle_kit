#!/usr/bin/env python3
from PIL import Image
import numpy as np
import sys

# Load full-res puzzle, no resizing yet
def load_rgb(path):
    return np.array(Image.open(path).convert("RGB"))

# Binarize to 1 where “black or blue”, else 0
def binarize(img):
    is_black = (img[:,:,0]==0) & (img[:,:,1]==0) & (img[:,:,2]==0)
    is_blue  = (img[:,:,0]==0) & (img[:,:,1]==0) & (img[:,:,2]==255)
    return (is_black | is_blue).astype(np.uint8)

A_full = load_rgb("puzzle.png")
B_full = load_rgb("puzzle_alt.jpg")

# assume A_full and B_full are same shape
H, W, _ = A_full.shape
A_bin = binarize(A_full)
B_bin = binarize(B_full)
C_bin = A_bin ^ B_bin

# Find the minimal row/col range in C_bin that contains ANY 1s
rows = np.any(C_bin, axis=1)
cols = np.any(C_bin, axis=0)
r0, r1 = np.where(rows)[0][[0, -1]]
c0, c1 = np.where(cols)[0][[0, -1]]

# We expect exactly a 14×14 block:
if (r1-r0+1)!=14 or (c1-c0+1)!=14:
    print(f"⚠️ Detected block is {r1-r0+1}×{c1-c0+1}, not 14×14. Check your images.")
    print(f"Row span: {r0}–{r1}, Col span: {c0}–{c1}")
    sys.exit(1)

print(f"✅ 14×14 block found at pixel rows {r0}–{r1}, cols {c0}–{c1}")

# Crop out that 14×14 region from C_bin
block = C_bin[r0:r1+1, c0:c1+1]
# Now you have your 14×14 bitmask in `block`

# Spiral‐read it:
def spiral_ccw(n):
    top, left, bottom, right = 0, 0, n-1, n-1
    while left<=right and top<=bottom:
        for c in range(left, right+1):      yield top, c
        top += 1
        for r in range(top, bottom+1):      yield r, right
        right -= 1
        if top>bottom or left>right: break
        for c in range(right, left-1, -1):  yield bottom, c
        bottom -= 1
        for r in range(bottom, top-1, -1):  yield r, left
        left += 1

bits = []
for r,c in spiral_ccw(14):
    bits.append(int(block[r,c]))

# Pack bits into bytes
data = bytearray()
for i in range(0,len(bits),8):
    byte = 0
    for b in bits[i:i+8]:
        byte = (byte<<1)|b
    data.append(byte)

print("Hex →", data.hex())
try:
    print("ASCII→", data.decode("ascii"))
except:
    print("ASCII →", data.decode("ascii","ignore"))
