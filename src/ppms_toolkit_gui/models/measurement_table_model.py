# This define what the sample model should be like and how 
# it reads data from the sqlite database.

from typing import Any
from PySide6.QtCore import QAbstractTableModel, QPersistentModelIndex, Qt, QModelIndex

from infrastructure.db.db import MeasurementDTO, SampleDTO
from ppms_toolkit import measurement
from ppms_toolkit_gui.dialogs.new_measurement_dialog import NewMeasurementDialog

class MeasurementTableModel(QAbstractTableModel):
    def __init__(self, measurements: list[MeasurementDTO], samples: list[SampleDTO]):
        super().__init__()
        self.measurements = measurements
        self.sample_by_id = {s.id: s for s in samples if getattr(s, "id", None) is not None}
        self.headers = ["x", "Sample" ,"Chemical", "Orientation", "Condition", "Field(Oe)", "Temp(K)","Mid","Notes"]
        self._checked_by_id: dict[int, bool] = {} # Set which measurement is checked
        # Initially all is unchecked.
        for m in self.measurements:
            mid = m.id
            if mid:
                self._checked_by_id[mid] = False


    # Self-defined API 
    def rowCount(self, parent = None):
        return len(self.measurements)
    
    def columnCount(self, parent=None):
        return len(self.headers)

    def data(self, index, role: int = Qt.ItemDataRole.DisplayRole):
        measurement = self.measurements[index.row()]
        col = index.column()

        # First Columns is the checkable column shows which measurement is selected.
        if col == 0:
            if role == Qt.ItemDataRole.CheckStateRole:
                mid = getattr(measurement, "id", None)
                if mid is None:
                    # Measurement has no ID, treat as unchecked
                    raise ValueError("Some measurement has no id.")
                else:
                    checked = self._checked_by_id.get(mid, False)
                return Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
            if role == Qt.ItemDataRole.DisplayRole:
                return None
        if measurement.extra_parameters is not None:
            condition = measurement.extra_parameters.get('condition', None)
        else:
            condition = None
        sample = self.sample_by_id[measurement.sample_id]
        if role == Qt.ItemDataRole.DisplayRole:
            return [
                sample.name,
                sample.chemical,
                sample.orientation,
                condition,
                measurement.const_field,
                measurement.const_temperature,
                measurement.id,
                measurement.comment
            ][col - 1]
        else:
            return None
        
    def flags(self, index: QModelIndex): # Set the first columns checkable
        base_flags = super().flags(index)
        if index.column() == 0:
            return base_flags | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled
        else:
            return base_flags
    
    def setData(self, index: QModelIndex | QPersistentModelIndex, value: Any, /, role: int = Qt.ItemDataRole.EditRole) -> bool:
        if index.column() == 0 and role == Qt.ItemDataRole.CheckStateRole:
            row = index.row()
            measurement = self.measurements[row]
            new_checked_state = (value == Qt.CheckState.Checked or value == 2) # True if it is checked
            # Defensive code, return True only if the new state differs from the old
            if not measurement.id:
                raise ValueError("The Checked Measurement has no ID")
            old = self._checked_by_id.get(measurement.id, False)
            if new_checked_state != old:
                self._checked_by_id[measurement.id] = new_checked_state
                self.dataChanged.emit(index,index, [Qt.ItemDataRole.CheckStateRole])
                return True
            return False
        return False

    def headerData(self, section, orientation, role: int = Qt.ItemDataRole.DisplayRole):
        # Set how the headers are shown.
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers [section]
        return super().headerData(section, orientation, role)
    
    def refresh(self, new_meansurements, new_samples):
        old_checked = dict(self._checked_by_id)
        self.beginResetModel()  # 通知视图“我要换数据了”
        self.measurements = new_meansurements
        self.sample_by_id = {s.id: s for s in new_samples if getattr(s, "id", None) is not None}
        #Defensive Coding, just to make sure.
        #reinit checked_by_id, preserving by id, 
        self._checked_by_id = {}
        for s in self.measurements:
            sid = getattr(s, "id", None)
            if sid is not None:
                self._checked_by_id[sid] = old_checked.get(sid, False)
        self.endResetModel()    # 通知视图“数据换完了，重画吧”

    def get_checked_meansurement_ids(self) -> list:
        """Return list of measurement ids that are currently checked (in arbitrary order)."""
        return [mid for mid, v in self._checked_by_id.items() if v]
    
    def select_all_visible(self, visible_rows: list[int]):
        """
        选中所有可见行（未被过滤隐藏的行）
        
        Args:
            visible_rows: 可见行的行号列表（从 proxy model 传递）
        """
        changed_any = False
        for row in visible_rows:
            if 0 <= row < len(self.measurements):
                measurement = self.measurements[row]
                mid = measurement.id
                if mid and not self._checked_by_id.get(mid, False):
                    self._checked_by_id[mid] = True
                    changed_any = True
        
        if changed_any:
            # 通知视图刷新所有行的第一列
            top_left = self.index(0, 0)
            bottom_right = self.index(len(self.measurements) - 1, 0)
            self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.CheckStateRole])

    def deselect_all(self):
        """取消选中所有行"""
        changed_any = False
        for mid in self._checked_by_id:
            if self._checked_by_id[mid]:
                self._checked_by_id[mid] = False
                changed_any = True
        
        if changed_any:
            top_left = self.index(0, 0)
            bottom_right = self.index(len(self.measurements) - 1, 0)
            self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.CheckStateRole])
