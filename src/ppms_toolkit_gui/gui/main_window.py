from PySide6.QtWidgets import QMainWindow
from .center_widget import MyCenterWidget
from ..controller.plot_controller import PlotController 
from PySide6.QtGui import QCloseEvent


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from infrastructure.db.db import LocalDB


class MainWindow(QMainWindow):
    def __init__(self, db: "LocalDB"):
        super().__init__()

        self.db = db

        self.statusBar().showMessage("Ready")
        self.setContentsMargins(20,20,20,0)


        self.setWindowTitle('PPMS TOOLKIT')
        self.center_widget = MyCenterWidget(self.db)
        self.center_widget.setContentsMargins(0,30,0,0)
        self.setCentralWidget(self.center_widget)
        self.controller = PlotController(self.center_widget.plot_widget)
        self.menuBar()
        self.statusBar()

    def closeEvent(self, event: QCloseEvent):
        # 应用窗口关闭时关闭数据库
        if self.db:
            self.db.close()
        super().closeEvent(event)


