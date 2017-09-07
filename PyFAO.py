from PyQt5 import QtCore, QtGui, QtWidgets
from PIL import Image
from pytesseract import *
import cv2
import numpy as np
import pytesseract

class View(QtWidgets.QGraphicsView):
    def __init__(self):
        super().__init__()

    def mousePressEvent(self, event):
        self.originQPoint = event.pos()
        self.currentQRubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)
        self.currentQRubberBand.show()

    def mouseMoveEvent(self, event):
        self.currentQRubberBand.setGeometry(QtCore.QRect(self.originQPoint, event.pos()).normalized())
        print('moved')

    def mouseReleaseEvent(self, event):
        print('released')
        self.currentQRubberBand.hide()
        self.currentQRect = self.currentQRubberBand.geometry()

class Viewer(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setGeometry(200,200,800,600)
        self.graphicsView = View()
        self.hbox = QtWidgets.QVBoxLayout()
        self.scene = QtWidgets.QGraphicsScene()
        self.table = QtWidgets.QTableWidget(0, 5)
        self.table.setHorizontalHeaderItem(0,QtWidgets.QTableWidgetItem('#'))
        self.table.setHorizontalHeaderLabels(("#;Type;CC;Requirement;Image").split(";"))
        self.splitter = QtWidgets.QSplitter()
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.addWidget(self.graphicsView)
        self.splitter.addWidget(self.table)


        #self.hbox.addWidget(self.graphicsView)
        self.hbox.addWidget(self.splitter)
        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(self.hbox)
        self.setCentralWidget(self.widget)

        self.createActions()
        self.createMenus()

    def createActions(self):
        self.openAct = QtWidgets.QAction("&Open...", self, shortcut="Ctrl+O",
                                         triggered=self.open_picture)
        # self.fitAct = QtWidgets.QAction("&Resize...", self, shortcut="Ctrl+F",
        #                                 triggered=self.fit)
        # self.ogSizeAct = QtWidgets.QAction("&Original size ...", self, shortcut="ctrl+G",
        #                                    triggered=self.ogSize)


    def createMenus(self):
        self.fileMenu = QtWidgets.QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)

        # self.editMenu = QtWidgets.QMenu("&Edit", self)
        # self.editMenu.addAction(self.fitAct)
        # self.editMenu.addAction(self.ogSizeAct)

        self.menuBar().addMenu(self.fileMenu)
#        self.menuBar().addMenu(self.editMenu)

    def open_picture(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File",
                                                            QtCore.QDir.currentPath())
        if fileName:
            image = QtGui.QImage(fileName)
            if image.isNull():
                QtWidgets.QMessageBox.information(self, "Image Viewer",
                                                  "Cannot load %s." % fileName)
                return

            self.scene.clear()                                  # clear graphics scene
            self.pixmap = QtGui.QPixmap.fromImage(image)

            # important for centering the picture within the scene
            #self.scene.setSceneRect(0, 0, self.pixmap.width(), self.pixmap.height())

            self.scene.addPixmap(self.pixmap)                  # assign picture to the scene
            self.graphicsView.setScene(self.scene)              # assign scene to a view
            self.graphicsView.show()                            # show the scene

            # fits the picture within the scene
            #self.rect = self.graphicsView.sceneRect()
            #self.graphicsView.fitInView(self.rect, QtCore.Qt.KeepAspectRatio)

if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Viewer = Viewer()
    Viewer.show()
app.exec_()