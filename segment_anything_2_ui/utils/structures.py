from enum import Enum


class PaintType(Enum):
    POINT = 0
    BOX = 1
    MASK = 2
    POLYGON = 3
    MASK_PICKER = 4