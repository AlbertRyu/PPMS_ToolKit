# The first dialog user will see. Ask if user has a exist project.

from PySide6.QtWidgets import (
    QDialog, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QSizePolicy, QFileDialog,
    QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from pathlib import Path

class ProjectDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.setWindowTitle('Welcome to PPMS Toolkit')
        self.setContentsMargins(20, 10, 20, 10)
        self.setFixedSize(500,180)

        self.label = QLabel('choose a work folder to start using       :)')
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)       # 水平垂直居中
        font = QFont()
        font.setPointSize(15)
        font.setBold(True)
        self.label.setFont(font)


        file_row = QHBoxLayout()
        self.file_edit = QLineEdit(placeholderText='Select your folder')
        self.file_edit.setReadOnly(True)
        self.file_edit.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.browse_btn = QPushButton('Browse')
        file_row.addWidget(self.file_edit)
        file_row.addWidget(self.browse_btn)
        self.browse_btn.clicked.connect(self._on_browse)

        self.button_confirm = QPushButton('Confirm')
        self.button_confirm.clicked.connect(self._on_confirm)
        self.button_confirm.setFixedWidth(120)
        self.button_confirm.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.addWidget(self.label)
        main_layout.addLayout(file_row)
        main_layout.addWidget(self.button_confirm, alignment=Qt.AlignmentFlag.AlignCenter)


    def _on_browse(self):
        start_dir = self.file_edit.text() or str(Path.home())
        folder = QFileDialog.getExistingDirectory(
            None, "Select your working directory.", start_dir,
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks |
            QFileDialog.Option.DontUseNativeDialog
        )
        if folder:
            self.file_edit.setText(folder)

    def _on_confirm(self):
        
        folder = self.file_edit.text().strip()
        if not folder:
            QMessageBox.critical(None, 
                                "Fatal Error", 
                                "You have to choose a directory to continue.",
                                buttons= QMessageBox.StandardButton.Ok)
            return
        self.accept()

    def get_folder(self):
        return self.file_edit.text()

        
        


