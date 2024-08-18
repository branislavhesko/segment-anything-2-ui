from sam2.build_sam import build_sam2_video_predictor
import torch


sam2_checkpoint = "../checkpoints/sam2_hiera_large.pt"
model_cfg = "sam2_hiera_l.yaml"


class VideoPrediction:
    
    def __init__(self, checkpooint_path, model_cfg):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.predictor = build_sam2_video_predictor(model_cfg, checkpooint_path, device=device)
        
    def add_video(self, video_path):
        inference_state = self.predictor.init_state(video_path=video_path)
        return inference_state

    def reset(self):
        self.predictor.reset()