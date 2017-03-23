# -*- coding: utf-8 -*-
from __future__ import print_function, division
from math import sqrt
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from shape import Shape
from m_utils.m_io import NewWriter
from m_utils.utils import compute_iou
from m_utils.utils import read, distance

CURSOR_DEFAULT = Qt.ArrowCursor
CURSOR_POINT = Qt.PointingHandCursor
CURSOR_DRAW = Qt.CrossCursor
CURSOR_MOVE = Qt.ClosedHandCursor
CURSOR_GRAB = Qt.OpenHandCursor
CURSOR_SIZE_V = Qt.SizeVerCursor
CURSOR_SIZE_H = Qt.SizeHorCursor
CURSOR_SIZE_F = Qt.SizeFDiagCursor
CURSOR_SIZE_B = Qt.SizeBDiagCursor

EDIT, DRAW = 1, 2

RESIZE_TOP = 0
RESIZE_BOTTOM = 1
RESIZE_LEFT = 2
RESIZE_RIGHT = 3
RESIZE_TOP_LEFT = 4
RESIZE_TOP_RIGHT = 5
RESIZE_BOTTOM_LEFT = 6
RESIZE_BOTTOM_RIGHT = 7


class Canvas(QWidget):
    zoomRequest = pyqtSignal(int, QPointF)
    mouseMoveSignal = pyqtSignal(str)
    newShape = pyqtSignal()

    epsilon = 11.0

    def __init__(self, *args, **kwargs):
        super(Canvas, self).__init__(*args, **kwargs)
        self.mode = EDIT
        self.keep_only = True
        self.true_meta_shapes = []
        self.prop_meta_shapes = []
        self.current_shape = None
        self.rect_points = None
        self._cursor = CURSOR_DEFAULT
        self._painter = QPainter()
        self.pixmap = QPixmap('test.jpg')
        self.scale = 1.0
        self.hpShape = None
        self.htShape = None
        self.selectedShape = None
        self.menus = QMenu()
        self.resize_tag = None
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

    def outOfPixmap(self, p):
        w, h = self.pixmap.width(), self.pixmap.height()
        return not (0 <= p.x() <= w and 0 <= p.y() <= h)

    def intersectionPoint(self, p1, p2):
        # Cycle through each image edge in clockwise fashion,
        # and find the one intersecting the current line segment.
        # http://paulbourke.net/geometry/lineline2d/
        size = self.pixmap.size()
        points = [(0, 0),
                  (size.width(), 0),
                  (size.width(), size.height()),
                  (0, size.height())]
        x1, y1 = p1.x(), p1.y()
        x2, y2 = p2.x(), p2.y()
        d, i, (x, y) = min(self.intersectingEdges((x1, y1), (x2, y2), points))
        x3, y3 = points[i]
        x4, y4 = points[(i+1)%4]
        if (x, y) == (x1, y1):
            # Handle cases where previous point is on one of the edges.
            if x3 == x4:
                return QPointF(x3, min(max(0, y2), max(y3, y4)))
            else: # y3 == y4
                return QPointF(min(max(0, x2), max(x3, x4)), y3)
        return QPointF(x, y)

    def intersectingEdges(self, x1y1, x2y2, points):
        """For each edge formed by `points', yield the intersection
        with the line segment `(x1,y1) - (x2,y2)`, if it exists.
        Also return the distance of `(x2,y2)' to the middle of the
        edge along with its index, so that the one closest can be chosen."""
        x1, y1 = x1y1
        x2, y2 = x2y2
        for i in range(4):
            x3, y3 = points[i]
            x4, y4 = points[(i+1) % 4]
            denom = (y4-y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
            nua = (x4-x3) * (y1-y3) - (y4-y3) * (x1-x3)
            nub = (x2-x1) * (y1-y3) - (y2-y1) * (x1-x3)
            if denom == 0:
                # This covers two cases:
                #   nua == nub == 0: Coincident
                #   otherwise: Parallel
                continue
            ua, ub = nua / denom, nub / denom
            if 0 <= ua <= 1 and 0 <= ub <= 1:
                x = x1 + ua * (x2 - x1)
                y = y1 + ua * (y2 - y1)
                m = QPointF((x3 + x4)/2, (y3 + y4)/2)
                d = distance(m - QPointF(x2, y2))
                yield d, i, (x, y)

    def paintEvent(self, ev):
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
        if self.current_shape:
            self.paintRect(p)
        p.end()

    def paintTrueShape(self, painter):
        for meta_shape in self.true_meta_shapes:
            shape = meta_shape['shape']
            if (meta_shape == self.htShape or shape.selected):
                shape.fill = True
            else:
                shape.fill = False
            shape.paint(painter)

    def paintPropShape(self, painter):
        color = QColor("#FFF68F")
        pen = QPen()
        for meta_shape in self.prop_meta_shapes:
            if meta_shape['keep'] == 1:
                color.setAlpha(255)
                width = 2
                pen.setStyle(Qt.SolidLine)
            else:
                color.setAlpha(180)
                width = 1
                pen.setStyle(Qt.DotLine)
            pen.setColor(color)
            pen.setWidth(width)
            shape = meta_shape['shape']
            if (meta_shape == self.hpShape or shape.selected) and \
                            meta_shape['keep'] == 1:
                shape.fill = True
            else:
                shape.fill = False
            if self.keep_only:
                if meta_shape['keep'] == 1:
                    shape.paint(painter, pen=pen)
            else:
                shape.paint(painter, pen=pen)

    def paintRect(self, painter):
        leftTop = self.rect_points[0]
        rightBottom = self.rect_points[1]
        rectWidth = rightBottom.x() - leftTop.x()
        rectHeight = rightBottom.y() - leftTop.y()
        color = QColor(127, 255, 0)
        painter.setPen(color)
        brush = QBrush(Qt.BDiagPattern)
        brush.setColor(QColor(127, 255, 0, 120))
        painter.setBrush(brush)
        painter.drawRect(leftTop.x(), leftTop.y(), rectWidth, rectHeight)

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

    def computeShapeIOU(self, meta_shape):
        ret = 0.0
        for true_meta_shape in self.true_meta_shapes:
            ret = max(ret, compute_iou(meta_shape, true_meta_shape))
        return ret

    def mouseMoveEvent(self, ev):
        # self.setCursor()
        # print(ev.pos())
        pos = self.transformPos(ev.pos())
        # inside pic
        if not self.outOfPixmap(pos):
            x = int(pos.x())
            y = int(pos.y())
            r, g, b = QColor(self.pixmap.toImage().pixel(x, y)).getRgb()[:-1]
            status_str = u"x: {:<4d} y: {:<4d} rgb: {:<4d} {:<4d} {:<4d}"\
                .format(x, y, r, g, b)
        else:
            status_str = u""
        self.mouseMoveSignal.emit(status_str)

        if self.isDrawMode():
            # draw mode
            self.setCursor(CURSOR_DRAW)
        #     self.overrideCursor(CURSOR_DRAW)
            if self.current_shape and Qt.LeftButton & ev.buttons():
                if self.outOfPixmap(pos):
                    pos = self.intersectionPoint(self.rect_points[0], pos)
                if pos.x() - self.rect_points[0].x() > 0 and \
                    pos.y() - self.rect_points[0].y() > 0:
                    self.rect_points[-1] = pos
                    self.update()
            return
        else:
            # edit mode
            if self.resize_tag is None:
                self.setCursor(CURSOR_DEFAULT)
            elif self.selectedShape:
                if self.resize_tag == RESIZE_TOP_LEFT:
                    self.selectedShape.xmin = int(pos.x())
                    self.selectedShape.ymin = int(pos.y())
                elif self.resize_tag == RESIZE_TOP_RIGHT:
                    self.selectedShape.xmax = int(pos.x())
                    self.selectedShape.ymin = int(pos.y())
                elif self.resize_tag == RESIZE_BOTTOM_LEFT:
                    self.selectedShape.xmin = int(pos.x())
                    self.selectedShape.ymax = int(pos.y())
                elif self.resize_tag == RESIZE_BOTTOM_RIGHT:
                    self.selectedShape.xmax = int(pos.x())
                    self.selectedShape.ymax = int(pos.y())
                elif self.resize_tag == RESIZE_TOP:
                    self.selectedShape.ymin = int(pos.y())
                elif self.resize_tag == RESIZE_BOTTOM:
                    self.selectedShape.ymax = int(pos.y())
                elif self.resize_tag == RESIZE_LEFT:
                    self.selectedShape.xmin = int(pos.x())
                elif self.resize_tag == RESIZE_RIGHT:
                    self.selectedShape.xmax = int(pos.x())

            for meta_shape in reversed([s for s in self.prop_meta_shapes]):
                if meta_shape['shape'].containsPoint(pos) and \
                                meta_shape['keep'] == 1:
                    self.hpShape = meta_shape
                    self.update()
                    break
            else:
                if self.hpShape:
                    self.update()
                self.hpShape = None

            for meta_shape in reversed([s for s in self.true_meta_shapes]):
                if meta_shape['shape'].containsPoint(pos):
                    self.htShape = meta_shape
                    self.hpShape = None
                    self.update()
                    break
            else:
                self.update()
                self.htShape = None

            if self.selectedShape:
                resize_tag = None
                if self.selectedShape.nearTopLeft(pos):
                    self.setCursor(CURSOR_SIZE_F)
                    resize_tag = RESIZE_TOP_LEFT
                elif self.selectedShape.nearTopRight(pos):
                    self.setCursor(CURSOR_SIZE_B)
                    resize_tag = RESIZE_TOP_RIGHT
                elif self.selectedShape.nearBottomLeft(pos):
                    self.setCursor(CURSOR_SIZE_B)
                    resize_tag = RESIZE_BOTTOM_LEFT
                elif self.selectedShape.nearBottomRight(pos):
                    self.setCursor(CURSOR_SIZE_F)
                    resize_tag = RESIZE_BOTTOM_RIGHT
                elif self.selectedShape.nearTop(pos):
                    self.setCursor(CURSOR_SIZE_V)
                    resize_tag = RESIZE_TOP
                elif self.selectedShape.nearBottom(pos):
                    self.setCursor(CURSOR_SIZE_V)
                    resize_tag = RESIZE_BOTTOM
                elif self.selectedShape.nearLeft(pos):
                    self.setCursor(CURSOR_SIZE_H)
                    resize_tag = RESIZE_LEFT
                elif self.selectedShape.nearRight(pos):
                    self.setCursor(CURSOR_SIZE_H)
                    resize_tag = RESIZE_RIGHT
                else:
                    self.resize_tag = None

                if Qt.LeftButton & ev.buttons():
                    if resize_tag is not None:
                        self.resize_tag = resize_tag



    def mousePressEvent(self, ev):
        pos = self.transformPos(ev.pos())
        if self.isDrawMode():
            if self.current_shape:
                pass
            elif not self.outOfPixmap(pos):
                self.current_shape = Shape()
                # self.current_shape.addPoint(pos)
                self.rect_points = [pos, pos]
        else:
            self.selectShapePoint(pos)
            self.repaint()

    def mouseReleaseEvent(self, ev):
        if ev.button() == Qt.RightButton:
            self.restoreCursor()
            self.menus.exec_(ev.globalPos())

        if ev.button() == Qt.LeftButton:
            if self.current_shape and self.rect_points:
                if self.rect_points[0] != self.rect_points[1]:
                    self.newShape.emit()
                self.rect_points = None
                self.current_shape = None
                print('draw done')
                self.repaint()
            self.resize_tag = None

    def addTrueShape(self):
        if self.current_shape and self.rect_points:
            xmin = int(self.rect_points[0].x())
            ymin = int(self.rect_points[0].y())
            xmax = int(self.rect_points[1].x())
            ymax = int(self.rect_points[1].y())
            name = self.current_shape.name
            self.current_shape.b_type = 'true'
            self.current_shape.xmin = xmin
            self.current_shape.ymin = ymin
            self.current_shape.xmax = xmax
            self.current_shape.ymax = ymax
            # self.current_shape.addPoint(QPoint(xmin, ymin))
            # self.current_shape.addPoint(QPoint(xmax, ymin))
            # self.current_shape.addPoint(QPoint(xmax, ymax))
            # self.current_shape.addPoint(QPoint(xmin, ymax))
            meta_shape = {
                'shape': self.current_shape,
                'name': name,
                # 'xmin': xmin,
                # 'ymin': ymin,
                # 'xmax': xmax,
                # 'ymax': ymax
            }
            self.true_meta_shapes.append(meta_shape)

    def deSelectShape(self):
        if self.selectedShape:
            self.selectedShape.selected = False
            self.selectedShape = None
            self.update()

    def selectShapePoint(self, point):
        self.deSelectShape()
        for meta_shape in reversed([s for s in self.prop_meta_shapes]):
            if meta_shape['shape'].containsPoint(point) and \
                                meta_shape['keep'] == 1:
                meta_shape['shape'].selected = True
                self.selectedShape = meta_shape['shape']
                self.update()
                break

        for meta_shape in reversed([s for s in self.true_meta_shapes]):
            if meta_shape['shape'].nearShape(point):
                self.deSelectShape()
                meta_shape['shape'].selected = True
                self.selectedShape = meta_shape['shape']
                self.update()
                break


    def loadPixmap(self, pixmap):
        self.pixmap = pixmap
        self.true_meta_shapes = []
        self.prop_meta_shapes = []
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

    def saveXMl(self, img_name=None, dir_path=None):
        if dir:
            img_size = (self.pixmap.height(), self.pixmap.width(), 3)
            writer = NewWriter(img_name, img_size)

            for meta_shape in self.true_meta_shapes:
                writer.addTrueBox(meta_shape['shape'].xmin,
                                  meta_shape['shape'].ymin,
                                  meta_shape['shape'].xmax,
                                  meta_shape['shape'].ymax,
                                  meta_shape['name'])
            writer.save(dir_path)



