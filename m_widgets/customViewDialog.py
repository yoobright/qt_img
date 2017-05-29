# -*- coding:utf-8 -*-
from copy import deepcopy
try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *
from m_utils.utils import ViewStyle

BB = QDialogButtonBox


def color2str(color):
    r, g, b, _ = color.getRgb()
    return '#{0:02x}{1:02x}{2:02x}'.format(r, g, b)


class customViewDialog(QDialog):
    def __init__(self, parent=None, listItem=None):
        super(customViewDialog, self).__init__(parent)
        layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        top_right_layout = QVBoxLayout()
        self.listWidget = QListWidget(self)
        self.listItem = deepcopy(listItem)
        self.updateListItem()
        self.addButton = QPushButton(u'Add')
        self.deleteButton = QPushButton(u'Delete')
        self.deleteButton.setEnabled(False)
        self.editButton = QPushButton(u'Edit')
        self.editButton.setEnabled(False)
        top_right_layout.addWidget(self.addButton)
        top_right_layout.addWidget(self.deleteButton)
        top_right_layout.addWidget(self.editButton)
        top_right_layout.addStretch()
        top_layout.addWidget(self.listWidget)
        top_layout.addLayout(top_right_layout)
        layout.addLayout(top_layout)
        self.buttonBox = BB(BB.Ok | BB.Cancel, Qt.Horizontal, self)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

        # slot
        self.addButton.clicked.connect(self.addItem)
        self.deleteButton.clicked.connect(self.delItem)
        self.listWidget.selectionModel().selectionChanged.connect(
            self.selectChanged)
        self.editButton.clicked.connect(self.editItem)
        self.buttonBox.accepted.connect(self.validate)
        self.buttonBox.rejected.connect(self.reject)

    def validate(self):
        self.accept()

    def updateListItem(self):
        self.listWidget.clear()
        if self.listItem is not None and len(self.listItem) > 0:
            for i, item in enumerate(self.listItem):
                self.listWidget.addItem(self.newItem(item.name, item.color))

    def newItem(self, name, color):
        color_icon = QPixmap(26, 26)
        color_icon.fill(QColor(color))
        item = QListWidgetItem(QIcon(color_icon), name)
        item.setFlags(item.flags() & ~Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Checked)
        return item

    def addItem(self):
        style = StyleDialog().popUp()
        if style:
            view_style = ViewStyle(style[0], style[1])
            self.listItem.append(view_style)
            self.updateListItem()

    def delItem(self):
        if len(self.listWidget.selectedIndexes()) > 0:
            row = self.listWidget.selectedIndexes()[0].row()
            self.listItem.pop(row)
            self.updateListItem()

    def editItem(self):
        if len(self.listWidget.selectedIndexes()) > 0:
            row = self.listWidget.selectedIndexes()[0].row()
            style = StyleDialog(self.listItem[row].name,
                                self.listItem[row].color).popUp()
            if style:
                view_style = ViewStyle(style[0], style[1])
                self.listItem[row] = view_style
                self.updateListItem()

    def selectChanged(self):
        if len(self.listWidget.selectedIndexes()) > 0:
            self.deleteButton.setEnabled(True)
            self.editButton.setEnabled(True)
        else:
            self.deleteButton.setEnabled(False)
            self.editButton.setEnabled(False)

    def popUp(self):
        if self.exec_():
            return self.listItem
        else:
            return None


class StyleDialog(QDialog):
    def __init__(self, name=None, color=None, parent=None):
        super(StyleDialog, self).__init__(parent)
        layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        self.setWindowTitle(u'edit style')
        self.name = name
        self.color = color
        self.nameLabel = QLabel(u'name:')
        self.nameLineEdit = QLineEdit(self.name)
        self.nameLineEdit.setMaximumWidth(120)
        self.colorLabel = QLabel(u'color:')
        self.colorShowLabel = QLabel()
        self.colorShowLabel.setStyleSheet('border: 1px solid black')
        self.colorShowLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.colorShowLabel.setMinimumWidth(80)
        self.setShowColor(self.color)
        self.buttonBox = BB(BB.Ok | BB.Cancel, Qt.Horizontal, self)
        top_layout.addWidget(self.nameLabel)
        top_layout.addWidget(self.nameLineEdit)
        top_layout.addWidget(self.colorLabel)
        top_layout.addWidget(self.colorShowLabel)
        top_layout.addStretch()
        layout.addLayout(top_layout)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

        # slot
        self.colorShowLabel.mousePressEvent = self.setColor
        self.nameLineEdit.textChanged.connect(self.setName)
        self.buttonBox.accepted.connect(self.validate)
        self.buttonBox.rejected.connect(self.reject)

    def validate(self):
        self.accept()

    def popUp(self):
        if self.exec_():
            if self.name and self.color:
                return self.name, self.color
        return None

    def setName(self):
        name = str(self.nameLineEdit.text()).strip()
        if len(name) > 0:
            self.name = name

    def setColor(self, ev):
        color = QColorDialog.getColor()
        if color.isValid():
            self.setShowColor(color)
            self.color = color2str(color)

    def setShowColor(self, color):
        if color:
            pix_color = QPixmap(80, 22)
            pix_color.fill(QColor(color))
            self.colorShowLabel.setPixmap(pix_color)


