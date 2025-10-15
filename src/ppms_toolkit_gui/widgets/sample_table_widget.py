'''GUI for the sample tab'''
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QTableView, QHBoxLayout,
    QPushButton, QAbstractItemView, QHeaderView
)
from ..models.sample_table_model import SampleTableModel
from ..controller.header_filter_controller import HeaderFilterController
from ..proxy.multi_value_filter import MultiValueFilterProxy

from infrastructure.db.db import LocalDB

class SampleTabWidget(QWidget):
    def __init__(self, db: 'LocalDB'):
        super().__init__()
        self.db = db
        layout = QVBoxLayout(self)


        samples = db.list_samples() #Read the samples from db

        # Add a search box
        self.search = QLineEdit(placeholderText='Search Sample Name or Comment')
        
        # Add a table
        self.table = QTableView()

        self.model = SampleTableModel(samples=samples)
        proxy = MultiValueFilterProxy()
        proxy.setSourceModel(self.model)
        self.filter_controller = HeaderFilterController(self.table, proxy)
        self.table.setModel(proxy)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.resizeColumnsToContents()
        header = self.table.horizontalHeader()
        for col in range(header.count()):
            w = header.sectionSize(col)
            header.resizeSection(col, w + 15)
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

