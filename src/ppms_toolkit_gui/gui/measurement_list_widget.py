# Measurement List is used for HC, VSM-MT and VSM-MH,
# A selfdefined widget could be handy.
from __future__ import annotations

from PySide6.QtWidgets import \
    (QListWidget, QListWidgetItem,
     QAbstractItemView)
from PySide6.QtCore import Qt

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ppms_toolkit.measurement import VSMMeasurement


class MeasurementListWidget(QListWidget):
    def __init__(self):
        super().__init__()

        # Make the list multi selectable
        self.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection)
        
    def add_vsm_measurement(self, m: VSMMeasurement):
        item = QListWidgetItem(m.__repr__())
        item.setData(Qt.ItemDataRole.UserRole, m)
        self.addItem(item)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable 
        | Qt.ItemFlag.ItemIsSelectable 
        | Qt.ItemFlag.ItemIsEnabled)
        item.setCheckState(Qt.CheckState.Unchecked)
