# Segment Anything 2 UI

Segment Anything 2 UI is a graphical user interface for video annotation, built using PySide6. It is inspired by Meta's demo web page and allows users to annotate videos with various tools such as bounding boxes, masks, and points.

This UI wraps the [Segment Anything 2](https://github.com/facebookresearch/sam2) model.

## Features

- **Video Playback**: Play, pause, and navigate through video frames.
- **Annotation Tools**: Annotate videos using bounding boxes, masks, and points.
- **Visualization Modes**: Toggle between different visualization modes, including image and image with mask.
- **Thumbnail Previews**: Generate and display thumbnail previews for quick navigation.
- **Configurable Settings**: Customize settings through a dedicated settings widget.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/segment-anything-2-ui.git
   cd segment-anything-2-ui
   ```

2. **Install dependencies**:
   Make sure you have Python 3.10+ installed. Then, install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Download the SAM2 model checkpoint**:
   Place the `sam2_hiera_small.pt` checkpoint file in the `checkpoints` directory.

## Usage

1. **Run the application**:
   ```bash
   export PYTHONPATH=$PYTHONPATH:.
   python segment_anything_2_ui/ui/sam2_main_window.py
   ```

2. **Load a video**:
   - Click on the "Load video" button in the settings widget to select a video file.

3. **Annotate the video**:
   - Use the annotation tools provided in the settings widget to annotate the video frames.

4. **Toggle visualization modes**:
   - Use the "Visualize image" button to switch between different visualization modes.

## Configuration

The application can be configured using the `UiConfig` class in `segment_anything_2_ui/configs/config.py`. You can adjust settings such as image size and model configuration.

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push them to your fork.
4. Submit a pull request with a detailed description of your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgments

- Inspired by Meta's demo web page.
- Built with PySide6 for a seamless user interface experience.
- [Segment Anything 2](https://github.com/facebookresearch/sam2) model.
- Used for annotation of videos or images.