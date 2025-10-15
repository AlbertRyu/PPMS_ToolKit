# This Widget Connects the PlotWidget and backend processing.
# Signal Control heißt das.
#from PySide6.QtWidgets import QDialog, QMessageBox
#from PySide6.QtCore import Qt

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..gui.sample_widget import SampleTabWidget
    from infrastructure.db.db import LocalDB

from ..dialogs.sample_dialog import SampleDialog
from PySide6.QtWidgets import QDialog

#from ppms_toolkit.sample import Sample 

class SampleController:
    def __init__(self, db: 'LocalDB', view: 'SampleTabWidget') -> None:
        self.view = view
        self.db = db
        self._connect_signal()
        

    def _connect_signal(self):
        self.view.button_add.clicked.connect(self.add_sample)
        self.view.button_del.clicked.connect(self.del_sample)
        self.view.button_edit.clicked.connect(self.edit_sample)

    def get_selected_sample(self):
        selection = self.view.table.selectionModel()
        if not selection or not selection.currentIndex().isValid():
            return None
        
        row = selection.currentIndex().row()
        samples = getattr(self.view.model, "samples", [])
        if 0  <= row < len(samples):
            return samples[row]
        
    def add_sample(self):
        dlg = SampleDialog(self.db)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            print('Accepted')
            new_sample = dlg.get_sample()
            self.db.add_sample(new_sample)
            print('Sample Added')

            new_samples = self.db.list_samples()
            self.view.model.refresh_samples(new_samples)
        else:
            print('Canceled')

    def edit_sample(self):
        sample = self.get_selected_sample()
        dlg = SampleDialog(self.db, sample)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            editted_sample = dlg.get_sample()
            self.db.update_sampe(editted_sample)

            new_samples = self.db.list_samples()
            self.view.model.refresh_samples(new_samples)

        else:
            print('Canceled')


    def del_sample(self):
        print('del sample clicked.')
        pass