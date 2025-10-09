# This Widget Connects the GUI and backend processing.
# Signal Control heißt das.
#from ..gui.central_widget import MyCenterWidget
from ..dialogs.new_measurement_dialog import NewMeasurementDialog
from PySide6.QtWidgets import QDialog

class DataController:
    def __init__(self, view) -> None:
        self.view = view

        self._connect_signal()
        

    def _connect_signal(self):
        #self.view = MyCenterWidget()
        self.view.button_add.clicked.connect(self.add_measurement)


    def test_function(self):
        print('Test Signal!')


    def add_measurement(self):
        dlg = NewMeasurementDialog(self.view)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            print('Accepted')
            pay_load = dlg._return_payload()
            print(pay_load)
        else:
            print('Canceled')
