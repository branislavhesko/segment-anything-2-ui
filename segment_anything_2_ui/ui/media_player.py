import cv2
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QDialog, QMessageBox, QWidget, QSlider, QPushButton, QVBoxLayout, QHBoxLayout

from segment_anything_2_ui.configs.config import UiConfig
from segment_anything_2_ui.ui.image_label import ImageLabel
from segment_anything_2_ui.ui.image_pixmap import ImagePixmap


class MediaPlayer(QWidget):

    def __init__(self, video: cv2.VideoCapture, config: UiConfig):
        super().__init__()
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
        self.move_to_frame(0)
        
    def on_slider_moved(self):
        self.move_to_frame(self.position_slider.value())
        
    def move_to_frame(self, frame_number):
        self.video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        self.current_frame = frame_number
        self.image_label.setPixmap(ImagePixmap.fromarray(self[frame_number]))
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
            self.image_label.setPixmap(ImagePixmap.fromarray(frame))
        else:
            self.current_frame = 0
        self.position_slider.setValue(self.current_frame)
            
    def __getitem__(self, index):
        self.video.set(cv2.CAP_PROP_POS_FRAMES, index)
        ret, frame = self.video.read()
        if ret:
            return frame
        else:
            QMessageBox.warning(QDialog(), "Video Ended", "Video has ended")
            return None
