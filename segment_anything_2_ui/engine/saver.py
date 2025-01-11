from safetensors.torch import save_file

from segment_anything_2_ui.configs.config import UiConfig
from segment_anything_2_ui.engine.video_prediction import VideoPredictionData


class InferenceSaver:
    def __init__(self, config: UiConfig):
        self.config = config

    def save_inference(self, video_prediction_data: VideoPredictionData):
        pass
    
    def load_inference(self, video_prediction_data: VideoPredictionData):
        pass
