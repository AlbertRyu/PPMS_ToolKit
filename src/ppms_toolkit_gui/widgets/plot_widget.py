from infrastructure.db.db import LocalDB
from ..adapters.mpl_canvas import MplCanvas
from PySide6.QtWidgets import \
    (QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
     QCheckBox, QFrame
    )
from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
from .measurement_list_widget import TitledMeasurementListWidget


class PlotWidget(QWidget):
    def __init__(self, db : LocalDB, parent=None):
        super().__init__(parent)

        self.canvas = MplCanvas()
        self.db = db

        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self.btn_zoom = QPushButton("Zoom")
        self.btn_pan = QPushButton("Pan")
        self.btn_reset = QPushButton("Reset")
        self.btn_addline = QPushButton("Add Line")
        self.btn_removeline = QPushButton("Remove Line")

        for btn in [self.btn_zoom, self.btn_pan, self.btn_reset,
                    self.btn_addline, self.btn_removeline]:
            toolbar.addWidget(btn)

        self.vsm_mt_measurement_list = TitledMeasurementListWidget('VSM - MT')
        self.vsm_mh_measurement_list = TitledMeasurementListWidget('VSM - MH')
        vsm_list_layout = QVBoxLayout()
        vsm_list_layout.addWidget(self.vsm_mt_measurement_list)
        vsm_list_layout.addWidget(self.vsm_mh_measurement_list)

        self.button_add = QPushButton('Add Measurement')
        self.button_add.setStatusTip("Click to add a measurement from DAT file")

        self.button_plot = QPushButton('Plot')
        self.button_plot.setStatusTip("Click to Plot selected measurements")
    
        self.if_chi = QCheckBox('Succeptiblity')
        self.if_chi.setStatusTip('Checked to plot suceptbity, otherwise moment')

        button_holder = QHBoxLayout()
        button_holder.addWidget(self.button_add)
        button_holder.addWidget(self.button_plot)
        button_holder.addWidget(self.if_chi)

        file_control_layout = QVBoxLayout()
        file_control_layout.addLayout(vsm_list_layout)
        file_control_layout.addLayout(button_holder)
        file_control_layout.setContentsMargins(10,10,10,10)

        self.toolbar = NavigationToolbar(self.canvas.canvas, self)

        plot_layout = QVBoxLayout()
        plot_layout.addWidget(self.canvas.canvas)
        plot_layout.addWidget(self.toolbar)
        plot_layout.setContentsMargins(10,10,10,10)


        vline = QFrame()
        vline.setFrameShape(QFrame.Shape.VLine)
        vline.setFrameShadow(QFrame.Shadow.Sunken)
        vline.setLineWidth(1)


        main_layout = QHBoxLayout(self)
        main_layout.addLayout(file_control_layout)
        main_layout.addWidget(vline)
        main_layout.addLayout(plot_layout)