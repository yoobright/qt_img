# -*- coding:utf-8 -*-
from __future__ import print_function, division
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
from lxml import etree


class ViewStyle(object):
    def __init__(self, name, color):
        self.name = name
        self.color = color

    def __repr__(self):
        return "<name: {}, color: {}>".format(self.name, self.color)


def getLabelList(filepath):
    parser = etree.XMLParser(encoding='utf-8')
    try:
        xmltree = ElementTree.parse(filepath, parser=parser).getroot()
    except Exception as ex:
        if ex == etree.XMLSyntaxError:
            print('XMLSyntaxError! '
                  'can not parse xml file: {}'.format(filepath))
        else:
            raise ex
    else:
        label_node = xmltree.find('labelList')
        label_list = [x.text for x in label_node.findall('label')]
        return label_list

def getViewList(filepath):
    parser = etree.XMLParser(encoding='utf-8')
    try:
        xmltree = ElementTree.parse(filepath, parser=parser).getroot()
    except Exception as ex:
        if ex == etree.XMLSyntaxError:
            print('XMLSyntaxError! '
                  'can not parse xml file: {}'.format(filepath))
        else:
            raise ex
    else:
        view_list = []
        label_node = xmltree.find('customView')
        for view in label_node.findall('view'):
            name = view.find('name').text
            color = view.find('color').text
            if name and color:
                view_list.append(ViewStyle(name, color))
        return view_list

if __name__ == '__main__':
    a = getViewList('../conf/conf.xml')
    print([x for x in a if x.name == 'xx'])