import copy
from enum import Enum

import cv2
import numpy as np
import PySide6
from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QPainter, QPen
from PySide6.QtMultimediaWidgets import QVideoWidget

from segment_anything_2_ui.configs.config import UiConfig
from segment_anything_2_ui.utils.shape import BoundingBox, Polygon
from segment_anything_2_ui.utils.structures import PaintType


class MaskIdPicker:

    def __init__(self, length) -> None:
        self.counter = 0
        self.length = length

    def increment(self):
        self.counter = (self.counter + 1) % self.length

    def pick(self, ids):
        print("Length of ids: ", len(ids), " counter: ", self.counter, " ids: ", ids)
        if len(ids) <= self.counter:
            self.counter = 0
        return_id = ids[self.counter]
        self.increment()
        return return_id


class ImageLabel(QtWidgets.QLabel):

    def __init__(self, parent=None, config: UiConfig | None = None):
        super().__init__()
        self.parent = parent
        self.video_predictor = self.parent.parent.video_predictor
        self.positive_points = []
        self.negative_points = []
        self.bounding_box = None
        self.partial_box = BoundingBox(0, 0)
        self._paint_type = PaintType.POINT
        self.polygon = Polygon()
        self.mask_enum: MaskIdPicker = MaskIdPicker(3)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self._zoom_center = (0, 0)
        self._zoom_factor = 1.0
        self._zoom_bounding_box: BoundingBox | None = None
        self.config = config
    
    @property
    def frame_idx(self):
        return self.parent.current_frame

    def paintEvent(self, paint_event):
        print("Painting event")
        super().paintEvent(paint_event)
        painter = QPainter(self)
        pen_positive = self._get_pen(QtCore.Qt.green, 5)
        pen_negative = self._get_pen(QtCore.Qt.red, 5)
        pen_partial = self._get_pen(QtCore.Qt.yellow, 1)
        pen_box = self._get_pen(QtCore.Qt.green, 1)
        painter.setRenderHint(QPainter.Antialiasing, False)

        painter.setPen(pen_box)

        if self.bounding_box is not None and self.bounding_box.xend != -1 and self.bounding_box.yend != -1:
            painter.drawRect(
                self.bounding_box.xstart,
                self.bounding_box.ystart,
                self.bounding_box.xend - self.bounding_box.xstart,
                self.bounding_box.yend - self.bounding_box.ystart
            )

        painter.setPen(pen_partial)
        painter.drawRect(self.partial_box.xstart, self.partial_box.ystart,
                         self.partial_box.xend - self.partial_box.xstart,
                         self.partial_box.yend - self.partial_box.ystart)

        painter.setPen(pen_positive)
        for pos in self.positive_points:
            painter.drawPoint(pos)

        painter.setPen(pen_negative)
        painter.setRenderHint(QPainter.Antialiasing, False)
        for pos in self.negative_points:
            painter.drawPoint(pos)

        if self.polygon.is_plotable():
            painter.setPen(pen_box)
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.drawPolygon(self.polygon.to_qpolygon())

    def _get_pen(self, color=QtCore.Qt.red, width=5):
        pen = QPen()
        pen.setWidth(width)
        pen.setColor(color)
        return pen

    @property
    def paint_type(self):
        return self._paint_type

    def change_paint_type(self, paint_type: PaintType):
        print(f"Changing paint type to {paint_type}")
        self._paint_type = paint_type

    def mouseMoveEvent(self, ev: PySide6.QtGui.QMouseEvent) -> None:
        if self._paint_type in [PaintType.BOX, PaintType.ZOOM_PICKER]:
            self.partial_box = copy.deepcopy(self.bounding_box)
            self.partial_box.xend = ev.pos().x()
            self.partial_box.yend = ev.pos().y()
            self.update()

        if self._paint_type == PaintType.POINT:
            point = ev.pos()
            if ev.buttons() == QtCore.Qt.LeftButton:
                self._move_update(None, point)
            elif ev.buttons() == QtCore.Qt.RightButton:
                self._move_update(point, None)
            else:
                pass
        self.update()

    def _move_update(self, temporary_point_negative, temporary_point_positive):
        # TODO: add new object id
        pass

    def mouseReleaseEvent(self, cursor_event):
        if self._paint_type == PaintType.POINT:
            if cursor_event.button() == QtCore.Qt.LeftButton:
                self.positive_points.append(cursor_event.pos())
                print(self.size())
            elif cursor_event.button() == QtCore.Qt.RightButton:
                self.negative_points.append(cursor_event.pos())
            out_obj_ids, out_mask_logits = self.video_predictor.add_new_points_box(
                frame_idx=self.frame_idx,
                object_idx=0,
                points=np.array([[cursor_event.pos().x(), cursor_event.pos().y()]]),
                labels=np.array([1]) if cursor_event.button() == QtCore.Qt.LeftButton else np.array([0])
            )
            self.visualize_mask(out_obj_ids, out_mask_logits)
            # self.chosen_points.append(self.mapFromGlobal(QtGui.QCursor.pos()))
        elif self._paint_type in [PaintType.BOX, PaintType.ZOOM_PICKER]:
            if cursor_event.button() == QtCore.Qt.LeftButton:
                self.bounding_box.xend = cursor_event.pos().x()
                self.bounding_box.yend = cursor_event.pos().y()
                self.partial_box = BoundingBox(-1, -1, -1, -1)

        self.update()

    def mousePressEvent(self, ev: PySide6.QtGui.QMouseEvent) -> None:
        if self._paint_type in [PaintType.BOX, PaintType.ZOOM_PICKER] and ev.button() == QtCore.Qt.LeftButton:
            self.bounding_box = BoundingBox(xstart=ev.pos().x(), ystart=ev.pos().y())

        if self._paint_type == PaintType.POLYGON and ev.button() == QtCore.Qt.LeftButton:
            self.polygon.points.append([ev.pos().x(), ev.pos().y()])

        if self._paint_type == PaintType.POINT:
            point = ev.pos()
            if ev.button() == QtCore.Qt.LeftButton:
                self._move_update(None, point)
            if ev.button() == QtCore.Qt.RightButton:
                self._move_update(point, None)
        self.update()

    def keyPressEvent(self, ev: PySide6.QtGui.QKeyEvent) -> None:
        print(ev.key())
        if self._paint_type == PaintType.MASK_PICKER and ev.key() == QtCore.Qt.Key.Key_D and len(self.parent().annotator.masks):
            print("Deleting mask")
            self.parent().annotator.masks.pop(self.parent().annotator.masks.mask_id)
            self.parent().annotator.masks.mask_id = -1
            self.parent().annotator.last_mask = None
            self.parent().update(self.parent().annotator.merge_image_visualization())
            
    def visualize_mask(self, out_obj_ids, out_mask_logits):
        pass

    def _get_scale(self):
        return self.config.image_size[0] / self.size().width(), self.config.image_size[1] / self.size().height()

    def get_annotations(
            self, 
            temporary_point_positive: PySide6.QtCore.QPoint | None = None, 
            temporary_point_negative: PySide6.QtCore.QPoint | None = None
        ):
        sx, sy = self._get_scale()
        positive_points = [(
            p.x() * sx,
            p.y() * sy) for p in self.positive_points]
        negative_points = [(
            p.x() * sx,
            p.y() * sy) for p in self.negative_points]
        
        if temporary_point_positive:
            positive_points += [(temporary_point_positive.x() * sx, temporary_point_positive.y() * sy)]
        if temporary_point_negative:
            negative_points += [(temporary_point_negative.x() * sx, temporary_point_negative.y() * sy)]
        
        positive_points = np.array(positive_points).reshape(-1, 2)
        negative_points = np.array(negative_points).reshape(-1, 2)
        labels = np.array([1, ] * len(positive_points) + [0, ] * len(negative_points))
        print(f"Positive points: {positive_points}")
        print(f"Negative points: {negative_points}")
        print(f"Labels: {labels}")
        return {
            "points": np.concatenate([positive_points, negative_points], axis=0),
            "labels": labels,
            "bounding_boxes": self.bounding_box.scale(sx, sy).to_numpy() if self.bounding_box else None
        }

    def clear(self):
        self.positive_points = []
        self.negative_points = []
        self.bounding_box = None
        self.partial_box = BoundingBox(0, 0, 0, 0)
        self.polygon = Polygon()
        self.update()