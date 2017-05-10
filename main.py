# -*- coding: utf-8 -*-
from __future__ import print_function, division

import os
import sys
from copy import deepcopy
from functools import partial

try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *

from m_widgets.canvas import Canvas
from m_widgets.shape import TrueShape
from m_widgets.labelDialog import LabelDialog
from m_widgets.viewDialog import viewDialog
from m_widgets.jumpDialog import jumpDialog
from m_utils.xmlFile import xmlFile
from m_utils.m_io import NewReader, NewWriter
from m_utils.conf import getLabelList
from m_utils.utils import get_stat, sort_nicely

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


def u(s):
    if sys.version_info[0] == 2:
        return s.decode('utf-8')
    if sys.version_info[0] == 3:
        return s

__appname__ = 'qt_img'


class ToolBar(QToolBar):
    def __init__(self, title):
        super(ToolBar, self).__init__(title)
        layout = self.layout()
        m = (0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setContentsMargins(*m)
        self.setContentsMargins(*m)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

    def addAction(self, action):
        if isinstance(action, QWidgetAction):
            return super(ToolBar, self).addAction(action)
        btn = QToolButton()
        btn.setDefaultAction(action)
        btn.setToolButtonStyle(self.toolButtonStyle())
        self.addWidget(btn)


class struct(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def newIcon(icon):
    return QIcon(':/' + icon)


def addActions(widget, actions):
    for action in actions:
        if action is None:
            widget.addSeparator()
        elif isinstance(action, QMenu):
            widget.addMenu(action)
        else:
            widget.addAction(action)


def newAction(parent, text, slot=None, shortcut=None, icon=None,
              tip=None, checkable=False, enabled=True):
    """Create a new action and assign callbacks, shortcuts, etc."""
    a = QAction(text, parent)
    if icon is not None:
        a.setIcon(newIcon(icon))
    if shortcut is not None:
        if isinstance(shortcut, (list, tuple)):
            a.setShortcuts(shortcut)
        else:
            a.setShortcut(shortcut)
    if tip is not None:
        a.setToolTip(tip)
        a.setStatusTip(tip)
    if slot is not None:
        a.triggered.connect(slot)
    if checkable:
        a.setCheckable(True)
    a.setEnabled(enabled)
    return a

def read(filename, default=None):
    try:
        with open(filename, 'rb') as f:
            return f.read()
    except:
        return default


class WindowMixin(object):
    def menu(self, title, actions=None):
        menu = self.menuBar().addMenu(title)
        if actions:
            addActions(menu, actions)
        return menu

    def toolbar(self, title, actions=None):
        toolbar = ToolBar(title)
        toolbar.setObjectName(u'%sToolBar' % title)
        # toolbar.setOrientation(Qt.Vertical)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        if actions:
            addActions(toolbar, actions)
        self.addToolBar(Qt.BottomToolBarArea, toolbar)
        return toolbar


class MainWindow(QMainWindow, WindowMixin):
    def __init__(self, parent=None, debug=False):
        self.imgFname = None
        self.imageData = None
        self.imageDir = None
        self.imageList = None
        self.imageIdx = None
        self.multiXml = False
        self.xmlDir = None
        self.saveDir = None
        self.annoList = None
        self.labelList = getLabelList('conf/conf.xml')
        self.xmlFname = None
        self.debug = debug

        QWidget.__init__(self, parent)
        self.setWindowTitle(__appname__)
        self.resize(800, 600)
        self.curr_canvas_scale = 1.0

        self.canvas = Canvas()
        self.canvas.setObjectName(_fromUtf8("canvas"))
        self.canvas.zoomRequest.connect(self.zoomRequest)
        self.canvas.mouseMoveSignal.connect(self.statusBar().showMessage)
        self.canvas.newShape.connect(self.newShape)
        self.canvas.selectionChanged.connect(self.shapeSelectionChanged)

        # init
        self.labelDialog = LabelDialog(parent=self,
                                       listItem=self.labelList)
        self.labelDialog.setWindowTitle('label')

        self.viewDialog = viewDialog(parent=self, listItem=['default'])
        self.viewDialog.setWindowTitle('view class')

        self.jumpDialog = jumpDialog(parent=self, img_len=0)
        self.jumpDialog.setWindowTitle('jump to ...')

        self.scroll = QScrollArea()
        self.scroll.setWidget(self.canvas)
        self.scroll.setWidgetResizable(True)

        # self.scrollArea.setWidget(self.canvas)
        # self.setCentralWidget(self.canvas)
        self.setCentralWidget(self.scroll)

        self.tools = self.toolbar(u"Tools")
        self.tools.setMovable(False)
        self.tools.setContextMenuPolicy(Qt.PreventContextMenu)
        self.statusBar().showMessage('test app started.')
        self.statusBar().show()

        action = partial(newAction, self)
        # menus action
        open_action = action('&Open File', self.openFile,
                             'Ctrl+O', None, u'Open image file')
        quit_action = action('&Quit', self.close,
                             None, None, u'Quit application')
        set_anno_action = action('Set XML Dir', self.setXMLDir,
                                  None, None, u'Set XML Dir')
        set_m_anno_action = action('Set Multi XML Dir', self.setMultiXMLDir,
                                   None, None, u'Set Multi XML Dir')
        set_s_dir_action = action('Set XML Save Dir', self.setXMLSaveDir,
                                  None, None, u'Set XML Save Dir')
        advanced_action = action('&Advanced Mode', self.toggleAdvancedMode,
                                 None, None, u'Switch to advanced mode',
                                 checkable=True)
        fit_action = action('&Fit Window', self.fitWindowSize,
                             None, None, u'Fit window')
        jump_action = action('&Jump To...', self.jumpToImg,
                             None, None, u'&Jump To...')
        view_action = action('&View Class', self.viewClass,
                             None, None, u'view Class')

        stat_action = action('&Pic Stat', self.showStat,
                             None, None, u'Pic Stat')
        all_stat_action = action('&All Stat', self.allStat,
                             None, None, u'All Stat')

        info_action = action('&Info', self.showInfo,
                             None, None, u'Info')

        # toolbar action
        draw_action = action('&Draw', self.draw,
                             'D', None, u'Draw')
        draw_action.setCheckable(True)
        next_action = action('&Next', self.openNextImg,
                             'Right', None, u'Open Next')
        prev_action = action('&Prev', self.openPrevImg,
                             'Left', None, u'Open Prev')
        save_action = action('&Save', self.saveLabel,
                             'Ctrl+S', None, u'Save Label')
        test_action = action('&Test', self.testImg,
                             None, None, u'Test')
        # box action
        set_true_action = action('Set True Box', self.setTrueBox,
                                 None, None, u'Set True Box')
        set_error_action = action('Set Error Box', self.setErrorBox,
                                 None, None, u'Set Error Box')
        set_dev_action = action('Set Deviation Box', self.setDevBox,
                                 None, None, u'Set Deviation Box')
        del_box_action = action('Del Current Box', self.delBox,
                                None, None, u'Del Current Box')
        res_box_action = action('Reset Box', self.resetBox,
                                None, None, u'Reset Box')

        # store actions for further handling.
        self.actions = struct(
            open=open_action,
            quit=quit_action,
            set_anno=set_anno_action,
            set_m_anno=set_m_anno_action,
            set_s_dir=set_s_dir_action,
            advanced=advanced_action,
            fit=fit_action,
            jump=jump_action,
            view=view_action,
            stat=stat_action,
            all_stat=all_stat_action,
            info=info_action,
            draw=draw_action,
            next=next_action,
            prev=prev_action,
            del_box=del_box_action,
            set_true=set_true_action,
            set_dev=set_dev_action,
            set_error=set_error_action,
            res_box=res_box_action,
        )
        # set tools
        tool = [prev_action, next_action, draw_action, save_action]
        if self.debug:
            tool.append(test_action)
        addActions(self.tools, tool)
        # set menus action
        self.menus = struct(file=self.menu('&File'), view=self.menu('&View'),
                            edit=self.menu('&Edit'), stat=self.menu('&Stat'))
        self.setDefaultContext()


    def scanAllImages(self, folderPath):
        name_filter = ['*.jpeg', '*.jpg', '*.png', '*.bmp']
        images = []
        file_dir = QDir(folderPath)
        file_dir.setNameFilters(name_filter)
        file_dir.setSorting(QDir.Name)

        images = [u(os.path.abspath(os.path.join(folderPath, str(image))))
                  for image in file_dir.entryList()]
        # for windows dir
        images = [x.replace('\\', '/') for x in images]
        images = sort_nicely(images)
        return images

    def openFile(self):
        path = os.path.dirname(str(self.imgFname)) \
            if self.imgFname else '.'
        # formats = ['*.%s' % str(fmt).lower() \
        #            for fmt in QImageReader.supportedImageFormats()]
        formats = "*.bmp *.jpeg *.jpg *.png"
        filters = "Image & Label files (%s)" % formats
        filename = str(QFileDialog.getOpenFileName(self,
            '%s - Choose Image file' % __appname__,
            path, filters))
        if filename:
            self.imageDir = os.path.dirname(filename)
            self.imageList = self.scanAllImages(self.imageDir)

            if filename in self.imageList:
                self.imageIdx = self.imageList.index(u(filename))
            if not self.loadFile(filename):
                self.resetState()

    def errorMessage(self, title, message):
        return QMessageBox.critical(self, title, '<p><b>%s</b></p>%s' %
                                    (title, message))

    def status(self, message, delay=5000):
        if delay is not None:
            self.statusBar().showMessage(message, delay)

    def scaleFitWindow(self):
        e = 2.0  # So that no scrollbars are generated.
        w1 = self.centralWidget().width() - e
        h1 = self.centralWidget().height() - e
        a1 = w1/ h1
        # Calculate a new scale value based on the pixmap's aspect ratio.
        w2 = self.canvas.pixmap.width() - 0.0
        h2 = self.canvas.pixmap.height() - 0.0
        a2 = w2 / h2
        return w1 / w2 if a2 >= a1 else h1 / h2

    def resetState(self):
        self.imgFname = None
        self.imageData = None
        self.canvas.resetState()
        self.canvas.setEnabled(False)

    def loadFile(self, filename=None):
        self.resetState()
        if filename and QFile.exists(filename):
            self.imageData = QImage()
            self.imageData.load(filename)
            if self.imageData.isNull():
                self.errorMessage(
                    u'Error opening file',
                    u"<p>Make sure <i>%s</i> is a valid image file." %
                    filename)
                self.status("Error reading %s" % filename)
                return False
            self.canvas.setEnabled(True)
            pixmap = QPixmap().fromImage(self.imageData)
            self.canvas.loadPixmap(pixmap)
            self.canvas.scale = self.scaleFitWindow()
            self.canvas.adjustSize()
            self.canvas.update()
            self.setEditMode()
            self.imgFname = u(filename)
            num_tag = u""
            if len(self.imageList) > 1:
                num_tag = u"[{}/{}]".format(self.imageIdx + 1,
                                               len(self.imageList))
            title = u"{} {} {}".format(__appname__,
                                       self.imageList[self.imageIdx],
                                       num_tag)
            self.setWindowTitle(title)
            return True
        return False

    def setEditMode(self):
        self.canvas.setMode('edit')
        self.actions.draw.setChecked(False)

    def setDefaultContext(self):
        file_actions = (self.actions.open,
                        self.actions.set_anno, None,
                        self.actions.set_s_dir, None,
                        self.actions.quit)
        view_actions = (self.actions.advanced, None,
                        self.actions.fit,
                        self.actions.jump, None,
                        self.actions.view)
        edit_actions = (self.actions.del_box,)

        self.menus.file.clear()
        addActions(self.menus.file, file_actions)
        self.menus.view.clear()
        addActions(self.menus.view, view_actions)
        self.menus.edit.clear()
        addActions(self.menus.edit, edit_actions)
        self.menus.stat.clear()
        self.menuBar().addAction(self.actions.info)
        # set canvas action
        self.canvas.menus.clear()
        addActions(self.canvas.menus, edit_actions)

    def setAdvanceContext(self):
        file_actions = (self.actions.open,
                        self.actions.set_anno,
                        self.actions.set_m_anno, None,
                        self.actions.set_s_dir, None,
                        self.actions.quit)
        view_actions = (self.actions.advanced, None,
                        self.actions.fit,
                        self.actions.jump, None,
                        self.actions.view)
        edit_actions = (self.actions.del_box, None,
                        self.actions.set_true,
                        self.actions.set_dev,
                        self.actions.set_error,
                        self.actions.res_box)
        stat_actions = (self.actions.stat,
                        self.actions.all_stat)

        self.menus.file.clear()
        addActions(self.menus.file, file_actions)
        self.menus.view.clear()
        addActions(self.menus.view, view_actions)
        self.menus.edit.clear()
        addActions(self.menus.edit, edit_actions)
        self.menus.stat.clear()
        addActions(self.menus.stat, stat_actions)
        self.menuBar().addAction(self.actions.info)
        # set canvas action
        self.canvas.menus.clear()
        addActions(self.canvas.menus, edit_actions)

    def advanced(self):
        return self.actions.advanced.isChecked()

    def toggleAdvancedMode(self, value=True):
        self.populateModeActions()

    def populateModeActions(self):
        if self.advanced():
            self.setAdvanceContext()
        else:
            self.setDefaultContext()

    def fitWindowSize(self):
        if self.canvas.pixmap:
            self.canvas.scale = self.scaleFitWindow()
            self.canvas.adjustSize()
            self.canvas.update()
            self.curr_canvas_scale = self.canvas.scale

    def setXMLDir(self):
        self.multiXml = False
        self.annoList = None
        curr_path = os.path.dirname(self.imgFname) \
                if self.imgFname else '.'

        dir_path = str(QFileDialog.getExistingDirectory(self,
            '%s - Open Directory' % __appname__,  curr_path,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks))

        if dir_path is not None and len(dir_path) > 1:
            dir_path = dir_path.replace('\\', '/')
            self.xmlDir = dir_path

        self.loadXMLFile()

    def setMultiXMLDir(self):
        curr_path = os.path.dirname(self.imgFname) \
                if self.imgFname else '.'

        dir_path = str(QFileDialog.getExistingDirectory(self,
            '%s - Open Directory' % __appname__,  curr_path,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks))

        if dir_path is not None and len(dir_path) > 1:
            dir_path = dir_path.replace('\\', '/')
            file_dir = QDir(dir_path)
            file_dir.setFilter(QDir.Dirs | QDir.NoDotAndDotDot)
            file_dir.setSorting(QDir.Name)

            if len(file_dir.entryList()) > 8:
                print('too much annotation class')
                return

            self.multiXml = True
            self.xmlDir = dir_path
            self.annoList = [str(x) for x in file_dir.entryList()]

            if len(self.annoList) > 0:
                self.viewDialog.setlistItem(self.annoList)
                self.canvas.showFilter = None
                self.loadXMLFile()
            else:
                print('multi dir does not exist')

    def setXMLSaveDir(self):
        curr_path = os.path.dirname(self.imgFname) \
                if self.imgFname else '.'
        dir_path = str(QFileDialog.getExistingDirectory(self,
            '%s - Open Directory' % __appname__,  curr_path,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks))

        if dir_path:
            self.saveDir = dir_path.replace('\\', '/')

    def getXMLFileName(self, image_name=None, xml_dir=None):
        ret = None
        if image_name is None and self.imgFname:
            image_name = self.imgFname
        else:
            return ret
        if xml_dir is None:
            xml_dir = self.xmlDir
        if xml_dir:
            name_list = [os.path.basename(image_name),
                         os.path.splitext(os.path.basename(image_name))[0]]
            xml_file = None
            for name in name_list:
                xml_file = os.path.join(xml_dir,
                                        name + ".xml").replace('\\', '/')
                if os.path.exists(xml_file):
                    ret = xml_file
                    break
        return ret

    def loadXMLFile(self):
            if self.multiXml:
                xml_list = []
                for f in self.annoList:
                    xml_dir = os.path.join(self.xmlDir, f).replace('\\', '/')
                    xml = self.getXMLFileName(xml_dir=xml_dir)
                    if xml:
                        xml_list.append(xml)
                self.canvas.true_shapes = []
                self.canvas.prop_shapes = []
                for xml in xml_list:
                    xml_file = xmlFile(xml)
                    self.canvas.prop_shapes.append(xml_file.prop_meta_shapes)
                self.canvas.update()
            else:
                xml_file = self.getXMLFileName()
                if xml_file:
                    self.status(u'find xml file', delay=1000)
                    self.xmlFname = xml_file
                    xml_file = xmlFile(self.xmlFname)
                    self.canvas.true_shapes = xml_file.true_meta_shapes
                    self.canvas.prop_shapes = []
                    self.canvas.prop_shapes.append(xml_file.prop_meta_shapes)
                    self.canvas.update()
                else:
                    self.status(u'can not find xml file', delay=3000)

    def viewClass(self):
        view_state = self.viewDialog.popUp()
        if view_state:
            self.canvas.showFilter = view_state
            self.canvas.update()

    def showInfo(self):
        print("imgFname: {}".format(self.imgFname))
        print("imageDir: {}".format(self.imageDir))
        print("imageIdx: {}".format(self.imageIdx))
        print("xmlDir: {}".format(self.xmlDir))
        print("xmlFname: {}".format(self.xmlFname))
        print("curr_canvas_scale: {}".format(self.curr_canvas_scale))
        print("true_shapes: {}".format(self.canvas.true_shapes))
        prop_shapes =[[s for s in shapes if s.keep]
                      for shapes in self.canvas.prop_shapes]
        print("prop_shapes: {}".format(prop_shapes))
        print("selectedShape: {}".format(self.canvas.selectedShape))


    def showStat(self):
        xml_file = self.getXMLFileName()
        if xml_file:
            reader = NewReader(xml_file)
            stat = get_stat(reader)
            print(stat)

    def allStat(self):
        all_stat = {
        'correct_box': 0,
        'deviation_box': 0,
        'error_box': 0,
        'miss_box': 0,
        }
        if self.imageList and len(self.imageList) > 0:
            for image_name in self.imageList:
                xml_file = self.getXMLFileName(image_name)
                if xml_file:
                    reader = NewReader(xml_file)
                    stat = get_stat(reader, a_threshold=0.6)
                    all_stat['correct_box'] += stat['correct_box']
                    all_stat['deviation_box'] += stat['deviation_box']
                    all_stat['error_box'] += stat['error_box']
                    all_stat['miss_box'] += stat['miss_box']

            print(all_stat)

    def loadImgFromIdx(self, idx):
        filename = self.imageList[idx]
        self.imageIdx = idx
        if self.loadFile(filename):
            self.loadXMLFile()
        else:
            self.resetState()

    def openNextImg(self):
        if (self.imageList is None) or (len(self.imageList) <= 0):
            return

        nextIdx = (self.imageIdx + 1) % len(self.imageList)
        self.loadImgFromIdx(nextIdx)


    def openPrevImg(self):
        if (self.imageList is None) or (len(self.imageList) <= 0):
            return

        prevIdx = (self.imageIdx - 1) % len(self.imageList)
        self.loadImgFromIdx(prevIdx)

    def jumpToImg(self):
        if self.imageList and len(self.imageList) > 1:
            num = self.jumpDialog.popUp(img_len=len(self.imageList))
            if num:
                idx = int(num) - 1
                self.loadImgFromIdx(idx)

    def saveLabel(self):
        dir_path = None
        if self.imgFname:
            if self.saveDir:
                message = QMessageBox()
                message.setIcon(QMessageBox.Information)
                message.setWindowTitle("save xml...")
                message.setText("Save XMl to '{}'?".format(self.saveDir))
                message.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                message.setDefaultButton(QMessageBox.Yes)
                if message.exec_() == QMessageBox.Yes:
                    dir_path = self.saveDir
            else:
                curr_path = os.path.dirname(self.imgFname) \
                    if self.imgFname else '.'
                dir_path = str(QFileDialog.getExistingDirectory(self,
                    '%s - Open Directory' % __appname__,  curr_path,
                    QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks))

        if dir_path is not None and len(dir_path) > 1:
            dir_path = dir_path.replace('\\', '/')
            img_name = os.path.basename(self.imgFname)
            self.saveXMl(img_name, dir_path)

    def saveXMl(self, img_name=None, dir_path=None, pIdx=0):
        if dir:
            img_size = (self.canvas.pixmap.width(),
                        self.canvas.pixmap.height(),
                        3)
            writer = NewWriter(img_name, img_size)

            for shape in self.canvas.true_shapes:
                if shape.mtag and self.advanced():
                    mtag = shape.mtag
                else:
                    mtag =None
                writer.addTrueBox(shape.xmin,
                                  shape.ymin,
                                  shape.xmax,
                                  shape.ymax,
                                  shape.name,
                                  mtag)

            if len(self.canvas.prop_shapes) > pIdx:
                for shape in self.canvas.prop_shapes[pIdx]:
                    if shape.mtag and self.advanced():
                        mtag = shape.mtag
                    else:
                        mtag =None
                    writer.addPropBox(shape.xmin,
                                      shape.ymin,
                                      shape.xmax,
                                      shape.ymax,
                                      shape.name,
                                      shape.score,
                                      shape.keep,
                                      mtag)
            print(writer.save(dir_path))

    def zoomRequest(self, delta, pos):
        units = delta / (8 * 15)
        scale = self.canvas.scale + units / 10
        if scale <= 0:
            scale = 0.01

        if self.canvas.pixmap:
            self.canvas.scale = scale
            self.canvas.adjustSize()
            self.canvas.update()
            ScrollbarPos = QPointF(self.scroll.horizontalScrollBar().value(),
                                   self.scroll.verticalScrollBar().value())
            DeltaToPos = (pos + QPointF(10, 10)) / self.curr_canvas_scale
            Delta = DeltaToPos * self.canvas.scale - \
                    DeltaToPos * self.curr_canvas_scale
            self.scroll.horizontalScrollBar().setValue(ScrollbarPos.x() +
                                                       Delta.x())
            self.scroll.verticalScrollBar().setValue(ScrollbarPos.y() +
                                                     Delta.y())
            # print(self.scroll.horizontalScrollBar().value())
            # print(pos)
            # print(ScrollbarPos)
            # print(self.scroll.pos())
            # print(self.canvas.pos())
            self.curr_canvas_scale = self.canvas.scale

    def shapeSelectionChanged(self, selected=False):
        self.actions.del_box.setEnabled(False)
        self.actions.set_true.setEnabled(False)
        self.actions.set_dev.setEnabled(False)
        self.actions.set_error.setEnabled(False)
        self.actions.res_box.setEnabled(False)
        if selected:
            if self.canvas.selectedShape.b_type == 'true':
                 self.actions.del_box.setEnabled(True)
            elif self.canvas.selectedShape.b_type == 'prop':
                self.actions.set_true.setEnabled(True)
                self.actions.set_dev.setEnabled(True)
                self.actions.set_error.setEnabled(True)
                self.actions.res_box.setEnabled(True)

    def newShape(self):
        text = self.labelDialog.popUp()
        if text is not None:
            self.canvas.current_shape.name = str(text)
            self.canvas.addTrueShape()
            print('draw done')
            self.setEditMode()

            if text not in self.labelList:
                self.labelList.insert(0, str(text))
                self.labelDialog.updateItem(self.labelList)
            return True

    def draw(self):
        if self.canvas.isEditMode():
            self.canvas.setMode('draw')
            self.status("draw mode")
        else:
            self.canvas.setMode('edit')
            self.status("edit mode")

        # def zoomRequest(self, delta):
        #     units = delta / (8 * 15)
        #     scale = 10
        #     self.addZoom(scale * units)

    # def center(self):
    #     qr = self.frameGeometry()
    #     cp = QDesktopWidget().availableGeometry().center()
    #     qr.moveCenter(cp)
    #     self.move(qr.topLeft())

    def setTrueBox(self):
        if self.canvas.selectedShape and \
           self.canvas.selectedShape.b_type == 'prop':
            self.canvas.selectedShape.mtag = 1
            newShape = TrueShape(self.canvas.selectedShape.name)
            newShape.xmin = self.canvas.selectedShape.xmin
            newShape.ymin = self.canvas.selectedShape.ymin
            newShape.xmax = self.canvas.selectedShape.xmax
            newShape.ymax = self.canvas.selectedShape.ymax
            self.canvas.true_shapes.append(newShape)
            self.canvas.update()

    def setDevBox(self):
        if self.canvas.selectedShape and \
           self.canvas.selectedShape.b_type == 'prop':
            self.canvas.selectedShape.mtag = 2

    def setErrorBox(self):
        if self.canvas.selectedShape and \
           self.canvas.selectedShape.b_type == 'prop':
            self.canvas.selectedShape.mtag = 4

    def resetBox(self):
        if self.canvas.selectedShape and \
           self.canvas.selectedShape.b_type == 'prop':
            self.canvas.selectedShape.mtag = 0

    def delBox(self):
        if self.canvas.selectedShape and \
           self.canvas.selectedShape.b_type == 'true':
            for shape in self.canvas.true_shapes:
                if shape == self.canvas.selectedShape:
                    self.canvas.true_shapes.remove(shape)
                    break
            self.canvas.update()


    def testImg(self):
        from m_widgets.shape import PropShape
        # if len(self.canvas.true_meta_shapes) < 1:
        if 1:
            test_shape = PropShape('test')
            test_shape.xmin = 100
            test_shape.ymin = 100
            test_shape.xmax = 200
            test_shape.ymax = 200
            test_shape.keep = 1
            test_shape.score = 0.9
            self.canvas.prop_shapes.append([test_shape])
        self.canvas.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    debug = 'debug' in sys.argv
    myapp = MainWindow(debug=debug)
    myapp.show()
    sys.exit(app.exec_())
