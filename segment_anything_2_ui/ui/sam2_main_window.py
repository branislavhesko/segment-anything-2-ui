import sys
import cv2

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider
from PySide6.QtGui import QPixmap, QImage, QIcon
from PySide6.QtCore import Qt, QUrl
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtMultimedia import QMediaPlayer


class PyVideoPlayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.mediaPlayer = QMediaPlayer()
        videoWidget = QVideoWidget()

        self.thumbnail_widget = QWidget()
        self.thumbnail = QHBoxLayout()
        self.thumbnail_widget.setLayout(self.thumbnail)

        self.playButton = QPushButton()
        self.playButton.setIcon(QIcon("segment_anything_2_ui/assets/play.svg"))
        self.playButton.setEnabled(False)
        self.playButton.clicked.connect(self.play)

        self.positionSlider = QSlider(orientation=Qt.Orientation.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.timeLabel = QLabel()
        self.timeLabel.setStyleSheet(
            "color: #4f5b6e; font-family: 'Roboto'; font-size: 9pt; font-weight: bold;"
        )
        # Set up the layout
        videoLayout = QVBoxLayout()
        videoLayout.addWidget(videoWidget, stretch=1)

        controlLayout = QHBoxLayout()
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.timeLabel)

        layout = QVBoxLayout()
        layout.addLayout(videoLayout)
        layout.addWidget(self.positionSlider)
        layout.addWidget(self.thumbnail_widget)
        layout.addLayout(controlLayout)

        layout.setContentsMargins(10, 0, 10, 0)

        self.setLayout(layout)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.playbackStateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.errorOccurred.connect(self.handleError)

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

    def play(self):
        if self.mediaPlayer.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.playButton.setIcon(QIcon("gui/images/svg_icons/icon_pause.svg"))
        else:
            self.playButton.setIcon(QIcon("gui/images/svg_icons/icon_play.svg"))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)
        self.timeLabel.setText(
            f"{position // 60000:02}:{(position // 1000) % 60:02} / {self.mediaPlayer.duration() // 60000:02}:{(self.mediaPlayer.duration() // 1000) % 60:02}"
        )
        
    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

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
        ex.setMedia("video.avi")  # Replace with your video file path
        ex.show()
        sys.exit(app.exec())
    except KeyboardInterrupt:
        exit()