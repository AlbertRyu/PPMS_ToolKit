# This Dialog Pop up each time when I need to add a new 
# measurement and ask infor from the USER.

from PySide6.QtWidgets import (QDialog, QDialogButtonBox, 
    QFormLayout, QDoubleSpinBox, QLineEdit, QPushButton,
    QWidget, QHBoxLayout, QAbstractSpinBox, QGroupBox,
    QRadioButton, QFileDialog, QVBoxLayout,QButtonGroup,
    QMessageBox
)

class NewMeasurementDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('New Measurement')
        form = QFormLayout(self)

        # Fundamental infomation
        self.mass_spin = QDoubleSpinBox(suffix=" mg")
        self.mass_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)


        # File Row 
        self.file_edit = QLineEdit(placeholderText='Select your file')
        self.browse_btn = QPushButton('Browse')
        self.browse_btn.clicked.connect(self._on_browse)

        file_row = QWidget()
        file_layout = QHBoxLayout(file_row)
        file_layout.addWidget(self.file_edit)
        file_layout.addWidget(self.browse_btn)

        # Select MT/MH and Orientation Row
        self.select_row = QWidget()
        select_layout =QHBoxLayout(self.select_row)

        self.mode = QGroupBox('Type of Exp')
        mode_MT = QRadioButton('MT')
        mode_MH = QRadioButton('MH')
        mode_layout = QVBoxLayout(self.mode)
        mode_layout.addWidget(mode_MH)
        mode_layout.addWidget(mode_MT)
        self.mode_btn_group = QButtonGroup()
        self.mode_btn_group.addButton(mode_MH)
        self.mode_btn_group.addButton(mode_MT)

        self.orientation = QGroupBox('Orientation of Sample')
        orientation_ip = QRadioButton('In Plane')
        orientation_oop = QRadioButton('Out of Plane')
        orientation_layout = QVBoxLayout(self.orientation)
        orientation_layout.addWidget(orientation_ip)
        orientation_layout.addWidget(orientation_oop)
        self.ori_btn_group = QButtonGroup()
        self.ori_btn_group.addButton(orientation_ip)
        self.ori_btn_group.addButton(orientation_oop)

        select_layout.addWidget(self.mode)
        select_layout.addWidget(self.orientation)

        # button row
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        # Add everything into form 
        form.addRow(file_row)
        form.addRow("Sample Mass", self.mass_spin)
        form.addRow(self.select_row)
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

        if not self.ori_btn_group.checkedButton():
            QMessageBox.critical(self,'Warning','No orientaton chosed')
            return
    
        if not self.mode_btn_group.checkedButton():
            QMessageBox.critical(self,'Warning','No Mode choosed')
            return

        self.accept()

    def _return_payload(self):
        return {
        "mode": self.mode_btn_group.checkedButton().text(),
        "sample_orientation": self.ori_btn_group.checkedButton().text(),
        "sample_mass": self.mass_spin.value(),
        "filepath": self.file_edit.text().strip(),
        }
        






        