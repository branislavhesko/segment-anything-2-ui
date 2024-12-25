from enum import Enum


class PaintType(Enum):
    POINT = 0
    BOX = 1
    MASK = 2
    POLYGON = 3
    MASK_PICKER = 4
    ZOOM_PICKER = 5


class PredictionResult:
    def __init__(self, masks, scores, logits):
        self.masks = masks
        self.scores = scores
        self.logits = logits
