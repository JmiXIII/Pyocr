from PyQt5 import QtCore, QtGui, QtWidgets
from PIL import Image
from pytesseract import *
import cv2
import numpy as np
import pytesseract
import pickle

'''
https://stackoverflow.com/questions/12249875/mousepressevent-position-offset-in-qgraphicsview
'''

class View(QtWidgets.QGraphicsView):

    mouseReleased = QtCore.pyqtSignal()
    def __init__(self):
        super().__init__()

    def mousePressEvent(self, event):
        self.originQPoint = event.pos()
        self.currentQRubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle)

    def mouseMoveEvent(self, event):
        self.currentQRubberBand.setGeometry(QtCore.QRect(self.originQPoint, event.pos()).normalized())
        self.currentQRubberBand.show()

    def mouseReleaseEvent(self, event):
        self.currentQRubberBand.hide()
        self.currentQRect = self.currentQRubberBand.geometry()
        print(self.currentQRect)
        self.mouseReleased.emit()

class Scene(QtWidgets.QGraphicsScene):

    mouseReleased = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(Scene, self).__init__(parent)

    def mousePressEvent(self, event):
        self.originQPoint = event.screenPos()
        self.currentQRubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle)
        self.currentQRubberBand.setWindowOpacity(0.5)
        self.originCropPoint = event.scenePos()

    def mouseMoveEvent(self, event):
        self.currentQRubberBand.setGeometry(QtCore.QRect(self.originQPoint, event.screenPos()))
        self.currentQRubberBand.show()

    def mouseReleaseEvent(self, event):
        self.currentQRubberBand.hide()
        self.currentQRect = self.currentQRubberBand.geometry()
        self.currentQRect = QtCore.QRect(self.originCropPoint.toPoint(), event.scenePos().toPoint())
        print(self.currentQRect)
        self.currentQRubberBand.deleteLater()
        self.mouseReleased.emit()
        # self.cropPixmap = self.pixmap.copy(currentQRect)
        # size = self.cropPixmap.size()/2
        # print(size)
        #self.cropPixmap = self.cropPixmap.scaled(size, QtCore.Qt.KeepAspectRatio,

class ImgWidget(QtWidgets.QLabel):

    def __init__(self, pic, parent=None):
        super(ImgWidget, self).__init__(parent)
        self.pic = pic
        self.setPixmap(self.pic)

class Item:
    def __init__(self, item_nbr, crop_pixmap, originepoint, designation):
        self.item_nbr = item_nbr            # integer
        self.crop_pixmap = crop_pixmap      # QPixmap
        self.origin_point = originepoint     # QPoint
        self.designation = designation      # str


class Viewer(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.items = []

        # UI setup
        self.setGeometry(200,200,800,600)
        self.graphicsView = QtWidgets.QGraphicsView()
        self.hbox = QtWidgets.QVBoxLayout()
        self.scene = Scene(self)
        self.table = QtWidgets.QTableWidget(0, 5)
        self.table.setHorizontalHeaderItem(0,QtWidgets.QTableWidgetItem('#'))
        self.table.setHorizontalHeaderLabels(("#;Type;CC;Requirement;Image").split(";"))
        self.splitter = QtWidgets.QSplitter()
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.addWidget(self.graphicsView)
        self.splitter.addWidget(self.table)

        self.test=['rt']

        self.scene.mouseReleased.connect(self.mReleasedAct)

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
        self.settingsSaveAct = QtWidgets.QAction("&Import data", self, shortcut="Ctrl+I",
                                                 triggered=self.readSettings)
        self.saveAct = QtWidgets.QAction("&Save project as", self, shortcut="Ctrl+S",
                                         triggered=self.save_file)
        # self.fitAct = QtWidgets.QAction("&Resize...", self, shortcut="Ctrl+F",
        #                                 triggered=self.fit)
        # self.ogSizeAct = QtWidgets.QAction("&Original size ...", self, shortcut="ctrl+G",
        #                                    triggered=self.ogSize)


    def createMenus(self):
        self.fileMenu = QtWidgets.QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.settingsSaveAct)
        self.fileMenu.addAction(self.saveAct)

        # self.editMenu = QtWidgets.QMenu("&Edit", self)
        # self.editMenu.addAction(self.fitAct)
        # self.editMenu.addAction(self.ogSizeAct)

        self.menuBar().addMenu(self.fileMenu)
#        self.menuBar().addMenu(self.editMenu)

    def mReleasedAct(self):
        print('Mouse Released')
        self.cropPixmap = self.pixmap.copy(self.scene.currentQRect)
        self.item = Item(1, self.cropPixmap, self.scene.originQPoint, 'Test')
        self.items.append(self.item)
        self.add_item(self.item)

    def add_item(self, item):
        self.table.insertRow(0)
        self.table.setCellWidget(0,1,ImgWidget(item.crop_pixmap))
        self.update()

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
            self.scene.setSceneRect(0, 0, self.pixmap.width(), self.pixmap.height())

            self.scene.addPixmap(self.pixmap)                  # assign picture to the scene
            self.graphicsView.setScene(self.scene)              # assign scene to a view
            self.graphicsView.show()                            # show the scene

            # fits the picture within the scene
            #self.rect = self.graphicsView.sceneRect()
            #self.graphicsView.fitInView(self.rect, QtCore.Qt.KeepAspectRatio)

    def settings(self):
        # use a custom location
        return QtCore.QSettings('app.conf', QtCore.QSettings.IniFormat)

    def readSettings(self):
        self.items = []
        settings = self.settings()
        for index in range(settings.beginReadArray('items')):
            settings.setArrayIndex(index)
            self.items.append(Item(
                settings.value('number', -1, int),
                settings.value('pixmap', None, QtGui.QPixmap),
                settings.value('point', None, QtCore.QPoint),
                settings.value('designation', '', str),
                ))
        self.initSettings(self.items)

    def initSettings(self, items):
        for item in items:
            self.add_item(item)

    def writeSettings(self):
        settings = self.settings()
        settings.beginWriteArray('items')
        for index, item in enumerate(self.items):
            settings.setArrayIndex(index)
            settings.setValue('number', item.item_nbr)
            settings.setValue('pixmap', item.crop_pixmap)
            settings.setValue('point', item.origin_point)
            settings.setValue('designation', item.designation)
        settings.endArray()



    def save_file(self):
        self.writeSettings()


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Viewer = Viewer()
    Viewer.show()
app.exec_()
