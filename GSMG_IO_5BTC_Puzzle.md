
# GSMG.IO 5 BTC Puzzle — Consolidated Progress & Roadmap

This document summarizes the multi-phase GSMG.IO puzzle leading to a 5 BTC prize. All known cryptographic and steganographic layers are broken down by phase. The current objective is correctly ordering 18 BIP39 mnemonic words derived from a decrypted binary to generate the prize address:

**Target Bitcoin Address: `1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe`**

---

## ✅ Phase 1 — puzzle.png → Spiral → URL
**Goal:** Decode a spiral traversal of a 14×14 color grid into ASCII text.

- Black/blue tiles mapped to 1; yellow/white mapped to 0.
- A hardcoded CCW spiral over the grid yielded 196 bits.
- Converted bits → bytes → ASCII → `gsmg.io/theseedisplanted`

**Status:** ✅ Complete

---

## ✅ Phase 2 — theseedisplanted.png → Hidden POST → AES Blob

**Clue Interpretation:**
- "War" + "ning" and "Lo" + "gic" = Logic's *The Warning*
- Revealed a hidden POST form in page source.

**Action:**
- Submitted: `theflowerblossomsthroughwhatseemstobeaconcretesurface`
- Received: AES-CBC encrypted blob.

**Status:** ✅ Complete

---

## ✅ Phase 3 — Multi-Part AES Decryption Chain

### 🔓 3.1: First Blob → “Causality” Riddle
- Decrypted using `SHA256("causality")`
- Output: 7-part riddle referencing tech, math, and history.

### 🔓 3.2: 7-Part Password → phase3.txt
- Components: `causality`, `Safenet`, `Luna`, `HSM`, `11110`, bitcoin source hex, chess FEN string.
- Concatenated and hashed → next AES key → success.

### 🔓 3.3: Architect Monologue + Beaufort Cipher
- Passphrase from Matrix + physics clues:
  `jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple`
- Decrypted output: long monologue + Beaufort cipher with key `THEMATRIXHASYOU`.

### 🔓 3.4: Final Key → Salphaseion Blob
- Derived password: `lastwordsbeforearchichoice_matrixsumlist_enter_thispassword`
- Decrypted → `salphaseion_decrypted.bin` (1327 bytes, high entropy).

**Status:** ✅ All 3.x phases complete

---

## ✅ Phase 4 — Extract BIP39 Words from salphaseion_decrypted.bin

**Method:**
- Manual grid carving → 13 ASCII-like sequences.
- ROT13 + column concat → 18 two-character pairs (e.g. `kr`, `4E`, `68`).
- Pairs → Base36 → mod 2048 → BIP39 index lookup.

**Extracted Words (Alphabetized):**
```
argue, because, bright, capital, charge, chest, either,
foam, forward, frost, grant, guilt, initial, juice,
lumber, memory, miracle, mountain
```

**Status:** ✅ Complete

---

## ⚠️ Phase 5 — Final Mnemonic Ordering & Address Derivation

**Goal:** Find the correct permutation of the 18 words that:

- ✅ Passes BIP39 checksum
- ✅ Derives Bitcoin address: `1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe`

### 🧪 Attempted Strategy:
- Manhattan-distance-based "Delta-walk" path across ROT13-transformed character grid.
- Yielded valid mnemonic:
```
frost argue mountain chest guilt memory bright juice initial
because lumber grant foam charge either forward capital miracle
```
- ✅ Valid checksum, ❌ No address match

---

## 🧩 Instruction Key Analysis

**String found:** `ksmhse:rfdfuesa`

### ➤ Mapping Method:
```python
def letter_to_index(letter): return ord(letter) - ord('a') % 18

from = 'ksmhse' → [10, 0, 12, 7, 0, 4]
to   = 'rfdfuesa' → [17, 5, 3, 5, 2, 4, 0, 0]
```

### ➤ Reordering:
1. Move `word[from[i]]` → `new[to[i]]`
2. Fill remaining `None` slots with unused words in original order

### ➤ Apply and Validate:
- Reconstruct mnemonic → Check BIP39 validity
- If ✅, derive BIP44 (legacy) address and compare

**Tooling:**
- Scripts now support:
  - Mnemonic checksum validation
  - BIP44/BIP49/BIP84/BIP86 address derivation
  - Brute-force + heuristic reordering
  - Logging all valid mnemonics

---

## 🧠 Overall Roadmap

### ✅ Extraction Complete
- 18 valid words are known and fixed.

### ⚠️ Blocker: Ordering Unknown
- Heuristics have failed so far.
- Likely clue embedded in grid traversal + instruction key.

---

## 🧪 Next Actions

1. **Instruction Key Application:** Use `ksmhse:rfdfuesa` to derive a new candidate word order.
2. **Permutation Solver Script:**
   - Input: 18 words
   - Output: All valid BIP39 permutations
   - Match against prize address.
3. **Heuristic Prioritization:**
   - Small group swaps, spiral-mirroring, entropy weighting.
4. **Audit Log:** Track all valid checksummed mnemonics and derived addresses for transparency.
