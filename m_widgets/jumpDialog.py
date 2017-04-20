# -*- coding:utf-8 -*-
try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *

BB = QDialogButtonBox


class jumpDialog(QDialog):
    def __init__(self, parent=None, img_len=1):
        super(jumpDialog, self).__init__(parent)
        # layout
        layout = QVBoxLayout()
        self.label = QLabel()
        self.label.setText('jump to:')
        self.label.setFixedWidth(48)
        self.spinBox = QSpinBox(self)
        self.spinBox.setRange(0, img_len)
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.label)
        top_layout.addWidget(self.spinBox)
        layout.addLayout(top_layout)
        layout.addWidget(self.spinBox)
        self.buttonBox = BB(BB.Ok | BB.Cancel, Qt.Horizontal, self)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
        # size policy
        self.layout().setSizeConstraint(QLayout.SetFixedSize)
        # signal
        self.buttonBox.accepted.connect(self.validate)
        self.buttonBox.rejected.connect(self.reject)

    def validate(self):
        self.accept()

    def popUp(self, img_len=1):
        self.spinBox.setRange(1, img_len)
        return self.spinBox.text() if self.exec_() else None

