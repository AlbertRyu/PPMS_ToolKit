# This define what the sample model should be like and how 
# it reads data from the sqlite database.

from PySide6.QtCore import QAbstractTableModel, Qt

class SampleTableModel(QAbstractTableModel):
    def __init__(self, samples):
        super().__init__()
        self.samples = samples
        self.headers = ["ID", "Name", "Mass", "Chemical","Orientation", "Created", "Note"]

    # Self-defined API 
    def rowCount(self, parent = None):
        return len(self.samples)
    
    def columnCount(self, parent=None):
        return len(self.headers)

    def data(self, index, role: int = Qt.ItemDataRole.DisplayRole):
        sample = self.samples[index.row()]
        col = index.column()
        if role == Qt.ItemDataRole.DisplayRole:
            return [
                sample.id,
                sample.name,
                sample.mass,
                sample.chemical,
                sample.orientation,
                sample.notes,
                sample.created_at
            ][col]
        else:
            return None

    def headerData(self, section, orientation, role: int = Qt.ItemDataRole.DisplayRole):
        # Set how the headers are shown.
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers [section]
        return super().headerData(section, orientation, role)
    
    def refresh_samples(self, new_samples):
        self.beginResetModel()  # 通知视图“我要换数据了”
        self.samples = new_samples
        self.endResetModel()    # 通知视图“数据换完了，重画吧”


