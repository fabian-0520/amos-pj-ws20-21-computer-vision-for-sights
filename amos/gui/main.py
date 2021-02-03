"""This module contains the overall UI frame object and is responsible for launching it."""
from helper import wipe_prediction_input_images, get_current_prediction_output_path
from label import ImageLabel
from detect import Detection
from PyQt5.QtWidgets import (
    QWidget,
    QPushButton,
    QStatusBar,
    QMenuBar,
    QMessageBox,
    QComboBox,
    QApplication,
    QMainWindow,
    QStackedWidget,
)
from PyQt5.QtMultimedia import QCamera, QCameraInfo
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QCoreApplication, QRect, QMetaObject

from api_communication.api_handler import get_downloaded_model, get_dwh_model_version, get_supported_cities
import shutil
import sys
import os
import time
from threading import Thread

OUTPUT_PREDICTION_DIR = "./runs/detect/"
INPUT_PREDICTION_DIR = "./data/images"
START = "Start Detection"
STOP = "Stop Detection"
ENABLE = "Enable File Drop"
DISABLE = "Disable File Drop"
WINDOW = "MainWindow"


class UiMainWindow(QWidget):
	"""Main UI window of the application.

	Attributes:
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
	model_selected : bool
		Shows whether a model is selected or not
	"""

	window_width = 800
	window_height = 650
	button_width = 180
	button_height = 50
	dist = 30
	model_selected = False

	def __init__(self, parent) -> None:
		"""Creates new configured instance of the UI's main window."""
		super().__init__(parent)

		main_window.setObjectName("main_window")
		main_window.resize(self.window_width, self.window_height)
		self.centralwidget = QWidget(main_window)
		self.centralwidget.setObjectName("centralwidget")

		self.detector = Detection()

		self.Box_Stadt = QComboBox(self.centralwidget)
		self.Box_Stadt.setGeometry(QRect(self.dist, self.dist, self.button_width, self.button_height))
		self.Box_Stadt.setObjectName("Box_Stadt")
		self.Box_Stadt.activated.connect(self.show_popup)

		self.Button_Detection = QPushButton(self.centralwidget)
		self.Button_Detection.setGeometry(
			QRect(
				self.window_width - (self.dist + self.button_width),
				self.window_height - (self.dist + self.button_height),
				self.button_width,
				self.button_height,
			)
		)
		self.Button_Detection.setObjectName("Button_Detection")
		self.Button_Detection.clicked.connect(self.detect_sights)

		self.Button_Bild = QPushButton(self.centralwidget)
		self.Button_Bild.setGeometry(
			QRect(
				self.dist,
				self.window_height - (self.dist + self.button_height),
				self.button_width,
				self.button_height,
			)
		)
		self.Button_Bild.setObjectName("Button_Bild")
		self.Button_Bild.clicked.connect(lambda: self.camera_viewfinder.hide())
		self.Button_Bild.clicked.connect(lambda: self.Box_Camera_selector.setCurrentIndex(0))
		self.Button_Bild.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
		self.Button_Bild.clicked.connect(lambda: self.Label_Bild.show())
		self.Button_Bild.clicked.connect(self.dragdrop)

		self.available_cameras = QCameraInfo.availableCameras()

		self.Box_Camera_selector = QComboBox(self.centralwidget)
		self.Box_Camera_selector.setGeometry(
			QRect(
				self.window_width - (self.dist + self.button_width),
				self.dist,
				self.button_width,
				self.button_height,
			)
		)
		self.Box_Camera_selector.setObjectName("Box_Camera_selector")
		self.Box_Camera_selector.addItem("")
		self.Box_Camera_selector.addItems([camera.description() for camera in self.available_cameras])
		self.Box_Camera_selector.currentIndexChanged.connect(self.select_camera)

		self.stacked_widget = QStackedWidget(self.centralwidget)
		label_height = (self.window_height - self.dist - self.button_height - self.dist) - (
			self.dist + self.button_height + self.dist
		)
		label_start_y = self.dist + self.button_height + self.dist
		self.stacked_widget.setGeometry(
			QRect(
				self.dist,
				label_start_y,
				self.window_width - (self.dist * 2),
				label_height,
			)
		)

		self.camera_viewfinder = QCameraViewfinder()

		self.Label_Bild = ImageLabel(self)
		self.Label_Bild.setGeometry(QRect(0, 0, self.window_width - (self.dist * 2), label_height))

		self.stacked_widget.addWidget(self.Label_Bild)
		self.stacked_widget.addWidget(self.camera_viewfinder)

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

	def retranslateUi(self, main_window: QMainWindow) -> None:
		"""Set the text initially for all items.

		Parameters
		----------
		main_window: QMainWindow
		    The instance of the prepared application window
		"""
		_translate = QCoreApplication.translate
		main_window.setWindowTitle(_translate(WINDOW, "SightScan"))
		self.Box_Stadt.addItems(['Choose City'] + get_supported_cities())
		self.Box_Camera_selector.setItemText(0, _translate(WINDOW, "Choose Webcam"))
		self.Button_Detection.setText(_translate(WINDOW, START))
		self.Button_Bild.setText(_translate(WINDOW, ENABLE))

	def show_popup(self) -> None:
		"""Shows a pop-up for confirming the download of the selected city."""
		city_pretty_print = self.Box_Stadt.currentText()
		city = self.Box_Stadt.currentText().replace(' ', '_').upper()

		if city != "CHOOSE_CITY":
			downloaded_version = -1  # initialization
			if not os.path.exists("weights/versions.txt"):
			    with open('weights/versions.txt', 'w'):  # creating a version file
			        pass
			print(city)
			with open("weights/versions.txt", "r") as file:
			    for line in file:
			        elements = line.split("=")
			        if elements[0].upper() == city:
			            downloaded_version = int(elements[1])
			            break

			latest_version = get_dwh_model_version(city)

			if downloaded_version == -1:
				msg = QMessageBox()
				msg.setWindowTitle("Download City")
				msg.setWindowIcon(QIcon("icon_logo.png"))
				msg.setText("Do you want to download " + city_pretty_print + "?")
				msg.setIcon(QMessageBox.Question)
				msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
				msg.setDefaultButton(QMessageBox.Ok)
				msg.setInformativeText("When downloaded, sights of " + city_pretty_print + " can be detected.")
				msg.buttonClicked.connect(self.handover_city)

				msg.exec_()

			elif latest_version > downloaded_version:
				update_msg = QMessageBox()
				update_msg.setWindowTitle("Update available")
				update_msg.setWindowIcon(QIcon("icon_logo.png"))
				update_msg.setText("Do you want to download an update for " + city + "?")
				update_msg.setIcon(QMessageBox.Question)
				update_msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
				update_msg.setDefaultButton(QMessageBox.Ok)
				update_msg.setInformativeText(
					"Updated cities can detect sights faster and more accurately. If you choose not to download, the " +
					"detection will still work.")
				update_msg.buttonClicked.connect(self.handover_city)

				update_msg.exec_()

			else:
				self.model_selected = True
				newest_vers_msg = QMessageBox()
				newest_vers_msg.setWindowTitle("Ready for Detection!")
				newest_vers_msg.setWindowIcon(QIcon("icon_logo.png"))
				newest_vers_msg.setText("You can start detecting sights in " + city_pretty_print + "!")
				newest_vers_msg.setStandardButtons(QMessageBox.Ok)
				newest_vers_msg.setDefaultButton(QMessageBox.Ok)

				newest_vers_msg.exec_()

		else:
			self.model_selected = False

	def handover_city(self, button) -> None:
		"""Starts the download of the pre-trained model of the selected city.

		Parameters
		----------
		button:
		    Pushed button inside the popup
		"""

		if button.text() == "OK":
			city = self.Box_Stadt.currentText().replace(' ', '_').upper()
			self.model_selected = True
			model = get_downloaded_model(city)
			if model is not None:
			    with open("weights/" + city + ".pt", "wb+") as file:
			        file.write(model)
		elif button.text() == "Cancel":
			self.Box_Stadt.setCurrentIndex(0)

	def detect_sights(self) -> None:
		"""Starts detection for the dropped image or shown webcam video
		with the downloaded model and displays the results in the label."""
		city = self.Box_Stadt.currentText().replace(' ', '_').upper()

		# start drag&drop image detection
		if self.stacked_widget.currentIndex() == 0 and self.Button_Bild.text() == DISABLE and \
				self.Label_Bild.image != "logo.png":
			# if no model selected
			if self.model_selected is False:
				self.show_missing_model_popup()
			# if model selected
			else:
				print(f"Starting detection of {self.Label_Bild.image}")
				wipe_prediction_input_images(INPUT_PREDICTION_DIR)
				shutil.copy2(self.Label_Bild.image, INPUT_PREDICTION_DIR)
				self.detector.detect(self, weights='weights/' + city + '.pt')
		# stop video detection
		elif self.stacked_widget.currentIndex() == 0 and self.Button_Detection.text() == STOP:
			self.stop_video_detection()
			time.sleep(2)
			self.reactivate_cam()
		# if webcam activated
		elif self.stacked_widget.currentIndex() == 1:
			if self.Button_Detection.text() == START:
				self.Button_Detection.setText(QCoreApplication.translate(WINDOW, STOP))
				if self.model_selected is False:
					self.show_missing_model_popup()
				# start webcam detection
				else:
					print("Video Detection Started")
					self.prep_video_detection()
					self.detection_thread = Thread(target=self.detector.detect, args=(self,),
												   kwargs={'weights': 'weights/' + city + '.pt', 'source': '0',
														   'image_size': 160})
					self.detection_thread.start()
		else:
			print("Drop a File or select a Webcam!")

	def show_missing_model_popup(self) -> None:
		# Show Pop Up to choose a city
		emsg = QMessageBox()
		emsg.setWindowTitle("No city chosen")
		emsg.setWindowIcon(QIcon("icon_logo.png"))
		emsg.setText("You need to choose a city before the detection can start.")
		emsg.setIcon(QMessageBox.Warning)
		emsg.setStandardButtons(QMessageBox.Ok)
		emsg.setDefaultButton(QMessageBox.Ok)

		emsg.exec_()

	def dragdrop(self) -> None:
		"""Enables / disables Drag&Drop of images."""
		if self.Button_Bild.text() == ENABLE:
			self.Label_Bild.setAcceptDrops(True)
			self.Label_Bild.setText("\n\n Drop Image here \n\n")
			self.Label_Bild.setStyleSheet(
				"""
				QLabel{
					border: 4px dashed #aaa
				}
			"""
			)
			self.Button_Bild.setText(QCoreApplication.translate(WINDOW, DISABLE))
		elif self.Button_Bild.text() == DISABLE:
			self.Label_Bild.setAcceptDrops(False)
			self.Label_Bild.setText("")
			self.Label_Bild.setStyleSheet("")
			self.Label_Bild.image = "logo.png"
			self.Label_Bild.setPixmap(QPixmap(self.Label_Bild.image))
			self.Button_Bild.setText(QCoreApplication.translate(WINDOW, ENABLE))

	def select_camera(self, i):
		"""Starts the selected camera. If "Choose webcam" is selected, it stops the camera.

		Parameters
		----------
		i:
		    Index of the chosen camera.
		"""
		if i == 0:
			self.camera.stop()
			self.detector.disable_detection()
			self.Button_Detection.setText(QCoreApplication.translate(WINDOW, START))
			self.stacked_widget.setCurrentIndex(0)
			self.camera_viewfinder.hide()
			self.Label_Bild.show()
			time.sleep(2)
			self.Label_Bild.image = "logo.png"
			self.Label_Bild.setPixmap(QPixmap(self.Label_Bild.image))
		else:
			self.camera_viewfinder.show()
			self.stacked_widget.setCurrentIndex(1)
			self.Label_Bild.hide()
			self.camera = QCamera(self.available_cameras[i - 1])
			self.camera.setViewfinder(self.camera_viewfinder)
			self.camera.error.connect(lambda: self.alert(self.camera.errorString()))
			self.camera.start()
			self.Button_Bild.setText(QCoreApplication.translate(WINDOW, ENABLE))

	def prep_video_detection(self) -> None:
		self.camera.stop()
		self.camera_viewfinder.hide()
		self.stacked_widget.setCurrentIndex(0)
		self.Label_Bild.show()

	def stop_video_detection(self) -> None:
		self.Button_Detection.setText(QCoreApplication.translate(WINDOW, START))
		self.detector.disable_detection()
		self.stacked_widget.setCurrentIndex(1)
		self.Label_Bild.hide()
		self.camera_viewfinder.show()

	def reactivate_cam(self) -> None:
		self.Label_Bild.image = "logo.png"
		self.Label_Bild.setPixmap(QPixmap(self.Label_Bild.image))
		self.camera.start()


if __name__ == "__main__":
	# starts the UI
	app = QApplication(sys.argv)
	main_window = QMainWindow()
	ui = UiMainWindow(main_window)
	main_window.show()
	sys.exit(app.exec_())
