from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox, QDialog
from PySide6.QtCore import QLocale
from .gui.main_window import MainWindow
from .dialogs.project_dialog import ProjectDialog
from infrastructure.db.db import LocalDB

import sys

app = QApplication(sys.argv)

QLocale.setDefault(QLocale.Language.C) # uses '.' as a decimal point

dlg = ProjectDialog()
if dlg.exec() != QDialog.DialogCode.Accepted:
    sys.exit(0)
 
folder = dlg.get_folder()
db = LocalDB(folder)

win = MainWindow(db)
win.show()

app.exec()