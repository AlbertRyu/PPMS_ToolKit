from PySide6.QtWidgets import QMainWindow
from .center_widget import MyCenterWidget
from ..controller.plot_controller import PlotController 


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.statusBar().showMessage("Ready")

        self.setContentsMargins(20,20,20,0)

        self.setWindowTitle('PPMS TOOLKIT')
        self.center_widget = MyCenterWidget()
        self.center_widget.setContentsMargins(0,30,0,0)
        self.setCentralWidget(self.center_widget)
        self.controller = PlotController(self.center_widget.plot_widget)
        self.menuBar()
        self.statusBar()



