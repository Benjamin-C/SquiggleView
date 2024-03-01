from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from PIL import Image

from scope.oscope import Oscilloscope

import numpy as np

class ScreenshotGUI(QWidget):
    def __init__(self, scope: Oscilloscope):
        super().__init__()

        def setw(obj, w):
            obj.setMaximumSize(QSize(w, 25))
            obj.setMinimumSize(QSize(w, 25))

        self.scope = scope

        if not self.objectName():
            self.setObjectName(u"channel")
        # self.resize(667, 174)
        self.setMinimumSize(QSize(810, 30+480))

        self.verticalLayoutWidget = QWidget(self)
        self.vlo = QVBoxLayout(self.verticalLayoutWidget)
        self.vlo.setObjectName(u"vlo")
        self.vlo.setContentsMargins(0, 0, 0, 0)

        self.horizontalLayoutWidget = QWidget(self.verticalLayoutWidget)
        self.vlo.addWidget(self.horizontalLayoutWidget)

        self.image_label = QLabel(self.verticalLayoutWidget)
        self.image_label.setMaximumSize(801, 480)
        self.image_label.setMinimumSize(801, 480)
        self.image_label.setContentsMargins(0, 0, 0, 0)
        self.vlo.addWidget(self.image_label)

        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        # self.horizontalLayoutWidget.setGeometry(QRect(50, 80, 478, 29))

        self.fields = QHBoxLayout(self.horizontalLayoutWidget)
        self.fields.setObjectName(u"fields")
        self.fields.setContentsMargins(0, 0, 0, 0)

        # self.id = QLabel(self.horizontalLayoutWidget)
        # self.id.setObjectName(u"id")
        # self.id.setText(QCoreApplication.translate("channel", u"CH" + str(self.scopech.id), None))
        # self.fields.addWidget(self.id)

        # Create a new button
        self.scbutton = QPushButton("Take Screenshot")
        setw(self.scbutton, 150)
        self._image = None
        def onScreenshot():
            self.save_label.setText("")
            self._image = scope.screenshot()
            self._image.save("gui_sc.png", "PNG")
            r, g, b = self._image.split()
            im = Image.merge("RGB", (b, g, r))
            im2 = im.convert("RGBA")
            data = im2.tobytes("raw", "RGBA")
            qim = QImage(data, im.size[0], im.size[1], QImage.Format.Format_ARGB32)
            pixmap = QPixmap.fromImage(qim)
            self.image_label.setPixmap(pixmap)
        self.scbutton.clicked.connect(onScreenshot)
        self.fields.addWidget(self.scbutton)
        # .save(file_name, "PNG")

        self.filenameinput = QLineEdit("screenshot")
        setw(self.filenameinput, 180)
        self.fields.addWidget(self.filenameinput)

        self.extlabel = QLabel(".png")
        setw(self.extlabel, 40)
        self.fields.addWidget(self.extlabel)

        self.savebutton = QPushButton("Save")
        setw(self.savebutton, 50)
        def onSave():
            print("Save")
            if self._image is not None:
                self._image.save(self.filenameinput.text() + ".png", "PNG")
                self.save_label.setText("Saved")

        self.savebutton.clicked.connect(onSave)
        self.fields.addWidget(self.savebutton)

        self.save_label = QLabel(self.verticalLayoutWidget)
        setw(self.save_label, 50)
        self.save_label.setText("Saved")
        self.fields.addWidget(self.save_label)

        self.fields.addStretch()

        # self.fields.addSpacerItem(QSpacerItem)

        # QWidget.setTabOrder(self.atten, self.coupling)
        # QWidget.setTabOrder(self.coupling, self.unit)
        # QWidget.setTabOrder(self.unit, self.bandwidth)

        QMetaObject.connectSlotsByName(self)