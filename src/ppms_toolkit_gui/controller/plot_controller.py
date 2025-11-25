# This Widget Connects the GUI and backend processing.
# Signal Control heißt das.
from ppms_toolkit.sample import Sample
from ..dialogs.new_measurement_dialog import NewMeasurementDialog
from PySide6.QtWidgets import QDialog, QMessageBox, QRadioButton
from PySide6.QtCore import Qt, QSortFilterProxyModel


from typing import TYPE_CHECKING, cast
if TYPE_CHECKING:
    from ..widgets.plot_widget import PlotWidget

from ppms_toolkit.measurement import VSMMeasurement
from infrastructure.db.db import LocalDB, MeasurementDTO 
from ..models.measurement_table_model import MeasurementTableModel

class PlotController:
    def __init__(self, db: LocalDB, view: 'PlotWidget', ) -> None:
        self.view = view
        self._connect_signal()
        self.db = db

        self._measurement_cache = {}  # VSMMeasurement 实例缓存
        # 启动时加载所有 metadata（很快）
        self._all_measurements = {}
        self._all_samples = {}
        self.samples = []
        self.measurements = []
        self.refresh_metadata()
        
    def refresh_metadata(self):
        """Reload metadata, whenever a new """
        self.measurements = self.db.list_measurements()
        self.samples = self.db.list_samples()
        self._all_measurements = {m.id: m for m in self.measurements}
        self._all_samples = {s.id: s for s in self.samples}
        self.view.model.refresh(self.measurements, self.samples)
        self.view.table.resizeColumnsToContents()
    
    def _connect_signal(self):
        self.view.button_add.clicked.connect(self.add_measurement)
        self.view.button_plot.clicked.connect(self._on_plot_clicked)
        self.view.button_del.clicked.connect(self.del_measurements)
        self.view.button_select_all.clicked.connect(self._on_select_all)       # 新增
        self.view.button_deselect_all.clicked.connect(self._on_deselect_all)   # 新增


    def add_measurement(self):
        samples = self.db.list_samples() 
        # This database query is not ideal. But I don't know how I 
        dlg = NewMeasurementDialog(self.view, samples)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            print('Accepted')
            partial_ms = dlg.get_measurements()
            for partial_m in partial_ms:
                try:
                    sample_id = partial_m.sample_id

                    cur_sample_DTO = self._all_samples.get(sample_id, None)
                    if cur_sample_DTO is None:
                        cur_sample_DTO = self.db.get_sample(sample_id)
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

                    self.db.add_measurement(new_m_DTO, m.raw_dataframe, m.dataframe)

                except Exception as e:
                    QMessageBox.critical(self.view, "Error", str(e))
            self.refresh_metadata()

        else:
            print('Canceled')

    def del_measurements(self):
        print('Clicked Del')
        checked_ids = self.view.model.get_checked_meansurement_ids()
        print(checked_ids)
        if not checked_ids:
            print("this?")
            return
        
        for mid in checked_ids:
            self.db.del_measurement(mid)
        self.refresh_metadata()


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

            legend_mode: str | None = None
            # Get selected radio button.
            for rb in self.view.legend_mode.findChildren(QRadioButton):
                if rb.isChecked():
                    legend = rb.text()
            
                            
            vsm.plot(mid, 
                     ax=self.view.canvas.ax,
                     susceptibility =(self.view.if_chi.checkState()== Qt.CheckState.Checked),
                     legend=legend_mode)


        legend = self.view.canvas.ax.legend()
        if legend:
            legend.set_draggable(True)  # 可拖动
            # 启用交互式图例（点击隐藏/显示线条）
            self._setup_interactive_legend(legend)

                
        self.view.canvas.figure.tight_layout()
        self.view.canvas.canvas.draw()
        self.view.toolbar.update()        # 让 toolbar 重新检测新的 artists
        self.view.toolbar.push_current()  # 保存当前视图为新的“home”

    def _setup_interactive_legend(self, legend):
        """设置可点击的图例来显示/隐藏线条"""
        # 存储原始可见性
        lined = {}  # 将图例线条映射到绘图线条
        
        for legline, origline in zip(legend.get_lines(), self.view.canvas.ax.get_lines()):
            legline.set_picker(5)  # 5 pts tolerance
            lined[legline] = origline
        
        def on_pick(event):
            # 在图例上点击时触发
            legline = event.artist

            # ✅ 检查点击的是否是图例中的线条对象
            if legline not in lined:
                return  # 如果不是线条（比如是整个图例框），忽略
            origline = lined[legline]
            visible = not origline.get_visible()
            origline.set_visible(visible)
            # 改变图例线条的透明度
            legline.set_alpha(1.0 if visible else 0.2)
            self.view.canvas.canvas.draw()
        
        # 连接 pick 事件
        self.view.canvas.canvas.mpl_connect('pick_event', on_pick)

            # 只连接一次（避免重复）
        if not hasattr(self, '_legend_pick_connected'):
            self.view.canvas.canvas.mpl_connect('pick_event', on_pick)
            self._legend_pick_connected = True

    def _on_select_all(self):
        """选中所有可见（未被过滤）的行"""
        proxy = cast(QSortFilterProxyModel, self.view.table.model()) # MultiValueFilterProxy
        source_model = cast(MeasurementTableModel, proxy.sourceModel()) # MeasurementTableModel
        
        # 获取所有可见行在源模型中的行号
        visible_source_rows = []
        for proxy_row in range(proxy.rowCount()):
            proxy_index = proxy.index(proxy_row, 0)
            source_index = proxy.mapToSource(proxy_index)
            if source_index.isValid():
                visible_source_rows.append(source_index.row())
        
        # 调用模型的 select_all_visible 方法
        source_model.select_all_visible(visible_source_rows)

    def _on_deselect_all(self):
        """取消选中所有行"""
        source_model = self.view.model  # MeasurementTableModel
        source_model.deselect_all()