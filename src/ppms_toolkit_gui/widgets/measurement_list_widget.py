# Measurement List is used for HC, VSM-MT and VSM-MH,
# A selfdefined widget could be handy.
from __future__ import annotations

from PySide6.QtWidgets import \
    (QListWidget, QListWidgetItem,
     QAbstractItemView, QWidget, QLabel,
     QHBoxLayout,QVBoxLayout)
from PySide6.QtCore import Qt

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ppms_toolkit.measurement import VSMMeasurement


class MeasurementListWidget(QListWidget):
    def __init__(self, parent= None):
        super().__init__(parent)

        # Make the list multi selectable
        self.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection)
        
    def add_vsm_measurement(self, name, m: VSMMeasurement):
        item = QListWidgetItem(name)
        item.setData(Qt.ItemDataRole.UserRole, m)
        self.addItem(item)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable 
        | Qt.ItemFlag.ItemIsSelectable 
        | Qt.ItemFlag.ItemIsEnabled)
        item.setCheckState(Qt.CheckState.Unchecked)

class TitledMeasurementListWidget(QWidget):
    def __init__(self, title, parent = None):
        super().__init__(parent)

        self._title = QLabel(title)

        self.list: 'MeasurementListWidget' =  MeasurementListWidget(parent=self)

        # 布局：标题行（可加按钮）+ 列表
        title_row = QHBoxLayout()
        title_row.addStretch()
        title_row.addWidget(self._title)
        title_row.addStretch()

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addLayout(title_row)
        root.addWidget(self.list)

    def add_vsm_measurement(self, name, m):
        return self.list.add_vsm_measurement(name, m)
    
    def __getattr__(self, name):
        return getattr(self.list, name)


