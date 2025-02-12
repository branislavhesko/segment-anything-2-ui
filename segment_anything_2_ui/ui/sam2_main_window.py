import sys
import cv2

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider
from PySide6.QtGui import QPixmap, QImage, QIcon
from PySide6.QtCore import Qt, QUrl

from segment_anything_2_ui.configs.config import UiConfig
from segment_anything_2_ui.engine.saver import InferenceSaver
from segment_anything_2_ui.engine.video_prediction import VideoPrediction
from segment_anything_2_ui.ui.media_player import MediaPlayer
from segment_anything_2_ui.ui.settings_widget import SettingsWidget
from segment_anything_2_ui.utils.structures import build_video_capture


# TODO: add visualization to the thumbnail
class ThumbnailLabel(QLabel):
    def __init__(self, parent=None, index: int = 0):
        super().__init__()
        self.index = index
        self.parent = parent

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent.set_position(self.index)


class PyVideoPlayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Segment Anything 2 UI")
        self.move(100, 100)
        self.config = UiConfig()
        self.video_predictor = VideoPrediction(
            self.config.sam2_model_cfg, 
            self.config.sam2_checkpoint, 
            self.config.config_path, 
            max_frames=100
        )
        self.video_layout = QVBoxLayout()
        self.main_layout = QHBoxLayout()

        self.thumbnail_widget = QWidget()
        self.thumbnail = QHBoxLayout()
        self.thumbnail_widget.setLayout(self.thumbnail)
        self.settings_widget = SettingsWidget(self)
        self.time_label = QLabel()
        self.time_label.setStyleSheet(
            "color: #4f5b6e; font-family: 'Roboto'; font-size: 9pt; font-weight: bold;"
        )
        self.media_player: MediaPlayer = None
        # Set up the layout
        self.media_path = "video.avi"
        self.inference_saver = InferenceSaver(self.config)
        self.main_layout.addWidget(self.settings_widget)
        self.main_layout.setContentsMargins(10, 0, 10, 0)
        self.main_layout.addLayout(self.video_layout)
        self.setLayout(self.main_layout)
        self.set_media(self.media_path)

    def set_media(self, fileName):
        self.media_path = fileName
        if self.media_player:
            self.video_layout.removeWidget(self.media_player)
        if self.thumbnail_widget:
            self.video_layout.removeWidget(self.thumbnail_widget)
        
        self.generate_thumbnail_previews(fileName)

        self.media_player = MediaPlayer(self, build_video_capture(fileName), prediction_data=self.video_predictor.video_data, config=self.config)
        self.media_player.play_button.setEnabled(True)
        self.video_predictor.add_video(fileName, step_size=self.media_player.step_size)
        self.video_layout.addWidget(self.media_player)
        self.video_layout.addWidget(self.thumbnail_widget)
        # self.mediaPlayer.play()

    def generate_thumbnail_previews(self, url):
        while self.thumbnail.count():
            item = self.thumbnail.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        video_capture = build_video_capture(url)
        total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        interval = total_frames // 10  # Generate 10 thumbnails
        thumbnails = []

        for i in range(10):
            video_capture.set(cv2.CAP_PROP_POS_FRAMES, i * interval)
            ret, frame = video_capture.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert frame to RGB
                height, width, _ = frame.shape
                img = QPixmap.fromImage(
                    QImage(frame.data, width, height, width * 3, QImage.Format_RGB888)
                )
                thumbnails.append(img)

        video_capture.release()

        # Display thumbnails on the slider
        for i, thumbnail in enumerate(thumbnails):
            label = ThumbnailLabel(self, i * interval)
            label.setPixmap(thumbnail.scaled(100, 100, Qt.KeepAspectRatio))
            self.thumbnail.addWidget(label)

    def set_position(self, position):
        self.media_player.move_to_frame(position)

    def handle_error(self):
        print("Error: " + self.media_player.errorString())
        
    @property
    def video_data(self):
        return self.video_predictor.video_data


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        ex = PyVideoPlayer()
        ex.resize(720, 480)
        ex.show()
        sys.exit(app.exec())
    except KeyboardInterrupt:
        exit()