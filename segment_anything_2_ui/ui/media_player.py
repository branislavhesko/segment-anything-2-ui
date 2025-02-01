import cv2
import numpy as np
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QDialog, QMessageBox, QWidget, QSlider, QPushButton, QVBoxLayout, QHBoxLayout

from segment_anything_2_ui.configs.config import UiConfig
from segment_anything_2_ui.ui.image_label import ImageLabel
from segment_anything_2_ui.ui.image_pixmap import ImagePixmap
from segment_anything_2_ui.engine.video_prediction import VideoPredictionData
    

class MediaPlayer(QWidget):

    def __init__(self, parent, video: cv2.VideoCapture, prediction_data: VideoPredictionData, config: UiConfig):
        super().__init__()
        self.parent = parent
        self.prediction_data = prediction_data
        self.config = config
        self.video = video
        self.image_label = ImageLabel(parent=self, prediction_data=self.prediction_data, config=self.config)
        self.fps = self.video.get(cv2.CAP_PROP_FPS) * self.config.video_speed
        self.current_frame = 0
        self.video_length = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.step_size = self.long_video_step_size_calculation()
        self.position_slider = QSlider(orientation=Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, self.video_length if self.step_size == 0 else self.video_length // self.step_size)
        self.position_slider.valueChanged.connect(self.on_slider_moved)
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
            
    def long_video_step_size_calculation(self):
        if self.video_length > self.config.max_frames:
            return self.video_length // self.config.max_frames
        else:
            return 0
        
    def on_slider_moved(self):
        self.move_to_frame(self.position_slider.value())
        
    def move_to_frame(self, frame_number):
        frame_number = int(frame_number)
        print(f"Moving to frame {frame_number}")
        self.current_frame = frame_number
        self.image_label.set_image(self[frame_number] if frame_number > 0 else self[0])
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
        self.increase_by_step_size(self.current_frame)
        ret, frame = self.video.read()
        if ret:
            self.current_frame += 1
            self.image_label.set_image(cv2.cvtColor(cv2.resize(frame, (1024, 1024)), cv2.COLOR_BGR2RGB))
        else:
            self.current_frame = 0
        self.position_slider.setValue(self.current_frame)
            
    def __getitem__(self, index):
        self.video.set(cv2.CAP_PROP_POS_FRAMES, index)
        self.increase_by_step_size(index)
        ret, frame = self.video.read()
        if ret:
            return cv2.cvtColor(cv2.resize(frame, (1024, 1024)), cv2.COLOR_BGR2RGB)
        else:
            QMessageBox.warning(QDialog(), "Video Ended", "Video has ended")
            return np.zeros((1024, 1024, 3), dtype=np.uint8)

    def increase_by_step_size(self, index):
        self.video.set(cv2.CAP_PROP_POS_FRAMES, index + self.step_size)
