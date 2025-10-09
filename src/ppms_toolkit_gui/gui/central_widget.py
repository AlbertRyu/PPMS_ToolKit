from ..adapters.mpl_canvas import MplCanvas
from PySide6.QtWidgets import \
    (QWidget, QListWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
     QAbstractItemView)

from PySide6.QtCore import Qt

class MyCenterWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.canvas = MplCanvas()
        self.measurement_list = QListWidget(self)
        self.measurement_list.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection)

        # Add a default measurement for debug purpose.
        from ppms_toolkit.measurement import VSMMeasurement
        from PySide6.QtWidgets import QListWidgetItem
        from PySide6.QtCore import Qt
        m = VSMMeasurement(
            filepath='/Users/ryunosuke/Documents/Research/PPMS/PPMS_ToolKit/examples/test_data/VSM_TestData_4Cl_IP/MT_0P1T_FC.DAT',
            mode='MT',
            sample_orientation='In Plane',
            sample_mass=12
        )
        item = QListWidgetItem(m.__repr__())
        item.setData(Qt.ItemDataRole.UserRole, m)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable 
                      | Qt.ItemFlag.ItemIsSelectable 
                      | Qt.ItemFlag.ItemIsEnabled)
        item.setCheckState(Qt.CheckState.Unchecked)
        self.measurement_list.addItem(item)
        # End of Test Measurement

        self.button_add = QPushButton('Add Measurement')
        self.button_plot = QPushButton('Plot')

        self.label = QLabel('Measurement List')

        button_holder = QHBoxLayout()
        button_holder.addWidget(self.button_add)
        button_holder.addWidget(self.button_plot)
        

        file_control_layout = QVBoxLayout()
        file_control_layout.addWidget(self.label)
        file_control_layout.addWidget(self.measurement_list)
        file_control_layout.addLayout(button_holder)


        main_layout = QHBoxLayout(self)
        main_layout.addLayout(file_control_layout)
        main_layout.addWidget(self.canvas)