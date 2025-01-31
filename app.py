import os
os.environ["QT_QPA_PLATFORM"] = "xcb"

import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QAction, QStatusBar, QPushButton, QVBoxLayout, QWidget
from screen import run, stop


class MyMainWindow(QMainWindow):
    """ Main application class"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Main window attributes
        self.display_mode = 'bar'
        self.setGeometry(300, 300, 600, 450)
        self.setWindowTitle("Vision")

        # Status bar to display information
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Information area, always useful")

        self.createActions()
        self.createMenus()

        # Central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Start and Stop buttons
        self.start_button = QPushButton("Start Capture")
        self.stop_button = QPushButton("Stop Capture")
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.stop_button)

        self.start_button.clicked.connect(self.start_capture)
        self.stop_button.clicked.connect(self.stop_capture)

        self.capture_thread = None

    def createActions(self):
        """ Create menu item actions and signal/slot connections"""
        self.exitAct = QAction(" &Quit", self)
        self.exitAct.setShortcut("Ctrl+X")
        self.exitAct.triggered.connect(self.myExit)

        self.startCaptureAct = QAction(" &Start Capture", self)
        self.startCaptureAct.setShortcut("Ctrl+S")
        self.startCaptureAct.triggered.connect(self.start_capture)

        self.stopCaptureAct = QAction(" &Stop Capture", self)
        self.stopCaptureAct.setShortcut("Ctrl+T")
        self.stopCaptureAct.triggered.connect(self.stop_capture)

    def createMenus(self):
        """ Create menus and menu items"""
        fileMenu = self.menuBar().addMenu("&Menu")
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAct)

        visionMenu = self.menuBar().addMenu("&Vision")
        visionMenu.addSeparator()
        visionMenu.addAction(self.startCaptureAct)
        visionMenu.addAction(self.stopCaptureAct)

    def myExit(self):
        """ Slot associated with exitAct, instance of QAction"""
        self.statusBar.showMessage("Quit ...")
        QApplication.quit()

    def start_capture(self):
        self.statusBar.showMessage("Starting capture ...")
        self.capture_thread = run()
        self.statusBar.showMessage("Capture started ...")

    def stop_capture(self):
        self.statusBar.showMessage("Stopping capture ...")
        stop()
        self.statusBar.showMessage("Capture stopped ...")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MyMainWindow()
    w.show()
    app.exec_()