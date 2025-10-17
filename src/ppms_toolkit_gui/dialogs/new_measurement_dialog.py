# This Dialog Pop up each time when I need to add a new 
# measurement and ask infor from the USER.
from __future__ import annotations
from PySide6.QtWidgets import (QDialog, QDialogButtonBox, 
    QFormLayout, QDoubleSpinBox, QLineEdit, QPushButton,
    QWidget, QHBoxLayout, QAbstractSpinBox, QGroupBox,
    QRadioButton, QFileDialog, QVBoxLayout,QButtonGroup,
    QMessageBox, QComboBox
)
from PySide6.QtCore import Qt
from infrastructure.db.db import MeasurementDTO

from typing import TYPE_CHECKING

from ppms_toolkit_gui.dialogs.sample_dialog import SampleDialog
if TYPE_CHECKING:
    from infrastructure.db.db import SampleDTO

class NewMeasurementDialog(QDialog):
    def __init__(self, parent=None, samples: list[SampleDTO] = []):
        super().__init__(parent)
        self._samples = samples
        self.setWindowTitle('New VSM Measurement')
        form = QFormLayout(self)

        # Which Sample
        self.sample_combo = QComboBox()
        for sample in self._samples:
            self.sample_combo.addItem(f'{sample.name}-{sample.mass}mg', userData=sample.id)

        # File Row 
        self.file_edit = QLineEdit(placeholderText='Select your file')
        self.browse_btn = QPushButton('Browse')
        self.browse_btn.clicked.connect(self._on_browse)

        # Fundamental infomation - Noe 
        # self.mass_spin = QDoubleSpinBox(suffix=" mg", value=1)
        # self.mass_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        file_row = QWidget()
        file_layout = QHBoxLayout(file_row)
        file_layout.addWidget(self.file_edit)
        file_layout.addWidget(self.browse_btn)

        # Select MT/MH
        self.mode = QGroupBox('Mode of Exp')
        mode_MT = QRadioButton('MT')
        mode_MH = QRadioButton('MH')
        mode_layout = QHBoxLayout(self.mode)
        mode_layout.addWidget(mode_MH)
        mode_layout.addWidget(mode_MT)
        # Button Group seems like redundant, but is used later for checked checking.
        self.mode_btn_group = QButtonGroup() 
        self.mode_btn_group.addButton(mode_MH)
        self.mode_btn_group.addButton(mode_MT)

        # button row
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        # Add everything into form 
        form.addRow("Sample", self.sample_combo)
        form.addRow(file_row)
        form.addRow(self.mode)
        form.addRow(buttons)

    def _on_browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select your data file",              # 对话框标题
            "",                                   # 起始目录
            "Data Files (*.csv *.txt *.dat);;All Files (*)"  # 过滤器
        )
        if path:  # 用户没点“取消”
            self.file_edit.setText(path)

    def _on_accept(self):
        # Check if every value exist.
        if not self.file_edit.text():
            QMessageBox.critical(self,'Warning','No dat file path')
            return
    
        if not self.mode_btn_group.checkedButton():
            QMessageBox.critical(self,'Warning','No Mode choosed')
            return
        
        if self.sample_combo.currentIndex() == -1 or not self._samples:
            QMessageBox.critical(self, 'Warning', 'No sample selected')
            return

        self.accept()

    def get_measurement(self) -> MeasurementDTO:
        return MeasurementDTO(sample_id=self.sample_combo.currentData(role=Qt.ItemDataRole.UserRole),
                              measurement_type = 'VSM',
                              mode=self.mode_btn_group.checkedButton().text(), 
                              original_filepath=self.file_edit.text().strip())






        