import sys, os, shutil
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QStatusBar, QMenuBar, QMessageBox, QComboBox, QApplication, QMainWindow
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QCoreApplication, QRect, QMetaObject

class Image_Label(QLabel):
    """
    Creates and handles with the label in the middle of the application
    Attributes
    ----------
    image : str
        path of image file
    """
    image = "logo.png"

    def __init__(self, parent) -> None:
        """
        Creates new configured instance of a label
        """
        super().__init__(parent)

        self.setText("")
        self.setPixmap(QPixmap(self.image))
        self.setScaledContents(True)
        self.setObjectName("Label_Bild")
        self.setAlignment(QtCore.Qt.AlignCenter)

    def dragEnterEvent(self, event : QtGui.QDragEnterEvent) -> None:
        """
        Handles with the enter event of the dragged image
        Parameters
        ----------
        event: QDragEnterEvent
            The identified event
        """
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event : QtGui.QDragMoveEvent) -> None:
        """
        Handles with the move event of the dragged image
        Parameters
        ----------
        event: QDragMoveEvent
            The identified event
        """
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event : QtGui.QDropEvent) -> None:
        """
        Handles with the drop event and loads the image into the label
        Parameters
        ----------
        event: QDropEvent
            The identified event
        """
        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            self.image = event.mimeData().urls()[0].toLocalFile()
            self.setPixmap(QPixmap(self.image))
            self.setStyleSheet("")
            event.accept()
        else:
            event.ignore()