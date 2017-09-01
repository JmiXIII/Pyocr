#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 22:21:01 2017
@author: sylvain
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from PIL import Image
from pytesseract import *
import cv2
import numpy as np
import pytesseract


# Path of working folder on Disk
src_path = "E:/Lab/Python/Project/OCR/"

def get_string(img_path):
    # Read image with opencv
    print('----------')
    img = cv2.imread(img_path)

    # Convert to gray
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply dilation and erosion to remove some noise
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)

    # Write image after removed noise
    cv2.imwrite("removed_noise.png", img)

    #  Apply threshold to get image with only black and white
    #img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)

    # Write the image after apply opencv to do some ...
    cv2.imwrite("thres.png", img)

    # Recognize text with tesseract for python
    result = pytesseract.image_to_string(Image.open("thres.png"))

    # Remove template file
    #os.remove(temp)

    print(result)


class Item(QtWidgets.QWidget):
    """
    Class qui décrit un item (caractéristique)
    Un item doit posséder:
        - une découpe d'image
        - une zone de texte
        - un N° d'identification
    """
    def __init__(self, cropPixmap, parent=None):
        super(Item, self).__init__()

        cropPixmap.save('output.png')
        self.setLayout(QtWidgets.QHBoxLayout())
        self.txt = QtWidgets.QLineEdit('test') #OCR to be performed
        self.label = QtWidgets.QLabel(self)
        self.layout().addWidget(self.label)
        self.layout().addWidget(self.txt)
        self.label.setPixmap(cropPixmap)
        self.label.adjustSize()
        print('done')

    def upadte_item(self):
        self.update.em

class Image(QtWidgets.QLabel):
    """
    Class où l'on effectue le rendu  partir d'un fichier image
    """

    #Signal pour la mise à jour des changements
    itemsChanged = QtCore.pyqtSignal()

    def __init__(self, filename):
        super(Image, self).__init__()
        #Connection du signal
        self.itemsChanged.connect(self.act)
        #Création de l'image
        image = QtGui.QImage(filename)
        self.pixmap = QtGui.QPixmap.fromImage(image)
        self.originQPoint = QtCore.QPoint(0,0)
        #tableau des items
        self.items = []
        self.itemNbr = 0

    #%% Gestion captre d'écran
    def mousePressEvent(self, event):
        self.originQPoint = event.pos()
        self.currentQRubberBand = QtWidgets.QRubberBand(
                QtWidgets.QRubberBand.Rectangle, self)
        self.currentQRubberBand.setGeometry(
                QtCore.QRect(self.originQPoint, QtCore.QSize()))
        self.currentQRubberBand.show()

    def mouseMoveEvent(self, event):
        self.currentQRubberBand.setGeometry(
                QtCore.QRect(self.originQPoint, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        print(self.items)
        self.currentQRubberBand.hide()
        currentQRect = self.currentQRubberBand.geometry()
        self.currentQRubberBand.deleteLater()
        cropPixmap = self.pixmap.copy(currentQRect)
        self.itemNbr = self.itemNbr + 1
        self.items.append((self.itemNbr ,self.originQPoint, Item(cropPixmap)))
        cropPixmap.save('testoutput.png')
        self.itemsChanged.emit()
        print('souis Ok')
    #%%

    def paintEvent(self, event):
        """
        Traçage des données
        """
        # Rayon + centre des annotations
        radx = 10
        rady = 10
        print('painting')
        # Instanciation de l'objet
        paint = QtGui.QPainter(self)
        paint.begin(self)
        # Traçage de l'image et des éléments
        paint.drawPixmap(self.rect(), self.pixmap)
        paint.setPen(QtCore.Qt.blue)
        paint.setFont(QtGui.QFont('Arial', 15))
        for item in self.items:
            center = QtCore.QPoint(item[1].x()+10,item[1].y()-5)
            paint.drawText(item[1],str(item[0]))
            paint.drawEllipse(center, radx, rady)
        paint.end()

    def act(self):
        print('signal émis')

class View(QtWidgets.QWidget):

    itemsChanged = QtCore.pyqtSignal()

    def __init__(self):
        super(View,self).__init__()

        fileName = r'/home/sylvain/test.jpg'
        self.image = Image(fileName)
        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().addWidget(self.image)


class Viewer(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.view = View()
        self.scroller = QtWidgets.QScrollArea(self)
        self.scroller.setWidget(self.view)
        self.scroller.setWidgetResizable(True)
        self.scroller.adjustSize()
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)

        self.hbox = QtWidgets.QVBoxLayout()
        self.hbox.addWidget(self.scroller)

        self.widget = QtWidgets.QWidget(self)
        self.widget.setLayout(self.hbox)

        self.createActions()
        self.createMenus()
        self.setCentralWidget(self.widget)


        self.view.image.itemsChanged.connect(self.itemUpdate)


    def itemUpdate(self):
        for item in self.view.image.items:
            self.hbox.addWidget(item[2])

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
            self.view.image.pixmap = QtGui.QPixmap.fromImage(image)
            self.view.image.ogpixmap = self.view.image.pixmap
            self.view.image.setPixmap(self.view.image.pixmap)
            self.view.image.adjustSize()
            self.view.image.updateGeometry()
            self.view.image.update()
            # self.scaleFactor = 1.0

    def fit(self):
        pass
#        repixmap = self.view.pixmap.scaled(self.size(), QtCore.Qt.KeepAspectRatio)
#        self.view.pixmap = repixmap
#        self.view.setPixmap(self.view.pixmap)
#        self.view.adjustSize()

    def ogSize(self):
        pass
#        self.view.pixmap = self.view.ogpixmap
#        self.view.setPixmap(self.view.pixmap)
#        self.view.adjustSize()
#%%

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Viewer = Viewer()
    Viewer.show()
app.exec_()
