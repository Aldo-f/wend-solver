"""Unit tests for Wend solver — Trie, path enumeration, exact cover."""

import pytest
from wend_solver import (
    WendPuzzle, WordPath, Trie,
    enumerate_paths, group_by_length,
    solve_exact_cover, solve_wend,
    print_solution,
)


# ============================================================================
# Trie
# ============================================================================

class TestTrie:
    def test_insert_and_lookup(self):
        t = Trie(["HELLO", "HELP", "HE"])
        assert t.is_word("HELLO")
        assert t.is_word("HELP")
        assert t.is_word("HE")
        assert not t.is_word("HEL")
        assert not t.is_word("HELL")
        assert not t.is_word("WORLD")

    def test_prefix_matches(self):
        t = Trie(["HELLO", "HELP"])
        assert t.is_prefix("HE")
        assert t.is_prefix("HEL")
        assert t.is_prefix("HELL")
        assert t.is_prefix("HELLO")
        assert not t.is_prefix("HA")
        assert not t.is_prefix("HELLX")
        # '' is a valid prefix (root of trie covers everything)
        # but empty string is a degenerate case we don't need to assert

    def test_prefix_empty_string(self):
        """Empty string should be a valid prefix (root of trie)."""
        t = Trie(["A"])
        assert t.is_prefix("")

    def test_case_insensitive(self):
        t = Trie(["hello", "WORLD"])
        assert t.is_word("HELLO")
        assert t.is_word("WORLD")
        assert t.is_prefix("HEL")
        assert t.is_prefix("WOR")

    def test_empty_trie(self):
        t = Trie([])
        assert not t.is_word("ANY")
        assert not t.is_prefix("A")

    def test_single_letter_words(self):
        t = Trie(["A", "I"])
        assert t.is_word("A")
        assert t.is_word("I")
        assert t.is_prefix("A")


# ============================================================================
# WendPuzzle
# ============================================================================

class TestWendPuzzle:
    def test_dimensions(self, run_fun_puzzle):
        assert run_fun_puzzle.rows == 2
        assert run_fun_puzzle.cols == 3

    def test_wall_detection(self, wend_5x5_puzzle):
        assert wend_5x5_puzzle.is_wall(1, 1)  # middle walls
        assert wend_5x5_puzzle.is_wall(1, 3)
        assert not wend_5x5_puzzle.is_wall(0, 0)  # letters
        assert not wend_5x5_puzzle.is_wall(4, 4)

    def test_letter_at(self, run_fun_puzzle):
        assert run_fun_puzzle.letter_at(0, 0) == 'R'
        assert run_fun_puzzle.letter_at(0, 2) == 'N'
        assert run_fun_puzzle.letter_at(1, 1) == 'U'

    def test_all_tiles_excludes_walls(self, wend_5x5_puzzle):
        tiles = wend_5x5_puzzle.all_tiles()
        assert len(tiles) == 19  # 25 total - 6 walls
        assert (1, 1) not in tiles  # wall
        assert (1, 3) not in tiles  # wall
        assert (0, 0) in tiles      # letter R

    def test_all_tiles_no_walls(self):
        p = WendPuzzle(grid=[['A', 'B'], ['C', 'D']], word_lengths=[4])
        tiles = p.all_tiles()
        assert len(tiles) == 4
        assert (0, 0) in tiles
        assert (1, 1) in tiles

    def test_neighbors_orthogonal(self):
        p = WendPuzzle(grid=[['A', 'B', 'C'], ['D', 'E', 'F'], ['G', 'H', 'I']])
        n = p.neighbors(1, 1)  # center
        assert len(n) == 4
        assert (0, 1) in n  # up
        assert (2, 1) in n  # down
        assert (1, 0) in n  # left
        assert (1, 2) in n  # right

    def test_neighbors_corner(self):
        p = WendPuzzle(grid=[['A', 'B'], ['C', 'D']])
        n = p.neighbors(0, 0)
        assert len(n) == 2
        assert (0, 1) in n
        assert (1, 0) in n

    def test_neighbors_avoid_walls(self, wall_puzzle):
        # Tile at (0,0)=A should have neighbors: (0,1)=B, (1,0)=C
        # NOT (0,2) because that's a wall
        n = wall_puzzle.neighbors(0, 0)
        assert (0, 1) in n
        assert (1, 0) in n
        assert (0, 2) not in n  # wall

    def test_grid_properties(self):
        p = WendPuzzle(grid=[['A', 'W', 'B']], word_lengths=[1])
        assert p.rows == 1
        assert p.cols == 3


# ============================================================================
# WordPath
# ============================================================================

class TestWordPath:
    def test_length(self):
        wp = WordPath(word="HELLO", path=[(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)])
        assert wp.length() == 5

    def test_tile_set(self):
        wp = WordPath(word="ABC", path=[(0, 0), (0, 1), (0, 2)])
        assert wp.tile_set() == {(0, 0), (0, 1), (0, 2)}

    def test_covers(self):
        wp = WordPath(word="ABC", path=[(0, 0), (0, 1), (0, 2)])
        assert wp.covers((0, 0))
        assert wp.covers((0, 2))
        assert not wp.covers((1, 0))


# ============================================================================
# Path enumeration
# ============================================================================

class TestEnumeratePaths:
    def test_small_grid(self, run_fun_puzzle, sample_dict):
        trie = Trie(sample_dict)
        paths = enumerate_paths(run_fun_puzzle, trie, min_len=2, max_len=3)
        words = {p.word for p in paths}
        assert "RUN" in words
        assert "FUN" in words
        assert "UN" in words  # 2-letter path

    def test_min_len_filter(self, run_fun_puzzle, sample_dict):
        trie = Trie(sample_dict)
        paths = enumerate_paths(run_fun_puzzle, trie, min_len=4)
        # Should only return words of length 4+
        for p in paths:
            assert len(p.word) >= 4

    def test_max_len_clamp(self, run_fun_puzzle, sample_dict):
        """max_len can't exceed total tiles."""
        trie = Trie(sample_dict)
        paths = enumerate_paths(run_fun_puzzle, trie, min_len=2, max_len=999)
        for p in paths:
            assert len(p.word) <= 6  # 2*3 total tiles

    def test_walls_respected(self, wall_puzzle, sample_dict):
        trie = Trie(sample_dict)
        paths = enumerate_paths(wall_puzzle, trie, min_len=3, max_len=4)
        # No path should cross a wall tile
        wall_coords = {(0, 2)}
        for p in paths:
            for coord in p.path:
                assert coord not in wall_coords

    def test_enumerate_5x5_wend(self, wend_5x5_puzzle, sample_dict):
        trie = Trie(sample_dict)
        paths = enumerate_paths(wend_5x5_puzzle, trie, min_len=3, max_len=7)
        # Should find BARCODE, HIGH, CHIEF, IVY at minimum
        words = {p.word for p in paths}
        assert "BARCODE" in words
        assert "HIGH" in words
        assert "CHIEF" in words
        assert "IVY" in words

    def test_no_results_for_wall_island(self):
        """Two isolated tiles with walls — 'AX' not in dict."""
        p = WendPuzzle(grid=[['A', 'W', 'X']], word_lengths=[2])
        t = Trie([])
        paths = enumerate_paths(p, t, min_len=2, max_len=2)
        assert len(paths) == 0

    def test_path_never_revisits_tiles(self):
        """Paths should not revisit tiles (no cycles)."""
        p = WendPuzzle(grid=[
            ['A', 'B', 'C'],
            ['D', 'E', 'F'],
        ])
        t = Trie(["ABC", "ABED"])
        paths = enumerate_paths(p, t, min_len=3, max_len=4)
        for wp in paths:
            # All coordinates in path must be unique
            assert len(set(wp.path)) == len(wp.path)


# ============================================================================
# Exact cover
# ============================================================================

class TestExactCover:
    def test_simple_solution(self, run_fun_puzzle, sample_dict):
        trie = Trie(sample_dict)
        paths = enumerate_paths(run_fun_puzzle, trie, min_len=2, max_len=3)
        grouped = group_by_length(paths)
        solution = solve_exact_cover(
            all_tiles=set(run_fun_puzzle.all_tiles()),
            word_lengths=[3, 3],
            paths_by_length=grouped,
        )
        assert solution is not None
        assert len(solution) == 2
        tile_union = set()
        for wp in solution:
            tile_union |= wp.tile_set()
        assert tile_union == set(run_fun_puzzle.all_tiles())

    def test_no_solution(self, wend_5x5_puzzle, sample_dict):
        """Ask for lengths that don't tile the grid."""
        trie = Trie(sample_dict)
        paths = enumerate_paths(wend_5x5_puzzle, trie, min_len=3, max_len=7)
        grouped = group_by_length(paths)
        solution = solve_exact_cover(
            all_tiles=set(wend_5x5_puzzle.all_tiles()),
            word_lengths=[3, 3, 3, 3, 7],  # 5 words = impossible
            paths_by_length=grouped,
        )
        assert solution is None

    def test_solution_covers_all_tiles(self, run_fun_puzzle, sample_dict):
        trie = Trie(sample_dict)
        paths = enumerate_paths(run_fun_puzzle, trie, min_len=2, max_len=3)
        grouped = group_by_length(paths)
        solution = solve_exact_cover(
            all_tiles=set(run_fun_puzzle.all_tiles()),
            word_lengths=[3, 3],
            paths_by_length=grouped,
        )
        assert solution is not None
        covered = set()
        for wp in solution:
            covered |= wp.tile_set()
        assert covered == set(run_fun_puzzle.all_tiles())

    def test_disjoint_paths(self, run_fun_puzzle, sample_dict):
        """The two paths must not share tiles."""
        trie = Trie(sample_dict)
        paths = enumerate_paths(run_fun_puzzle, trie, min_len=2, max_len=3)
        grouped = group_by_length(paths)
        solution = solve_exact_cover(
            all_tiles=set(run_fun_puzzle.all_tiles()),
            word_lengths=[3, 3],
            paths_by_length=grouped,
        )
        assert solution is not None
        # RUN + FUN path: R-U-N covers (0,0)-(0,1)-(0,2)
        #                F-U-N covers (1,0)-(1,1)-(1,2)
        # These are disjoint so the solution must assign them cleanly
        all_tiles_covered = set()
        for wp in solution:
            for t in wp.path:
                assert t not in all_tiles_covered  # no overlap
                all_tiles_covered.add(t)

    def test_solve_wend_full(self, wend_5x5_puzzle, sample_dict):
        """Full solve_wend pipeline should find BARCODE/HIGH/CHIEF/IVY."""
        solution = solve_wend(wend_5x5_puzzle, sample_dict)
        assert solution is not None
        assert len(solution) == 4  # one per word length
        words = {wp.word for wp in solution}
        assert "BARCODE" in words
        assert "HIGH" in words
        assert "CHIEF" in words
        assert "IVY" in words


# ============================================================================
# group_by_length
# ============================================================================

class TestGroupByLength:
    def test_groups_correctly(self):
        paths = [
            WordPath("AB", [(0, 0), (0, 1)]),
            WordPath("ABC", [(0, 0), (0, 1), (0, 2)]),
            WordPath("DEF", [(1, 0), (1, 1), (1, 2)]),
        ]
        groups = group_by_length(paths)
        assert len(groups[2]) == 1
        assert len(groups[3]) == 2
        assert 4 not in groups


# ============================================================================
# solve_wend
# ============================================================================

class TestSolveWend:
    def test_no_solution(self, unsolvable_puzzle, sample_dict):
        """Isolated tiles can't form words — should return None."""
        sol = solve_wend(unsolvable_puzzle, sample_dict)
        assert sol is None

    def test_solution_word_paths_connect(self, run_fun_puzzle, sample_dict):
        """Each word path should trace through adjacent tiles."""
        sol = solve_wend(run_fun_puzzle, sample_dict)
        assert sol is not None
        for wp in sol:
            for i in range(len(wp.path) - 1):
                r1, c1 = wp.path[i]
                r2, c2 = wp.path[i + 1]
                # Must be orthogonal neighbors
                dist = abs(r1 - r2) + abs(c1 - c2)
                assert dist == 1, f"Path {wp.word}: non-adjacent tiles {wp.path[i]} → {wp.path[i+1]}"

    def test_print_solution_doesnt_crash(self, run_fun_puzzle, sample_dict, capsys):
        """print_solution should handle valid output gracefully."""
        sol = solve_wend(run_fun_puzzle, sample_dict)
        assert sol is not None
        print_solution(run_fun_puzzle, sol)
        captured = capsys.readouterr()
        assert "Wend Solution" in captured.out
        for wp in sol:
            assert wp.word in captured.out

    def test_print_solution_none(self, capsys):
        """print_solution with None should not crash."""
        p = WendPuzzle(grid=[['A']], word_lengths=[1])
        print_solution(p, None)
        captured = capsys.readouterr()
        assert "No solution" in captured.out

    def test_solution_path_lengths_match(self, wend_5x5_puzzle, sample_dict):
        """Each solution word's path length must match its word length."""
        sol = solve_wend(wend_5x5_puzzle, sample_dict)
        assert sol is not None
        for wp in sol:
            assert len(wp.path) == len(wp.word)
