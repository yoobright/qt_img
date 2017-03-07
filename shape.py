# -*- coding:utf-8 -*-
from PyQt4.QtGui import *
from PyQt4.QtCore import *

DEFAULT_LINE_COLOR = QColor(0, 255, 0, 128)

class Shape(object):
    line_color = DEFAULT_LINE_COLOR
    scale = 1.0
    def __init__(self, label=None, line_color=None):
        self.label = label
        self.points = []
        self.fill = False
        self.selected = False

    def paint(self, painter):
        if self.points:
            color = self.line_color
            pen = QPen(color)
            pen.setWidth(max(1, int(round(2.0 / self.scale))))

            line_path = QPainterPath()
            line_path.moveTo(self.points[0])

            for i, p in enumerate(self.points):
                line_path.lineTo(p)
            line_path.lineTo(self.points[0])