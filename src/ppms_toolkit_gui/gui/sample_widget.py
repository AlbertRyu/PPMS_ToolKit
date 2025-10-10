'''GUI for the sample tab'''
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QTableView, QHBoxLayout,
    QPushButton
)
from .sample_table_model import SampleTableModel

from infrastructure.db.db import LocalDB

class SampleTabWidget(QWidget):
    def __init__(self, db: 'LocalDB'):
        super().__init__()
        self.db = db

        layout = QVBoxLayout(self)

        #Read the samples from db
        samples = db.list_samples()

        # Add a search box
        self.search = QLineEdit(placeholderText='Search Sample Name or Comment')
        
        # Add a table
        self.table = QTableView()
        self.model = SampleTableModel(samples=samples)
        self.table.setModel(self.model)

        # Add button bar
        button_holder = QHBoxLayout()
        button_add = QPushButton()

        layout.addWidget(self.search)
        layout.addWidget(self.table)
