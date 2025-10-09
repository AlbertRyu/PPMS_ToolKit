from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QLocale, Qt
from .gui.main_window import MainWindow
import sys

app = QApplication(sys.argv)

QLocale.setDefault(QLocale.Language.C) # uses '.' as a decimal point

win = MainWindow()
win.show()

app.exec()