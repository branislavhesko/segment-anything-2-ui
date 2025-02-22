import dataclasses


@dataclasses.dataclass(frozen=True)
class Keybindings:
    add_annotation: str = "A"
    box_annotation: str = "B"
    mask_annotation: str = "M"
    point_annotation: str = "P"
    cancel_annotation: str = "C"
    visualize_image: str = "V"
    mask_picker: str = "D"
    load_video: str = "Ctrl+O"
    save_inference: str = "Ctrl+S"
    propagate: str = "Return"
    propagate_reverse: str = "Ctrl+Return"
    clear_annotations: str = "Delete"
    play_video: str = "W"