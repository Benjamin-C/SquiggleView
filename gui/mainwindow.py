from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from scope.oscope import Oscilloscope
from gui.screenshot import ScreenshotGUI

from gui.triggergui import TriggerGUI
from gui.channelgui import ChannelGUI

class MainWindow(QMainWindow):
    def __init__(self, scope: Oscilloscope):
        super().__init__()

        self.scope = scope

        # Create the central widget
        central_widget = QWidget()
        # Create a layout
        layout = QVBoxLayout()

        trigger = TriggerGUI(scope.trigger)
        layout.addWidget(trigger)

        for i in range(self.scope.channelCount()):
            ch = self.scope.ch(i+1)
            cr = ChannelGUI(ch)
            scope.valueChangeListeners.append(cr.onChannelUpdate)
            layout.addWidget(cr)

        sc = ScreenshotGUI(scope)
        layout.addWidget(sc)

        # Set layout to the central widget
        central_widget.setLayout(layout)
        # Set central widget to the main window
        self.setCentralWidget(central_widget)
        # Set window title
        self.setWindowTitle("Scope Controller")