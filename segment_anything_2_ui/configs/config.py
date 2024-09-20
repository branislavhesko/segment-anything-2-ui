import dataclasses


@dataclasses.dataclass
class UiConfig:
    image_size: tuple[int, int] = (1024, 1024)
    mask_id_picker_length: int = 3
    sam2_checkpoint = "sam2_hiera_small.pt"
    sam2_model_cfg = "sam2_hiera_s.yaml"
    