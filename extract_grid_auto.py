#!/usr/bin/env python3
import cv2
import numpy as np
from sklearn.cluster import KMeans
import argparse, itertools, string

GRID_SIZE = 14
QR_REGION = (0.8, 1.0, 0.0, 0.3)

def make_spiral(n):
    dirs = [(0,1),(1,0),(0,-1),(-1,0)]
    seen = [[False]*n for _ in range(n)]
    y = x = di = 0
    for _ in range(n*n):
        yield y,x
        seen[y][x] = True
        dy,dx = dirs[di]
        ny,nx = y+dy, x+dx
        if not (0<=ny<n and 0<=nx<n and not seen[ny][nx]):
            di=(di+1)%4
            dy,dx=dirs[di]
            ny,nx=y+dy,x+dx
        y,x=ny,nx

def auto_crop(img): return img[:int(img.shape[0]*0.95),:]

def load_and_cluster(path):
    img = cv2.imread(path)
    if img is None: raise FileNotFoundError(path)
    img = auto_crop(img)
    h,w = img.shape[:2]
    ch, cw = h//GRID_SIZE, w//GRID_SIZE

    avgs = []
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            cell = img[r*ch:(r+1)*ch, c*cw:(c+1)*cw]
            avgs.append(cell.reshape(-1,3).mean(axis=0))
    avgs = np.array(avgs)

    km = KMeans(n_clusters=4, random_state=0).fit(avgs)
    labels = km.labels_.reshape(GRID_SIZE,GRID_SIZE)
    return labels, km.cluster_centers_

def decode(labels, ones):
    bits = ['1' if labels[y,x] in ones else '0'
            for y,x in make_spiral(GRID_SIZE)]
    chars = [chr(int(''.join(bits[i:i+8]),2))
             for i in range(0,len(bits),8)]
    return ''.join(chars)

def score(s):
    good = sum(1 for ch in s if ch in string.printable and ch not in '\r\n\t')
    return good/len(s)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("image")
    p.add_argument("--minscore",type=float,default=0.75)
    args=p.parse_args()

    labels, centers = load_and_cluster(args.image)
    ids = list(range(len(centers)))
    print("Clusters (B,G,R):")
    for i,c in enumerate(centers):
        print(f"  {i}: ({int(c[0])},{int(c[1])},{int(c[2])})")

    print("\nTrying subsets as ‘1’ (printable≥%.2f)…\n" % args.minscore)
    for r in range(1,len(ids)):
        for ones in itertools.combinations(ids,r):
            txt = decode(labels,set(ones))
            sc = score(txt)
            if sc>=args.minscore:
                print(f"ones={ones} score={sc:.2f} → {txt!r}")

if __name__=="__main__":
    main()
