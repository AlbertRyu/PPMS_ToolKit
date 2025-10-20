from ..adapters.mpl_canvas import MplCanvas
from PySide6.QtWidgets import \
    (QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
     QCheckBox, QFrame, QTableView, QAbstractItemView,
     QLabel
    )

from PySide6.QtCore import Qt
from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
from ..models.measurement_table_model import MeasurementTableModel
from ..controller.header_filter_controller import HeaderFilterController
from ..proxy.multi_value_filter import MultiValueFilterProxy

class PlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.canvas = MplCanvas()

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

        self.button_add = QPushButton('Add Measurement')
        self.button_add.setStatusTip("Click to add a measurement from DAT file")

        self.button_plot = QPushButton('Plot')
        self.button_plot.setStatusTip("Click to Plot selected measurements")

        self.button_del = QPushButton('Delete Measurement')
        self.button_del.setStatusTip('Click to delete selected measurements')

        self.if_chi = QCheckBox('Succeptiblity')
        self.if_chi.setCheckState(Qt.CheckState.Checked)
        self.if_chi.setStatusTip('Checked to plot suceptbity, otherwise moment')

        button_holder = QHBoxLayout()
        button_holder.addWidget(self.button_add)
        button_holder.addWidget(self.button_del)
        button_holder.addWidget(self.button_plot)
        button_holder.addWidget(self.if_chi)

        # The Measurement Table
        self.table = QTableView()
        self.model = MeasurementTableModel([], []) # Measurement is added when Controller is initialized.
        proxy = MultiValueFilterProxy()
        self.filter_controller = HeaderFilterController(self.table, proxy)
        proxy.setSourceModel(self.model)
        self.table.setModel(proxy)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)

        # Title Row
        title_label = QLabel("VSM Measurements ")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 设置样式：加大字体、加粗
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
            }
        """)

        file_control_layout = QVBoxLayout()
        file_control_layout.addWidget(title_label)
        file_control_layout.addWidget(self.table)
        file_control_layout.addLayout(button_holder)
        file_control_layout.setContentsMargins(10,10,10,10)

        self.toolbar = NavigationToolbar(self.canvas.canvas, self)

        plot_layout = QVBoxLayout()
        plot_layout.addWidget(self.canvas.canvas)
        plot_layout.addWidget(self.toolbar)
        plot_layout.setContentsMargins(10,0,10,10)


        vline = QFrame()
        vline.setFrameShape(QFrame.Shape.VLine)
        vline.setFrameShadow(QFrame.Shadow.Sunken)
        vline.setLineWidth(1)


        main_layout = QHBoxLayout(self)
        main_layout.addLayout(file_control_layout)
        main_layout.addWidget(vline)
        main_layout.addLayout(plot_layout)