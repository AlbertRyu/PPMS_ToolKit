# CenterWidget is a Tab Widget, has Tabs suchs as Plot, Fit, ...

from PySide6.QtWidgets import QTabWidget
from .plot_widget import PlotWidget

class MyCenterWidget(QTabWidget):

    def __init__(self, parent =None):
        super().__init__(parent)
        
        self.plot_widget = PlotWidget(self)
        self.addTab(self.plot_widget,"General Plot")
        
