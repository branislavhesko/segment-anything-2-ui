import logging
import cv2
from hydra import compose
from hydra.utils import instantiate
from omegaconf import OmegaConf
import numpy as np
import torch

sam2_checkpoint = "sam2_hiera_small.pt"
model_cfg = "sam2_hiera_s.yaml"

from segment_anything_2_ui.engine.sam2_video_predictor import SAM2VideoPredictor


def build_sam2_video_predictor(
    config_file,
    ckpt_path=None,
    device="cuda",
    mode="eval",
    hydra_overrides_extra=[],
    apply_postprocessing=True,
    **kwargs,
):
    hydra_overrides = [
        "++model._target_=segment_anything_2_ui.engine.sam2_video_predictor.SAM2VideoPredictor",
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
    
    def __init__(self, checkpooint_path, model_cfg):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.predictor = build_sam2_video_predictor(model_cfg, checkpooint_path, device=device)
        self.segmentation_results = {}
        self.inference_state = None
        
    def add_video(self, video_path):
        self.inference_state = self.predictor.init_state(frames=self.load_video(video_path))
        self.predictor.reset_state(self.inference_state)
    
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
        )
        return out_obj_ids, out_mask_logits
    
    def propagate(self):
        for out_frame_idx, out_obj_ids, out_mask_logits in self.predictor.propagate_in_video(self.inference_state):
            self.segmentation_results[out_frame_idx] = {
                out_obj_id: (out_mask_logits[i] > 0.0).cpu().numpy()
                for i, out_obj_id in enumerate(out_obj_ids)
            }
        return self.segmentation_results
    
    def cleanup(self):
        self.segmentation_results = {}
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
