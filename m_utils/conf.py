# -*- coding:utf-8 -*-
from __future__ import print_function, division
import re
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
from lxml import etree
from m_utils.utils import ViewStyle


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


def check_color_code(str):
    pattern = re.compile('^#(?:[0-9a-fA-F]{3}){1,2}$')
    match = re.search(pattern, str)
    return match


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
            if name and color and check_color_code(color):
                view_list.append(ViewStyle(name, color))
        return view_list

if __name__ == '__main__':
    a = getViewList('../conf/conf.xml')
    print(a)