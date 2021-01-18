"""This module contains the label component of the UI."""
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel

import os


class ImageLabel(QLabel):
    """Creates and handles the label in the middle of the application.

    Attributes
    ----------
    image : str
        path of image_name file
    """
    image = "logo.png"

    def __init__(self, parent) -> None:
        """
        Creates new configured instance of a label
        """
        super().__init__(parent)

        self.setText("")
        self.setPixmap(QPixmap(self.image))
        self.setScaledContents(False)
        self.setObjectName("Label_Bild")
        self.setAlignment(QtCore.Qt.AlignCenter)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        """Handles the enter event of the dragged image.

        Parameters
        ----------
        event: QDragEnterEvent
            The identified event
        """
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        """Handles the move event of the dragged image.

        Parameters
        ----------
        event: QDragMoveEvent
            The identified event
        """
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        """Handles the drop event and loads the image_name into the label.

        Parameters
        ----------
        event: QDropEvent
            The identified event
        """
        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            self.image = event.mimeData().urls()[0].toLocalFile()
            x = self.width()
            y = self.height()
            im = QPixmap(self.image).scaled(x, y)  # , aspectRatioMode=Qt.KeepAspectRatio)
            im.save(os.getcwd() + "/tmp.jpg")
            self.image = (os.getcwd() + "/tmp.jpg")
            self.setPixmap(im)
            # self.setPixmap(QPixmap(self.image))
            self.setStyleSheet("")
            event.accept()
        else:
            event.ignore()
