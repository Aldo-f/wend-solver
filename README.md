# 🧩 Wend Solver

An educational solver for [LinkedIn Wend](https://www.linkedin.com/games/wend) puzzles — a daily word game where you trace words through a grid using an **exact cover** approach.

> ⚠️ **Not for automated gameplay.** LinkedIn's ToS prohibit bots. This is a learning/assistance tool — you enter the grid manually or upload a screenshot, then get the solution.

## Features

- **🖼️ Screenshot upload** — upload a LinkedIn Wend screenshot, walls are auto-detected, you fill in the letters
- **⌨️ Manual input** — type the grid directly (4×4 up to 8×8, any size supported)
- **🧠 Algorithm X solver** — exact cover backtracking with dictionary trie for fast lookup
- **🌐 Web UI** at `http://localhost:3232/`
- **📐 Dynamic grid sizes** — not limited to 5×5; works with any N×N Wend variant
- **🧪 Tested** — 36 unit tests, pre-commit hook, GitHub Actions CI

## Quick Start

```bash
# Clone
git clone https://github.com/Aldo-f/wend-solver.git
cd wend-solver

# Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install flask Pillow pytesseract pytest

# (Optional) Install Tesseract OCR for screenshot upload
#   macOS: brew install tesseract
#   Ubuntu/Debian: sudo apt-get install tesseract-ocr
#   Fedora: sudo dnf install tesseract

# Run
python app.py
```

Open **http://localhost:3232/** in your browser.

### Run as a service (systemd — Linux)

```bash
sudo cp wend-solver.service /etc/systemd/system/
sudo systemctl enable wend-solver
sudo systemctl start wend-solver
```

Edit the service file first if your paths differ from the defaults.

## Project Structure

```
wend-solver/
├── app.py                 # Flask web app (routes, solver wrapper)
├── grid_detect.py         # N×N grid detection from images
├── wend_solver.py         # Core solver (trie, path enumeration, exact cover)
├── templates/
│   └── index.html         # Web UI
├── tests/
│   ├── conftest.py        # Shared fixtures & test dictionary
│   └── test_wend_solver.py # 36 unit tests
├── hooks/
│   └── pre-commit         # Pre-commit hook (runs pytest, blocks on failure)
├── .github/workflows/
│   └── test.yml           # GitHub Actions CI (push & PR)
├── wend-solver.service    # systemd unit for auto-start on boot
├── wend-strategy-guide.md # Strategy guide for playing Wend
├── README.md              # This file
└── .gitignore
```

## How It Works

1. **Grid detection** — `grid_detect.py` finds the N×N grid lines in a screenshot using horizontal/vertical dark line scanning. Walls (gray cells) are identified by sampling RGB values at cell centers.

2. **Path enumeration** — `wend_solver.py` performs a DFS from every tile, tracing orthogonal paths (up/down/left/right, no diagonals). A **Trie** prunes paths that can't form dictionary words. Only paths matching known English words (from the [an-array-of-english-words](https://github.com/words/an-array-of-english-words) dictionary, 75k+ words) are kept.

3. **Exact cover** — The solver implements **Algorithm X** (backtracking with constraint propagation). It finds a set of paths (one per target word length) that covers every tile exactly once.

## Running the Tests

```bash
# All tests
python -m pytest tests/ -v

# Just solver tests (fast, no extra deps)
python -m pytest tests/test_wend_solver.py -v
```

### Pre-commit hook (auto-run on every commit)

```bash
git config core.hooksPath hooks
```

Now `pytest` runs automatically before every `git commit`. If tests fail, the commit is blocked.

## API

### `POST /api/solve`

**JSON grid string:**
```bash
curl -X POST http://localhost:3232/api/solve \
  -H "Content-Type: application/json" \
  -d '{"grid":"RCOHI/A#D#G/B#E#H/C#F#I/HIEYV","lengths":"3,4,5,7"}'
```

**Parameters:**
- `grid` — rows separated by `/`, cells separated by position. `#` = wall, `.` = empty, letter = that letter.
- `lengths` — comma-separated word lengths to find, e.g. `"3,4,5,7"` or `[3,4,5,7]`

**File upload:**
```bash
curl -X POST http://localhost:3232/api/solve \
  -F "image=@screenshot.png"
```

### `POST /api/detect`

Upload an image to detect walls only (no OCR — you fill letters in the UI):

```bash
curl -X POST http://localhost:3232/api/detect \
  -F "image=@screenshot.png"
```

Returns `{"success": true, "grid": [...], "walls": [...], "size": 6}`.

### `GET /api/health`

```bash
curl http://localhost:3232/api/health
```
```json
{"status": "ok", "dict_loaded": true, "dict_size": 75213}
```

## Solver Variants

The core solver supports:
- **Any grid size** (N×N) — not limited to 5×5
- **Any number of words** — as long as they tile the grid exactly
- **Any word lengths** — specify per puzzle
- **Orthogonal paths** — no diagonals (matching Wend rules)
- **Letter tiles only** — walls are impassable

## Future Ideas

- [ ] **Grid generator** — given a word list, generate a Wend puzzle with a unique solution
- [ ] **DLX backend** — Dancing Links for faster solving on larger grids (7×7+)
- [ ] **Toolbox integration** — embed as a tool in the Toolbox web app
- [ ] **Multi-color walls** — different wall types with different constraints

## License

MIT — educational use only.

## Resources

- [LinkedIn Wend](https://www.linkedin.com/games/wend)
- [Wend Strategy Guide](wend-strategy-guide.md)
- [Dictionary source](https://github.com/words/an-array-of-english-words)
