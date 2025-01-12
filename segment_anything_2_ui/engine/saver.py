import pathlib

from safetensors.torch import save_file, load_file

from segment_anything_2_ui.configs.config import UiConfig
from segment_anything_2_ui.engine.video_prediction import VideoPredictionData


class InferenceSaver:
    def __init__(self, config: UiConfig):
        self.config = config

    def save_inference(self, media_path: str, video_prediction_data: VideoPredictionData, save_raw: bool = False):
        extension = pathlib.Path(media_path).suffix
        prediction_dict = video_prediction_data.to_dict(save_raw=save_raw)
        save_file(prediction_dict, media_path.replace(extension, ".safetensors"), metadata={})
    
    def load_inference(self, file_path: str) -> VideoPredictionData:
        return VideoPredictionData.from_dict(load_file(file_path))
