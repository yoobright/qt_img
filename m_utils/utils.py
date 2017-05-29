# -*- coding:utf-8 -*-
from __future__ import print_function
import re
from math import sqrt
from copy import deepcopy


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


def get_stat(reader, a_threshold=0.8, d_threshold=0.1):
    correct_box = 0
    deviation_box = 0
    error_box = 0
    miss_box = 0
    true_boxlist = deepcopy(reader.true_boxlist)
    prop_keep_boxlist = []

    for true_box in true_boxlist:
        true_box['find'] = False

    for prop_box in reader.prop_boxlist:
        if prop_box['keep'] == 1:
            prop_box['iou'] = 0
            for true_box in true_boxlist:
                iou = compute_iou(prop_box, true_box)
                if iou > d_threshold:
                    true_box['find'] = True
                prop_box['iou'] = max(prop_box['iou'], iou)
            prop_keep_boxlist.append(prop_box)

    correct_box = len(filter(lambda x: x['iou'] >= a_threshold,
                             prop_keep_boxlist))
    deviation_box = len(filter(lambda x: a_threshold > x['iou'] >= d_threshold,
                               prop_keep_boxlist))
    error_box = len(filter(lambda x: x['iou'] < d_threshold,
                           prop_keep_boxlist))
    miss_box = len(filter(lambda x: not x['find'], true_boxlist))

    return {
        'correct_box': correct_box,
        'deviation_box': deviation_box,
        'error_box': error_box,
        'miss_box': miss_box
    }


def tryint(s):
    try:
        return int(s)
    except:
        return s


def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [tryint(c) for c in re.split('([0-9]+)', s)]


def sort_nicely(l):
    """ Sort the given list in the way that humans expect.
    """
    return sorted(l, key=alphanum_key)


class ViewStyle(object):
    def __init__(self, name, color):
        self.name = name
        self.color = color

    def __repr__(self):
        return "<name: {}, color: {}>".format(self.name, self.color)





