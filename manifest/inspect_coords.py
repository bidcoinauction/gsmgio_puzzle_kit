GRID = [
  'KBKWBWKKKBWKYK','WKBKWKKWBKKWKW','KWKWKWKKKWKWKK','BKWBKWKWKYKWK',
  'KWKKKWYYWKKWKW','WKBKWKWWWKWKKB','KWKWBWKBWKWKK','KKKKKWKWYKWKW',
  'WKWKYKYWKKKBWK','KBKWKWKWWKKWKY','WKWKBKKWKWKWKK','KWKWKWKYWKBKWK',
  'WKYKWKWKKWKBKW','KKBKWKWYKWKWK'
]

def dump_block(r,c,size=1):
    for dr in range(-size,size+1):
        row_idx = r+dr
        if not (0 <= row_idx < len(GRID)): continue
        line = ""
        for dc in range(-size,size+1):
            col_idx = c+dc
            if not (0 <= col_idx < len(GRID[row_idx])): continue
            line += GRID[row_idx][col_idx]
        print(f"r={row_idx}, cols {c-size}→{c+size}: {line}")
    print()

# Suspect coordinates
print("Around (7,9):")
dump_block(7,9)

print("Around (11,7):")
dump_block(11,7)
