# 🧩 Wend Solver

An educational solver for [LinkedIn Wend](https://www.linkedin.com/games/wend) puzzles — a daily word game where you trace words through a grid using an **exact cover** approach.

> ⚠️ **Not for automated gameplay.** LinkedIn's ToS prohibit bots. This is a learning/assistance tool — you enter the grid manually or upload a screenshot, then get the solution.

## Features

- **🖼️ Screenshot upload** — upload a Wend screenshot, walls auto-detected, you fill the letters
- **⌨️ Manual input** — type the grid directly (4×4 up to 8×8, any size)
- **🧠 Algorithm X solver** — exact cover backtracking with dictionary trie
- **🌐 Web UI** — open `http://localhost:3232/`
- **📐 Dynamic grid sizes** — works with any N×N grid
- **🧪 36 unit tests** + pre-commit hook + GitHub Actions CI
- **🐍 Pure Python** — Flask + Pillow only. Tesseract/OCR is optional.

## Quick Start

### Linux / macOS

```bash
# Clone
git clone https://github.com/Aldo-f/wend-solver.git
cd wend-solver

# Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
python app.py
```

### Windows (PowerShell)

```powershell
# Clone
git clone https://github.com/Aldo-f/wend-solver.git
cd wend-solver

# Set up virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run
python app.py
```

*Or use `cmd`: `.venv\Scripts\activate.bat` instead of the PowerShell line.*

Open **http://localhost:3232/** in your browser.

### Optional: Tesseract OCR (for automatic letter recognition from screenshots)

The app works **without Tesseract** — walls are auto-detected, you type letters in the UI.
Only install this if you want OCR to guess the letters:

- **macOS**: `brew install tesseract`
- **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
- **Windows**: Download from [GitHub UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
- **Fedora**: `sudo dnf install tesseract`
- Then: `pip install pytesseract`

### Run as a service (Linux systemd)

```bash
cp _examples/wend-solver.service /tmp/
# Edit /tmp/wend-solver.service with correct paths + user
sudo cp /tmp/wend-solver.service /etc/systemd/system/
sudo systemctl enable wend-solver
sudo systemctl start wend-solver
```

## Project Structure

```
wend-solver/
├── app.py                 # Flask web app (routes, solver wrapper)
├── grid_detect.py         # N×N grid detection from images
├── wend_solver.py         # Core solver (trie, path enumeration, exact cover)
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html         # Web UI
├── tests/
│   ├── conftest.py        # Shared fixtures & test dictionary
│   └── test_wend_solver.py # 36 unit tests
├── hooks/
│   ├── pre-commit         # Pre-commit hook (bash — Linux/macOS)
│   └── pre-commit.ps1     # Pre-commit hook (PowerShell — Windows)
├── _examples/
│   └── wend-solver.service # systemd unit template (Linux)
├── .github/workflows/
│   └── test.yml           # GitHub Actions CI (push & PR)
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
# Install test dependency
pip install pytest

# All tests
python -m pytest tests/ -v

# Just solver core tests (fast)
python -m pytest tests/test_wend_solver.py -v
```

### Pre-commit hook (auto-run on every commit)

```bash
git config core.hooksPath hooks
```

On **Windows**: Git for Windows runs `hooks/pre-commit` if you use Git Bash, or you can manually run `hooks/pre-commit.ps1` in PowerShell.

## API

### `POST /api/solve`

**JSON grid string:**
```bash
curl -X POST http://localhost:3232/api/solve \
  -H "Content-Type: application/json" \
  -d '{"grid":"RCOHI/A#D#G/B#E#H/C#F#I/HIEYV","lengths":"3,4,5,7"}'
```

**Parameters:**
- `grid` — rows separated by `/`. `#` = wall, `.` = empty, letter = that letter.
- `lengths` — comma-separated word lengths, e.g. `"3,4,5,7"` or `[3,4,5,7]`

**File upload:**
```bash
curl -X POST http://localhost:3232/api/solve \
  -F "image=@screenshot.png"
```

### `POST /api/detect`

Upload an image to detect walls (no OCR — you fill letters in the UI):

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

## What's NOT in this repo

This project is **fully portable** — no machine-specific paths or configs.
The following live **only on the original dev machine** and are not needed to run the app:

- `~/wend-venv/` — virtual environment (create your own with `python -m venv .venv`)
- `/etc/systemd/system/wend-solver.service` — systemd service (template in `_examples/`)
- `tesseract-ocr` — optional, lazy-imported if installed

## License

MIT — educational use only.

## Resources

- [LinkedIn Wend](https://www.linkedin.com/games/wend)
- [Wend Strategy Guide](wend-strategy-guide.md)
- [Dictionary source](https://github.com/words/an-array-of-english-words)
