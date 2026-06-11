"""Grid detection for Wend screenshots — supports N×N grids."""

from PIL import Image


MIN_CELL_SIZE = 20
MAX_CELL_SIZE = 150


def find_grid_lines(image):
    """Find an N×N Wend grid by detecting the cell pattern.
    
    Strategy:
    1. Find vertical dark lines (grid column separators) 
    2. Find the largest set of evenly-spaced columns → determines N
    3. Find matching horizontal rows
    4. Detect any extra border lines to exclude
    
    Returns (left, top, right, bottom, cell_w, cell_h, n_cols, n_rows) or None.
    """
    w, h = image.size
    rgb = image.convert("RGB")

    # ── Find vertical dark lines ──
    vert_candidates = []
    for x in range(w):
        dark = 0
        for y in range(0, h, 2):
            r, g, b = rgb.getpixel((x, y))
            if r < 80 and g < 80 and b < 80:
                dark += 1
        if dark > h * 0.06:
            vert_candidates.append(x)

    # Group consecutive x coords into single lines
    vert_groups = []
    if vert_candidates:
        cur = [vert_candidates[0]]
        for x in vert_candidates[1:]:
            if x - cur[-1] <= 3:
                cur.append(x)
            else:
                vert_groups.append(sum(cur) // len(cur))
                cur = [x]
        vert_groups.append(sum(cur) // len(cur))

    if len(vert_groups) < 3:
        return None

    # ── Find horizontal dark lines ──
    horiz_candidates = []
    for y in range(h):
        dark = 0
        for x in range(0, w, 2):
            r, g, b = rgb.getpixel((x, y))
            if r < 80 and g < 80 and b < 80:
                dark += 1
        if dark > w * 0.06:
            horiz_candidates.append(y)

    # Group consecutive y coords
    horiz_groups = []
    if horiz_candidates:
        cur = [horiz_candidates[0]]
        for y in horiz_candidates[1:]:
            if y - cur[-1] <= 3:
                cur.append(y)
            else:
                horiz_groups.append(sum(cur) // len(cur))
                cur = [y]
        horiz_groups.append(sum(cur) // len(cur))

    if len(horiz_groups) < 3:
        return None

    # ── Find the largest set of evenly-spaced vertical lines ──
    def find_even_grid(lines, size_range=(2, 10)):
        """Find largest contiguous subset of lines forming an evenly-spaced grid."""
        best = None
        for grid_size in range(size_range[1], size_range[0] - 1, -1):
            n_lines = grid_size + 1
            if n_lines > len(lines):
                continue
            for start in range(len(lines) - n_lines + 1):
                segment = lines[start:start + n_lines]
                spacings = [segment[i+1] - segment[i] for i in range(grid_size)]
                avg = sum(spacings) / grid_size
                if (MIN_CELL_SIZE <= avg <= MAX_CELL_SIZE and
                    all(abs(s - avg) / avg < 0.30 for s in spacings)):
                    return segment, grid_size, avg
        return None

    vert_result = find_even_grid(vert_groups)
    if vert_result is None:
        return None

    v_lines, n_cols, cell_w = vert_result
    grid_left = v_lines[0]
    grid_right = v_lines[-1]

    # ── Find matching horizontal lines ──
    # Try to find horiz lines matching the same spacing
    horiz_result = find_even_grid(horiz_groups, size_range=(2, 10))
    if horiz_result:
        h_lines, n_rows, cell_h = horiz_result
        grid_top = h_lines[0]
        grid_bottom = h_lines[-1]
    else:
        # Fallback: scan vertically using column centers to find rows
        n_rows = n_cols  # assume square
        cell_h = cell_w

        col_centers = [int(grid_left + c * cell_w + cell_w / 2) for c in range(n_cols)]

        def is_grid_row(y):
            white_count = 0
            for cx in col_centers:
                if 0 <= cx < w and 0 <= y < h:
                    r, g, b = rgb.getpixel((cx, y))
                    avg = (r + g + b) // 3
                    if avg > 200:
                        white_count += 1
            return white_count >= max(2, n_cols // 3)

        start_y = None
        for y in range(int(h * 0.15), int(h * 0.85), 2):
            if is_grid_row(y):
                start_y = y
                break

        if start_y is None:
            return None

        top = start_y
        for y in range(start_y, max(0, start_y - int(cell_w * 3)), -2):
            if not is_grid_row(y):
                top = y + 2
                break
            top = y

        bottom = start_y
        for y in range(start_y, min(h - 1, start_y + int(cell_w * 3)), 2):
            if not is_grid_row(y):
                bottom = y - 2
                break
            bottom = y

        grid_top = top
        grid_bottom = bottom
        cell_h = (bottom - top) / n_rows
        if cell_h < MIN_CELL_SIZE or cell_h > MAX_CELL_SIZE:
            cell_h = cell_w
        grid_bottom = int(top + cell_h * n_rows)
        if grid_bottom >= h:
            grid_bottom = bottom

    return (grid_left, grid_top, grid_right, grid_bottom, cell_w, cell_h, n_cols, n_rows)


def ocr_letter(cell_img):
    """OCR a single uppercase letter from a cropped cell image."""
    try:
        # Lazy imports — Tesseract is optional
        from PIL import ImageEnhance
        import pytesseract

        img = cell_img.convert("L")
        img = ImageEnhance.Contrast(img).enhance(3.0)
        img = img.point(lambda x: 0 if x < 120 else 255, "1")
        
        text = pytesseract.image_to_string(
            img,
            config="--psm 10 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        ).strip()
        if len(text) == 1 and text.isalpha():
            return text.upper()
    except:
        pass
    return None


def detect_grid(image):
    """
    Detect an N×N Wend grid from a screenshot.
    
    Returns:
        grid: N×N list of letters (upper) or "?" for unknown
        walls: N×N list of bool (True = wall/gray cell)
        n: grid size (N)
    
    Returns (None, None, 0) if detection fails.
    """
    result = find_grid_lines(image)
    if result is None:
        return None, None, 0

    left, top, right, bottom, cell_w, cell_h, n_cols, n_rows = result
    w, h = image.size
    rgb = image.convert("RGB")
    pixels = rgb.load()

    grid = [["?" for _ in range(n_cols)] for _ in range(n_rows)]
    walls = [[False for _ in range(n_cols)] for _ in range(n_rows)]

    for row in range(n_rows):
        for col in range(n_cols):
            cx = int(left + col * cell_w + cell_w / 2)
            cy = int(top + row * cell_h + cell_h / 2)

            # Determine if wall by sampling cell center + offsets
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

            if not walls[row][col]:
                # Bright cell → OCR the letter
                cl = max(0, int(left + col * cell_w + cell_w * 0.12))
                cr = min(w, int(left + (col + 1) * cell_w - cell_w * 0.12))
                ct = max(0, int(top + row * cell_h + cell_h * 0.12))
                cb = min(h, int(top + (row + 1) * cell_h - cell_h * 0.12))

                if cr > cl and cb > ct:
                    cell_img = image.crop((cl, ct, cr, cb))
                    letter = ocr_letter(cell_img)
                    if letter:
                        grid[row][col] = letter

    return grid, walls, n_cols
