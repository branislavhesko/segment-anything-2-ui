import dataclasses


@dataclasses.dataclass
class UiConfig:
    image_size: tuple[int, int] = (1024, 1024)
    mask_id_picker_length: int = 3