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
        print('moving')
        self.currentQRubberBand.setGeometry(QtCore.QRect(self.originQPoint, event.screenPos()))
        self.currentQRubberBand.show()


    def mouseReleaseEvent(self, event):
        self.currentQRubberBand.deleteLater()
        self.currentQRubberBand.hide()
        self.currentQRect = self.currentQRubberBand.geometry()
        self.currentQRect = QtCore.QRect(self.originCropPoint.toPoint(), event.scenePos().toPoint())
        #print(self.currentQRect)

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
        super(Viewer, self).__init__()

        self.items = []

        # UI setup
        self.setGeometry(200,200,800,600)
        self.graphicsView = QtWidgets.QGraphicsView()
        self.graphicsView.setRenderHint(QtGui.QPainter.Antialiasing)
        self.hbox = QtWidgets.QVBoxLayout()
        self.scene = Scene(self)
        self.table = QtWidgets.QTableWidget(0, 5)
        self.table.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        # self.table.setHorizontalHeaderItem(0,QtWidgets.QTableWidgetItem('#'))
        self.table.setHorizontalHeaderLabels(("#;Type;CC;Requirement;Image").split(";"))
        self.splitter = QtWidgets.QSplitter()
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.addWidget(self.graphicsView)
        self.splitter.addWidget(self.table)

        self.scene.mouseReleased.connect(self.mReleasedAct)

        #self.hbox.addWidget(self.graphicsView)
        self.hbox.addWidget(self.splitter)
        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(self.hbox)
        self.setCentralWidget(self.widget)

        self.createActions()
        self.createMenus()

    def createActions(self):
        self.openAct = QtWidgets.QAction("&Importer une image", self, shortcut="Ctrl+O",
                                         triggered=self.open_picture)
        self.settingsSaveAct = QtWidgets.QAction("&Importer les données", self, shortcut="Ctrl+I",
                                                 triggered=self.readSettings)
        self.saveAct = QtWidgets.QAction("&Exporter les données", self, shortcut="Ctrl+S",
                                         triggered=self.save_file)
        self.exportProjAct = QtWidgets.QAction("&Sauvegarder le projet sous", self, shortcut="Ctrl+E",
                                               triggered=self.exportProject)
        self.openProjAct = QtWidgets.QAction('&Ouvrir le projet', self, shortcut="Ctrl+P",
                                               triggered=self.openProject)
        self.exportDwgAct = QtWidgets.QAction('&Export DWG as PDF', self, shortcut="Ctrl+D",
                                               triggered=self.exportDWG)
        self.listAct = QtWidgets.QAction("&List Items in DWG", self, shortcut="Ctrl+L",
                                            triggered=self.listItems)
        self.removeItemAct = QtWidgets.QAction("&Remove Item",self, triggered=self.removeItem)
        self.sortItemNbrAct = QtWidgets.QAction("&Renuméroter",self, triggered=self.sortItemNbr)

        # self.fitAct = QtWidgets.QAction("&Resize...", self, shortcut="Ctrl+F",
        #                                 triggered=self.fit)
        # self.ogSizeAct = QtWidgets.QAction("&Original size ...", self, shortcut="ctrl+G",
        #                                    triggered=self.ogSize)


    def createMenus(self):
        self.fileMenu = QtWidgets.QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.settingsSaveAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.openProjAct)
        self.fileMenu.addAction(self.exportProjAct)
        self.fileMenu.addAction(self.exportDwgAct)

        self.editMenu = QtWidgets.QMenu("&Edit", self)
        self.editMenu.addAction(self.listAct)

        self.menuBar().addMenu(self.fileMenu)

        # Context Menu for tableWidget
        self.table.addAction(self.removeItemAct)
        self.table.addAction(self.sortItemNbrAct)

    def mReleasedAct(self):
        # Handle Table feeding
        self.cropPixmap = self.pixmap.copy(self.scene.currentQRect)
        size = self.cropPixmap.size() / 2
        self.cropPixmap = self.cropPixmap.scaled(size, QtCore.Qt.KeepAspectRatio,
                                                 transformMode=QtCore.Qt.SmoothTransformation)
        self.item = Item(self.defineItemNbr(), self.cropPixmap, self.scene.originCropPoint, 'Test')
        self.items.append(self.item)
        self.add_item(self.item)
        self.hasFocus()

    def defineItemNbr(self):
        l = [0]
        for i, d in enumerate(self.items):
            l.append(d.item_nbr)
        itemNbr = max(l)+1
        return(itemNbr)

    def sortItemNbr(self):
        for i,item in enumerate(self.items):
            item.item_nbr = i+1
        self.refreshScene()

    def ballonItem(self, item):

        x = item.origin_point.x()
        y = item.origin_point.y()
        nbr = str(item.item_nbr)
        stylo = QtGui.QPen(QtCore.Qt.blue)
        stylo.setWidth(3)
        stylotxt = QtGui.QPen(QtCore.Qt.blue)
        stylotxt.setWidth(1)
        text = QtWidgets.QGraphicsSimpleTextItem(nbr)
        text.setPos(x+5, y+7)
        #text.setBrush(QtCore.Qt.blue)
        text.setPen(stylotxt)
        self.scene.addItem(text)
        print(text)
        self.scene.addEllipse(x, y, 30, 30, pen=stylo)

    def add_item(self, item):
        self.table.insertRow(0)
        self.table.setCellWidget(0,4,ImgWidget(item.crop_pixmap))
        self.table.setItem(0,0,QtWidgets.QTableWidgetItem(str(item.item_nbr)))
        self.table.setItem(0,2,QtWidgets.QTableWidgetItem(item.designation))
        self.ballonItem(item)
        self.update()

    def removeItem(self):
        row = self.table.currentRow()
        nbr = self.table.item(row, 0).text()
        for i, d in enumerate(self.items):
            if str(d.item_nbr) == nbr:
                self.items.pop(i)
                break
        self.refreshScene()

    def refreshScene(self):
        self.scene.clear()
        self.scene.addPixmap(self.pixmap)
        self.scene.clear()
        self.scene.addPixmap(self.pixmap)
        self.table.setRowCount(0)
        for item in self.items:
            self.add_item(item)

    def listItems(self):
        items = self.items
        print(items)
        pass

    def open_picture(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File",
                                                            QtCore.QDir.currentPath())
        if fileName:
            self.image = QtGui.QImage(fileName)
            if self.image.isNull():
                QtWidgets.QMessageBox.information(self, "Image Viewer",
                                                  "Cannot load %s." % fileName)
                return

            self.scene.clear()                                  # clear graphics scene
            self.pixmap = QtGui.QPixmap.fromImage(self.image)

            # important for centering the picture within the scene
            self.scene.setSceneRect(0, 0, self.pixmap.width(), self.pixmap.height())

            self.scene.addPixmap(self.pixmap)                  # assign picture to the scene
            self.graphicsView.setScene(self.scene)             # assign scene to a view
            self.graphicsView.show()                           # show the scene

            # fits the picture within the scene -
            # self.rect = self.graphicsView.sceneRect()
            # self.graphicsView.fitInView(self.rect, QtCore.Qt.KeepAspectRatio)

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
            #self.ballonItem(item)

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

    def exportProject(self):
        pass

    def openProject(self):
        pass

    def exportDWG(self):
        pass

if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Viewer = Viewer()
    Viewer.show()
app.exec_()
