# This Widget Connects the GUI and backend processing.
# Signal Control heißt das.
from curses import curs_set
from multiprocessing import Value

import comm
from ppms_toolkit.sample import Sample
from ..dialogs.new_measurement_dialog import NewMeasurementDialog
from PySide6.QtWidgets import QDialog, QMessageBox
from PySide6.QtCore import Qt

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..widgets.plot_widget import PlotWidget

from ppms_toolkit.measurement import VSMMeasurement

class PlotController:
    def __init__(self, view: 'PlotWidget') -> None:
        self.view = view
        self._connect_signal()
        

    def _connect_signal(self):
        self.view.button_add.clicked.connect(self.add_measurement)
        self.view.button_plot.clicked.connect(self._on_plot_clicked)


    def add_measurement(self):
        database = self.view.db
        samples = database.list_samples()
        dlg = NewMeasurementDialog(self.view, samples)


        if dlg.exec() == QDialog.DialogCode.Accepted:
            print('Accepted')
            new_m = dlg.get_measurement()

            try:
                sample_id = new_m.sample_id
                cur_sample_DTO = database.get_sample(sample_id)
                if cur_sample_DTO is None:
                    raise ValueError("Something is wrong, no sample with this id exist.")

                cur_sample_entity = Sample(
                    name = cur_sample_DTO.name,
                    id = cur_sample_DTO.id,
                    orientation= cur_sample_DTO.orientation,
                    mass = cur_sample_DTO.mass,
                    make_date=cur_sample_DTO.created_at,
                )

                m = VSMMeasurement(
                    filepath=new_m.original_filepath,
                    mode = new_m.mode if new_m.mode else "None", # MH or MT
                    sample=cur_sample_entity
                )
                self.view.db.add_measurement(new_m, m.raw_dataframe, m.dataframe)

            except Exception as e:
                QMessageBox.critical(self.view, "Error", str(e))
        else:
            print('Canceled')

    def _on_plot_clicked(self):

        # Get all the checked measurement id.
        self.view.




        self.view.canvas.ax.clear()


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