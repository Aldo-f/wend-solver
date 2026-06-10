"""
Wend Solver — Educational implementation
Solves LinkedIn Wend puzzles using exact cover (Algorithm X / DLX).
Not for automated gameplay on LinkedIn.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Set, Dict, Optional
from collections import defaultdict

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

Coord = Tuple[int, int]  # (row, col)


@dataclass
class WendPuzzle:
    """A Wend grid puzzle."""
    grid: List[List[str]]          # '.' = empty tile, 'W' = wall, letter = letter
    word_lengths: List[int] = field(default_factory=lambda: [3, 4, 5, 6])

    @property
    def rows(self) -> int:
        return len(self.grid)

    @property
    def cols(self) -> int:
        return len(self.grid[0]) if self.grid else 0

    def is_wall(self, r: int, c: int) -> bool:
        return self.grid[r][c] == 'W'

    def letter_at(self, r: int, c: int) -> str:
        return self.grid[r][c]

    def all_tiles(self) -> List[Coord]:
        return [(r, c) for r in range(self.rows)
                for c in range(self.cols) if not self.is_wall(r, c)]

    def neighbors(self, r: int, c: int) -> List[Coord]:
        """Orthogonal neighbors (up/down/left/right), excluding walls."""
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        result = []
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols and not self.is_wall(nr, nc):
                result.append((nr, nc))
        return result


@dataclass
class WordPath:
    """A valid word with its traced path through the grid."""
    word: str
    path: List[Coord]  # ordered list of coordinates

    def length(self) -> int:
        return len(self.word)

    def tile_set(self) -> Set[Coord]:
        return set(self.path)

    def covers(self, tile: Coord) -> bool:
        return tile in self.tile_set()


# ---------------------------------------------------------------------------
# Trie for dictionary lookup
# ---------------------------------------------------------------------------

class TrieNode:
    __slots__ = ('children', 'is_word')
    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = {}
        self.is_word = False


class Trie:
    """Prefix tree for fast dictionary lookups during path enumeration."""

    def __init__(self, words: List[str]):
        self.root = TrieNode()
        for w in words:
            self.insert(w.upper())

    def insert(self, word: str):
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.is_word = True

    def is_prefix(self, s: str) -> bool:
        node = self.root
        for ch in s:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return True

    def is_word(self, s: str) -> bool:
        node = self.root
        for ch in s:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.is_word


# ---------------------------------------------------------------------------
# Path enumerator
# ---------------------------------------------------------------------------

def enumerate_paths(puzzle: WendPuzzle, trie: Trie,
                    min_len: int = 3, max_len: int = 6) -> List[WordPath]:
    """
    DFS from every tile, collecting all valid dictionary words
    that can be traced through orthogonal paths.
    """
    results: List[WordPath] = []
    max_len = min(max_len, puzzle.rows * puzzle.cols)

    def dfs(path: List[Coord], visited: Set[Coord]):
        if len(path) > max_len:
            return
        current_word = ''.join(puzzle.letter_at(r, c) for r, c in path)

        # Prune: if not a prefix of any dictionary word
        if not trie.is_prefix(current_word):
            return

        # Record if it's a complete word of valid length
        if len(path) >= min_len and trie.is_word(current_word):
            results.append(WordPath(word=current_word, path=list(path)))

        # Extend path
        r, c = path[-1]
        for nr, nc in puzzle.neighbors(r, c):
            if (nr, nc) not in visited:
                visited.add((nr, nc))
                path.append((nr, nc))
                dfs(path, visited)
                path.pop()
                visited.discard((nr, nc))

    for tile in puzzle.all_tiles():
        dfs([tile], {tile})

    return results


def group_by_length(paths: List[WordPath]) -> Dict[int, List[WordPath]]:
    groups: Dict[int, List[WordPath]] = defaultdict(list)
    for wp in paths:
        groups[wp.length()].append(wp)
    return dict(groups)


# ---------------------------------------------------------------------------
# Exact Cover (Algorithm X)
# ---------------------------------------------------------------------------

def solve_exact_cover(
    all_tiles: Set[Coord],
    word_lengths: List[int],
    paths_by_length: Dict[int, List[WordPath]]
) -> Optional[List[WordPath]]:
    """
    Find a set of paths (one per word_length) that covers all tiles exactly once.
    Uses backtracking with constraint propagation.
    """
    solution: List[WordPath] = []
    uncovered_tiles = set(all_tiles)

    def backtrack(length_idx: int) -> bool:
        nonlocal uncovered_tiles
        # Check if we've assigned all word lengths
        if length_idx == len(word_lengths):
            return len(uncovered_tiles) == 0

        target_len = word_lengths[length_idx]
        candidates = paths_by_length.get(target_len, [])

        # Heuristic: sort candidates by how well they match remaining tiles
        def score(wp: WordPath) -> float:
            covered = wp.tile_set() & uncovered_tiles
            return len(covered) / len(wp.path) if wp.path else 0

        candidates.sort(key=score, reverse=True)

        for wp in candidates:
            wp_tiles = wp.tile_set()
            if not wp_tiles.issubset(uncovered_tiles):
                continue

            solution.append(wp)
            uncovered_tiles -= wp_tiles

            if backtrack(length_idx + 1):
                return True

            uncovered_tiles |= wp_tiles
            solution.pop()

        return False

    if backtrack(0):
        return solution
    return None


# ---------------------------------------------------------------------------
# High-level solver
# ---------------------------------------------------------------------------

def solve_wend(puzzle: WendPuzzle, dictionary: List[str]) -> Optional[List[WordPath]]:
    """
    Solve a Wend puzzle given the grid and a dictionary.

    Returns a list of 4 WordPath objects (3,4,5,6 letters) or None if unsolvable.
    """
    trie = Trie(dictionary)
    all_paths = enumerate_paths(puzzle, trie)
    grouped = group_by_length(all_paths)

    print(f"Enumerated paths: 3={len(grouped.get(3, []))}, "
          f"4={len(grouped.get(4, []))}, 5={len(grouped.get(5, []))}, "
          f"6={len(grouped.get(6, []))}")

    solution = solve_exact_cover(
        all_tiles=set(puzzle.all_tiles()),
        word_lengths=puzzle.word_lengths,
        paths_by_length=grouped
    )

    return solution


# ---------------------------------------------------------------------------
# Pretty printer
# ---------------------------------------------------------------------------

def print_solution(puzzle: WendPuzzle, solution: List[WordPath]):
    """Print the solution grid with color-coded word paths."""
    if not solution:
        print("No solution found.")
        return

    print("\n=== Wend Solution ===\n")
    # Assign each word a distinct color label
    color_names = ["RED", "GREEN", "BLUE", "YELLOW"]
    tile_map: Dict[Coord, str] = {}
    for wp, color in zip(solution, color_names):
        for (r, c) in wp.path:
            tile_map[(r, c)] = f"{color}({wp.word})"

    for r in range(puzzle.rows):
        row_parts = []
        for c in range(puzzle.cols):
            if puzzle.is_wall(r, c):
                row_parts.append(" WALL ")
            elif (r, c) in tile_map:
                row_parts.append(f" {puzzle.letter_at(r,c)}    ")
            else:
                row_parts.append(f" {puzzle.letter_at(r,c)}    ")
        print(" ".join(row_parts))

    print("\nWords found:")
    for wp in solution:
        print(f"  [{len(wp.word)}] {wp.word}: {wp.path}")


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Demo: Synthetic 2x3 grid, two disjoint 3-letter words: RUN + FUN
    puzzle = WendPuzzle(grid=[
        ['R', 'U', 'N'],
        ['F', 'U', 'N'],
    ], word_lengths=[3, 3])

    sample_dict = ["RUN", "FUN", "FUR", "RUF"]

    sol = solve_wend(puzzle, sample_dict)
    if sol:
        print_solution(puzzle, sol)
    else:
        print("No solution found.")
