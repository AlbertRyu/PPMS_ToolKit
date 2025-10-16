# This define what the sample model should be like and how 
# it reads data from the sqlite database.

from tabnanny import check
from typing import Any
from PySide6.QtCore import QAbstractTableModel, QPersistentModelIndex, Qt, QModelIndex

from ppms_toolkit_gui.dialogs import sample_dialog

class SampleTableModel(QAbstractTableModel):
    def __init__(self, samples):
        super().__init__()
        self.samples = samples
        self.headers = ["Load", "Name", "Mass", "Chemical","Orientation", "Created", "Note"]
        self._checked_by_id: dict[int, bool] = {}
        # Initially all is unchecked.
        for s in self.samples:
            self._checked_by_id[s.id] = False


    # Self-defined API 
    def rowCount(self, parent = None):
        return len(self.samples)
    
    def columnCount(self, parent=None):
        return len(self.headers)

    def data(self, index, role: int = Qt.ItemDataRole.DisplayRole):
        sample = self.samples[index.row()]
        col = index.column()

        # First Columns is the checkable column shows which sample is loaded.
        if col == 0:
            if role == Qt.ItemDataRole.CheckStateRole:
                checked = self._checked_by_id.get(sample.id, False)
                return Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
            if role == Qt.ItemDataRole.DisplayRole:
                return None
            
        if role == Qt.ItemDataRole.DisplayRole:
            return [
                sample.name,
                sample.mass,
                sample.chemical,
                sample.orientation,
                sample.created_at,
                sample.notes,
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
            sample = self.samples[row]
            new_checked_state = (value == Qt.CheckState.Checked or value == 2) # True if it is checked
            # Defensive code, return True only if the new state differs from the old
            old = self._checked_by_id.get(sample.id, False)
            if new_checked_state != old:
                self._checked_by_id[sample.id] = new_checked_state
                self.dataChanged.emit(index,index, [Qt.ItemDataRole.CheckStateRole])
                return True
            return False
        return False

    def headerData(self, section, orientation, role: int = Qt.ItemDataRole.DisplayRole):
        # Set how the headers are shown.
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers [section]
        return super().headerData(section, orientation, role)
    
    def refresh_samples(self, new_samples):
        old_checked = dict(self._checked_by_id)
        self.beginResetModel()  # 通知视图“我要换数据了”
        self.samples = new_samples
        #Defensive Coding, just to make sure.
        #reinit checked_by_id, preserving by id, 
        self._checked_by_id = {}
        for s in self.samples:
            sid = getattr(s, "id", None)
            if sid is not None:
                self._checked_by_id[sid] = old_checked.get(sid, False)
        self.endResetModel()    # 通知视图“数据换完了，重画吧”

    def get_checked_sample_ids(self) -> list:
        """Return list of sample ids that are currently checked (in arbitrary order)."""
        return [sid for sid, v in self._checked_by_id.items() if v]
