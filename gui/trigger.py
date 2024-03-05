from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QCheckBox, QComboBox, QHBoxLayout, QLabel, QWidget

from gui.decadespinbox import DecadeSpinBox
from gui.quantizedspinbox import QuantizedSpinBox

from scope.channel import Channel

class ChannelGUI(QWidget):
    def __init__(self, scopech: Channel):
        super().__init__()

        def setw(obj, w):
            obj.setMaximumSize(QSize(w, 25))
            obj.setMinimumSize(QSize(w, 25))

        self.scopech = scopech

        if not self.objectName():
            self.setObjectName(u"channel")
        # self.resize(667, 174)
        self.setMinimumSize(QSize(800, 30))

        self.horizontalLayoutWidget = QWidget(self)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        # self.horizontalLayoutWidget.setGeometry(QRect(50, 80, 478, 29))

        self.fields = QHBoxLayout(self.horizontalLayoutWidget)
        self.fields.setObjectName(u"fields")
        self.fields.setContentsMargins(0, 0, 0, 0)

        self.id = QLabel(self.horizontalLayoutWidget)
        self.id.setText("Trigger")
        self.fields.addWidget(self.id)

        self.mode = QComboBox(self.horizontalLayoutWidget)
        self.mode.addItem("STOP")
        self.mode.addItem("AUTO")
        self.mode.addItem("NORM")
        self.mode.addItem("SINGLE")
        self.mode.setCurrentText(f"{self.scopech.getCache('TRIG_MODE'):g}")
        setw(self.mode, 55)
        self.mode.setToolTip("Probe attenuation - How many volts/amps at the probe results in 1 volt at the scope input")
        def onAttenChange(value):
            self.scopech.setAtten(float(self.mode.itemText(value)[:-1]))
        self.mode.currentIndexChanged.connect(onAttenChange)
        self.fields.addWidget(self.mode)

        # self.scale = DecadeSpinBox(self.horizontalLayoutWidget)
        # setw(self.scale, 110)
        # self.scale.setDecimals(7)
        # self.scale.setMaximum(1e6-1)
        # self.scale.setMinimum(1e-6)
        # self.scale.setValue(self.scopech.getCache("VOLT_DIV"))
        # self.scale.setKeyboardTracking(False)
        # self.scale.setToolTip("Trigger Position")
        # self.scale.setSuffix("V/div")
        # def onScaleChange(value):
        #     self.scopech.setScale(value)
        #     self.offset.setSingleStep(self.scale.value())
        # self.scale.valueChanged.connect(onScaleChange)
        # self.fields.addWidget(self.scale)