from functools import partial

from PySide6.QtWidgets import QCheckBox, QComboBox, QFileDialog, QHBoxLayout, QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator
from segment_anything_2_ui.utils.structures import PaintType
from segment_anything_2_ui.utils.keybindings import Keybindings


class ObjectPicker(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setEditable(False)
        self.setValidator(QIntValidator())
        self._items = {}

    def add_object(self, object_id: int):
        self._items[object_id] = f"Current object {object_id}"
        self.addItem(self._items[object_id])
    
    def get_object(self):
        return int(self.currentText().split(" ")[-1])
    
    def set_current_object(self, object_id: int):
        self.setCurrentText(self._items[object_id])


class SettingsWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 300, 200)
        self.keybindings = Keybindings()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.load_video = QPushButton("Load video")
        self.load_video.clicked.connect(self.load_video_clicked)
        self.load_video.setShortcut(self.keybindings.load_video)
        self.object_picker = ObjectPicker(self)
        self.object_picker.add_object(0)
        self.object_picker.currentTextChanged.connect(self.on_object_picker_changed)
        self.add_annotation = QPushButton(f"Add annotation [{self.keybindings.add_annotation}]")
        self.add_annotation.clicked.connect(self.add_annotation_clicked)
        self.add_annotation.setShortcut(self.keybindings.add_annotation)
        self.box_annotation = QPushButton(f"Box annotation [{self.keybindings.box_annotation}]")
        self.box_annotation.setShortcut(self.keybindings.box_annotation)
        self.mask_annotation = QPushButton(f"Mask annotation [{self.keybindings.mask_annotation}]")
        self.mask_annotation.setShortcut(self.keybindings.mask_annotation)
        self.point_annotation = QPushButton(f"Point annotation [{self.keybindings.point_annotation}]")
        self.point_annotation.setShortcut(self.keybindings.point_annotation)
        self.cancel_annotation = QPushButton(f"Cancel annotation [{self.keybindings.cancel_annotation}]")
        self.cancel_annotation.clicked.connect(self.cancel_annotation_clicked)
        self.cancel_annotation.setShortcut(self.keybindings.cancel_annotation)
        self.mask_picker = QPushButton(f"Mask picker [{self.keybindings.mask_picker}]")
        self.mask_picker.clicked.connect(self.mask_picker_clicked)
        self.mask_picker.setShortcut(self.keybindings.mask_picker)
        self.visualization_button = QPushButton(f"Visualize image [{self.keybindings.visualize_image}]")
        self.visualization_button.setShortcut(self.keybindings.visualize_image)
        self.propagate = QPushButton(f"Propagate [{self.keybindings.propagate}]")
        self.propagate.setShortcut(self.keybindings.propagate)
        self.propagate.clicked.connect(self.propagate_clicked)
        self.propagate_reverse = QPushButton(f"Propagate reverse [{self.keybindings.propagate_reverse}]")
        self.propagate_reverse.setShortcut(self.keybindings.propagate_reverse)
        self.propagate_reverse.clicked.connect(self.propagate_reverse_clicked)
        self.clear_annotations = QPushButton(f"Clear annotations [{self.keybindings.clear_annotations}]")
        self.clear_annotations.setShortcut(self.keybindings.clear_annotations)
        self.box_annotation.clicked.connect(partial(self.set_annotation_type, PaintType.BOX))
        self.mask_annotation.clicked.connect(partial(self.set_annotation_type, PaintType.MASK))
        self.point_annotation.clicked.connect(partial(self.set_annotation_type, PaintType.POINT))
        self.clear_annotations.clicked.connect(self.clear_annotations_clicked)
        self.visualization_button.clicked.connect(self.visualitation_clicked)
        self.save_inference = QPushButton(f"Save inference [{self.keybindings.save_inference}]")
        self.save_inference.setShortcut(self.keybindings.save_inference)
        self.save_inference.clicked.connect(self.save_inference_clicked)
        self.save_raw = QCheckBox("Save raw")
        self.save_raw.setChecked(False)
        self.layout.addWidget(self.load_video)
        self.layout.addWidget(self.object_picker)
        self.layout.addWidget(self.add_annotation)
        self.layout.addWidget(self.box_annotation)
        self.layout.addWidget(self.mask_annotation)
        self.layout.addWidget(self.point_annotation)
        self.layout.addWidget(self.cancel_annotation)
        self.layout.addWidget(self.visualization_button)
        self.layout.addWidget(self.mask_picker)
        self.layout.addWidget(self.propagate)
        self.layout.addWidget(self.propagate_reverse)
        self.layout.addWidget(self.clear_annotations)
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.save_inference)
        h_layout.addWidget(self.save_raw)
        self.layout.addLayout(h_layout)
        self.annotation_type = PaintType.POINT
        self.layout.addStretch(1)

    def on_object_picker_changed(self):
        self.parent.video_predictor.current_object_id = self.object_picker.get_object()
        
    def cancel_annotation_clicked(self):
        self.parent.media_player.image_label.clear()
        self.parent.video_predictor.clear_prompts_in_frame_for_object_id(
            self.parent.media_player.image_label.frame_idx,
        )
        self.parent.media_player.image_label.update_visualization()
        
    def mask_picker_clicked(self):
        self.parent.media_player.image_label.set_annotation_type(PaintType.MASK_PICKER)

    def save_inference_clicked(self):
        self.parent.inference_saver.save_inference(self.parent.media_path, self.parent.video_data, save_raw=self.save_raw.isChecked())
    
    def visualitation_clicked(self):
        self.parent.media_player.image_label.visualization_mode.next()
        if self.visualization_button.text() == "Visualize image":
            self.visualization_button.setText("Visualize image with mask")
        else:
            self.visualization_button.setText("Visualize image")
            
    def add_annotation_clicked(self):
        print("Adding new object, new object id: ", self.parent.video_predictor.current_object_id + 1)
        object_id = self.parent.video_predictor.add_new_object()
        self.parent.settings_widget.object_picker.add_object(object_id)
        self.parent.settings_widget.object_picker.set_current_object(object_id)

    def propagate_clicked(self):
        self.parent.video_predictor.propagate()
        
    def propagate_reverse_clicked(self):
        self.parent.video_predictor.propagate_reverse()
    
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
            self.parent.set_media(selected_video)
            return selected_video
        except IndexError:
            return None

    def keyPressEvent(self, event):
        if chr(event.key()) == self.keybindings.play_video:
            self.parent.media_player.on_play_button()
        super().keyPressEvent(event)