# This Widget Connects the GUI and backend processing.
# Signal Control heißt das.

from email.contentmanager import ContentManager
from ppms_toolkit.sample import Sample
from ..dialogs.new_measurement_dialog import NewMeasurementDialog
from PySide6.QtWidgets import QDialog, QMessageBox
from PySide6.QtCore import Qt

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..widgets.plot_widget import PlotWidget

from ppms_toolkit.measurement import VSMMeasurement
from infrastructure.db.db import LocalDB, MeasurementDTO, SampleDTO

class PlotController:
    def __init__(self, db: LocalDB, view: 'PlotWidget', ) -> None:
        self.view = view
        self._connect_signal()
        self.db = db

        self._measurement_cache = {}  # VSMMeasurement 实例缓存
        # 启动时加载所有 metadata（很快）
        self._all_measurements = {}
        self._all_samples = {}
        self.refresh_metadata()
        
    def refresh_metadata(self):
        """Reload metadata, whenever a new """
        measurements = self.db.list_measurements()
        samples = self.db.list_samples()
        self._all_measurements = {m.id: m for m in measurements}
        self._all_samples = {s.id: s for s in samples}
        self.view.model.refresh(measurements, samples)

    
    def _connect_signal(self):
        self.view.button_add.clicked.connect(self.add_measurement)
        self.view.button_plot.clicked.connect(self._on_plot_clicked)


    def add_measurement(self):
        database = self.db
        samples = database.list_samples()
        dlg = NewMeasurementDialog(self.view, samples)


        if dlg.exec() == QDialog.DialogCode.Accepted:
            print('Accepted')
            partial_m = dlg.get_measurement()

            try:
                sample_id = partial_m.sample_id
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
                    filepath=partial_m.original_filepath,
                    mode = partial_m.mode if partial_m.mode else "None", # MH or MT
                    sample=cur_sample_entity
                )

                new_m_DTO = MeasurementDTO(
                    sample_id=partial_m.sample_id,
                    measurement_type=partial_m.measurement_type,
                    mode=partial_m.mode,
                    original_filepath=partial_m.original_filepath,
                    const_field= float(m.const_field) if m.const_field is not None else None,
                    const_temperature= float(m.const_temp) if m.const_temp is not None else None,
                    extra_parameters= {"condition" : m.condition}
                )

                database.add_measurement(new_m_DTO, m.raw_dataframe, m.dataframe)
                self.refresh_metadata()

            except Exception as e:
                QMessageBox.critical(self.view, "Error", str(e))
        else:
            print('Canceled')

    def _on_plot_clicked(self):

        # Get all the checked measurement id.
        checked_ids = self.view.model.get_checked_meansurement_ids()
        if not checked_ids:
            return 
        
        self.view.canvas.ax.clear()

        for mid in checked_ids:
            dto = self._all_measurements[mid]
            if not dto:
                continue # No meansurement exist with this mid in _all_measurements
            if mid not in self._measurement_cache:
                # If not in cache, init it.
                sample_dto = self._all_samples[dto.sample_id]
                if not sample_dto:
                    continue # No sample info exist for this measurement's sample id

                # 从 parquet 加载（这是主要耗时）
                try:
                    import pandas as pd
                    assert (dto.data_filepath is not None) and (dto.processed_data_filepath is not None)
                    raw_df = pd.read_parquet(dto.data_filepath)
                    processed_df = pd.read_parquet(dto.processed_data_filepath)
                    
                    sample = Sample(
                        name=sample_dto.name,
                        mass=sample_dto.mass,
                        id = sample_dto.id,
                        orientation=sample_dto.orientation,
                    )

                    assert dto.mode is not None
                    metadata = {
                    'const_field': dto.const_field,
                    'const_temperature': dto.const_temperature,
                    'condition': dto.extra_parameters['condition'] if dto.extra_parameters else None
                    }
                    
                    vsm = VSMMeasurement(
                        sample=sample,
                        mode=dto.mode,
                        raw_dataframe=raw_df,
                        processed_dataframe=processed_df,
                        metadata = metadata
                    )
                    
                    self._measurement_cache[mid] = vsm
                except Exception as e:
                    print(f"Failed to load measurement {mid}: {e}")
                    continue

            vsm = self._measurement_cache[mid]
            if self.view.if_chi.checkState()== Qt.CheckState.Checked:
                vsm.plot(ax=self.view.canvas.ax)
                #for line in self.view.canvas.ax.lines:
                    #print(line)
            else:
                vsm.plot_magnetisation(ax=self.view.canvas.ax)

        self.view.canvas.canvas.draw()
        self.view.toolbar.update()        # 让 toolbar 重新检测新的 artists
        self.view.toolbar.push_current()  # 保存当前视图为新的“home”