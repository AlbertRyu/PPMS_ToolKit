# This QDialog Pops up when user wants to add a Sample

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QHBoxLayout, QRadioButton, QButtonGroup,
    QLineEdit, QDoubleSpinBox, QAbstractSpinBox, QComboBox,
    QDateEdit, QPlainTextEdit, QDialogButtonBox,QMessageBox
)
from PySide6.QtCore import QDate
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from infrastructure.db.db import LocalDB

class NewSampleDialog(QDialog):
    def __init__(self, db: 'LocalDB', parent = None):
        super().__init__(parent)

        self.setWindowTitle('New Sample Dialog')

        form_layout = QFormLayout(self)

        # ["ID", "Name", "Mass", "Chemical","Orientation", "Created", "Note"]

        # Name Row
        self.name_edit = QLineEdit(placeholderText="Sample Name")
        
        # Mass Row
        self.mass_spin = QDoubleSpinBox(suffix=" mg", value=1)
        self.mass_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        # Chemical Row
        self.chemical_edit = QComboBox(editable=True)
        self.chemical_edit.addItem('')
        self.chemical_edit.addItems(db.fetch_all_distinct_chemical())

        # Select the Orientation
        ori_layout = QHBoxLayout()
        ori_OOP = QRadioButton('Out of Plane')
        ori_IP = QRadioButton('In Plane')
        ori_layout.addWidget(ori_IP)
        ori_layout.addWidget(ori_OOP)
        self.ori_btn_group = QButtonGroup()
        self.ori_btn_group.addButton(ori_OOP)
        self.ori_btn_group.addButton(ori_IP)

        # Created time row.
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True) 
        self.date_edit.setDisplayFormat("yyyy-MM-dd")  
        self.date_edit.setDate(QDate.currentDate())     

        # Note Edit Row

        self.notes_edit = QPlainTextEdit()
        self.notes_edit.setPlaceholderText("(Optional) Enter notes here...")

        # button row
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        form_layout.addRow('Sample Name', self.name_edit)
        form_layout.addRow('Mass', self.mass_spin)
        form_layout.addRow('Chemical', self.chemical_edit)
        form_layout.addRow('Orientation', ori_layout)
        form_layout.addRow('Create Date',self.date_edit)
        form_layout.addRow('Note', self.notes_edit)
        form_layout.addRow(buttons)

    def _on_accept(self):
        # Check if every value exist.
        if not self.name_edit.text():
            QMessageBox.critical(self,'Warning','No Name')
            return

        if not self.ori_btn_group.checkedButton():
            QMessageBox.critical(self,'Warning','No orientaton chosed')
            return
    
        if not self.chemical_edit.currentText():
            QMessageBox.critical(self,'Warning','No Chemical')
            return

        if not self.date_edit.text():
            QMessageBox.critical(self,'Warning','No Date')
            return

        self.accept()
    
    def _return_payload(self):
        return {
        "name": self.name_edit.text(),
        "sample_mass": self.mass_spin.value(),
        "chemical": self.chemical_edit.currentText(),
        "sample_orientation": self.ori_btn_group.checkedButton().text(),
        "create_date": self.date_edit.text(),
        "note":self.notes_edit.toPlainText()
        }
