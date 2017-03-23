# -*- coding:utf-8 -*-
from math import sqrt

def compute_iou(box1, box2):
    x_inter = min(box1['xmax'], box2['xmax']) - max(box1['xmin'], box2['xmin'])
    y_inter = min(box1['ymax'], box2['ymax']) - max(box1['ymin'], box2['ymin'])

    if x_inter <= 0 or y_inter <= 0:
        return 0
    else:
        area_inter = x_inter * y_inter
        area_union = \
            (box1['xmax'] - box1['xmin']) * (box1['ymax'] - box1['ymin']) + \
            (box2['xmax'] - box2['xmin']) * (box2['ymax'] - box2['ymin']) - \
            area_inter
        return area_inter / area_union

def read(filename, default=None):
    try:
        with open(filename, 'rb') as f:
            return f.read()
    except:
        return default

def distance(p):
    return sqrt(p.x() * p.x() + p.y() * p.y())