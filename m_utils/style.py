# -*- coding:utf-8 -*-
from PyQt4.QtGui import *
from PyQt4.QtCore import *

TRUE_STYLE = 0
PROP_1_STYLE = 1
PROP_2_STYLE = 2
PROP_3_STYLE = 3
PROP_4_STYLE = 4
PROP_5_STYLE = 5
PROP_6_STYLE = 6
PROP_7_STYLE = 7
PROP_8_STYLE = 8
PROP_D_STYLE = 9

COLOR_STYLE = [
    # true
    '#00ff33',
    # prop
    '#ffe599',
    '#f6b26b',
    '#93c47d',
    '#76a5af',
    '#6d9eeb',
    '#6fa8dc',
    '#8e7cc3',
    '#c27ba0',
    # grey
    '#989898',
]

def getRectStyle(st, keep=1):
    color = QColor(COLOR_STYLE[st])
    pen = QPen()
    if keep == 1:
        color.setAlpha(255)
        width = 2
        pen.setStyle(Qt.SolidLine)
    else:
        color.setAlpha(180)
        width = 1
        pen.setStyle(Qt.DotLine)
    pen.setColor(color)
    pen.setWidth(width)
    return pen

