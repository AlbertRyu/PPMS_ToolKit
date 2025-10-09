# CenterWidget is a Tab Widget, has Tabs suchs as Plot, Fit, ...

from PySide6.QtWidgets import QTabWidget
from .plot_widget import PlotWidget
from .analysis_widget import AnalysisWidget
from .settings_widget import SettingWidget

class MyCenterWidget(QTabWidget):

    def __init__(self, parent =None):
        super().__init__(parent)
        
        self.plot_widget = PlotWidget(self)
        self.analysis_widget = AnalysisWidget()
        self.setting_widget = SettingWidget()
        self.addTab(self.plot_widget,"General Plot")
        self.addTab(self.analysis_widget, "Fit")
        self.addTab(self.setting_widget, "Settings")
