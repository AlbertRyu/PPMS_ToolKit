# This Widget Connects the PlotWidget and backend processing.
# Signal Control heißt das.
#from PySide6.QtWidgets import QDialog, QMessageBox
#from PySide6.QtCore import Qt

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..gui.sample_widget import SampleTabWidget

from ..dialogs.new_sample_dialog import NewSampleDialog

#from ppms_toolkit.sample import Sample 

class SampleController:
    def __init__(self, view: 'SampleTabWidget') -> None:
        self.view = view
        self._connect_signal()
        

    def _connect_signal(self):
        self.view.button_add.clicked.connect(self.add_sample)
        self.view.button_del.clicked.connect(self.del_sample)

    def add_sample(self):
        dlg = NewSampleDialog()
        dlg.exec()
        print('add sample clicked')

    def del_sample(self):
        print('del sample clicked.')
        pass