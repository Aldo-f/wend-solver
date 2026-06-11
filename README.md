# 🧩 Wend Solver

An educational solver for [LinkedIn Wend](https://www.linkedin.com/games/wend) puzzles — a daily word game where you trace words through a grid using an **exact cover** approach.

> ⚠️ **Not for automated gameplay.** LinkedIn's ToS prohibit bots. This is a learning/assistance tool — you enter the grid manually or upload a screenshot, then get the solution.

## Features

- **🖼️ Screenshot upload** — upload a LinkedIn Wend screenshot, walls are auto-detected, you fill in the letters
- **⌨️ Manual input** — type the grid directly (4×4 up to 8×8, any size supported)
- **🧠 Algorithm X solver** — exact cover backtracking with dictionary trie for fast lookup
- **🌐 Web UI** at `http://192.168.0.5:3232/`
- **📐 Dynamic grid sizes** — not limited to 5×5; works with any N×N Wend variant

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (fast Python package manager)
- Tesseract OCR (for optional letter OCR — walls detection works without it)

```bash
# Install system deps
sudo apt-get install -y tesseract-ocr

# Create venv & install Python deps
uv venv ~/.hermes/scripts/wend-venv --seed
source ~/.hermes/scripts/wend-venv/bin/activate
uv pip install pytesseract flask Pillow
```

### Run

```bash
cd ~/.hermes/scripts/wend
source ~/.hermes/scripts/wend-venv/bin/activate
python app.py
```

Open `http://192.168.0.5:3232/` in your browser.

### Run as a service (auto-start after reboot)

```bash
sudo cp wend-solver.service /etc/systemd/system/
sudo systemctl enable wend-solver
sudo systemctl start wend-solver
```

Now the solver starts automatically on every boot.

## How It Works

1. **Grid detection** — `grid_detect.py` finds the N×N grid lines in a screenshot using horizontal/vertical dark line scanning. Walls (gray cells) are identified by sampling RGB values at cell centers.

2. **Path enumeration** — `wend_solver.py` performs a DFS from every tile, tracing orthogonal paths (up/down/left/right, no diagonals). A **Trie** prunes paths that can't form dictionary words. Only paths matching known English words (from the [an-array-of-english-words](https://github.com/words/an-array-of-english-words) dictionary, 75k+ words) are kept.

3. **Exact cover** — The solver implements **Algorithm X** (backtracking with constraint propagation). It finds a set of paths (one per target word length) that covers every tile exactly once.

## API

### `POST /api/solve`

**JSON grid string:**
```bash
curl -X POST http://192.168.0.5:3232/api/solve \
  -H "Content-Type: application/json" \
  -d '{"grid":"RCOHI/A#D#G/B#E#H/C#F#I/HIEYV","lengths":"3,4,5,7"}'
```

**Parameters:**
- `grid` — rows separated by `/`, cells separated by position. `#` = wall, `.` = empty, letter = that letter.
- `lengths` — comma-separated word lengths to find, e.g. `"3,4,5,7"` or `[3,4,5,7]`

**File upload:**
```bash
curl -X POST http://192.168.0.5:3232/api/solve \
  -F "image=@screenshot.png"
```

### `POST /api/detect`

Upload an image to detect walls only (no OCR — you fill letters in the UI):

```bash
curl -X POST http://192.168.0.5:3232/api/detect \
  -F "image=@screenshot.png"
```

Returns `{"success": true, "grid": [...], "walls": [...], "size": 6}`.

### `GET /api/health`

```bash
curl http://192.168.0.5:3232/api/health
```
```json
{"status": "ok", "dict_loaded": true, "dict_size": 75213}
```

## Project Structure

```
~/.hermes/scripts/wend/
├── app.py              # Flask web app (routes, solver wrapper)
├── grid_detect.py      # N×N grid detection from images
├── wend_solver.py      # Core solver (trie, path enumeration, exact cover)
├── templates/
│   └── index.html      # Web UI
├── wend-solver.service # systemd service file
└── README.md           # This file
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
- [Wend Strategy Guide](wend-strategy-guide.md) (local)
- [Dictionary source](https://github.com/words/an-array-of-english-words)
