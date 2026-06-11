#!/usr/bin/env python3
"""Wend Solver POC — OCR + solver web app for LinkedIn Wend puzzles."""

import base64
import io
import json
import os
import sys
import threading
import time
from pathlib import Path

from flask import Flask, request, jsonify, send_file
from PIL import Image

# Add solver directory to path (same dir as this file)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wend_solver import WendPuzzle, solve_wend
from grid_detect import detect_grid as detect_grid_fn, find_grid_lines

app = Flask(__name__)

# -------------------------------------------------------------------
# Dictionary (background load)
# -------------------------------------------------------------------
DICTIONARY = []
DICT_READY = False

DICT_SOURCES = [
    ("an-array-of-english-words",
     "https://raw.githubusercontent.com/words/an-array-of-english-words/master/index.json",
     "json_list"),
]

# Embedded curated words — words likely in LinkedIn's curated list
CURATED_WORDS = """BARCODE CHIEF HIGH IVY CRAB CODE ARCO OCRA RAB COD ODE
HOD HOC ARC ABC DOC DOH DEF GHI BAR BCH EDO CHI FED FEI FEY HCB HIE
IVY CHIEF HIGH CRAB CODE ARCO BARCODE""".split()


def load_dictionary():
    global DICTIONARY, DICT_READY
    words = set(CURATED_WORDS)
    for name, url, fmt in DICT_SOURCES:
        try:
            import urllib.request
            resp = urllib.request.urlopen(url, timeout=15)
            if fmt == "json_list":
                data = json.load(resp)
                words.update(w.upper() for w in data if 3 <= len(w) <= 7)
            elif fmt == "json_dict":
                data = json.load(resp)
                words.update(k.upper() for k in data if 3 <= len(k) <= 7)
            elif fmt == "txt":
                text = resp.read().decode()
                data = text.split()
                words.update(w.strip().upper() for w in data if 3 <= len(w.strip()) <= 7)
            print(f"[dict] Loaded {name}")
        except Exception as e:
            print(f"[dict] {name} failed: {e}")
    DICTIONARY = list(words)
    DICT_READY = True
    print(f"[dict] Ready: {len(DICTIONARY)} words")


# Start dictionary load in background
threading.Thread(target=load_dictionary, daemon=True).start()


def get_dictionary():
    """Wait for dictionary to load (max 30s) then return."""
    deadline = time.time() + 30
    while not DICT_READY and time.time() < deadline:
        time.sleep(0.5)
    return DICTIONARY


# -------------------------------------------------------------------
# Grid detection from image (via grid_detect module)
# -------------------------------------------------------------------

def is_wall_color(r, g, b):
    return (r + g + b) / 3 < 190


def detect_grid(image):
    """Detect N×N Wend grid from screenshot. Falls back to grid_detect module."""
    try:
        result, walls, n = detect_grid_fn(image)
    except Exception:
        result, walls, n = None, None, 0

    if result is not None:
        return result, walls, n

    return None, None, 0


# -------------------------------------------------------------------
# Solver wrapper
# -------------------------------------------------------------------

def grid_to_solver(grid):
    """Convert OCR grid to solver format (dynamic size)."""
    n_rows = len(grid)
    n_cols = len(grid[0]) if grid else 0
    solver_grid = []
    for r in range(n_rows):
        row = []
        for c in range(n_cols):
            val = grid[r][c]
            if val in ('W', '#'):
                row.append('W')
            elif val in ('?', '.'):
                row.append('.')
            else:
                row.append(val.upper())
        solver_grid.append(row)
    return solver_grid


def solve_grid(grid, word_lengths=None):
    """Solve a Wend grid."""
    if word_lengths is None:
        num_letters = sum(1 for row in grid for c in row if c not in ('W', '.', '?'))
        if num_letters == 18:
            word_lengths = [3, 4, 5, 6]
        elif num_letters == 19:
            word_lengths = [3, 4, 5, 7]
        else:
            word_lengths = [3, 4, 5, max(3, num_letters - 12)]

    dict_words = get_dictionary()
    if not dict_words:
        return None, "Dictionary not loaded yet (try again in 10s)"

    puzzle = WendPuzzle(grid=grid, word_lengths=word_lengths)
    solution = solve_wend(puzzle, dict_words)

    if solution:
        return [{
            'word': wp.word,
            'length': wp.length(),
            'path': [(int(r), int(c)) for r, c in wp.path]
        } for wp in solution], None
    return None, "No solution found"


def format_grid_string(s):
    """Parse 'RCOHI/A#D#G/B#E#H/C#F#I/HIEYV' → 5x5 list."""
    rows = s.strip().split('/')
    grid = []
    for row_str in rows:
        row = []
        for ch in row_str.strip():
            if ch in ('#', 'W'):
                row.append('W')
            elif ch in ('.', '?'):
                row.append('.')
            else:
                row.append(ch.upper())
        grid.append(row)
    return grid


# -------------------------------------------------------------------
# Flask routes
# -------------------------------------------------------------------

@app.route('/')
def index():
    return send_file(str(Path(__file__).parent / 'templates' / 'index.html'))


@app.route('/api/health')
def health():
    return jsonify({
        'status': 'ok',
        'dict_loaded': DICT_READY,
        'dict_size': len(DICTIONARY)
    })


def detect_grid_no_ocr(image):
    """Detect grid walls only — fast, no OCR. Returns grid, walls, n."""
    result = find_grid_lines(image)
    if result is None:
        return None, None, 0

    left, top, right, bottom, cell_w, cell_h, n_cols, n_rows = result
    w, h = image.size
    rgb = image.convert("RGB")
    pixels = rgb.load()

    grid = [["." for _ in range(n_cols)] for _ in range(n_rows)]
    walls = [[False for _ in range(n_cols)] for _ in range(n_rows)]

    for row in range(n_rows):
        for col in range(n_cols):
            cx = int(left + col * cell_w + cell_w / 2)
            cy = int(top + row * cell_h + cell_h / 2)

            sample_pts = [
                (cx, cy),
                (cx - int(cell_w * 0.2), cy),
                (cx + int(cell_w * 0.2), cy),
                (cx, cy - int(cell_h * 0.2)),
                (cx, cy + int(cell_h * 0.2)),
            ]
            gray_count = 0
            for sx, sy in sample_pts:
                if 0 <= sx < w and 0 <= sy < h:
                    r, g, b = pixels[sx, sy]
                    if (r + g + b) // 3 < 180:
                        gray_count += 1
            walls[row][col] = gray_count >= 3
            if walls[row][col]:
                grid[row][col] = 'W'

    return grid, walls, n_cols


@app.route('/api/detect', methods=['POST'])
def detect():
    """Detect grid from an image upload — walls only, no OCR.
    User will review/correct letters in the UI."""
    if 'image' not in request.files:
        if request.is_json:
            data = request.get_json(silent=True)
            if data and 'base64' in data:
                try:
                    b64 = data['base64']
                    if ',' in b64:
                        b64 = b64.split(',')[1]
                    img = Image.open(io.BytesIO(base64.b64decode(b64)))
                except Exception as e:
                    return jsonify({'success': False, 'error': str(e)})
            else:
                return jsonify({'success': False, 'error': 'No image provided'})
        else:
            return jsonify({'success': False, 'error': 'No image provided'})
    else:
        file = request.files['image']
        if not file.filename:
            return jsonify({'success': False, 'error': 'No file'})
        try:
            img = Image.open(file.stream)
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    grid, walls, n = detect_grid_no_ocr(img)
    if grid is None:
        return jsonify({'success': False, 'error': 'Could not detect grid in image. Try manual input.'})

    return jsonify({'success': True, 'grid': grid, 'walls': walls, 'size': n})


@app.route('/api/solve', methods=['POST'])
def solve():
    """Solve a Wend puzzle from image or grid string."""

    # --- Manual grid input ---
    data = request.get_json(silent=True) if request.is_json else None
    if data and 'grid' in data:
        grid = format_grid_string(data['grid'])
        raw_lengths = data.get('lengths')
        if raw_lengths:
            if isinstance(raw_lengths, str):
                word_lengths = [int(x.strip()) for x in raw_lengths.split(',') if x.strip()]
            else:
                word_lengths = [int(x) for x in raw_lengths]
        else:
            word_lengths = None
        result, error = solve_grid(grid, word_lengths)
        if result:
            return jsonify({'success': True, 'solution': result, 'grid': grid})
        return jsonify({'success': False, 'error': error, 'grid': grid})

    # --- File upload ---
    if 'image' in request.files:
        file = request.files['image']
        if not file.filename:
            return jsonify({'success': False, 'error': 'No file'})
        try:
            img = Image.open(file.stream)
            grid, walls, n = detect_grid(img)
            if grid is None:
                return jsonify({
                    'success': False,
                    'error': 'Could not detect grid in image. Try manual input.'
                })
            solver_grid = grid_to_solver(grid)
            result, error = solve_grid(solver_grid)
            if result:
                return jsonify({
                    'success': True,
                    'solution': result,
                    'grid': solver_grid,
                    'ocr_grid': grid,
                    'walls': walls,
                })
            return jsonify({
                'success': False,
                'error': error,
                'grid_guess': solver_grid,
                'ocr_grid': grid,
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    # --- Clipboard paste (base64) ---
    if data and 'base64' in data:
        try:
            b64 = data['base64']
            if ',' in b64:
                b64 = b64.split(',')[1]
            img = Image.open(io.BytesIO(base64.b64decode(b64)))
            grid, walls, n = detect_grid(img)
            if grid is None:
                return jsonify({
                    'success': False,
                    'error': 'Could not detect grid in image.'
                })
            solver_grid = grid_to_solver(grid)
            result, error = solve_grid(solver_grid)
            if result:
                return jsonify({
                    'success': True,
                    'solution': result,
                    'grid': solver_grid,
                    'ocr_grid': grid,
                })
            return jsonify({
                'success': False,
                'error': error,
                'grid_guess': solver_grid,
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    return jsonify({'success': False, 'error': 'Provide image or grid string'})


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

if __name__ == '__main__':
    print("Wend Solver — http://localhost:3232")
    print("Dictionary loading in background...")
    app.run(host='0.0.0.0', port=3232, debug=False)
