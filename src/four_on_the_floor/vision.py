"""Webcam-style chip tracking for *4 on the Floor* (paper Section 3.1.1).

The paper says only: "Via a webcam-based image processing approach, the chips
were tracked in real time, converted into midi triggers, and then sent to a
digital audio workstations for sound generation." No library, no colour space,
no thresholds, no calibration procedure are given.

What we implement (all of it ASSUMPTION, see REPRODUCIBILITY.md):
  - the grid is rectified, i.e. the camera pose is known and the 8x8 grid maps
    onto a fixed axis-aligned raster (no homography estimation);
  - per cell, the median hue/saturation/value of a central disc is taken;
  - a cell is "empty" if saturation or value falls below a threshold, otherwise
    it is classified to the nearest reference hue.

`render_board` produces the synthetic frames we test the detector on, because
the authors released neither footage nor the physical artifact.
"""

from __future__ import annotations

import numpy as np

from .board import COLORS, Board

# ASSUMPTION: reference RGB for each chip colour (used for both rendering and
# classification). The paper does not state the chips' colours.
REFERENCE_RGB = {
    "red": (200, 40, 40),
    "yellow": (225, 200, 50),
    "blue": (45, 80, 200),
    "green": (50, 165, 70),
}
BACKGROUND_RGB = (28, 28, 32)
FRAME_RGB = (90, 90, 96)

# ASSUMPTION: detection thresholds.
SAT_MIN = 0.35
VAL_MIN = 0.18
CELL_PX = 40
DISC_RADIUS_FRAC = 0.38  # fraction of the cell size sampled for classification


def rgb_to_hsv(arr: np.ndarray) -> np.ndarray:
    """Vectorised RGB->HSV. `arr` is float in [0,1], shape (..., 3)."""
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    mx = arr.max(axis=-1)
    mn = arr.min(axis=-1)
    diff = mx - mn
    h = np.zeros_like(mx)
    mask = diff > 1e-12
    idx = (mx == r) & mask
    h[idx] = (60 * ((g[idx] - b[idx]) / diff[idx])) % 360
    idx = (mx == g) & mask
    h[idx] = 60 * ((b[idx] - r[idx]) / diff[idx]) + 120
    idx = (mx == b) & mask
    h[idx] = 60 * ((r[idx] - g[idx]) / diff[idx]) + 240
    s = np.where(mx > 1e-12, diff / np.maximum(mx, 1e-12), 0.0)
    return np.stack([h, s, mx], axis=-1)


REFERENCE_HSV = {
    name: rgb_to_hsv(np.array(rgb, dtype=float) / 255.0)
    for name, rgb in REFERENCE_RGB.items()
}


def render_board(board: Board, cell_px: int = CELL_PX, noise: float = 0.0,
                 seed: int = 0) -> np.ndarray:
    """Render a board as an RGB uint8 image, roughly what a webcam would see."""
    rng = np.random.default_rng(seed)
    h, w = board.rows * cell_px, board.cols * cell_px
    img = np.zeros((h, w, 3), dtype=float)
    img[:, :] = BACKGROUND_RGB
    yy, xx = np.mgrid[0:cell_px, 0:cell_px]
    centre = (cell_px - 1) / 2.0
    dist = np.sqrt((yy - centre) ** 2 + (xx - centre) ** 2)
    chip_mask = dist <= cell_px * 0.42
    ring_mask = (dist > cell_px * 0.44) & (dist <= cell_px * 0.48)
    for row in range(board.rows):
        for col in range(board.cols):
            # row 0 is the bottom row; images have y growing downwards
            y0 = (board.rows - 1 - row) * cell_px
            x0 = col * cell_px
            tile = img[y0:y0 + cell_px, x0:x0 + cell_px]
            tile[ring_mask] = FRAME_RGB
            color = board.cells[row][col]
            if color is not None:
                tile[chip_mask] = REFERENCE_RGB[color]
    if noise > 0:
        img += rng.normal(0.0, noise * 255.0, img.shape)
    return np.clip(img, 0, 255).astype(np.uint8)


def classify_cell(tile: np.ndarray) -> str | None:
    """Classify one cell tile into a chip colour, or None for empty."""
    cell_px = tile.shape[0]
    yy, xx = np.mgrid[0:cell_px, 0:tile.shape[1]]
    centre_y = (cell_px - 1) / 2.0
    centre_x = (tile.shape[1] - 1) / 2.0
    dist = np.sqrt((yy - centre_y) ** 2 + (xx - centre_x) ** 2)
    disc = dist <= cell_px * DISC_RADIUS_FRAC
    px = tile[disc].astype(float) / 255.0
    hsv = rgb_to_hsv(px)
    h_med = float(np.median(np.cos(np.deg2rad(hsv[:, 0])))), float(
        np.median(np.sin(np.deg2rad(hsv[:, 0])))
    )
    hue = float(np.rad2deg(np.arctan2(h_med[1], h_med[0])) % 360)
    sat = float(np.median(hsv[:, 1]))
    val = float(np.median(hsv[:, 2]))
    if sat < SAT_MIN or val < VAL_MIN:
        return None
    best, best_d = None, 1e9
    for name in COLORS:
        ref = REFERENCE_HSV[name]
        d = abs((hue - float(ref[0]) + 180) % 360 - 180)
        if d < best_d:
            best, best_d = name, d
    return best


def detect_board(img: np.ndarray, rows: int = 8, cols: int = 8,
                 config: str = "A") -> Board:
    """Recover the grid state from a frame."""
    cell_h = img.shape[0] // rows
    cell_w = img.shape[1] // cols
    board = Board(rows=rows, cols=cols, config=config)
    for row in range(rows):
        y0 = (rows - 1 - row) * cell_h
        for col in range(cols):
            tile = img[y0:y0 + cell_h, col * cell_w:(col + 1) * cell_w]
            board.cells[row][col] = classify_cell(tile)
    return board
