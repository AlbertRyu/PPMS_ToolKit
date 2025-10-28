# This QDialog Pops up when user wants to add or edit Sample
from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QHBoxLayout, QRadioButton, QButtonGroup,
    QLineEdit, QDoubleSpinBox, QAbstractSpinBox, QComboBox,
    QDateEdit, QPlainTextEdit, QDialogButtonBox,QMessageBox
)
from PySide6.QtCore import QDate
from typing import TYPE_CHECKING
from infrastructure.db.db import SampleDTO
if TYPE_CHECKING:
    from infrastructure.db.db import LocalDB

class SampleDialog(QDialog):
    def __init__(self, db: LocalDB, sample: SampleDTO | None = None, parent = None):
        super().__init__(parent)
        self.db = db
        self._build_ui()
        self.sample = sample
        if self.sample:
            self._prefill(self.sample)
            self.setWindowTitle('Edit Sample')
        else:
            self.setWindowTitle('Sample Dialog')

    def _build_ui(self):
        
        form_layout = QFormLayout(self)

        # Name Row
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Sample Name")
        
        # Mass Row
        self.mass_spin = QDoubleSpinBox()
        self.mass_spin.setSuffix('mg')
        self.mass_spin.setValue(1)
        self.mass_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        # Chemical Row
        self.chemical_edit = QComboBox()
        self.chemical_edit.setEditable(True)
        self.chemical_edit.addItem('')
        self.chemical_edit.addItems(self.db.fetch_all_distinct_chemical())

        # Select the Orientation
        ori_layout = QHBoxLayout()
        self.ori_OOP = QRadioButton('Out of Plane')
        self.ori_IP = QRadioButton('In Plane')
        ori_layout.addWidget(self.ori_IP)
        ori_layout.addWidget(self.ori_OOP)
        self.ori_btn_group = QButtonGroup()
        self.ori_btn_group.addButton(self.ori_OOP)
        self.ori_btn_group.addButton(self.ori_IP)

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

    def _prefill(self, sample: SampleDTO):
        self.name_edit.setText(sample.name)
        self.mass_spin.setValue(sample.mass)
        self.chemical_edit.setCurrentText(sample.chemical)

        ori = sample.orientation
        if ori == "In Plane":
            self.ori_IP.setChecked(True)
        elif ori == "Out of Plane":
            self.ori_OOP.setChecked(True)

        self.date_edit.setDate(QDate.fromString(sample.created_at, "yyyy-MM-dd"))
        self.notes_edit.setPlainText(sample.notes or '')

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
    
    def get_sample(self) -> SampleDTO:
        return SampleDTO(
            id = self.sample.id if self.sample else None, # Return the sample_id in edit mode
            name = self.name_edit.text(),
            mass=self.mass_spin.value(),
            chemical=self.chemical_edit.currentText(),
            orientation=self.ori_btn_group.checkedButton().text(),
            created_at=self.date_edit.text(),
            notes=self.notes_edit.toPlainText()
        )

