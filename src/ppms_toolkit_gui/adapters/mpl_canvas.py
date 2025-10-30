from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

import matplotlib as mpl
mpl.rcParams['figure.dpi'] = 100      # GUI里看的
mpl.rcParams['savefig.dpi'] = 300     # 点“保存”按钮时的


class MplCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self.canvas)
        