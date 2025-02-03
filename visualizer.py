import safetensors
from safetensors.torch import load_file
import torch


def load_inference(path):
    frames = load_file(path)
    keys = list(frames.keys())
    sorted_keys = sorted(keys, key=lambda x: int(x.split("_")[-1]))
    print(sorted_keys)
    new_frames = [frames[key] for key in sorted_keys]
    return torch.stack(new_frames)


def visualize_inference(inference):
    from vedo import dataurl, Volume, show, BoxCutter
    from vedo.applications import RayCastPlotter

    vol = Volume(inference.numpy())

    vol.mode(1).cmap("jet")  # change visual properties

    # Create a Plotter instance and show
    plt = RayCastPlotter(vol, bg='black', bg2='blackboard', axes=7)
    plt.show(viewup="z")
    plt.close()

if __name__ == "__main__":
    inference = load_inference("wtf.safetensors")
    print(inference.shape)
    visualize_inference(inference)
