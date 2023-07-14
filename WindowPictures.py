from PyQt6.QtWidgets import *
from PIL import Image
from PyQt6.QtGui import *
import os
import time

class WindowPictures(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stacklayout = QStackedLayout()
        pagelayout = QVBoxLayout()
        pagelayout.addLayout(self.stacklayout)
        widget = QWidget()
        widget.setLayout(pagelayout)
        self.setCentralWidget(widget)
        self.stacklayout.setCurrentIndex(0)
        self.title = "Image Viewer"
        self.setWindowTitle(self.title)
        self.numberOfPictures=0
        self.actualPicture=0

    def resizePicture(self,directory, filename):
        image = Image.open(os.path.join(directory, filename))
        new_image = image.resize((400, 400))
        new_image.save(directory+'\\'+'resized\\'+filename)
    def addPictures(self):
        directory = 'resources'
        secondDirectory='resources\\resized\\'
        for filename in os.listdir(directory):
            f = os.path.join(directory, filename)
            if os.path.isfile(f):
                self.resizePicture(directory, filename)
                pixmap = QPixmap(secondDirectory+filename)
                label = QLabel()
                label.setPixmap(pixmap)
                self.stacklayout.addWidget(label)
                self.numberOfPictures=self.numberOfPictures+1
    def changePicture(self,progress_callback):
        while self.actualPicture<self.numberOfPictures:
            self.stacklayout.setCurrentIndex(self.actualPicture)
            self.actualPicture=self.actualPicture+1
           # self.stacklayout.setCurrentIndex(self.actualPicture)
            time.sleep(2)
            progress_callback.emit(100 / 4)
        self.actualPicture=0
        return "Done"