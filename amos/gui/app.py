import sys, os, shutil
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QStatusBar, QMenuBar, QMessageBox, QComboBox, QApplication, QMainWindow
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QCoreApplication, QRect, QMetaObject
from amos.gui.label import *

class UI_MainWindow(QWidget):
    """
    Window of the application
    Attributes
    ----------
    window_width : int
        Width of the window
    window_height : int
        Height of the window
    button_width : int
        Width of buttons
    button_height : int
        Height of buttons
    dist : int
        Distance to the edge of Widgets(Window/Button/Label...)
    """
    window_width = 800
    window_height = 650
    button_width = 180
    button_height = 50
    dist = 30

    def __init__(self, parent) -> None:
        """
        Creates new configured instance of a Label
        """
        super().__init__(parent)
  
        main_window.setObjectName("main_window")
        main_window.resize(self.window_width, self.window_height)
        self.centralwidget = QWidget(main_window)
        self.centralwidget.setObjectName("centralwidget")
       
        self.Box_Stadt = QComboBox(self.centralwidget)
        self.Box_Stadt.setGeometry(QRect(self.dist, self.dist, self.button_width, self.button_height))
        self.Box_Stadt.setObjectName("Box_Stadt")
        self.Box_Stadt.addItem("")
        self.Box_Stadt.addItem("")
        self.Box_Stadt.activated.connect(self.show_popup)

        self.Button_Detection = QPushButton(self.centralwidget)
        self.Button_Detection.setGeometry(QRect(self.window_width-(self.dist+self.button_width), self.window_height-(self.dist+self.button_height), self.button_width, self.button_height))
        self.Button_Detection.setObjectName("Button_Detection")
        self.Button_Detection.clicked.connect(self.start_detection)

        self.Button_Bild = QPushButton(self.centralwidget)
        self.Button_Bild.setGeometry(QRect(self.dist, self.window_height-(self.dist+self.button_height), self.button_width, self.button_height))
        self.Button_Bild.setObjectName("Button_Bild")
        self.Button_Bild.clicked.connect(self.dragdrop)

        self.Label_Bild = Image_Label(self.centralwidget)
        label_height = (self.window_height - self.dist - self.button_height - self.dist) - (self.dist + self.button_height + self.dist)
        label_startY = self.dist + self.button_height + self.dist
        self.Label_Bild.setGeometry(QRect(self.dist, label_startY, self.window_width-(self.dist*2), label_height))

        main_window.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(main_window)
        self.menubar.setGeometry(QRect(0, 0, 678, 21))
        self.menubar.setObjectName("menubar")
        main_window.setMenuBar(self.menubar)

        self.statusbar = QStatusBar(main_window)
        self.statusbar.setObjectName("statusbar")
        main_window.setStatusBar(self.statusbar)

        main_window.setWindowIcon(QIcon("icon_logo.png"))

        self.retranslateUi(main_window)
        QMetaObject.connectSlotsByName(main_window)

    def retranslateUi(self, main_window : QMainWindow) -> None:
        """
        Set the text initially of all items
        Parameters
        ----------
        main_window: QMainWindow
            The instance of the prepared application window
        """
        window = "main_window"
        _translate = QCoreApplication.translate
        main_window.setWindowTitle(_translate(window, "SightScan"))
        self.Box_Stadt.setItemText(0, _translate(window, "Choose City"))
        self.Box_Stadt.setItemText(1, _translate(window, "Berlin"))
        self.Button_Detection.setText(_translate(window, "Start Detection"))
        self.Button_Bild.setText(_translate(window, "Enable File Drop"))

    def show_popup(self) -> None:
        """
        Shows pop-up for confirming the download of the selected city
        """
        if self.Box_Stadt.currentIndex() > 0:
            msg = QMessageBox()
            msg.setWindowTitle("Download City")
            msg.setWindowIcon(QIcon("icon_logo.png"))
            msg.setText("Do you want to download " + self.Box_Stadt.currentText() + "?")
            msg.setIcon(QMessageBox.Question)
            msg.setStandardButtons(QMessageBox.Cancel|QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            msg.setInformativeText("When downloaded sights of " + self.Box_Stadt.currentText() + " can be detected.")

            msg.buttonClicked.connect(self.handover_city)

            x = msg.exec_()

    def handover_city(self, button) -> None:
        """
        Starts the download of the pretrained model of the selected city
        Parameters
        ----------
        button:
            Pushed button inside the popup
        """
        if button.text() == "OK":
            city = self.Box_Stadt.currentText()
            print(city)
            # start download of model with city

    def start_detection (self) -> None:
        """
        Starts detection for the dropped image with the downloaded model and displays the result in the label
        """
        print('start detection of ' + self.Label_Bild.image)

        image_index = self.Label_Bild.image.rfind('/')
        image = self.Label_Bild.image[image_index:]
        yoloPath = './../mts/yolov5'
        guiPath = './../../gui'
        image_dir = "./data/images/"
        detect_dir = "/runs/detect/"
        os.chdir(yoloPath)

        # delete images from data
        if( os.path.isdir(image_dir) == True ):
            for file in os.listdir(image_dir):
                os.remove(image_dir + file)
        # create images directory
        elif( os.path.isdir(image_dir) == False ):
            os.mkdir(image_dir)

        # copy image to data
        shutil.copy2(self.Label_Bild.image, image_dir)

        # start python script
        os.system('python ./detect.py --weights ./weights/best.pt')

        os.chdir(guiPath)
        # set image in label from most recent exp-dir in yolo
        dirs = [(yoloPath + detect_dir + d) for d in os.listdir(yoloPath + detect_dir)]
        newestDir = max(dirs, key=os.path.getmtime)
        image = newestDir + '/' + image
        self.Label_Bild.setPixmap(QPixmap(image))

    def dragdrop(self) -> None:
        """
        Enable / Disable Drag&Drop of images
        """
        disable = "Disable File Drop"
        enable = "Enable File Drop"
        window = "MainWindow"
        if self.Button_Bild.text() == enable:
            self.Label_Bild.setAcceptDrops(True)
            self.Label_Bild.setText('\n\n Drop Image here \n\n')
            self.Label_Bild.setStyleSheet('''
                QLabel{
                    border: 4px dashed #aaa
                }
            ''')
            self.Button_Bild.setText(QCoreApplication.translate(window, disable))
        elif self.Button_Bild.text() == disable:
            self.Label_Bild.setAcceptDrops(False)
            self.Label_Bild.setText("")
            self.Label_Bild.setStyleSheet('')
            self.Label_Bild.setPixmap(QPixmap(self.Label_Bild.image))
            self.Label_Bild.image = "logo.png"
            self.Button_Bild.setText(QCoreApplication.translate(window, enable))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    ui = UI_MainWindow(main_window)
    main_window.show()
    sys.exit(app.exec_())
