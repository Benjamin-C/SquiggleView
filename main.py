from scope.oscope import Oscilloscope

from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtGui import QPixmap

from gui.mainwindow import MainWindow

from secrete_config import addr

app = QApplication([])
pixmap = QPixmap("splash.png")
splash = QSplashScreen(pixmap)
splash.show()
app.processEvents()
app.processEvents()

with Oscilloscope(addr, debug=True) as scope:
    print("Go!")
    
    # file_name = input("Please enter a filename: ") + ".png"
    file_name = "test3.png"

    # scope.setupFFTHoriz(min=0, max=20e6)

    # print(scope.ch(1).getBWLimit())

    scope.menu(False)

    # print("Settling before screenshot ... ")
    # time.sleep(5)

    app.processEvents()
    window = MainWindow(scope)
    window.show()
    splash.finish(window)

    # ch = scope.ch(1)
    # ch.setCoupling("AC")
    # ch.setBWLimit(False)
    # ch.setAtten(1)
    # ch.setUnit("v")
    # ch.setOffset(-0.04)
    # ch.setScale(200e-3)
    # time.sleep(1)
    
    # scope.screenshot().save(file_name, "PNG")
    # print("Saved to " + file_name)

    app.exec()

