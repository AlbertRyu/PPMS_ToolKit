from ..adapters.mpl_canvas import MplCanvas
from PySide6.QtWidgets import \
    (QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    )
from .measurement_list_widget import TitledMeasurementListWidget


class MyCenterWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.canvas = MplCanvas()
        self.vsm_mt_measurement_list = TitledMeasurementListWidget('VSM - MT')
        self.vsm_mh_measurement_list = TitledMeasurementListWidget('VSM - MH')
        vsm_list_layout = QVBoxLayout()
        vsm_list_layout.addWidget(self.vsm_mt_measurement_list)
        vsm_list_layout.addWidget(self.vsm_mh_measurement_list)

        # Add a default measurement for debug purpose.
        from ppms_toolkit.measurement import VSMMeasurement
        m = VSMMeasurement(
            filepath='/Users/ryunosuke/Documents/Research/PPMS/PPMS_ToolKit/examples/test_data/VSM_TestData_4Cl_IP/MT_0P1T_FC.DAT',
            mode='MT',
            sample_orientation='In Plane',
            sample_mass=12
        )
        name =(f'{m.sample_name} - {m.sample_orientation} - {m.const_field}Oe')
        self.vsm_mt_measurement_list.add_vsm_measurement(name, m)
        # End of Test Measurement

        self.button_add = QPushButton('Add Measurement')
        self.button_plot = QPushButton('Plot')

        self.label = QLabel('Measurement List')

        button_holder = QHBoxLayout()
        button_holder.addWidget(self.button_add)
        button_holder.addWidget(self.button_plot)
        

        file_control_layout = QVBoxLayout()
        file_control_layout.addWidget(self.label)
        file_control_layout.addLayout(vsm_list_layout)
        file_control_layout.addLayout(button_holder)


        main_layout = QHBoxLayout(self)
        main_layout.addLayout(file_control_layout)
        main_layout.addWidget(self.canvas)