# CenterWidget is a Tab Widget, has Tabs suchs as Plot, Fit, ...

from PySide6.QtWidgets import QTabWidget
from .plot_widget import PlotWidget
from .analysis_widget import AnalysisWidget
from .settings_widget import SettingWidget
from .sample_widget import SampleTableWidget

class MyCenterWidget(QTabWidget):

    def __init__(self, db, parent =None):
        super().__init__(parent)
        self.db = db
        self.plot_widget = PlotWidget(self)
        self.analysis_widget = AnalysisWidget()
        self.setting_widget = SettingWidget()
        self.sample_table = SampleTableWidget(db)
        self.addTab(self.sample_table, "Sample Table")
        self.addTab(self.plot_widget,"General Plot")
        self.addTab(self.analysis_widget, "Fit")
        self.addTab(self.setting_widget, "Settings")
