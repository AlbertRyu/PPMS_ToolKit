import turtle
from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QSortFilterProxyModel, Qt


class MultiValueFilterProxy(QSortFilterProxyModel):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.allowed_values = {} # {col : Set(values)}
    
    def set_allowed_values(self, column, values: set | None):
        if values is None or len(values)==0:
            self.allowed_values.pop(column, None)
        else:
            self.allowed_values[column] = set(values)
        self.invalidateFilter() # This will trigger filterAcceptRow

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex | QPersistentModelIndex) -> bool:
        m = self.sourceModel()
        for col, allowed in self.allowed_values.items():
            idx = m.index(source_row, col, source_parent) # Source model is unnecessary in my case
            data = m.data(idx, Qt.ItemDataRole.DisplayRole)
            if data not in allowed:
                return False
        return True    

    def flags(self, index):
        src = self.mapToSource(index)
        src_model = self.sourceModel()
        return src_model.flags(src)
    
    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        src_index = self.mapToSource(index)
        ok = self.sourceModel().setData(src_index, value, role)
        if ok:
            self.dataChanged.emit(index, index, [role])
        return ok


    



    