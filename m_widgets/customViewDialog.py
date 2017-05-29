# -*- coding:utf-8 -*-
try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *
from m_utils.style import COLOR_STYLE

BB = QDialogButtonBox


class customViewDialog(QDialog):
    def __init__(self, parent=None, listItem=None):
        super(customViewDialog, self).__init__(parent)
        layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        top_right_layout = QVBoxLayout()
        self.listWidget = QListWidget(self)
        self.setlistItem(listItem)
        self.addButton = QPushButton(u'Add')
        self.deleteButton = QPushButton(u'Delete')
        self.editButton = QPushButton(u'Edit')
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

        self.buttonBox.accepted.connect(self.validate)
        self.buttonBox.rejected.connect(self.reject)

    def validate(self):
        self.accept()

    def setlistItem(self, listItem):
        self.listWidget.clear()
        if listItem is not None and len(listItem) > 0:
            for i, item in enumerate(listItem):
                self.listWidget.addItem(self.newItem(item.name, item.color))


    def newItem(self, name, color):
        color_icon = QPixmap(26, 26)
        color_icon.fill(QColor(color))
        item = QListWidgetItem(QIcon(color_icon), name)
        item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
        item.setCheckState(Qt.Checked)
        item.checkState()
        return item

    def popUp(self):
        if self.exec_():
            item_state = []
            for i in range(self.listWidget.count()):
                item = self.listWidget.item(i)
                if item.flags():
                    item_state.append(bool(item.checkState()))
            return item_state
        else:
            return None
