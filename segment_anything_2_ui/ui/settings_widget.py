from enum import Enum
from functools import partial

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QFileDialog

from segment_anything_2_ui.utils.structures import PaintType


class SettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 300, 200)
        self.setStyleSheet("background-color: #f0f0f0;")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.load_video = QPushButton("Load video")
        self.load_video.clicked.connect(self.load_video_clicked)
        self.layout.addWidget(self.load_video)
        self.box_annotation = QPushButton("Box annotation")
        self.mask_annotation = QPushButton("Mask annotation")
        self.point_annotation = QPushButton("Point annotation")
        self.box_annotation.clicked.connect(partial(self.set_annotation_type, PaintType.BOX))
        self.mask_annotation.clicked.connect(partial(self.set_annotation_type, PaintType.MASK))
        self.point_annotation.clicked.connect(partial(self.set_annotation_type, PaintType.POINT))
        self.layout.addWidget(self.box_annotation)
        self.layout.addWidget(self.mask_annotation)
        self.layout.addWidget(self.point_annotation)
        self.annotation_type = PaintType.POINT
    
    def set_annotation_type(self, annotation_type):
        self.annotation_type = annotation_type
        self.update()
        
    def load_video_clicked(self):
        self.load_video_dialog = QFileDialog()
        self.load_video_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        self.load_video_dialog.setNameFilter("Video files (*.mp4 *.avi *.mkv)")
        self.load_video_dialog.exec()
        self.load_video_dialog.selectedFiles()