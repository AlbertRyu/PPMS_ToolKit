from PySide6.QtWidgets import QMainWindow
from .widgets.center_widget import MyCenterWidget
from .controller.plot_controller import PlotController 
from .controller.sample_controller import SampleController
from PySide6.QtGui import QCloseEvent, QGuiApplication


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
        self.plot_controller = PlotController(self.center_widget.plot_tab)
        self.sample_controller = SampleController(self.db, self.center_widget.sample_tab)

        screen = QGuiApplication.primaryScreen().geometry()
        self.resize(int(screen.width() * 0.9), int(screen.height() * 0.7)) 
                                                   
        # 居中到屏幕
        frame_geo = self.frameGeometry()
        center_point = QGuiApplication.primaryScreen().availableGeometry().center()
        frame_geo.moveCenter(center_point)
        self.move(frame_geo.topLeft())

        self.menuBar()
        self.statusBar()

    def closeEvent(self, event: QCloseEvent):
        # 应用窗口关闭时关闭数据库
        if self.db:
            self.db.close()
        super().closeEvent(event)


