# GSMG Puzzle Movement Pattern Analysis

## Overview
This document catalogs all the movement patterns and traversal methods that have been implemented in the GSMG puzzle solving attempts, and identifies potential missing patterns.

## Implemented Movement Patterns

### 1. Basic Grid Traversals
- **Row-major**: Left-to-right, top-to-bottom
- **Column-major**: Top-to-bottom, left-to-right  
- **Diagonal**: Based on (row+col) sum
- **Reverse orderings**: All above patterns in reverse

### 2. Spiral Patterns
- **Counter-clockwise spiral**: From center outward
- **Clockwise spiral**: From center outward
- **Outer-to-inner spiral**: From edges toward center
- **Spiral with different starting points**: Various center positions

### 3. Distance-Based Patterns
- **Euclidean distance**: Closest neighbor traversal
- **Manhattan distance**: L1 norm closest neighbor
- **Distance from center**: Sort by distance from grid center
- **Distance from corners**: Sort by distance from specific corners

### 4. Coordinate-Based Patterns
- **Sort by row, then column**: (r,c) ordering
- **Sort by column, then row**: (c,r) ordering
- **Sort by coordinate sum**: (r+c) ordering
- **Sort by coordinate product**: (r*c) ordering

### 5. Value-Based Patterns
- **Base36 pair values**: Sort by numerical value of pairs
- **ASCII values**: Sort by character codes
- **BIP39 indices**: Sort by wordlist position

### 6. Advanced Traversal Patterns
- **Zigzag**: Alternating row directions
- **Snake pattern**: S-shaped traversal
- **Mirrored patterns**: Y-axis mirroring
- **Josephus-style**: Skip-counting traversal

### 7. Delta-Based Patterns
- **Delta walking**: Following specific step sequences
- **Offset-based**: Using predefined offsets
- **Weighted deltas**: Delta values with weights

### 8. Color-Based Patterns
- **Blue path traversal**: Following blue squares only
- **Yellow path traversal**: Following yellow squares only
- **Color alternation**: Blue-yellow-blue pattern
- **Color concatenation**: All blue then all yellow

### 9. Matrix-Based Patterns
- **Column extraction**: Reading matrix columns
- **Row extraction**: Reading matrix rows
- **Diagonal extraction**: Reading matrix diagonals
- **Transpose operations**: Matrix transposition

### 10. Permutation-Based Patterns
- **From-to mapping**: Specific index reordering
- **Instruction key parsing**: Using decoded instructions
- **Pattern-based backtracking**: N-gram frequency guided

## Potentially Missing Movement Patterns

### 1. Wave Patterns
- **Sine wave traversal**: Following sine wave path
- **Cosine wave traversal**: Following cosine wave path
- **Square wave**: Alternating between two levels
- **Sawtooth wave**: Linear increase with sudden drops

### 2. Fractal Patterns
- **Hilbert curve**: Space-filling curve
- **Peano curve**: Another space-filling curve
- **Sierpinski triangle**: Fractal-based traversal
- **Mandelbrot set**: Complex number based

### 3. Geometric Patterns
- **Circle traversal**: Following circular paths
- **Ellipse traversal**: Following elliptical paths
- **Parabola traversal**: Following parabolic curves
- **Hyperbola traversal**: Following hyperbolic curves

### 4. Number Theory Patterns
- **Prime number sequence**: Using prime positions
- **Fibonacci sequence**: Using Fibonacci positions
- **Pascal's triangle**: Using triangle positions
- **Golden ratio**: Using φ-based positioning

### 5. Cryptographic Patterns
- **Hash-based ordering**: Using hash values for ordering
- **XOR patterns**: Using XOR operations
- **Modular arithmetic**: Using modulo operations
- **Bit manipulation**: Using bit operations

### 6. Physics-Based Patterns
- **Gravity simulation**: Simulating gravitational attraction
- **Magnetic field**: Following magnetic field lines
- **Wave interference**: Simulating wave patterns
- **Particle motion**: Simulating particle trajectories

### 7. Game Theory Patterns
- **Chess piece moves**: Knight's tour, queen's moves
- **Checkers patterns**: Diagonal jumping
- **Go patterns**: Stone placement patterns
- **Maze solving**: Wall-following algorithms

### 8. Biological Patterns
- **DNA helix**: Following double helix structure
- **Protein folding**: Following folding patterns
- **Neural network**: Following neural pathways
- **Evolutionary**: Genetic algorithm patterns

### 9. Musical Patterns
- **Musical scales**: Following scale patterns
- **Rhythm patterns**: Following beat patterns
- **Harmony progressions**: Following chord progressions
- **Melodic contours**: Following pitch contours

### 10. Linguistic Patterns
- **Word frequency**: Using word frequency data
- **Phonetic patterns**: Using phonetic similarity
- **Semantic patterns**: Using word relationships
- **Morphological patterns**: Using word structure

## Recommendations for New Implementations

### High Priority
1. **Hilbert Curve**: Space-filling curve that might match the puzzle's structure
2. **Chess Knight's Tour**: Classic traversal pattern
3. **Hash-based Ordering**: Using cryptographic hash of coordinates
4. **Musical Scale Patterns**: Following musical intervals

### Medium Priority
1. **Wave Patterns**: Sine/cosine wave traversals
2. **Fractal Patterns**: Self-similar structures
3. **Physics Simulations**: Gravity or magnetic field patterns
4. **Number Theory**: Prime or Fibonacci sequences

### Low Priority
1. **Biological Patterns**: DNA or protein folding
2. **Game Theory**: Advanced chess patterns
3. **Linguistic Patterns**: Word relationship based
4. **Cryptographic**: Advanced crypto operations

## Implementation Strategy

1. **Start with Hilbert Curve**: Most likely to match grid-based puzzles
2. **Try Chess Patterns**: Classic and well-studied
3. **Implement Hash-based**: Simple but effective
4. **Add Wave Patterns**: Mathematical and systematic

## Next Steps

1. Implement the high-priority missing patterns
2. Test each pattern systematically
3. Document results and success rates
4. Iterate based on findings
