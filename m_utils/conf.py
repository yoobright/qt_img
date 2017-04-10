# -*- coding:utf-8 -*-

from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
from lxml import etree


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

# if __name__ == '__main__':
#     getLabelList('../conf/conf.xml')