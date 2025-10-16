# CenterWidget is a Tab Widget, has Tabs suchs as Plot, Fit, ...

from PySide6.QtWidgets import QTabWidget
from .plot_widget import PlotWidget
from .analysis_widget import AnalysisWidget
from .settings_widget import SettingWidget
from .sample_table_widget import SampleTabWidget

class MyCenterWidget(QTabWidget):

    def __init__(self, db, parent =None):
        super().__init__(parent)
        self.db = db
        self.plot_tab = PlotWidget(self.db)
        self.analysis_tab = AnalysisWidget()
        self.setting_tab = SettingWidget()
        self.sample_tab = SampleTabWidget(self.db)
        self.addTab(self.sample_tab,"Sample Table")
        self.addTab(self.plot_tab,"General Plot")
        self.addTab(self.analysis_tab, "Fit")
        self.addTab(self.setting_tab, "Settings")
