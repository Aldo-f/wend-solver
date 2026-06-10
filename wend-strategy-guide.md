# Wend Strategy Guide & Solver Design

## Game Rules Summary

**Wend** is LinkedIn's daily word puzzle (launched June 9, 2026). Key mechanics:

- **Grid**: ~5×5 with letters + gray wall blocks
- **Goal**: Find exactly 4 words (3, 4, 5, 6 letters = 18 letters total)
- **Constraint**: Every non-wall tile used **exactly once** across all 4 words
- **Movement**: Orthogonal only (up/down/left/right), no diagonals
- **Words can bend** 90° mid-path
- **Walls block paths** — route around them
- **Unique solution** per puzzle (walls guarantee this)
- **Hints**: Unlimited, reveal one letter at a time per word
- **Undo**: Unlimited

---

## Core Strategies

### 1. Wall-First Analysis
Walls are the puzzle's "spine" — they dictate valid paths.
- Identify wall-enclosed regions
- Letters in dead-end corridors must belong to words ending there
- Walls split the grid into forced path segments

### 2. Length-Based Deduction
With fixed word lengths (3, 4, 5, 6), use combinatorics:
- **3-letter word**: Shortest path, often in tight spaces
- **6-letter word**: Longest path, likely spans grid or snakes through open areas
- Count available tiles per region → match to word lengths

### 3. Letter Frequency & Word Patterns
- High-frequency letters (E, A, R, I, O, T, N, S) appear in multiple word positions
- Rare letters (Q, X, Z, J) anchor specific words
- Look for common prefixes/suffixes: IN-, UN-, RE-, -ED, -ING, -ER

### 4. Tiling Constraint (Every Letter Once)
This is the key differentiator from Boggle/Strands.
- **No orphan tiles**: Every letter must connect to a word path
- **No overlaps**: A tile used in the 5-letter word cannot be in the 3-letter word
- If a candidate word leaves isolated letters → invalid

### 5. Path Topology
- Words are **simple paths** (no self-intersection, no revisiting tiles)
- Grid is partitioned into 4 disjoint paths covering all letters
- Think of it as: tile the grid with 4 polyomino paths of lengths 3,4,5,6

---

## Step-by-Step Solving Process

```
1. MAP THE GRID
   - Mark walls, label each letter with coordinates
   - Identify connected components (regions separated by walls)

2. CATALOG CANDIDATE WORDS
   - For each region, enumerate all valid dictionary words
   - Filter by length (3/4/5/6) and path constraints
   - Note: words can cross region boundaries if path allows

3. APPLY TILING CONSTRAINT
   - Find set of 4 words (one per length) covering ALL letters exactly once
   - This is an Exact Cover problem → Algorithm X / DLX

4. VALIDATE UNIQUENESS
   - Confirm only one valid tiling exists (walls guarantee this)
   - If multiple → re-check wall constraints

5. EXECUTE IN GAME
   - Trace each word path in order (any order works)
   - Use hints only if stuck on a specific word's start letter
```

---

## Solver Algorithm Design (Educational)

### Problem Formulation
**Exact Cover**: Select 4 paths (one per length) such that every letter tile is covered exactly once.

- Universe U = all non-wall letter tiles (|U| = 18)
- Subsets S = all valid dictionary words that can be traced as orthogonal paths
- Each subset has a "length tag" (3, 4, 5, or 6)
- Constraint: pick exactly 1 subset of each length tag, union = U, disjoint

### Algorithm: DLX (Dancing Links) — Knuth's Algorithm X

```python
# Pseudocode structure
class WendSolver:
    def __init__(self, grid, walls, dictionary):
        self.tiles = [(r,c) for r in rows for c in cols if not walls[r][c]]
        self.dictionary = set(dictionary)
        self.paths_by_length = {3:[], 4:[], 5:[], 6:[]}

    def enumerate_paths(self):
        # DFS from each tile, build all valid words up to length 6
        # Track: current_path, visited_tiles, current_word
        # When word in dictionary and len in [3,4,5,6]: record path
        # Prune: prefix not in dictionary trie → stop

    def build_exact_cover_matrix(self):
        # Rows = valid paths (with length tag)
        # Columns = 18 tiles + 4 length-slots (3,4,5,6)
        # 1 in tile-columns if path covers tile
        # 1 in length-column matching path's length
        # Each solution picks exactly 1 row per length-column, covers all tiles

    def solve(self):
        # Run Algorithm X on matrix
        # Return list of 4 paths (the unique solution)
```

### Complexity
- Grid: 5×5 = 25 cells, ~18 letters
- Paths per tile: branching factor ≤ 4, depth ≤ 6 → manageable
- Dictionary filter (trie) prunes >99% of paths
- Exact cover matrix: ~hundreds of rows × 22 columns → solves in ms

### Optimization: Wall-Aware Pruning
- Pre-compute connected components separated by walls
- Paths cannot cross walls → enumerate per-component, then combine
- Reduces search space dramatically

---

## Example Puzzle Walkthrough (Puzzle #1, June 9, 2026)

Based on published solution:

```
Grid (W=wall, .=letter):
W . . . .
. . W . .
. . . . W
. W . . .
. . . W .
```

**Solution words** (from TechWiser):
- 3-letter: **WIN** (vertical)
- 4-letter: **HOLD** (bends 90°)
- 5-letter: **????** 
- 6-letter: **????**

*Apply the strategy:*
1. Walls create corridors → WIN forced in left column
2. HOLD snakes through middle-top
3. Remaining tiles → deduce 5 & 6 letter words by tiling

---

## Tips for Human Play

| Situation | Strategy |
|-----------|----------|
| Stuck on 6-letter | Find the longest snake path first; it constrains others |
| Isolated letter cluster | Must be a complete word (3 or 4 letters) |
| Two candidate words overlap | Test both; only one allows full tiling |
| Used hint on word start | Now trace all valid paths from that letter |
| Dead-end corridor | Word must END there (cannot pass through) |

---

## Files in This Project

```
/home/aldo/
├── wend-strategy-guide.md    # This file
├── wend_solver.py            # Python solver implementation
└── test_puzzle_1.json        # Puzzle #1 test case
```

---

*Strategy guide compiled from The Word Finder, TechWiser, and game analysis. Solver design for educational purposes only — not for automated gameplay on LinkedIn.*