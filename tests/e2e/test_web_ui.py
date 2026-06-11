"""Playwright E2E tests for Wend Solver web UI (sync API)."""

import pytest
import os


# Path to current puzzle screenshot
PUZZLE_IMAGE = os.path.join(
    os.path.dirname(__file__), "wend_puzzle_current.png"
)


BASE_URL = os.environ.get("WEND_BASE_URL", "http://localhost:3232")


def test_web_ui_loads(page):
    """Test that the web UI loads correctly."""
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")

    # Check title
    title = page.title()
    assert "Wend Solver" in title

    # Check main elements are present
    page.wait_for_selector("#dropZone", state="visible")
    page.wait_for_selector("#fileInput", state="attached")
    page.wait_for_selector("#detectBtn", state="attached")
    page.wait_for_selector("#gridSizeSelect", state="visible")
    page.wait_for_selector("#solveBtn", state="visible")


def test_manual_grid_solve(page):
    """Test solving a puzzle via manual grid input."""
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")

    # Switch to manual tab
    page.locator("#m-manual").click()
    page.wait_for_selector("#method-manual", state="visible")

    # Set grid size to 5
    page.locator("#gridSizeSelect").select_option("5")
    page.wait_for_selector("#editorSection", state="visible")

    # Fill in a known 5x5 puzzle
    grid_data = [
        ["R", "C", "O", "H", "I"],
        ["A", "#", "D", "#", "G"],
        ["B", "#", "E", "#", "H"],
        ["C", "#", "F", "#", "I"],
        ["H", "I", "E", "Y", "V"],
    ]

    for row_idx, row in enumerate(grid_data):
        for col_idx, val in enumerate(row):
            cell = page.locator(f"#gridEditor input[data-row='{row_idx}'][data-col='{col_idx}']")
            cell.fill(val)

    # Set word lengths
    page.locator("#lengthsInput").fill("3,4,5,7")

    # Click solve
    page.locator("#solveBtn").click()

    # Wait for result
    page.wait_for_selector("#resultCard", state="visible", timeout=10000)

    # Check that solution is found
    solution_text = page.locator("#resultContent").inner_text()
    assert "BARCODE" in solution_text or "HIGH" in solution_text or "CHIEF" in solution_text


def test_file_upload_detect(page):
    """Test uploading an image and detecting grid (walls only)."""
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")

    # Upload the puzzle screenshot (upload tab is active by default)
    file_input = page.locator("#fileInput")
    file_input.set_input_files(PUZZLE_IMAGE)

    # Wait for preview to appear
    page.wait_for_selector("#previewImg", state="visible", timeout=5000)

    # Click detect button
    page.locator("#detectBtn").click()

    # Wait for grid editor to appear
    page.wait_for_selector("#editorSection", state="visible", timeout=15000)

    # Check that grid was detected (size shown)
    # The grid size is shown in the gridSizeSelect
    size_val = page.locator("#gridSizeSelect").input_value()
    assert size_val in ["5", "6"]  # today's puzzle is 6x6

    # Check walls were detected (wall cells have class 'wall')
    wall_cells = page.locator("#gridEditor input.wall").count()
    assert wall_cells > 0


def test_file_upload_solve(page):
    """Test full solve via file upload."""
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")

    # Upload the puzzle screenshot
    file_input = page.locator("#fileInput")
    file_input.set_input_files(PUZZLE_IMAGE)

    # Wait for preview
    page.wait_for_selector("#previewImg", state="visible", timeout=5000)

    # Click detect
    page.locator("#detectBtn").click()

    # Wait for grid editor
    page.wait_for_selector("#editorSection", state="visible", timeout=15000)

    # Click solve
    page.locator("#solveBtn").click()

    # Wait for result
    page.wait_for_selector("#resultCard", state="visible", timeout=15000)

    # Check solution found
    solution_text = page.locator("#resultContent").inner_text()
    assert len(solution_text) > 0
