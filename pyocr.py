#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 22:21:01 2017
@author: sylvain
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from PIL import Image
import cv2
import numpy as np
import pytesseract

# Windows Tesseract
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract'

def get_string(img_path):
    # Read image with opencv
    print('----------')
    img = cv2.imread(img_path)

    # Convert to gray
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#    # Apply dilation and erosion to remove some noise
#    kernel = np.ones((1, 1), np.uint8)
#    img = cv2.dilate(img, kernel, iterations=1)
#    img = cv2.erode(img, kernel, iterations=1)
#
    # Write image after removed noise
    cv2.imwrite("removed_noise.png", img)

#    #  Apply threshold to get image with only black and white
#    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#                                cv2.THRESH_BINARY, 51, 2)

    # Write the image after apply opencv to do some ...
    cv2.imwrite("thres.png", img)

    # Recognize text with tesseract for python
    result = pytesseract.image_to_string(Image.open("thres.png"), config='-psm 7')

    # Remove template file
    #os.remove(temp)

    print(result)

class View(QtWidgets.QLabel):
    def __init__(self):
        super().__init__()

        self.cropLabel = QtWidgets.QLabel(self)
        self.label = QtWidgets.QLabel(self)

        self.ogpixmap = QtGui.QPixmap()
        fileName = r'C:/Users/user11.HPO-SAMAT/Pictures/Lake.jpg'
        image = QtGui.QImage(fileName)
        self.pixmap = QtGui.QPixmap.fromImage(image)
        self.label.setPixmap(self.pixmap)
        #self.label.adjustSize()

    def mousePressEvent(self, event):
        self.originQPoint = event.pos()
        self.currentQRubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)
        self.currentQRubberBand.setGeometry(QtCore.QRect(self.originQPoint, QtCore.QSize()))
        self.currentQRubberBand.show()

    def mouseMoveEvent(self, event):
        self.currentQRubberBand.setGeometry(QtCore.QRect(self.originQPoint, event.pos()).normalized())

    def mouseReleaseEvent (self, event):
        self.currentQRubberBand.hide()
        currentQRect = self.currentQRubberBand.geometry()
        self.currentQRubberBand.deleteLater()
        cropPixmap = self.pixmap.copy(currentQRect)
        self.cropLabel.setPixmap(cropPixmap)
        cropPixmap.save('output.png')
        print(pytesseract.image_to_string(Image.open('output.png')))
        get_string('output.png')










class Viewer(QtWidgets.QMainWindow):
    def __init__(self):
        super(Viewer, self).__init__()

        self.view = View()
        self.scroller = QtWidgets.QScrollArea(self)
        self.scroller.setWidget(self.view)
        self.scroller.setWidgetResizable(True)
        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        #splitter.addWidget(self.view)
        splitter.addWidget(self.scroller)
        splitter.addWidget(self.view.cropLabel)
        hbox = QtWidgets.QVBoxLayout()
        hbox.addWidget(self.scroller)
        self.widget = QtWidgets.QWidget(self)
        self.widget.setLayout(hbox)

        self.createActions()
        self.createMenus()
        self.setCentralWidget(self.scroller)


    def createActions(self):
        self.openAct = QtWidgets.QAction("&Open...", self, shortcut="Ctrl+O",
                              triggered=self.open)
        self.fitAct = QtWidgets.QAction("&Resize...", self, shortcut="Ctrl+F",
                              triggered=self.fit)
        self.ogSizeAct = QtWidgets.QAction("&Original size ...",self,shortcut="ctrl+G",
                              triggered=self.ogSize)

    def createMenus(self):
        self.fileMenu = QtWidgets.QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)

        self.editMenu = QtWidgets.QMenu("&Edit", self)
        self.editMenu.addAction(self.fitAct)
        self.editMenu.addAction(self.ogSizeAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.editMenu)

    def open(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File",
                QtCore.QDir.currentPath())
        if fileName:
            image = QtGui.QImage(fileName)
            if image.isNull():
                QtWidgets.QMessageBox.information(self, "Image Viewer",
                        "Cannot load %s." % fileName)
                return
            self.view.pixmap = QtGui.QPixmap.fromImage(image)
            self.view.ogpixmap = self.view.pixmap
            self.view.label.setPixmap(self.view.pixmap)
            self.view.label.adjustSize()
            #self.view.label.updateGeometry()
            # self.scaleFactor = 1.0

    def fit(self):
        repixmap = self.view.pixmap.scaled(self.size(), QtCore.Qt.KeepAspectRatio)
        self.view.pixmap = repixmap
        self.view.label.setPixmap(self.view.pixmap)
        self.view.label.adjustSize()

    def ogSize(self):
        self.view.pixmap = self.view.ogpixmap
        self.view.label.setPixmap(self.view.pixmap)
        self.view.label.adjustSize()


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Viewer = Viewer()
    Viewer.show()
app.exec_()