# -*- coding:utf-8 -*-
from __future__ import print_function, division

from PyQt4.QtCore import *

from m_io import NewReader
from m_widgets.shape import Shape

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
            shape = Shape(box['name'], b_type='true')
            shape.addPoint(QPoint(box['xmin'], box['ymin']))
            shape.addPoint(QPoint(box['xmax'], box['ymin']))
            shape.addPoint(QPoint(box['xmax'], box['ymax']))
            shape.addPoint(QPoint(box['xmin'], box['ymax']))
            meta_shape = {
                'shape': shape,
                'name': box['name'],
                'xmin': box['xmin'],
                'ymin': box['ymin'],
                'xmax': box['xmax'],
                'ymax': box['ymax']
            }
            self.true_meta_shapes.append(meta_shape)

        for box in self.reader.prop_boxlist:
            shape = Shape(box['name'], b_type='prop')
            shape.addPoint(QPoint(box['xmin'], box['ymin']))
            shape.addPoint(QPoint(box['xmax'], box['ymin']))
            shape.addPoint(QPoint(box['xmax'], box['ymax']))
            shape.addPoint(QPoint(box['xmin'], box['ymax']))
            meta_shape = {
                'shape': shape,
                'name': box['name'],
                'score': box['score'],
                'keep': box['keep'],
                'xmin': box['xmin'],
                'ymin': box['ymin'],
                'xmax': box['xmax'],
                'ymax': box['ymax']
            }
            self.prop_meta_shapes.append(meta_shape)

# if __name__ == '__main__':
#     test = xmlFile('../test/anno/grp09_1280x720_00000.jpg.xml')
#     print(test.true_meta_shapes[0]['shape'].points)
#     print(test.prop_meta_shapes[0]['shape'].points)
#     print(test.prop_meta_shapes[0]['score'])
