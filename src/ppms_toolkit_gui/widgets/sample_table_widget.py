'''GUI for the sample tab'''
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QTableView, QHBoxLayout,
    QPushButton, QAbstractItemView, QHeaderView
)
from ..models.sample_table_model import SampleTableModel

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
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        
        # Add button bar
        button_holder = QHBoxLayout()
        button_holder.setSpacing(10)
        self.button_add = QPushButton('Add Sample')
        self.button_del = QPushButton('Delete Sample')
        self.button_edit = QPushButton('Edit Sample')
        button_holder.addStretch()
        button_holder.addWidget(self.button_add)
        button_holder.addWidget(self.button_del)
        button_holder.addWidget(self.button_edit)
        button_holder.addStretch()

        layout.addWidget(self.search)
        layout.addWidget(self.table)
        layout.addLayout(button_holder)

