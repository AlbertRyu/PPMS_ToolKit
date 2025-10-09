from PySide6.QtWidgets import QMainWindow
from .central_widget import MyCenterWidget
from ..controller.data_controller import DataController


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()


        self.setWindowTitle('PPMS TOOLKIT')
        self.center_widget = MyCenterWidget()
        self.setCentralWidget(self.center_widget)
        self.controller = DataController(self.center_widget)
        self.menuBar()
        self.statusBar()



