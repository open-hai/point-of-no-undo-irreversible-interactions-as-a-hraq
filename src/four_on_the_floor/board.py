"""Board state for the *4 on the Floor* speculation (paper Section 3.1.1).

Paper facts used here (Section 3.1.1):
  - "eight by eight vertically suspended grid"
  - chips are *dropped* / *thrown* into the grid (Connect-Four mechanics)
  - "The colors represent pitch or samples and the columns along the x-axis
    represent time increments."
  - stacking chips "forms chords or layers sounds"
Configuration A / B (Section 3.1.2):
  - A: "used the irreversible interaction"
  - B: "allowed removing individual chips at all times"

Everything marked ASSUMPTION below is a decision the paper does not state; see
REPRODUCIBILITY.md, "Hidden decisions".
"""

from __future__ import annotations

from dataclasses import dataclass, field

ROWS = 8  # Section 3.1.1: "eight by eight"
COLS = 8

# ASSUMPTION: chip colours. The paper shows a multi-colour grid in Fig. 2 but
# never lists the palette. We use four colours; the pitch mapping lives in
# sequencer.py.
COLORS = ("red", "yellow", "blue", "green")

EMPTY = None


class IrreversibleActionError(RuntimeError):
    """Raised when configuration A is asked to undo something."""


@dataclass
class Board:
    """An 8x8 gravity grid. cells[row][col]; row 0 is the BOTTOM row."""

    rows: int = ROWS
    cols: int = COLS
    config: str = "A"  # "A" = irreversible, "B" = chips removable
    # ASSUMPTION: in configuration B, removing a chip lets the chips above it
    # fall down one row (physical Connect-Four behaviour). The paper only says
    # "allowed removing individual chips at all times".
    collapse_on_remove: bool = True
    cells: list[list[str | None]] = field(default_factory=list)
    history: list[tuple[str, int, int, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.cells:
            self.cells = [[EMPTY] * self.cols for _ in range(self.rows)]
        if self.config not in ("A", "B"):
            raise ValueError("config must be 'A' or 'B'")

    def drop(self, col: int, color: str) -> int:
        """Drop a chip into `col`. Returns the row it lands in."""
        if color not in COLORS:
            raise ValueError(f"unknown chip colour {color!r}")
        if not 0 <= col < self.cols:
            raise ValueError(f"column {col} out of range")
        for row in range(self.rows):
            if self.cells[row][col] is EMPTY:
                self.cells[row][col] = color
                self.history.append(("drop", row, col, color))
                return row
        raise ValueError(f"column {col} is full")

    def remove(self, row: int, col: int) -> str:
        """Remove one chip. Only legal in configuration B."""
        if self.config == "A":
            raise IrreversibleActionError(
                "configuration A: a chip that has been thrown cannot be removed "
                "(paper Section 3.1.2)"
            )
        color = self.cells[row][col]
        if color is EMPTY:
            raise ValueError(f"cell ({row},{col}) is empty")
        self.cells[row][col] = EMPTY
        if self.collapse_on_remove:
            for r in range(row, self.rows - 1):
                self.cells[r][col] = self.cells[r + 1][col]
            self.cells[self.rows - 1][col] = EMPTY
        self.history.append(("remove", row, col, color))
        return color

    def occupied(self) -> list[tuple[int, int, str]]:
        return [
            (r, c, self.cells[r][c])
            for r in range(self.rows)
            for c in range(self.cols)
            if self.cells[r][c] is not EMPTY
        ]

    def as_text(self) -> str:
        glyph = {"red": "R", "yellow": "Y", "blue": "B", "green": "G", None: "."}
        lines = []
        for row in reversed(range(self.rows)):
            lines.append(" ".join(glyph[self.cells[row][c]] for c in range(self.cols)))
        return "\n".join(lines)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Board) and self.cells == other.cells
