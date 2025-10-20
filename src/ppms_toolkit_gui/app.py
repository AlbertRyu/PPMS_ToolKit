from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtCore import QLocale, QCoreApplication
from PySide6.QtGui import QGuiApplication

from .main_window import MainWindow
from .dialogs.project_dialog import ProjectDialog
from infrastructure.db.db import LocalDB
from PySide6.QtGui import QIcon
from pathlib import Path
import sys

def main():
    app = QApplication(sys.argv)

    # 设置全局应用图标（Windows 任务栏）
    icon_path = Path(__file__).parent.parent / "resources" / "app_icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    QCoreApplication.setOrganizationName("PPMS_Toolkit")
    QCoreApplication.setApplicationName("GUI_Configuration")

    QLocale.setDefault(QLocale.Language.C) # uses '.' as a decimal point

    dlg = ProjectDialog(None)
    # This part is to make sure the window 
    # appear from the center of user's screen.
    screen = QGuiApplication.primaryScreen()
    geo = screen.availableGeometry()
    dlg_rect = dlg.rect()
    target_top_left = geo.center() - dlg_rect.center()
    dlg.move(target_top_left) 

    if dlg.exec() != QDialog.DialogCode.Accepted:
        sys.exit(0)
    
    folder = dlg.get_folder()
    db = LocalDB(folder)

    win = MainWindow(db)
    win.show()

    return app.exec()

if __name__ == '__main__':
    sys.exit(main())