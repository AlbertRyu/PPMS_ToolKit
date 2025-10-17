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
        self.headers = ["Checked", "Sample", "Mass(mg)", "Orientation", "Field(Oe)", "Temp(K)","Notes"]
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
                checked = self._checked_by_id.get(measurement.id, False)
                return Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
            if role == Qt.ItemDataRole.DisplayRole:
                return None
            
        sample = self.sample_by_id[measurement.sample_id]
        if role == Qt.ItemDataRole.DisplayRole:
            return [
                sample.name,
                sample.mass,
                sample.orientation,
                measurement.const_field,
                measurement.const_temperature,
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
