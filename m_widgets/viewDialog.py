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

class viewDialog(QDialog):
    def __init__(self, text="prop class", parent=None, listItem=None):
        super(viewDialog, self).__init__(parent)
        layout = QVBoxLayout()
        self.listWidget = QListWidget(self)
        if listItem is not None and len(listItem) > 0:
            color_icon = QPixmap(26, 26)
            color_icon.fill(QColor(COLOR_STYLE[0]))
            item = QListWidgetItem(QIcon(color_icon), 'true')
            self.listWidget.addItem(item)
            separator = QListWidgetItem('--------------')
            separator.setSizeHint(QSize(8, 8))
            separator.setFlags(Qt.NoItemFlags)
            self.listWidget.addItem(separator)
            for i, item in enumerate(listItem):
                color_icon = QPixmap(26, 26)
                color_icon.fill(QColor(COLOR_STYLE[i + 1]))
                item = QListWidgetItem(QIcon(color_icon), item)
                self.listWidget.addItem(item)
        layout.addWidget(self.listWidget)
        self.buttonBox = BB(BB.Ok | BB.Cancel, Qt.Horizontal, self)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

        self.buttonBox.accepted.connect(self.validate)
        self.buttonBox.rejected.connect(self.reject)

    def validate(self):
        self.accept()
