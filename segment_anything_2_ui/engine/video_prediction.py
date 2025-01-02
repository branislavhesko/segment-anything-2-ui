import dataclasses
import logging
import os

import cv2
from hydra import compose
from hydra.utils import instantiate
from omegaconf import OmegaConf
import numpy as np
import torch
from tqdm import tqdm
from segment_anything_2_ui.engine.sam2_video_predictor import Sam2VideoPredictorCustom


@dataclasses.dataclass
class SingleFramePrediction:
    frame_idx: int
    obj_ids: list[int]
    mask_logits: np.ndarray
    points: np.ndarray | None = None
    labels: np.ndarray | None = None
    box: np.ndarray | None = None
    mask: np.ndarray | None = None
    object_id: int = 0
    
    
class VideoPredictionData:
    def __init__(self, max_frames: int):
        self.predictions: list[SingleFramePrediction] = [None] * max_frames
        self.current_frame_idx: int = 0
        self.max_frames: int = max_frames
        
    def add_prediction(self, prediction: SingleFramePrediction, frame_idx: int):
        self.predictions[frame_idx] = prediction
        self.current_frame_idx = frame_idx
        
    def get_prediction(self, frame_idx: int) -> SingleFramePrediction | None:
        return self.predictions[frame_idx]
    
    def clear(self):
        self.predictions = [None] * self.max_frames
        self.current_frame_idx = 0
        
    def set_video_length(self, num_frames: int):
        self.predictions = [None] * num_frames
        self.max_frames = num_frames


HF_MODEL_ID_TO_FILENAMES = {
    "facebook/sam2-hiera-tiny": (
        "configs/sam2/sam2_hiera_t.yaml",
        "sam2_hiera_tiny.pt",
    ),
    "facebook/sam2-hiera-small": (
        "configs/sam2/sam2_hiera_s.yaml",
        "sam2_hiera_small.pt",
    ),
    "facebook/sam2-hiera-base-plus": (
        "configs/sam2/sam2_hiera_b+.yaml",
        "sam2_hiera_base_plus.pt",
    ),
    "facebook/sam2-hiera-large": (
        "configs/sam2/sam2_hiera_l.yaml",
        "sam2_hiera_large.pt",
    ),
    "facebook/sam2.1-hiera-tiny": (
        "configs/sam2.1/sam2.1_hiera_t.yaml",
        "sam2.1_hiera_tiny.pt",
    ),
    "facebook/sam2.1-hiera-small": (
        "configs/sam2.1/sam2.1_hiera_s.yaml",
        "sam2.1_hiera_small.pt",
    ),
    "facebook/sam2.1-hiera-base-plus": (
        "configs/sam2.1/sam2.1_hiera_b+.yaml",
        "sam2.1_hiera_base_plus.pt",
    ),
    "facebook/sam2.1-hiera-large": (
        "configs/sam2.1/sam2.1_hiera_l.yaml",
        "sam2.1_hiera_large.pt",
    ),
}


def _hf_download(model_id):
    from huggingface_hub import hf_hub_download

    config_name, checkpoint_name = HF_MODEL_ID_TO_FILENAMES[model_id]
    ckpt_path = hf_hub_download(repo_id=model_id, filename=checkpoint_name)
    return config_name, ckpt_path


def build_sam2_hf(model_id, **kwargs):
    config_name, ckpt_path = _hf_download(model_id)
    return build_sam2_video_predictor(config_file=config_name, ckpt_path=ckpt_path, **kwargs)


def build_sam2_video_predictor_hf(model_id, **kwargs):
    config_name, ckpt_path = _hf_download(model_id)
    return build_sam2_video_predictor(
        config_file=config_name, ckpt_path=ckpt_path, **kwargs
    )


def build_sam2_video_predictor(
    config_file,
    ckpt_path=None,
    device="cuda",
    mode="eval",
    hydra_overrides_extra=[],
    apply_postprocessing=True,
    config_path=None,
    **kwargs,
) -> Sam2VideoPredictorCustom:
    hydra_overrides = [
        "++model._target_=segment_anything_2_ui.engine.sam2_video_predictor.Sam2VideoPredictorCustom",
    ]
    if apply_postprocessing:
        hydra_overrides_extra = hydra_overrides_extra.copy()
        hydra_overrides_extra += [
            # dynamically fall back to multi-mask if the single mask is not stable
            "++model.sam_mask_decoder_extra_args.dynamic_multimask_via_stability=true",
            "++model.sam_mask_decoder_extra_args.dynamic_multimask_stability_delta=0.05",
            "++model.sam_mask_decoder_extra_args.dynamic_multimask_stability_thresh=0.98",
            # the sigmoid mask logits on interacted frames with clicks in the memory encoder so that the encoded masks are exactly as what users see from clicking
            "++model.binarize_mask_from_pts_for_mem_enc=true",
            # fill small holes in the low-res masks up to `fill_hole_area` (before resizing them to the original video resolution)
            "++model.fill_hole_area=8",
        ]
    hydra_overrides.extend(hydra_overrides_extra)
    
    # Configure Hydra's config path
    from hydra.core.global_hydra import GlobalHydra
    from hydra import initialize

    # Reset Hydra's global configuration
    if GlobalHydra.instance().is_initialized():
        GlobalHydra.instance().clear()

    # NOTE: Rel path should be relative to the caller directory
    if config_path and os.path.isabs(config_path):
        caller_dir = os.path.dirname(os.path.abspath(__file__))
        rel_config_path = os.path.relpath(config_path, caller_dir)
    else:
        rel_config_path = config_path


    # Initialize Hydra with the config path
    with initialize(version_base=None, config_path=rel_config_path):
        # Read config and init model
        cfg = compose(config_name=config_file, overrides=hydra_overrides)
        OmegaConf.resolve(cfg)
        model = instantiate(cfg.model, _recursive_=True)
        _load_checkpoint(model, ckpt_path)
        model = model.to(device)
        if mode == "eval":
            model.eval()
        return model


class VideoPrediction:
    
    def __init__(self, model_cfg, checkpoint_path, config_path, max_frames: int):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.predictor = build_sam2_video_predictor(model_cfg, checkpoint_path, device=device, config_path=config_path)
        self.inference_state = None
        self.is_propagated: bool = False
        self.video_data = VideoPredictionData(max_frames)
        
    def add_video(self, video_path):
        self.inference_state = self.predictor.init_state(frames=self.load_video(video_path))
        self.predictor.reset_state(self.inference_state)
        self.video_data.set_video_length(len(self.inference_state["images"]))
        print(f"Loaded video with {len(self.inference_state['images'])} frames")

    def load_video(self, video_path):
        video = cv2.VideoCapture(video_path)
        frames = []
        while video.isOpened():
            ret, frame = video.read()
            if not ret:
                break
            frames.append(frame)
        video.release()
        return np.array(frames)

    def reset(self):
        self.predictor.reset()
        
    def add_new_points_box(self, frame_idx, object_idx, box=None, points=None, labels=None):
        # BOX is a list of 4 numbers [x1, y1, x2, y2]
        # box = np.array([300, 0, 500, 400], dtype=np.float32)
        # points = np.array([[460, 60]], dtype=np.float32)
        # labels = np.array([1], np.int32)
        _, out_obj_ids, out_mask_logits = self.predictor.add_new_points_or_box(
            inference_state=self.inference_state,
            frame_idx=frame_idx,
            obj_id=object_idx,
            points=points,
            labels=labels,
            box=box,
            clear_old_points=False
        )
        self.video_data.add_prediction(SingleFramePrediction(
            frame_idx=frame_idx, 
            obj_ids=out_obj_ids, 
            mask_logits=out_mask_logits.squeeze().numpy(),
            points=points,
            labels=labels,
            box=box,
            mask=out_mask_logits.squeeze().numpy()
        ), frame_idx)
    
    def get_segmentation_results(self, index):
        if not self.is_propagated:
            return None
        return self.segmentation_results[index]
    
    def propagate(self):
        print("Propagating mask to next frame")
        for out_frame_idx, out_obj_ids, out_mask_logits in tqdm(self.predictor.propagate_in_video(self.inference_state)):
            self.video_data.add_prediction(SingleFramePrediction(
                frame_idx=out_frame_idx, 
                obj_ids=out_obj_ids, 
                mask_logits=out_mask_logits.squeeze().numpy(),
            ), out_frame_idx)    
        self.is_propagated = True
        
    def cleanup(self):
        self.video_data.clear()
        self.predictor.reset_state(self.inference_state)
        self.inference_state = None


def _load_checkpoint(model, ckpt_path):
    if ckpt_path is not None:
        sd = torch.load(ckpt_path, map_location="cpu")["model"]
        missing_keys, unexpected_keys = model.load_state_dict(sd)
        if missing_keys:
            logging.error(missing_keys)
            raise RuntimeError()
        if unexpected_keys:
            logging.error(unexpected_keys)
            raise RuntimeError()
        logging.info("Loaded checkpoint sucessfully")


if __name__ == "__main__":
    video_prediction = VideoPrediction(sam2_checkpoint, model_cfg)
    video_prediction.add_video("/Users/brani/code/segment-anything-2-ui/video.avi")
