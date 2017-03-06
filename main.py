# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import os
from functools import partial
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from canvas import Canvas

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


def u(s):
    if sys.version_info[0] == 2:
        return s.decode('utf-8')
    if sys.version_info[0] == 3:
        return s

__appname__ = 'qt_img'


class ToolBar(QToolBar):
    def __init__(self, title):
        super(ToolBar, self).__init__(title)
        layout = self.layout()
        m = (0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setContentsMargins(*m)
        self.setContentsMargins(*m)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

    def addAction(self, action):
        if isinstance(action, QWidgetAction):
            return super(ToolBar, self).addAction(action)
        btn = QToolButton()
        btn.setDefaultAction(action)
        btn.setToolButtonStyle(self.toolButtonStyle())
        self.addWidget(btn)


class struct(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def newIcon(icon):
    return QIcon(':/' + icon)


def addActions(widget, actions):
    for action in actions:
        if action is None:
            widget.addSeparator()
        elif isinstance(action, QMenu):
            widget.addMenu(action)
        else:
            widget.addAction(action)


def newAction(parent, text, slot=None, shortcut=None, icon=None,
              tip=None, checkable=False, enabled=True):
    """Create a new action and assign callbacks, shortcuts, etc."""
    a = QAction(text, parent)
    if icon is not None:
        a.setIcon(newIcon(icon))
    if shortcut is not None:
        if isinstance(shortcut, (list, tuple)):
            a.setShortcuts(shortcut)
        else:
            a.setShortcut(shortcut)
    if tip is not None:
        a.setToolTip(tip)
        a.setStatusTip(tip)
    if slot is not None:
        a.triggered.connect(slot)
    if checkable:
        a.setCheckable(True)
    a.setEnabled(enabled)
    return a

def read(filename, default=None):
    try:
        with open(filename, 'rb') as f:
            return f.read()
    except:
        return default


class WindowMixin(object):
    def menu(self, title, actions=None):
        menu = self.menuBar().addMenu(title)
        if actions:
            addActions(menu, actions)
        return menu

    def toolbar(self, title, actions=None):
        toolbar = ToolBar(title)
        toolbar.setObjectName(u'%sToolBar' % title)
        # toolbar.setOrientation(Qt.Vertical)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        if actions:
            addActions(toolbar, actions)
        self.addToolBar(Qt.BottomToolBarArea, toolbar)
        return toolbar


class MainWindow(QMainWindow, WindowMixin):
    def __init__(self, parent=None):
        self.filename = None
        self.imageData = None
        self.imageDir = None
        self.imageList = None
        self.imageIdx = None

        QWidget.__init__(self, parent)
        self.setWindowTitle(__appname__)
        self.resize(800, 600)

        self.canvas = Canvas()
        self.canvas.setObjectName(_fromUtf8("canvas"))
        # self.canvas.zoomRequest.connect(self.zoomRequest)

        self.scroll = QScrollArea()
        self.scroll.setWidget(self.canvas)
        self.scroll.setWidgetResizable(True)

        # self.scrollArea.setWidget(self.canvas)
        # self.setCentralWidget(self.canvas)
        self.setCentralWidget(self.scroll)

        self.tools = self.toolbar(u"Tools")
        self.statusBar().showMessage('test app started.')
        self.statusBar().show()

        action = partial(newAction, self)
        # menus action
        open_action = action('&Open File', self.openFile,
                             'Ctrl+O', None, u'Open image file')
        quit_action = action('&Quit', self.close,
                             'Ctrl+Q', None, u'Quit application')
        fit_action = action('&Fit Window', self.fitWindowSize,
                             None, None, u'Fit window')
        # toolbar action
        draw_action = action('&Draw', self.draw,
                             None, None, u'draw')
        next_action = action('&Next', self.openNextImg,
                             None, None, u'Open Next')
        prev_action = action('&Prev', self.openPrevImg,
                             None, None, u'Open Prev')
        # set tools
        tool = [next_action, prev_action, draw_action]
        addActions(self.tools, tool)
        # set menus
        self.menus = struct(file=self.menu('&File'),  view=self.menu('&View'))
        addActions(self.menus.file, (open_action, None, quit_action))
        addActions(self.menus.view, (fit_action,))

    def scanAllImages(self, folderPath):
        extensions = ['.jpeg','.jpg', '.png', '.bmp']
        images = []
        for root, dirs, files in os.walk(folderPath):
            for file in files:
                if file.lower().endswith(tuple(extensions)):
                    relatviePath = os.path.join(root, file)
                    path = u(os.path.abspath(relatviePath))
                    images.append(path)
        images.sort(key=lambda x: x.lower())
        images = [x.replace('\\', '/') for x in images]
        return images

    def openFile(self):
        path = os.path.dirname(str(self.filename)) \
            if self.filename else '.'
        # formats = ['*.%s' % str(fmt).lower() \
        #            for fmt in QImageReader.supportedImageFormats()]
        formats = "*.bmp *.jpeg *.jpg *.png"
        filters = "Image & Label files (%s)" % formats
        filename = str(QFileDialog.getOpenFileName(self,
            '%s - Choose Image file' % __appname__,
            path, filters))
        if filename:
            self.imageDir = os.path.dirname(filename)
            self.imageList = self.scanAllImages(self.imageDir)

            if filename in self.imageList:
                self.imageIdx = self.imageList.index(u(filename))
            self.loadFile(filename)

    def errorMessage(self, title, message):
        return QMessageBox.critical(self, title, '<p><b>%s</b></p>%s' %
                                    (title, message))

    def status(self, message, delay=5000):
        if delay is not None:
            self.statusBar().showMessage(message, delay)

    def scaleFitWindow(self):
        e = 2.0 # So that no scrollbars are generated.
        w1 = self.centralWidget().width() - e
        h1 = self.centralWidget().height() - e
        a1 = w1/ h1
        # Calculate a new scale value based on the pixmap's aspect ratio.
        w2 = self.canvas.pixmap.width() - 0.0
        h2 = self.canvas.pixmap.height() - 0.0
        a2 = w2 / h2
        return w1 / w2 if a2 >= a1 else h1 / h2

    def resetState(self):
        self.filename = None
        self.canvas.resetState()

    def loadFile(self, filename=None):
        self.resetState()
        self.canvas.setEnabled(False)
        if filename and QFile.exists(filename):
            self.imageData = read(filename, None)
            image = QImage.fromData(self.imageData)
            if image.isNull():
                self.errorMessage(u'Error opening file',
                        u"<p>Make sure <i>%s</i> is a valid image file." % filename)
                self.status("Error reading %s" % filename)
                return False
            self.canvas.loadPixmap(QPixmap.fromImage(image))
            self.canvas.setEnabled(True)
            self.canvas.scale = self.scaleFitWindow()
            self.canvas.adjustSize()
            self.canvas.update()
            self.canvas.setMode('edit')
            self.filename = u(filename)
            return True
        return False

    def fitWindowSize(self):
        if self.canvas.pixmap:
            self.canvas.scale = self.scaleFitWindow()
            self.canvas.adjustSize()
            self.canvas.update()

    def openNextImg(self):
        if (self.imageList is None) or (len(self.imageList) <= 0):
            return

        filename = None
        if self.imageIdx + 1 < len(self.imageList):
            nextIdx = self.imageIdx + 1
        elif self.imageIdx + 1 == len(self.imageList):
            nextIdx = 0
        else:
            return

        filename = self.imageList[nextIdx]
        self.loadFile(filename)
        self.imageIdx = nextIdx

    def openPrevImg(self):
        if (self.imageList is None) or (len(self.imageList) <= 0):
            return

        filename = None
        if self.imageIdx - 1 >= 0:
            prevIdx = self.imageIdx - 1
        elif self.imageIdx - 1 == -1:
            prevIdx = len(self.imageList) - 1
        else:
            return

        filename = self.imageList[prevIdx]
        self.loadFile(filename)
        self.imageIdx = prevIdx

    def draw(self):
        if self.canvas.isEditMode():
            self.canvas.setMode('draw')
            self.status("draw mode")
        else:
            self.canvas.setMode('edit')

        # def zoomRequest(self, delta):
        #     units = delta / (8 * 15)
        #     scale = 10
        #     self.addZoom(scale * units)

    # def center(self):
    #     qr = self.frameGeometry()
    #     cp = QDesktopWidget().availableGeometry().center()
    #     qr.moveCenter(cp)
    #     self.move(qr.topLeft())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = MainWindow()
    myapp.show()
    sys.exit(app.exec_())
