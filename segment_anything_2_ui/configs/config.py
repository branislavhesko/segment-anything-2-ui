import dataclasses
import os

@dataclasses.dataclass
class UiConfig:
    image_size: tuple[int, int] = (1024, 1024)
    mask_id_picker_length: int = 3
    sam2_checkpoint = os.path.join(os.getcwd(), "checkpoints", "sam2.1_hiera_tiny.pt")
    sam2_model_cfg = "sam2.1_hiera_t.yaml"
    config_path = os.path.join(os.getcwd(), "segment_anything_2_ui", "assets", "sam2_configs")