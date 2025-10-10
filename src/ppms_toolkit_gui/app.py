from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox
from PySide6.QtCore import QLocale
from .gui.main_window import MainWindow
from infrastructure.db.db import LocalDB
import sys

app = QApplication(sys.argv)

QLocale.setDefault(QLocale.Language.C) # uses '.' as a decimal point


folder = QFileDialog.getExistingDirectory(
    None, "Select your working directory.", '',
    QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks |
    QFileDialog.Option.DontUseNativeDialog

)
if not folder:
    QMessageBox.critical(None, 
                         "Fatal Error", 
                         "You have to have a working directory.",
                         buttons= QMessageBox.StandardButton.Ok)
    sys.exit(0)

db = LocalDB(folder)




win = MainWindow(db)
win.show()

app.exec()