# This Widget Connects the PlotWidget and backend processing.
# Signal Control heißt das.
#from PySide6.QtWidgets import QDialog, QMessageBox
#from PySide6.QtCore import Qt

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..gui.sample_widget import SampleTabWidget
    from infrastructure.db.db import LocalDB

from ..dialogs.new_sample_dialog import NewSampleDialog, QDialog

#from ppms_toolkit.sample import Sample 

class SampleController:
    def __init__(self, db: 'LocalDB', view: 'SampleTabWidget') -> None:
        self.view = view
        self.db = db
        self._connect_signal()
        

    def _connect_signal(self):
        self.view.button_add.clicked.connect(self.add_sample)
        self.view.button_del.clicked.connect(self.del_sample)

    def add_sample(self):
        dlg = NewSampleDialog(self.db)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            print('Accepted')
            pay_load = dlg._return_payload()
            self.db.add_sample(
                name=pay_load['name'],
                mass=pay_load['sample_mass'],
                chemical=pay_load['chemical'],
                orientation=pay_load['sample_orientation'],
                create_at=pay_load['create_date']
            )
            print('Sample Added')
            new_samples = self.db.list_samples()
            self.view.model.refresh_samples(new_samples)
        else:
            print('Canceled')

    def del_sample(self):
        print('del sample clicked.')
        pass