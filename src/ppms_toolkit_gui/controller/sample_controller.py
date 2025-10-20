# This Widget Connects the PlotWidget and backend processing.
# Signal Control heißt das.
#from PySide6.QtWidgets import QDialog, QMessageBox
#from PySide6.QtCore import Qt

from typing import TYPE_CHECKING

from infrastructure.db.db import SampleDTO
if TYPE_CHECKING:
    from ..widgets.sample_table_widget import SampleTabWidget
    from infrastructure.db.db import LocalDB

from ..dialogs.sample_dialog import SampleDialog
from PySide6.QtWidgets import QDialog, QMessageBox

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

    def get_selected_sample(self) -> SampleDTO | None:
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
            self.refresh_table()
        else:
            print('Canceled')

    def edit_sample(self):
        sample = self.get_selected_sample()
        dlg = SampleDialog(self.db, sample)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            editted_sample = dlg.get_sample()
            self.db.update_sampel(editted_sample)
            self.refresh_table()
        else:
            print('Canceled')


    def del_sample(self):
        sample = self.get_selected_sample()

        if sample is None:
            QMessageBox.information(self.view, "Delete", "please first choose a line")
            return 

        msg  = f"Confirm you want delete {sample.name}（mass={sample.mass}mg)？This is irreversible"
        if QMessageBox.question(self.view, "Cofirm", msg,
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                            QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        
        self.db.delete_sample(sample)
        self.refresh_table()

    def refresh_table(self):
        new_samples = self.db.list_samples()
        self.view.model.refresh_samples(new_samples)
        self.view.table.resizeColumnsToContents()

