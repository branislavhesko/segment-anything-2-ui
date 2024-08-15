from enum import Enum
from functools import partial

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout


class AnnotationType(Enum):
    BOX = "Box"
    MASK = "Mask"
    POINT = "Point"


class SettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 300, 200)
        self.setStyleSheet("background-color: #f0f0f0;")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.box_annotation = QPushButton("Box annotation")
        self.mask_annotation = QPushButton("Mask annotation")
        self.point_annotation = QPushButton("Point annotation")
        self.box_annotation.clicked.connect(partial(self.set_annotation_type, AnnotationType.BOX))
        self.mask_annotation.clicked.connect(partial(self.set_annotation_type, AnnotationType.MASK))
        self.point_annotation.clicked.connect(partial(self.set_annotation_type, AnnotationType.POINT))
        self.layout.addWidget(self.box_annotation)
        self.layout.addWidget(self.mask_annotation)
        self.layout.addWidget(self.point_annotation)
        self.annotation_type = AnnotationType.POINT
    
    def set_annotation_type(self, annotation_type):
        self.annotation_type = annotation_type
        self.update()