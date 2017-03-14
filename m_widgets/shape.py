# -*- coding:utf-8 -*-
from PyQt4.QtGui import *
from PyQt4.QtCore import *

GT_LINE_COLOR = QColor("#7FFF00")
DEFAULT_FILL_COLOR = QColor(255, 0, 0, 100)


class Shape(object):
    line_color = GT_LINE_COLOR
    fill_color = DEFAULT_FILL_COLOR
    scale = 1.0

    def __init__(self, name):
        self.name = name
        self.points = []
        self.fill = False
        self.selected = False

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
                color = self.fill_color
                painter.fillPath(line_path, color)

    def containsPoint(self, point):
        return self.makePath().contains(point)

    def makePath(self):
        path = QPainterPath(self.points[0])
        for p in self.points[1:]:
            path.lineTo(p)
        return path

    def addPoint(self, point):
            self.points.append(point)
