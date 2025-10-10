# This QDialog Pops up when user wants to add a Sample

from PySide6.QtWidgets import QDialog, QFormLayout, QHBoxLayout, QRadioButton

class NewSampleDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.setWindowTitle('New Sample Dialog')

        form_layout = QFormLayout(self)

        # ["ID", "Name", "Mass", "Chemical","Orientation", "Created", "Note"]

        # Name Line


        # Select MT/MH and Orientation Row
        mode_layout = QHBoxLayout()
        mode_mh = QRadioButton('MH')
        mode_mt = QRadioButton('MT')
        mode_layout.addWidget(mode_mh)
        mode_layout.addWidget(mode_mt)
        form_layout.addRow('Mode', mode_layout)

        # Select the Orientation



