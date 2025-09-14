from pathlib import Path
import itertools

# Input file (from stage2_results/ascii_sequences.txt)
SEQ_FILE = "stage2_results/ascii_sequences.txt"
OUTDIR = Path("matrix_results")
OUTDIR.mkdir(exist_ok=True)

# ----------------------------------------------------
# Load sequences from ascii_sequences.txt
# ----------------------------------------------------
sequences = []
with open(SEQ_FILE) as f:
    for line in f:
        # line format: 0000002c: xGth
        if ":" in line:
            parts = line.strip().split(":", 1)
            seq = parts[1].strip()
            if seq:
                sequences.append(seq)

print(f"[+] Loaded {len(sequences)} sequences")
for s in sequences:
    print(s)

# ----------------------------------------------------
# Pad sequences to equal length
# ----------------------------------------------------
max_len = max(len(s) for s in sequences)
grid = [list(s.ljust(max_len)) for s in sequences]

print(f"[+] Grid size: {len(grid)} x {max_len}")

def save_variant(name, text):
    out_file = OUTDIR / f"{name}.txt"
    out_file.write_text(text)
    print(f"[+] Saved {name} to {out_file}")

# ----------------------------------------------------
# 1. Column-wise reading
# ----------------------------------------------------
cols = []
for col in range(max_len):
    col_str = ''.join(row[col] for row in grid)
    cols.append(col_str)
col_text = '\n'.join(cols)
save_variant("columns", col_text)

# ----------------------------------------------------
# 2. Full column concatenation (no newlines)
# ----------------------------------------------------
concat_cols = ''.join(cols)
save_variant("columns_concat", concat_cols)

# ----------------------------------------------------
# 3. Mirrored grid (horizontal and vertical flips)
# ----------------------------------------------------
def flip_horiz(grid):
    return [list(reversed(row)) for row in grid]

def flip_vert(grid):
    return list(reversed(grid))

flips = {
    "flip_horizontal": flip_horiz(grid),
    "flip_vertical": flip_vert(grid),
    "flip_both": flip_vert(flip_horiz(grid)),
}

for name, g in flips.items():
    cols_flip = []
    for col in range(max_len):
        cols_flip.append(''.join(row[col] for row in g))
    save_variant(f"{name}_cols_concat", ''.join(cols_flip))

# ----------------------------------------------------
# 4. Diagonals (top-left to bottom-right)
# ----------------------------------------------------
def diagonals(g):
    diag_list = []
    rows = len(g)
    cols = len(g[0])
    for start_col in range(cols):
        diag = []
        r, c = 0, start_col
        while r < rows and c < cols:
            diag.append(g[r][c])
            r += 1
            c += 1
        diag_list.append(''.join(diag))
    for start_row in range(1, rows):
        diag = []
        r, c = start_row, 0
        while r < rows and c < cols:
            diag.append(g[r][c])
            r += 1
            c += 1
        diag_list.append(''.join(diag))
    return diag_list

diag_text = '\n'.join(diagonals(grid))
save_variant("diagonals", diag_text)

# ----------------------------------------------------
# 5. All permutations of row order (optional, limited)
# ----------------------------------------------------
# NOTE: Only try small factorial subsets (first 5 rows) to avoid huge output
perm_output = []
rows_to_permute = min(5, len(grid))
for perm in itertools.permutations(range(rows_to_permute)):
    permuted = [grid[i] for i in perm] + grid[rows_to_permute:]
    concat = ''.join(''.join(row) for row in permuted)
    perm_output.append(concat)

(OUTDIR / "row_permutations_preview.txt").write_text('\n'.join(perm_output[:50]))
print("[+] Previewed first 50 row permutations")

print("[*] Matrix analysis complete. Check matrix_results/ for variants.")
