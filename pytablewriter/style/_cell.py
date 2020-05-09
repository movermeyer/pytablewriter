from typing import Any

from ._style import Style


# @dataclass  # starting PYthon 3.7
class Cell:
    def __init__(self, row: int, col: int, value: Any, default_style: Style):
        self.row = row
        self.col = col
        self.value = value
        self.default_style = default_style

    def is_header_row(self) -> bool:
        """
        Return |True| if the cell is a header.
        """

        return self.row < 0
