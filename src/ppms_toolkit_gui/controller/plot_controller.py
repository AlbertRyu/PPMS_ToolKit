# This Widget Connects the GUI and backend processing.
# Signal Control heißt das.
from ..dialogs.new_measurement_dialog import NewMeasurementDialog
from PySide6.QtWidgets import QDialog, QMessageBox
from PySide6.QtCore import Qt

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..gui.plot_widget import PlotWidget

from ppms_toolkit.measurement import VSMMeasurement

class PlotController:
    def __init__(self, view: 'PlotWidget') -> None:
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
                if pay_load['mode'] == 'MT':
                    name =(f'{m.sample_name} - {m.sample_orientation} - {m.const_field}Oe')
                    self.view.vsm_mt_measurement_list.add_vsm_measurement(name, m)
                else:
                    name =(f'{m.sample_name} - {m.sample_orientation} - {m.const_temp} K')
                    self.view.vsm_mh_measurement_list.add_vsm_measurement(name, m)
            except Exception as e:
                QMessageBox.critical(self.view, "Error", str(e))
        else:
            print('Canceled')

    def plot_measurement(self):

        self.view.canvas.ax.clear()
        QList = self.view.vsm_mt_measurement_list
        for i in range(QList.count()):
            item = QList.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                m : VSMMeasurement = item.data(Qt.ItemDataRole.UserRole)
                if self.view.if_chi.checkState()== Qt.CheckState.Checked:
                    m.plot(ax=self.view.canvas.ax)
                    #for line in self.view.canvas.ax.lines:
                        #print(line)
                else:
                    m.plot_magnetisation(ax=self.view.canvas.ax)
        self.view.canvas.canvas.draw()
        self.view.toolbar.update()        # 让 toolbar 重新检测新的 artists
        self.view.toolbar.push_current()  # 保存当前视图为新的“home”