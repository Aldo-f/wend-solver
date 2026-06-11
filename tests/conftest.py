"""Shared fixtures for Wend solver tests."""

import pytest
from wend_solver import WendPuzzle


# Small dictionary with known words for deterministic tests
TEST_DICT = [
    "BAR", "BARE", "BARCODE", "BARN", "CAR", "CARE", "CHIEF", "CHIEFLY",
    "FUN", "FUR", "FURY", "GIN", "HIGH", "HIGHER", "IVY", "RAN",
    "RUN", "RURAL", "TAG", "TAP", "TAR", "UN", "UP",
]


@pytest.fixture
def sample_dict():
    return list(TEST_DICT)


@pytest.fixture
def run_fun_puzzle():
    """Simple 2×3 grid with two disjoint 3-letter paths: RUN + FUN."""
    return WendPuzzle(grid=[
        ['R', 'U', 'N'],
        ['F', 'U', 'N'],
    ], word_lengths=[3, 3])


@pytest.fixture
def wend_5x5_puzzle():
    """The standard LinkedIn Wend 5×5 grid from our known solution."""
    return WendPuzzle(grid=[
        ['R', 'C', 'O', 'H', 'I'],
        ['A', 'W', 'D', 'W', 'G'],
        ['B', 'W', 'E', 'W', 'H'],
        ['C', 'W', 'F', 'W', 'I'],
        ['H', 'I', 'E', 'Y', 'V'],
    ], word_lengths=[3, 4, 5, 7])


@pytest.fixture
def unsolvable_puzzle():
    """Two isolated tiles - can't form a path."""
    return WendPuzzle(grid=[
        ['A', 'W', 'B'],
    ], word_lengths=[2])


@pytest.fixture
def wall_puzzle():
    """3×3 grid with an L-shaped wall."""
    return WendPuzzle(grid=[
        ['A', 'B', 'W'],
        ['C', 'W', 'D'],
        ['E', 'F', 'G'],
    ], word_lengths=[3, 4])
