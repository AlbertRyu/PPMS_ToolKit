'''GUI for the sample tab'''
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QTableView

class SampleTableWidget(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db

        layout = QVBoxLayout(self)

        # Add a search box
        self.search = QLineEdit(placeholderText='Search Sample Name or Comment')
        
        # Add a table
        self.table = QTableView()

        layout.addWidget(self.search)
        layout.addWidget(self.table)
