import cv2
import numpy as np
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QDialog, QMessageBox, QWidget, QSlider, QPushButton, QVBoxLayout, QHBoxLayout

from segment_anything_2_ui.configs.config import UiConfig
from segment_anything_2_ui.ui.image_label import ImageLabel
from segment_anything_2_ui.ui.image_pixmap import ImagePixmap
from segment_anything_2_ui.engine.video_prediction import VideoPredictionData, SingleFramePrediction


COLORS = [
    (0, 255, 0),
    (255, 0, 0),
    (0, 0, 255),
    (255, 255, 0),
    (0, 255, 255),
    (255, 0, 255),
]


class VisualizationMode:
    IMAGE = "IMAGE"
    IMAGE_WITH_MASK = "IMAGE_WITH_MASK"
    
    def __init__(self):
        self.mode = VisualizationMode.IMAGE
        
    def next(self):
        if self.mode == VisualizationMode.IMAGE:
            self.mode = VisualizationMode.IMAGE_WITH_MASK
        else:
            self.mode = VisualizationMode.IMAGE
        return self.mode
    
    def prev(self):
        if self.mode == VisualizationMode.IMAGE_WITH_MASK:
            self.mode = VisualizationMode.IMAGE
        else:
            self.mode = VisualizationMode.IMAGE_WITH_MASK
        return self.mode
    
    
def make_visualization_with_mask(frame: np.ndarray, prediction: SingleFramePrediction):
    mask = prediction.mask > 0.0
    mask_colored = np.zeros_like(frame)
    mask_colored[mask] = np.array([255, 0, 0])
    return cv2.addWeighted(frame, 1.0, mask_colored, 0.2, 0)


class MediaPlayer(QWidget):

    def __init__(self, parent, video: cv2.VideoCapture, prediction_data: VideoPredictionData, config: UiConfig):
        super().__init__()
        self.parent = parent
        self.prediction_data = prediction_data
        self.visualization_mode = VisualizationMode()
        self.config = config
        self.video = video
        self.image_label = ImageLabel(parent=self, config=self.config)
        self.video_length = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.video.get(cv2.CAP_PROP_FPS)
        self.current_frame = 0
        self.position_slider = QSlider(orientation=Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, self.video_length)
        self.position_slider.sliderMoved.connect(self.on_slider_moved)
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.on_play_button)
        self.play_button.setShortcut("Space")
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.image_label)
        hbox = QHBoxLayout()
        hbox.addWidget(self.position_slider)
        hbox.addWidget(self.play_button)
        self.layout.addLayout(hbox)
        self.setLayout(self.layout)
        if self.video_length > 0:
            self.move_to_frame(0)
        else:
            self.play_button.setEnabled(False)
        
    def on_slider_moved(self):
        self.move_to_frame(self.position_slider.value())
        
    def on_visualization_mode_changed(self, mode: VisualizationMode):
        self.visualization_mode = mode
        
    def move_to_frame(self, frame_number):
        self.video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        self.current_frame = frame_number
        self.image_label.setPixmap(ImagePixmap.fromarray(self.make_visualization(self[frame_number], frame_number)))
        self.position_slider.setValue(frame_number)
        
    def on_play_button(self):
        if self.play_button.text() == "Play":
            self.play()
        else:
            self.pause()
        
    def play(self):
        self.timer.start(1000 / self.fps)
        self.play_button.setText("Pause")
        
    def pause(self):
        self.timer.stop()
        self.play_button.setText("Play")
        
    def next_frame(self):
        ret, frame = self.video.read()
        if ret:
            self.current_frame += 1
            self.image_label.setPixmap(ImagePixmap.fromarray(self.make_visualization(frame, self.current_frame)))
        else:
            self.current_frame = 0
        self.position_slider.setValue(self.current_frame)
        
    def make_visualization(self, frame: np.ndarray, frame_idx: int):
        prediction = self.prediction_data.get_prediction(frame_idx)
        if prediction is not None and self.visualization_mode.mode == VisualizationMode.IMAGE_WITH_MASK:
            return make_visualization_with_mask(frame, prediction)
        return frame
            
    def __getitem__(self, index):
        self.video.set(cv2.CAP_PROP_POS_FRAMES, index)
        ret, frame = self.video.read()
        if ret:
            return frame
        else:
            QMessageBox.warning(QDialog(), "Video Ended", "Video has ended")
            return None
