from enum import Enum
from functools import partial

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QComboBox, QFileDialog
from PySide6.QtGui import QIntValidator
from segment_anything_2_ui.utils.structures import PaintType


class ObjectPicker(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setEditable(True)
        self.setValidator(QIntValidator())
    
    def add_object(self, object_id: int):
        self.addItem(str(object_id))
    
    def get_object(self):
        return int(self.currentText())


class SettingsWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 300, 200)
        self.setStyleSheet("background-color: #ffffff;")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.load_video = QPushButton("Load video")
        self.load_video.clicked.connect(self.load_video_clicked)
        self.layout.addWidget(self.load_video)
        self.object_picker = ObjectPicker(self)
        self.object_picker.add_object(0)
        self.layout.addWidget(self.object_picker)
        self.add_annotation = QPushButton("Add annotation")
        self.add_annotation.clicked.connect(self.add_annotation_clicked)
        self.layout.addWidget(self.add_annotation)
        self.box_annotation = QPushButton("Box annotation")
        self.mask_annotation = QPushButton("Mask annotation")
        self.point_annotation = QPushButton("Point annotation")
        self.visualitation_button = QPushButton("Visualize image")
        self.propagate = QPushButton("Propagate")
        self.propagate.setShortcut("F4")
        self.propagate.clicked.connect(self.propagate_clicked)
        self.clear_annotations = QPushButton("Clear annotations")
        self.box_annotation.clicked.connect(partial(self.set_annotation_type, PaintType.BOX))
        self.mask_annotation.clicked.connect(partial(self.set_annotation_type, PaintType.MASK))
        self.point_annotation.clicked.connect(partial(self.set_annotation_type, PaintType.POINT))
        self.clear_annotations.clicked.connect(self.clear_annotations_clicked)
        self.visualitation_button.clicked.connect(self.visualitation_clicked)
        self.layout.addWidget(self.box_annotation)
        self.layout.addWidget(self.mask_annotation)
        self.layout.addWidget(self.point_annotation)
        self.layout.addWidget(self.visualitation_button)
        self.layout.addWidget(self.propagate)
        self.layout.addWidget(self.clear_annotations)
        self.annotation_type = PaintType.POINT
        self.layout.addStretch(1)

    
    def visualitation_clicked(self):
        self.parent.media_player.image_label.visualization_mode.next()
        if self.visualitation_button.text() == "Visualize image":
            self.visualitation_button.setText("Visualize image with mask")
        else:
            self.visualitation_button.setText("Visualize image")
            
    def add_annotation_clicked(self):
        print("Adding new object, new object id: ", self.parent.video_predictor.current_object_id + 1)
        self.parent.video_predictor.add_new_object()
        self.parent.settings_widget.object_picker.add_object(self.parent.video_predictor.current_object_id)
    
    def propagate_clicked(self):
        self.parent.video_predictor.propagate()
    
    def clear_annotations_clicked(self):
        self.parent.video_predictor.cleanup()
    
    def set_annotation_type(self, annotation_type):
        self.parent.media_player.image_label.set_annotation_type(annotation_type)
        
    def load_video_clicked(self):
        self.load_video_dialog = QFileDialog()
        self.load_video_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        self.load_video_dialog.setNameFilter("Video files (*.mp4 *.avi *.mkv)")
        self.load_video_dialog.exec()
        try:
            selected_video = self.load_video_dialog.selectedFiles()[0]
            self.parent.setMedia(selected_video)
            return selected_video
        except IndexError:
            return None
