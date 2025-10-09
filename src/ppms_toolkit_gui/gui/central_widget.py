from ..adapters.mpl_canvas import MplCanvas
from PySide6.QtWidgets import QWidget, QListWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel


class MyCenterWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.canvas = MplCanvas()
        self.file_list = QListWidget(self)
        self.file_list.addItems(['item 1','Item 2','Item 3'])

        self.button_add = QPushButton('Add Measurement')
        self.button_plot = QPushButton('Plot')

        self.label = QLabel('Measurement List')

        button_holder = QHBoxLayout()
        button_holder.addWidget(self.button_add)
        button_holder.addWidget(self.button_plot)
        

        file_control_layout = QVBoxLayout()
        file_control_layout.addWidget(self.label)
        file_control_layout.addWidget(self.file_list)
        file_control_layout.addLayout(button_holder)


        main_layout = QHBoxLayout(self)
        main_layout.addLayout(file_control_layout)
        main_layout.addWidget(self.canvas)