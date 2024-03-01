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
        self.id.setObjectName("id")
        self.id.setText("CH" + str(self.scopech.id))
        self.fields.addWidget(self.id)

        self.scale = DecadeSpinBox(self.horizontalLayoutWidget)
        self.scale.setObjectName(u"scale")
        setw(self.scale, 110)
        self.scale.setDecimals(7)
        self.scale.setMaximum(1e6-1)
        self.scale.setMinimum(1e-6)
        self.scale.setValue(self.scopech.getCache("VOLT_DIV"))
        self.scale.setKeyboardTracking(False)
        self.scale.setToolTip("Vertical scale")
        self.scale.setSuffix("V/div")
        def onScaleChange(value):
            self.scopech.setScale(value)
            self.offset.setSingleStep(self.scale.value())
        self.scale.valueChanged.connect(onScaleChange)
        self.fields.addWidget(self.scale)

        self.offset = QuantizedSpinBox(self.horizontalLayoutWidget)
        self.offset.setObjectName(u"offset")
        setw(self.offset, 100)
        self.scale.setDecimals(7)
        self.offset.setMinimum(-1e6+1)
        self.offset.setMaximum(1e6-1)
        self.offset.setValue(self.scopech.getCache("OFFSET"))
        self.offset.setToolTip("Vertical Offset")
        self.offset.setSuffix("V")
        def onOffsetChange(value):
            self.scopech.setOffset(value)
        self.offset.valueChanged.connect(onOffsetChange)
        self.fields.addWidget(self.offset)

        self.atten = QComboBox(self.horizontalLayoutWidget)
        self.atten.setObjectName(u"atten")
        self.atten.addItem("1X")
        self.atten.addItem("10X")
        self.atten.setCurrentText(f"{self.scopech.getCache('ATTENUATION'):g}X")
        setw(self.atten, 55)
        self.atten.setToolTip("Probe attenuation - How many volts/amps at the probe results in 1 volt at the scope input")
        def onAttenChange(value):
            self.scopech.setAtten(float(self.atten.itemText(value)[:-1]))
        self.atten.currentIndexChanged.connect(onAttenChange)
        self.fields.addWidget(self.atten)

        self.coupling = QComboBox(self.horizontalLayoutWidget)
        self.coupling.setObjectName(u"coupling")
        self.coupling.addItem("DC")
        self.coupling.addItem("AC")
        self.coupling.addItem("GND")
        setw(self.coupling, 65)
        self.coupling.setEditable(False)
        self.coupling.setToolTip("Coupling")
        self.coupling.setCurrentText(self.scopech.cacheCouplingHR())
        def onCouplingChange(value):
            self.scopech.setCoupling(self.coupling.itemText(value))
        self.coupling.currentIndexChanged.connect(onCouplingChange)
        self.fields.addWidget(self.coupling)

        self.unit = QComboBox(self.horizontalLayoutWidget)
        self.unit.setObjectName(u"unit")
        self.unit.addItem("A")
        self.unit.addItem("V")
        setw(self.unit, 40)
        self.unit.setCurrentText(self.scopech.getCache("UNIT"))
        self.unit.setToolTip("Probe unit")
        def onUnitChange(value):
            self.scopech.setUnit(self.unit.itemText(value))
        self.unit.currentIndexChanged.connect(onUnitChange)
        self.fields.addWidget(self.unit)

        self.bandwidth = QCheckBox(self.horizontalLayoutWidget)
        self.bandwidth.setObjectName(u"bandwidth")
        self.bandwidth.setText("BW")
        self.bandwidth.setToolTip("Software bandwidth limit")
        self.bandwidth.setChecked(self.scopech.getCache("BANDWIDTH_LIMIT"))
        def onBWChange(value):
            self.scopech.setBWLimit(value == 2)
        self.bandwidth.stateChanged.connect(onBWChange)
        self.fields.addWidget(self.bandwidth)

    def onChannelUpdate(self, field, value, source):
        # print("Time to update " + field + " to " + str(value))
        if field == "VOLT_DIV":
            self.scale.setValue(float(value))
        elif field == "OFFSET":
            self.offset.setValue(float(value))
        elif field == "UNIT":
            self.unit.setCurrentText(str(value))
        elif field == "ATTENUATION":
            self.atten.setCurrentText(str(value))
        elif field == "BANDWIDTH_LIMIT":
            self.bandwidth.setChecked(bool(value))
        elif field == "COUPLING":
            self.coupling.setCurrentText(str(value))