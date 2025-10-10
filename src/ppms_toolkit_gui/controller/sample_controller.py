# This Widget Connects the PlotWidget and backend processing.
# Signal Control heißt das.
#from PySide6.QtWidgets import QDialog, QMessageBox
#from PySide6.QtCore import Qt

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..gui.sample_widget import SampleTabWidget

#from ppms_toolkit.sample import Sample 

class SampleController:
    def __init__(self, view: 'SampleTabWidget') -> None:
        self.view = view
        self._connect_signal()
        

    def _connect_signal(self):
        pass

    def add_sample(self):
        pass

    def del_sample(self):
        pass