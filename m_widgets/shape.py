# -*- coding:utf-8 -*-
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from m_utils.utils import distance

GT_LINE_COLOR = QColor("#7FFF00")
DEFAULT_FILL_COLOR = QColor(255, 0, 0, 100)
DEFAULT_SELECT_FILL_COLOR = QColor(0, 128, 255, 155)


class Shape(object):
    line_color = GT_LINE_COLOR
    fill_color = DEFAULT_FILL_COLOR
    select_fill_color = DEFAULT_SELECT_FILL_COLOR
    scale = 1.0

    def __init__(self, name=None, b_type=None):
        self.name = name
        self.xmin = None
        self.ymin = None
        self.xmax = None
        self.ymax = None
        # self.points = self.getPoints()
        self.fill = False
        self.selected = False
        self.b_type = b_type

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    @property
    def points(self):
        if (self.xmin is not None) and (self.ymin is not None) and \
                (self.xmax is not None) and (self.ymax is not None):
            return [
                QPoint(self.xmin, self.ymin),
                QPoint(self.xmax, self.ymin),
                QPoint(self.xmax, self.ymax),
                QPoint(self.xmin, self.ymax)
            ]
        else:
            return []

    def paint(self, painter, pen=None):
        if self.points:
            if pen is None:
                color = self.line_color
                color.setAlpha(240)
                pen = QPen()
                pen.setColor(color)
                pen.setWidth(max(1, int(round(2.0 / self.scale))))
            painter.setPen(pen)

            line_path = QPainterPath()
            line_path.moveTo(self.points[0])

            for i, p in enumerate(self.points):
                line_path.lineTo(p)
            line_path.lineTo(self.points[0])
            painter.drawPath(line_path)

            if self.fill:
                color = self.select_fill_color if self.selected else self.fill_color
                painter.fillPath(line_path, color)

    def containsPoint(self, point):
        return self.makePath().contains(point)

    def nearTop(self, point):
        if (self.points[0].x() < point.x() < self.points[1].x()) and \
                (abs(self.points[0].y() - point.y()) < 3):
            return True
        return False

    def nearBottom(self, point):
        if (self.points[3].x() < point.x() < self.points[2].x()) and \
                (abs(self.points[2].y() - point.y()) < 3):
            return True
        return False

    def nearLeft(self, point):
        if (self.points[0].y() < point.y() < self.points[3].y()) and \
                (abs(self.points[0].x() - point.x()) < 3):
            return True
        return False

    def nearRight(self, point):
        if (self.points[1].y() < point.y() < self.points[2].y()) and \
                (abs(self.points[1].x() - point.x()) < 3):
            return True
        return False

    def nearTopLeft(self, point):
        if distance(point - self.points[0]) < 3:
            return True
        return False

    def nearTopRight(self, point):
        if distance(point - self.points[1]) < 3:
            return True
        return False

    def nearBottomLeft(self, point):
        if distance(point - self.points[3]) < 3:
            return True
        return False

    def nearBottomRight(self, point):
        if distance(point - self.points[2]) < 3:
            return True
        return False

    def nearShape(self, point):
        if (self.points[0].x() - 2 < point.x() < self.points[2].x() + 2) and \
           (self.points[0].y() - 2 < point.y() < self.points[2].y() + 2):
            return True
        return False



    def makePath(self):
        path = QPainterPath(self.points[0])
        for p in self.points[1:]:
            path.lineTo(p)
        return path

    def addPoint(self, point):
            self.points.append(point)

    # def __len__(self):
    #     return len(self.points)
    #
    # def __getitem__(self, key):
    #     return self.points[key]
    #
    # def __setitem__(self, key, value):
    #     self.points[key] = value


class TrueMixin():
    def __init__(self, *args, **kwargs):
        print("mixin")
        self.mtag = 0


class PropMixin():
    def __init__(self, *args, **kwargs):
        print("mixin")
        self.mtag = 0
        self.keep = 0
        self.score = 0


class TrueShape(Shape, TrueMixin):
    def __init__(self, name=None, *args, **kwargs):
        for base in self.__class__.__bases__:
            if hasattr(base, '__init__'):
                if base.__name__ == 'Shape':
                    base.__init__(self, name, 'true')
                else:
                    base.__init__(self, *args, **kwargs)


class PropShape(Shape, PropMixin):
    def __init__(self, name=None, *args, **kwargs):
        for base in self.__class__.__bases__:
            if hasattr(base, '__init__'):
                if base.__name__ == 'Shape':
                    base.__init__(self, name, 'prop')
                else:
                    base.__init__(self, *args, **kwargs)