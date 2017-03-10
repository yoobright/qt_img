# -*- coding: utf-8 -*-
from __future__ import print_function, division
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from shape import Shape

CURSOR_DEFAULT = Qt.ArrowCursor
CURSOR_POINT = Qt.PointingHandCursor
CURSOR_DRAW = Qt.CrossCursor
CURSOR_MOVE = Qt.ClosedHandCursor
CURSOR_GRAB = Qt.OpenHandCursor

EDIT, DRAW = 1, 2


def read(filename, default=None):
    try:
        with open(filename, 'rb') as f:
            return f.read()
    except:
        return default


class Canvas(QWidget):
    zoomRequest = pyqtSignal(int, QPointF)
    mouseMoveSignal = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(Canvas, self).__init__(*args, **kwargs)
        self.mode = EDIT
        self.true_meta_shapes = []
        self.prop_meta_shapes = []
        self._cursor = CURSOR_DEFAULT
        self._painter = QPainter()
        self.pixmap = QPixmap('test.jpg')
        self.scale = 1.0
        # Set widget options
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.WheelFocus)

    def transformPos(self, point):
        return point / self.scale - self.offsetToCenter()

    def offsetToCenter(self):
        s = self.scale
        area = super(Canvas, self).size()
        w, h = self.pixmap.width() * s, self.pixmap.height() * s
        aw, ah = area.width(), area.height()
        x = (aw-w)/(2*s) if aw > w else 0
        y = (ah-h)/(2*s) if ah > h else 0
        return QPointF(x, y)

    def paintEvent(self, QPaintEvent):
        p = self._painter
        p.begin(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.HighQualityAntialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        p.scale(self.scale, self.scale)
        p.translate(self.offsetToCenter())
        # print(self.pixmap)
        p.drawPixmap(0, 0, self.pixmap)
        Shape.scale = self.scale
        self.paintPropShape(p)
        self.paintTrueShape(p)
        p.end()

    def paintTrueShape(self, painter):
        for meta_shape in self.true_meta_shapes:
            shape = meta_shape['shape']
            shape.paint(painter)

    def paintPropShape(self, painter):
        color = QColor("#FFF68F")
        pen = QPen()
        for meta_shape in self.prop_meta_shapes:
            if meta_shape['keep'] == 1:
                color.setAlpha(255)
                width = 2
            else:
                color.setAlpha(180)
                width = 1
            pen.setColor(color)
            pen.setWidth(width)
            shape = meta_shape['shape']
            shape.paint(painter, pen=pen)



    def isEditMode(self):
        return self.mode == EDIT

    def isDrawMode(self):
        return self.mode == DRAW

    def setMode(self, mode):
        if mode == 'edit':
            self.mode = EDIT
        elif mode == 'draw':
            self.mode = DRAW

    def enterEvent(self, ev):
        pass

    def leaveEvent(self, ev):
        self.restoreCursor()

    def focusOutEvent(self, ev):
        self.restoreCursor()
        # print('focus')

    def mouseMoveEvent(self, ev):
        # self.setCursor()
        # print(ev.pos())
        pos = self.transformPos(ev.pos())
        # inside pic
        if (0 < pos.x() < self.pixmap.width() and
            0 < pos.y() < self.pixmap.height()):
            x = int(pos.x())
            y = int(pos.y())
            r, g, b = QColor(self.pixmap.toImage().pixel(x, y)).getRgb()[:-1]
            status_str = u"x: {:<4d} y: {:<4d} rgb: {:<4d} {:<4d} {:<4d}"\
                .format(x, y, r, g, b)
            self.mouseMoveSignal.emit(status_str)

        if self.isDrawMode():
            self.setCursor(CURSOR_DRAW)
        #     self.overrideCursor(CURSOR_DRAW)
        else:
            self.setCursor(CURSOR_DEFAULT)

    def loadPixmap(self, pixmap):
        self.pixmap = pixmap
        self.true_shapes = []
        self.repaint()

    def overrideCursor(self, cursor):
        self.restoreCursor()
        self._cursor = cursor
        QApplication.setOverrideCursor(cursor)



    def restoreCursor(self):
        QApplication.restoreOverrideCursor()

    def sizeHint(self):
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        if self.pixmap:
            return self.scale * self.pixmap.size()
        return super(Canvas, self).minimumSizeHint()

    def wheelEvent(self, ev):
        if ev.orientation() == Qt.Vertical:
            mods = ev.modifiers()
            if Qt.ControlModifier == int(mods):
                # print('zoom')
                # print(ev.delta())
                self.zoomRequest.emit(ev.delta(), ev.pos())
                # units = ev.delta() / (8 * 15)
                # scale = 10
                # self.scale += units * scale / 100
                # # print(self.scale)
                # self.adjustSize()
                # self.update()
        # ev.accept()

    def resetState(self):
        self.restoreCursor()
        self.pixmap = None
        self.update()


