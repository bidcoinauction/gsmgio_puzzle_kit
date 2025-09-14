#!/usr/bin/env python3
import cv2
import numpy as np
from sklearn.cluster import KMeans
import argparse
import itertools
import string

GRID_SIZE = 14
QR_REGION = (0.8, 1.0, 0.0, 0.3)

def make_spiral(n):
    dirs = [(0,1),(1,0),(0,-1),(-1,0)]
    seen = [[False]*n for _ in range(n)]
    y = x = di = 0
    for _ in range(n*n):
        yield y, x
        seen[y][x] = True
        dy,dx = dirs[di]
        ny,nx = y+dy, x+dx
        if not (0<=ny<n and 0<=nx<n and not seen[ny][nx]):
            di=(di+1)%4
            dy,dx=dirs[di]
            ny,nx=y+dy,x+dx
        y,x=ny,nx

def auto_crop_bottom(img, frac=0.95):
    return img[:int(img.shape[0]*frac), :]

def load_and_cluster(path, k=4):
    img = cv2.imread(path)
    if img is None: raise FileNotFoundError(path)
    img = auto_crop_bottom(img)
    h,w = img.shape[:2]
    ch, cw = h//GRID_SIZE, w//GRID_SIZE

    avgs = []
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            cell = img[r*ch:(r+1)*ch, c*cw:(c+1)*cw]
            avgs.append(cell.reshape(-1,3).mean(axis=0))
    avgs = np.array(avgs)

    km = KMeans(n_clusters=k, random_state=0).fit(avgs)
    labels = km.labels_.reshape(GRID_SIZE, GRID_SIZE)
    return img, labels, km.cluster_centers_

def decode_with_mapping(labels, ones):
    bits = []
    for y,x in make_spiral(GRID_SIZE):
        bits.append('1' if labels[y,x] in ones else '0')
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        chars.append(chr(int("".join(byte),2)))
    return "".join(chars)

def score_printable(s):
    cnt = sum(1 for ch in s if ch in string.printable and ch not in '\t\n\r\x0b\x0c')
    return cnt/len(s)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("image", help="puzzle PNG to decode")
    p.add_argument("--minscore", type=float, default=0.8,
                   help="min fraction printable to show (0–1)")
    args = p.parse_args()

    img, labels, centers = load_and_cluster(args.image, k=4)
    print("Cluster centroids (B,G,R):")
    for i,c in enumerate(centers):
        print(f"  ID {i}: ({int(c[0])},{int(c[1])},{int(c[2])})")
    ids = list(range(len(centers)))

    print("\nTrying all non-empty, non-full subsets of clusters as “1”…\n")
    for r in range(1, len(ids)):
        for ones in itertools.combinations(ids, r):
            txt = decode_with_mapping(labels, set(ones))
            score = score_printable(txt)
            if score >= args.minscore:
                print(f"  → ones={ones}  printable={score:.2f}  → {txt!r}")

if __name__=="__main__":
    main()
