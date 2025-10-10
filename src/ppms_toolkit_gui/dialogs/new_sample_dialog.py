# This QDialog Pops up when user wants to add a Sample

from PySide6.QtWidgets import QDialog, QFormLayout

class NewSampleDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.setWindowTitle('New Sample Dialog')

        form_layout = QFormLayout(self)

        # ["ID", "Name", "Mass", "Chemical","Orientation", "Created", "Note"]

        # Name Line

        
        # Select MT/MH and Orientation Row
        self.select_row = QWidget()
        select_layout =QHBoxLayout(self.select_row)



