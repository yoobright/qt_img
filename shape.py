# -*- coding:utf-8 -*-
from PyQt4.QtGui import *
from PyQt4.QtCore import *

GT_LINE_COLOR = QColor("#7FFF00")


class Shape(object):
    line_color = GT_LINE_COLOR
    scale = 1.0

    def __init__(self, label=None, line_color=None):
        self.label = label
        self.points = []
        self.fill = False
        self.selected = False

    def paint(self, painter):
        if self.points:
            color = self.line_color
            color.setAlpha(200)
            pen = QPen()
            pen.setColor(color)
            print(self.scale)
            pen.setWidth(max(1, int(round(2.0 / self.scale))))
            painter.setPen(pen)

            line_path = QPainterPath()
            line_path.moveTo(self.points[0])

            for i, p in enumerate(self.points):
                print(p)
                line_path.lineTo(p)
            line_path.lineTo(self.points[0])
            painter.drawPath(line_path)
