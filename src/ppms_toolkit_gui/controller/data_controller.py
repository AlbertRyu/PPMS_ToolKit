# This Widget Connects the GUI and backend processing.
# Signal Control heißt das.
#from ..gui.central_widget import MyCenterWidget
from ..dialogs.new_measurement_dialog import NewMeasurementDialog
from PySide6.QtWidgets import QDialog, QMessageBox
from PySide6.QtCore import Qt

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..gui.central_widget import MyCenterWidget

from ppms_toolkit.measurement import VSMMeasurement

class DataController:
    def __init__(self, view: 'MyCenterWidget') -> None:
        self.view = view

        self._connect_signal()
        

    def _connect_signal(self):
        self.view.button_add.clicked.connect(self.add_measurement)
        self.view.button_plot.clicked.connect(self.plot_measurement)


    def test_function(self):
        print('Test Signal!')


    def add_measurement(self):
        dlg = NewMeasurementDialog(self.view)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            print('Accepted')
            pay_load = dlg._return_payload()
            try:
                m = VSMMeasurement(**pay_load)
                self.view.vsm_mt_measurement_list.add_vsm_measurement(m)

            except Exception as e:
                QMessageBox.critical(self.view, "Error", str(e))
        else:
            print('Canceled')

    def plot_measurement(self):
        m : VSMMeasurement = self.view.vsm_mt_measurement_list.currentItem().data(Qt.ItemDataRole.UserRole)
        m.plot_magnetisation(ax=self.view.canvas.ax)
        self.view.canvas.canvas.draw()