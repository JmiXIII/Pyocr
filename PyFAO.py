from PyQt5 import QtCore, QtGui, QtWidgets
from PIL import Image
import subprocess
import os
import cv2

import xlwings as xw
import pytesseract


def get_string(img_path):
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract'
    img = cv2.imread(img_path)
    result = pytesseract.image_to_string(Image.open("output.png"))
    # Remove template file
    # os.remove(temp)
    return result


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

class MyTableWidget(QtWidgets.QTableWidget):

    returnPressed = QtCore.pyqtSignal()

    def __init__(self, row, col, parent = None):
        super(MyTableWidget, self).__init__(row,col)

    def keyPressEvent(self, event):
         key = event.key()

         if key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
             self.currentItem().text()
             self.returnPressed.emit()
         else:
             super(MyTableWidget, self).keyPressEvent(event)

    def MouseDoubleClickEvent(self,event):
        self.mouseDoubleClickEvent(self, event)

class Item:
    "Create DWG item object"
    position = ['item_nbr',
                     'designation',
                     'origin_point',
                     'crop_pixmap',
                     'image']

    def __init__(self, item_nbr=None, crop_pixmap=None, originepoint=None, designation=None, image=None):
        self.item_nbr = item_nbr            # integer
        self.crop_pixmap = crop_pixmap      # QPixmap
        self.origin_point = originepoint    # QPoint
        self.designation = designation      # str
        self.image = image                  # image only for item 1


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
        self.table = MyTableWidget(0,5)
        self.table.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.photo = QtWidgets.QLabel()
        # self.table.setHorizontalHeaderItem(0,QtWidgets.QTableWidgetItem('#'))
        self.table.setHorizontalHeaderLabels(Item.position)
        self.splitter = QtWidgets.QSplitter()
        self.splitter2 = QtWidgets.QSplitter()
        self.splitter2.addWidget(self.table)
        self.splitter2.addWidget(self.photo)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.addWidget(self.graphicsView)
        self.splitter.addWidget(self.splitter2)
        #self.splitter.addWidget(self.table)

        self.table.returnPressed.connect(self.modifyItem)
        self.table.cellClicked.connect(self.viewPhoto)
        self.scene.mouseReleased.connect(self.mReleasedAct)

        #self.hbox.addWidget(self.graphicsView)
        self.hbox.addWidget(self.splitter)
        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(self.hbox)
        self.setCentralWidget(self.widget)

        self.createActions()
        self.createMenus()

    def createActions(self):
        # noinspection PyArgumentList
        self.openAct = QtWidgets.QAction("&Importer une image...", self, shortcut="Ctrl+I",
                                         triggered=self.open_picture)
        self.openProjAct = QtWidgets.QAction('&Ouvrir le projet...', self, shortcut="Ctrl+O",
                                               triggered=self.readSettings)
        self.saveAct = QtWidgets.QAction("&Sauver le Projet sous ...", self, shortcut="Ctrl+S",
                                         triggered=self.save_file)
        self.exportDwgAct = QtWidgets.QAction('Exporter en image PDF...', self, shortcut="Ctrl+D",
                                               triggered=self.exportDWG)
        self.listAct = QtWidgets.QAction("&Lister les items du plan", self, shortcut="Ctrl+L",
                                            triggered=self.listItems)
        self.removeItemAct = QtWidgets.QAction("&Remove Item",self, triggered=self.removeItem)
        self.sortItemNbrAct = QtWidgets.QAction("&Renuméroter",self, triggered=self.sortItemNbr)

        self.importPdfAct = QtWidgets.QAction("&Importer une image...", self, shortcut="Ctrl+P",
                                         triggered=self.importPdf)


    def createMenus(self):
        self.fileMenu = QtWidgets.QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.openProjAct)
        self.fileMenu.addAction(self.importPdfAct)
        self.fileMenu.addAction(self.saveAct)
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
        self.cropPixmap = self.cropPixmap.scaledToHeight(50, QtCore.Qt.SmoothTransformation)
        # size = self.cropPixmap.size()
        # self.cropPixmap = self.cropPixmap.scaled(300, QtCore.Qt.KeepAspectRatio,
        #                                          transformMode=QtCore.Qt.SmoothTransformation)
        self.cropPixmap.save('output.png')
        path = QtCore.QDir.currentPath()+r'output.png'
        txt = get_string(path)
        print(txt)
        self.item = Item(self.defineItemNbr(), self.cropPixmap, self.scene.originCropPoint, txt,None)
        if self.item.item_nbr ==1:
            self.image = self.pixmap
        self.items.append(self.item)
        self.add_item(self.item)

    def defineItemNbr(self):
        l = [0]
        for i, d in enumerate(self.items):
            l.append(int(d.item_nbr))
        itemNbr = max(l)+1
        return(itemNbr)

    def searchKeyItem(self, nbr):
        for i, d in enumerate(self.items):
            if str(d.item_nbr) == nbr:
                key = i
                break
        return key

    def searchItemAttribut(self, nbr):
        for i, item in enumerate(self.items):
            if str(item.item_nbr) == nbr:
                key = item
                break
        return item

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

        # Ajout sur le tableau
        self.table.insertRow(0)
        imgWidget = ImgWidget(item.crop_pixmap)
        nbrWidget = QtWidgets.QTableWidgetItem(str(item.item_nbr))
        desWidget = QtWidgets.QTableWidgetItem(item.designation)
        desWidget.setData(QtCore.Qt.UserRole,0)
        # self.table.setCellWidget(0,4,imgWidget)
        self.table.setItem(0,item.position.index('item_nbr'),nbrWidget)
        self.table.setItem(0,item.position.index('designation'),desWidget)
        # Mise à jour du graphique
        self.ballonItem(item)
        # Mise à jour de la capture
        self.add_photo(item.crop_pixmap)
        # self.update()

    def add_photo(self, photo):
        self.photo.setPixmap(photo)

    def removeItem(self):
        row = self.table.currentRow()
        nbr = self.table.item(row, 0).text()
        key = self.searchKeyItem(nbr)
        self.items.pop(key)
        self.refreshScene()

    def modifyItem(self):
        before = self.table.currentItem().text()
        row = self.table.currentRow()
        col = self.table.currentColumn()
        attribut = Item.position[col]
        nbr = self.table.item(row,0).text()
        print("avant :",before)
        QtGui.QGuiApplication.processEvents()
        after = self.table.currentItem().text()
        print('après :',after)
        item = self.searchItemAttribut(nbr)
        setattr(item,attribut,after)
        self.refreshScene()

    def refreshScene(self):
        self.scene.clear()
        self.scene.addPixmap(self.pixmap)
        self.table.setRowCount(0)
        for item in self.items:
            self.add_item(item)

    def listItems(self):
        items = self.items
        print(items)
        pass

    def viewPhoto(self):
        row = self.table.currentRow()
        nbr = self.table.item(row, 0).text()
        for i,item in enumerate(self.items):
            if str(item.item_nbr) == nbr:
                self.photo.setPixmap(item.crop_pixmap)
                print(nbr, 'done')
                break

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

    def importPdf(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File",
                                                            QtCore.QDir.currentPath())
        print(filename)
        if not filename:
            print('error')
            return
        command = "convert" + " " + filename
        args = " -units PixelsPerInch -density 20x20 -background white -flatten converted_pdf2.jpg"
        cmd = "convert -units PixelsPerInch -density 300 -background white -flatten " + filename + " converted_pdf.jpg"
        print(cmd)
        os.system(cmd)
        # subprocess.run([command, args],
        #                  stdout=subprocess.PIPE)
        # with Img(filename=filename,format='jpeg', resolution=300) as image:
        #     image.compression_quality = 99
        #     image.background_color=Color('White')
        #     image.alpha_channel = True
        #     image.save(filename='file.jpeg')
        self.open_picture()



    def settings(self):
        # use a custom location
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File",
                                                            QtCore.QDir.currentPath(),"hpo (*.hpo)", "*.hpo")
        if not fileName:
            return
        return QtCore.QSettings(fileName, QtCore.QSettings.IniFormat)

    def readSettings(self):
        self.items = []
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File",
                                                            QtCore.QDir.currentPath(),"hpo (*.hpo)","hpo")
        if not fileName:
            return
        settings = QtCore.QSettings(fileName, QtCore.QSettings.IniFormat)
        for index in range(settings.beginReadArray('items')):
            settings.setArrayIndex(index)
            item = Item(None, None, None, None, None)
            for key in Item.position:
                print(key)
                setattr(item,str(key),settings.value(str(key)))
            self.items.append(item)
        print(self.items)

            #self.items.append(Item(settings.value(str(key))))
                    # settings.value('number', -1, int),
                    # settings.value('pixmap', None, QtGui.QPixmap),
                    # settings.value('point', None, QtCore.QPoint),
                    # settings.value('designation', '', str),
                    # settings.value('image',None, QtGui.QPixmap),

        self.initSettings(self.items)

    def initSettings(self, items):
        self.pixmap = items[0].image
        self.table.setRowCount(0)
        self.scene.addPixmap(self.pixmap)  # assign picture to the scene
        self.graphicsView.setScene(self.scene)  # assign scene to a view
        self.graphicsView.show()  # show the scene
        for item in items:
            self.add_item(item)

    def writeSettings(self):
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save File",
                                                            ".hpo","hpo (*.hpo)",".hpo")
        if not fileName:
            return
        settings = QtCore.QSettings(fileName, QtCore.QSettings.IniFormat)
        settings.beginWriteArray('items')
        for index, item in enumerate(self.items):
            settings.setArrayIndex(index)
            for key in Item.position:
                attribut = getattr(item,key)
                settings.setValue(str(key), attribut)
            if item.item_nbr == 1:
                settings.setValue('image', self.pixmap)
            else:
                settings.setValue('image', None)
        settings.endArray()

    def save_file(self):
        self.writeSettings()

    def exportDWG(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self,"export PDF",".pdf", "pdf (*.pdf)","pdf")
        pdf_writer = QtGui.QPdfWriter(filename)
        painter = QtGui.QPainter()
        painter.begin(pdf_writer)
        self.scene.render(painter)
        painter.end()

        wb = xw.Book()
        for l, item in enumerate(self.items):
            print(item.item_nbr)
            xw.Range('A'+str(l+1)).value = item.item_nbr
            xw.Range('B'+str(l+1)).value = item.designation


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Viewer = Viewer()
    Viewer.show()
app.exec_()
