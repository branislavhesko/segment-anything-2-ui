from enum import Enum

import cv2
import tifffile


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
        
        
def build_video_capture(path):
    if path.endswith(".tif"):
        return TifDataset(path)
    else:
        return cv2.VideoCapture(path)


class TifDataset:
    
    def __init__(self, path):
        self.path = path
        self.position_pointer = 0
        with tifffile.TiffFile(path) as tif:
            self.frames = [frame for frame in tif.asarray()]
        
    def __getitem__(self, index):
        return self.frames[index]
    
    def read(self):
        if self.position_pointer < len(self.frames):
            frame = self.frames[self.position_pointer]
            self.position_pointer += 1
            return True, frame
        else:
            return False, None

    def get(self, property):
        match property:
            case cv2.CAP_PROP_FRAME_COUNT:
                return len(self.frames)
            
            case cv2.CAP_PROP_FPS:
                return 10
            
            case _:
                raise ValueError(f"Unsupported property: {property}")
            
    def set(self, property, value):
        match property:
            case cv2.CAP_PROP_POS_FRAMES:
                self.position_pointer = value
            case _:
                raise ValueError(f"Unsupported property: {property}")

    def release(self):
        self.frames = None
