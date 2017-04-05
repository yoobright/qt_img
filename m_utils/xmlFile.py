# -*- coding:utf-8 -*-
from __future__ import print_function, division

from PyQt4.QtCore import *

from m_io import NewReader
from m_widgets.shape import TrueShape, PropShape

'''
in meta shapes, data format like
{
    'shape': shape
    'score': score,
    'keep': keep
}
'''


class xmlFile(object):
    def __init__(self, filename=None):
        self.reader = NewReader(filename)
        self.true_meta_shapes = []
        self.prop_meta_shapes = []
        self.covert_shape()

    def covert_shape(self):
        for box in self.reader.true_boxlist:
            shape = TrueShape(box['name'])
            shape.xmin = box['xmin']
            shape.ymin = box['ymin']
            shape.xmax = box['xmax']
            shape.ymax = box['ymax']
            self.true_meta_shapes.append(shape)

        for box in self.reader.prop_boxlist:
            shape = PropShape(box['name'])
            shape.xmin = box['xmin']
            shape.ymin = box['ymin']
            shape.xmax = box['xmax']
            shape.ymax = box['ymax']
            shape.score = box['score']
            shape.keep = box['score']
            self.prop_meta_shapes.append(shape)

# if __name__ == '__main__':
#     test = xmlFile('../test/anno/grp09_1280x720_00000.jpg.xml')
#     print(test.true_meta_shapes[0]['shape'].points)
#     print(test.prop_meta_shapes[0]['shape'].points)
#     print(test.prop_meta_shapes[0]['score'])
