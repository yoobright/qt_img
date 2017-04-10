# -*- coding: utf8 -*-
# import _init_path
from __future__ import print_function, division
import sys
import os
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
from lxml import etree
import codecs

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


def u(s):
    if PY2:
        return unicode(s.replace(r'\\', r'\\\\'), "unicode_escape")
    if PY3:
        return s


'''
in box list, data format like
{
    'xmin': xmin,
    'ymin': ymin,
    'xmax': xmax,
    'ymax': ymax,
    'name': name,
    'score': score,
    'keep': keep
}
'''


class NewWriter:

    def __init__(self, filename, imgSize, foldername='Unknown',
                 databaseSrc='Unknown', localImgPath=None):
        self.filename = filename
        self.foldername = foldername
        self.databaseSrc = databaseSrc
        self.imgSize = imgSize
        self.true_boxlist = []
        self.localImgPath = localImgPath
        # proposal box list & test box list
        self.prop_boxlist = []
        # self.test_boxlist = []

    def prettify(self, elem):
        """
            Return a pretty-printed XML string for the Element.
        """
        rough_string = ElementTree.tostring(elem, 'utf8')
        root = etree.fromstring(rough_string)
        return etree.tostring(root, pretty_print=True)

    def genXML(self):
        """
            Return XML root
        """
        # Check conditions
        if self.filename is None or \
                self.foldername is None or \
                self.imgSize is None or \
                len(self.true_boxlist) <= 0:
            return None

        top = Element('annotation')
        folder = SubElement(top, 'folder')
        folder.text = self.foldername

        filename = SubElement(top, 'filename')
        filename.text = self.filename

        source = SubElement(top, 'source')
        database = SubElement(source, 'database')
        database.text = self.databaseSrc

        size_part = SubElement(top, 'size')
        width = SubElement(size_part, 'width')
        height = SubElement(size_part, 'height')
        depth = SubElement(size_part, 'depth')
        width.text = str(self.imgSize[1])
        height.text = str(self.imgSize[0])
        if len(self.imgSize) == 3:
            depth.text = str(self.imgSize[2])
        else:
            depth.text = '1'

        segmented = SubElement(top, 'segmented')
        segmented.text = '0'
        return top

    def addTrueBox(self, xmin, ymin, xmax, ymax, name, mtag=None):
        bndbox = {'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax,
                  'name': name}
        if mtag is not None:
            bndbox['mtag'] = mtag
        self.true_boxlist.append(bndbox)

    def addPropBox(self, xmin, ymin, xmax, ymax, name, score=0, keep=0,
                   mtag=None):
        bndbox = {'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax,
                  'name': name, 'score': score, 'keep': keep}
        if mtag is not None:
            bndbox['mtag'] = mtag
        self.prop_boxlist.append(bndbox)

    def appendObjects(self, top):
        for true_box in self.true_boxlist:
            object_item = SubElement(top, 'object')
            name = SubElement(object_item, 'name')
            name.text = u(true_box['name'])
            pose = SubElement(object_item, 'pose')
            pose.text = "Unspecified"
            truncated = SubElement(object_item, 'truncated')
            truncated.text = "0"
            difficult = SubElement(object_item, 'difficult')
            difficult.text = "0"
            bndbox = SubElement(object_item, 'bndbox')
            xmin = SubElement(bndbox, 'xmin')
            xmin.text = str(true_box['xmin'])
            ymin = SubElement(bndbox, 'ymin')
            ymin.text = str(true_box['ymin'])
            xmax = SubElement(bndbox, 'xmax')
            xmax.text = str(true_box['xmax'])
            ymax = SubElement(bndbox, 'ymax')
            ymax.text = str(true_box['ymax'])
            if 'mtag' in true_box.keys():
                mtag = SubElement(object_item, 'mtag')
                mtag.text = str(true_box['mtag'])

        for proposal_box in self.prop_boxlist:
            proposal_item = SubElement(top, 'proposal')
            name = SubElement(proposal_item, 'name')
            name.text = u(proposal_box['name'])
            bndbox = SubElement(proposal_item, 'bndbox')
            xmin = SubElement(bndbox, 'xmin')
            xmin.text = str(proposal_box['xmin'])
            ymin = SubElement(bndbox, 'ymin')
            ymin.text = str(proposal_box['ymin'])
            xmax = SubElement(bndbox, 'xmax')
            xmax.text = str(proposal_box['xmax'])
            ymax = SubElement(bndbox, 'ymax')
            ymax.text = str(proposal_box['ymax'])
            score = SubElement(proposal_item, 'score')
            score.text = str(proposal_box['score'])
            keep = SubElement(proposal_item, 'keep')
            keep.text = str(proposal_box['keep'])
            if 'mtag' in proposal_box.keys():
                mtag = SubElement(proposal_item, 'mtag')
                mtag.text = str(proposal_box['mtag'])

    def save(self, dir=None, targetFile=None,):
        root = self.genXML()
        if root is not None:
            self.appendObjects(root)
            out_file = None
            if targetFile is None:
                targetFile = self.filename + '.xml'
            if dir:
                if not os.path.exists(dir):
                    os.mkdir(dir)
                targetFile = os.path.join(dir, targetFile)
            out_file = codecs.open(targetFile, 'w', encoding='utf-8')
            prettifyResult = self.prettify(root)
            out_file.write(prettifyResult.decode('utf8'))
            out_file.close()
            return True
        else: False


def get_points(bndbox):
    xmin = float(bndbox.find('xmin').text)
    ymin = float(bndbox.find('ymin').text)
    xmax = float(bndbox.find('xmax').text)
    ymax = float(bndbox.find('ymax').text)
    return xmin, ymin, xmax, ymax


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


class NewReader:

    def __init__(self, filepath):
        self.filepath = filepath
        self.true_boxlist = []
        self.prop_boxlist = []
        self.parseXML()

    def getTrueBox(self, idx):
        return self.true_boxlist[idx]

    def getPropBox(self, idx):
        return self.prop_boxlist[idx]

    def getTrueBoxLen(self):
        return len(self.true_boxlist)

    def getProBoxLen(self):
        return len(self.prop_boxlist)

    def addTrueBox(self, label, bndbox):
        xmin, ymin, xmax, ymax = get_points(bndbox)
        bndbox = {'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax,
                  'name': label}
        self.true_boxlist.append(bndbox)

    def addPropBox(self, label, bndbox, score, keep):
        xmin, ymin, xmax, ymax = get_points(bndbox)
        bndbox = {'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax,
                  'name': label, 'score': float(score), 'keep': int(keep)}
        self.prop_boxlist.append(bndbox)

    def parseXML(self):
        assert self.filepath.endswith('.xml'), "Unsupport file format"
        parser = etree.XMLParser(encoding='utf-8')
        try:
            xmltree = ElementTree.parse(self.filepath, parser=parser).getroot()
        except Exception as ex:
            if ex == etree.XMLSyntaxError:
                print('XMLSyntaxError! '
                      'can not parse xml file: {}'.format(self.filepath))
            else:
                raise ex
        else:
            for object_iter in xmltree.findall('object'):
                bndbox = object_iter.find("bndbox")
                label = object_iter.find('name').text
                self.addTrueBox(label, bndbox)

            for proposal_iter in xmltree.findall('proposal'):
                bndbox = proposal_iter.find("bndbox")
                label = proposal_iter.find('name').text
                score = proposal_iter.find('score').text
                keep = proposal_iter.find('keep').text
                self.addPropBox(label, bndbox, score, keep)

            return True
