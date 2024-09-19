import numpy as np
import torch


def load_from_numpy_frames(
        frames: np.ndarray,
        image_size: int,
        offload_video_to_cpu: bool,
        img_mean: tuple[float, float, float] = (0.485, 0.456, 0.406),
        img_std: tuple[float, float, float] = (0.229, 0.224, 0.225),
        compute_device: torch.device = torch.device("cpu"),
        async_loading_frames: bool = False
    ) -> tuple[torch.Tensor, int, int]:
    """
    Load video frames from a numpy array.
    """
    img_mean = torch.tensor(img_mean, dtype=torch.float32)[:, None, None]
    img_std = torch.tensor(img_std, dtype=torch.float32)[:, None, None]
    if frames.dtype == np.uint8:
        frames = frames / 255.0
    print(frames.shape)
    frames = torch.from_numpy(frames).permute(0, 3, 1, 2)
    if not offload_video_to_cpu:
        frames = frames.to(compute_device, non_blocking=True)
    print(frames.shape)
    frames -= img_mean
    frames /= img_std
    frames = torch.nn.functional.interpolate(frames, size=(image_size, image_size), mode='bilinear', align_corners=False)
    return frames, frames.shape[2], frames.shape[3]