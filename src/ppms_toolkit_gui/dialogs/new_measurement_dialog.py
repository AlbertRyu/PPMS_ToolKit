# This Dialog Pop up each time when I need to add a new 
# measurement and ask infor from the USER.
from __future__ import annotations
from PySide6.QtWidgets import (QDialog, QDialogButtonBox, 
    QFormLayout, QDoubleSpinBox, QLineEdit, QPushButton,
    QWidget, QHBoxLayout, QAbstractSpinBox, QGroupBox,
    QRadioButton, QFileDialog, QVBoxLayout,QButtonGroup,
    QMessageBox, QComboBox, QListWidget
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
            self.sample_combo.addItem(f'{sample.name}-{sample.orientation}-{sample.mass}mg', userData=sample.id)

        # File list section (supports batch import)
        self.file_list = QListWidget()
        self.file_list.setMaximumHeight(150)
        
        self.browse_btn = QPushButton('Browse Files')
        self.browse_btn.clicked.connect(self._on_browse)
        
        self.clear_btn = QPushButton('Clear')
        self.clear_btn.clicked.connect(self.file_list.clear)

        file_row = QWidget()
        file_layout = QVBoxLayout(file_row)
        
        
        btn_row = QHBoxLayout()
        btn_row.addWidget(self.browse_btn)
        btn_row.addWidget(self.clear_btn)
        
        #file_layout.addLayout(btn_row)
        #file_layout.addWidget(self.file_list)

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
        form.addRow("Add Files", btn_row)
        form.addRow(self.file_list)
        form.addRow(self.mode)
        form.addRow(buttons)

    def _on_browse(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select your data file",              # 对话框标题
            "",                                   # 起始目录
            "Data Files (*.csv *.txt *.dat);;All Files (*)"  # 过滤器
        )
        if paths:
            self.file_list.clear()
            self.file_list.addItems(paths)

    def _on_accept(self):
        # Check if every value exist.
        if self.file_list.count() == 0:
            QMessageBox.critical(self, 'Warning', 'No data file selected')
            return
    
        if not self.mode_btn_group.checkedButton():
            QMessageBox.critical(self,'Warning','No Mode choosed')
            return
        
        if self.sample_combo.currentIndex() == -1 or not self._samples:
            QMessageBox.critical(self, 'Warning', 'No sample selected')
            return

        self.accept()

    def get_measurements(self) -> list[MeasurementDTO]:
        
        measurements = []
        sample_id = self.sample_combo.currentData(role=Qt.ItemDataRole.UserRole)
        mode=self.mode_btn_group.checkedButton().text()

        for i in range(self.file_list.count()):
            filepath = self.file_list.item(i).text()
            m_DTO = MeasurementDTO(
                sample_id=sample_id,
                measurement_type="VSM",
                mode=mode,
                original_filepath=filepath
            )
            measurements.append(m_DTO)
        
        return measurements






        