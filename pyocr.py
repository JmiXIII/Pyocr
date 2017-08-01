#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 22:21:01 2017

@author: sylvain
"""

from PyQt5 import QtCore, QtGui, QtWidgets


class View(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.cropLabel = QtWidgets.QLabel(self)
        self.label = QtWidgets.QLabel(self)
        self.ogpixmap = QtGui.QPixmap()
        fileName = r'C:/Users/user11.HPO-SAMAT/Pictures/Lake.jpg'
        image = QtGui.QImage(fileName)
        self.pixmap = QtGui.QPixmap.fromImage(image)
        self.label.setPixmap(self.pixmap)

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

class Viewer(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.view = View()
        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        splitter.addWidget(self.view)
        splitter.addWidget(self.view.cropLabel)
        hbox = QtWidgets.QVBoxLayout()
        hbox.addWidget(splitter)
        self.widget = QtWidgets.QWidget(self)
        self.widget.setLayout(hbox)

        self.createActions()
        self.createMenus()
        self.setCentralWidget(self.widget)

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
            self.view.label.updateGeometry()
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