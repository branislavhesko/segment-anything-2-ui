from PySide6.QtGui import QImage, QPixmap, QPainter, QPen
from PySide6.QtCore import Qt


class ImagePixmap(QPixmap):
    def __init__(self):
        super().__init__()

    def set_image(self, image):
        if image.dtype == "uint8":
            image = image.astype("float32") / 255.0
        image = (image * 255).astype("uint8")
        image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888)
        self.convertFromImage(image)
        
    @classmethod
    def fromarray(cls, image):
        pixmap = cls()
        pixmap.set_image(image)
        return pixmap