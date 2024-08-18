import sys
import cv2

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider
from PySide6.QtGui import QPixmap, QImage, QIcon
from PySide6.QtCore import Qt, QUrl

from segment_anything_2_ui.configs.config import UiConfig
from segment_anything_2_ui.ui.media_player import MediaPlayer
from segment_anything_2_ui.ui.settings_widget import SettingsWidget

class PyVideoPlayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Segment Anything 2 UI")
        self.move(100, 100)
        self.config = UiConfig()
        self.mediaPlayer = MediaPlayer(cv2.VideoCapture("video.avi"), config=self.config)

        self.thumbnail_widget = QWidget()
        self.thumbnail = QHBoxLayout()
        self.thumbnail_widget.setLayout(self.thumbnail)
        self.settings_widget = SettingsWidget()
        self.timeLabel = QLabel()
        self.timeLabel.setStyleSheet(
            "color: #4f5b6e; font-family: 'Roboto'; font-size: 9pt; font-weight: bold;"
        )
        # Set up the layout

        layout = QVBoxLayout()
        layout.addWidget(self.mediaPlayer)
        layout.addWidget(self.thumbnail_widget)

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.settings_widget)
        layout.setContentsMargins(10, 0, 10, 0)
        hlayout.addLayout(layout)
        self.setLayout(hlayout)

    def setMedia(self, fileName):
        self.generate_thumbnail_previews(fileName)
        self.mediaPlayer.setSource(QUrl.fromLocalFile(fileName))
        self.playButton.setEnabled(True)
        self.play()

    def generate_thumbnail_previews(self, url):
        video_capture = cv2.VideoCapture(url)
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
            label = QLabel()
            label.setPixmap(thumbnail.scaled(100, 100, Qt.KeepAspectRatio))
            self.thumbnail.addWidget(label)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        print("Error: " + self.mediaPlayer.errorString())


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        ex = PyVideoPlayer()
        ex.resize(720, 480)
        ex.show()
        sys.exit(app.exec())
    except KeyboardInterrupt:
        exit()