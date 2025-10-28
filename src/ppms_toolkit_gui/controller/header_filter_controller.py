from __future__ import annotations

from PySide6.QtWidgets import (
    QTableView, QHeaderView, QMenu, QWidget, QHBoxLayout, QVBoxLayout,
    QLineEdit, QListWidget, QPushButton, QWidgetAction, QListWidgetItem
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QFontMetrics

from ..proxy.multi_value_filter import MultiValueFilterProxy



class HeaderFilterController:
    def __init__(self, table: QTableView, proxy: MultiValueFilterProxy):
        self.table = table
        self.proxy =proxy
        header : QHeaderView = self.table.horizontalHeader()
        header.setSectionsClickable(True)
        header.sectionClicked.connect(self._on_section_clicked)

    def _unique_values_for_column(self, col):
        src = self.proxy.sourceModel()
        vals = []
        seen = set()
        for row in range(src.rowCount()):
            data = src.index(row, col).data()
            if data not in seen:
                seen.add(data)
                vals.append(data)
        
        # Show sorted list
        try:
            vals.sort(key=lambda x: str(x).lower())
        except Exception:
            vals.sort(key=lambda x: str(x))
        return vals

    def _on_section_clicked(self, logical_index):
        header : QHeaderView = self.table.horizontalHeader()

        menu = QMenu(self.table)
        panel = QWidget(menu)
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(8,8,8,8)

        container = QWidget(panel)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0,0,0,0)
        container_layout.setSpacing(6)
        
        search = QLineEdit(container)
        search.setPlaceholderText('search...')
        container_layout.addWidget(search)

        lst = QListWidget(container)
        lst.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        container_layout.addWidget(lst)

        btn_holder = QWidget(container)
        btn_col = QVBoxLayout(btn_holder)
        btn_col.setContentsMargins(0, 0, 0, 0)
        btn_col.setSpacing(6)
        btn_all = QPushButton("All", btn_holder)
        btn_none = QPushButton("Clear",btn_holder)
        btn_apply = QPushButton("Apply", btn_holder)
        btn_cancel = QPushButton("Cancel", btn_holder)

        btn_row1 = QHBoxLayout()
        btn_row1.addWidget(btn_all)
        btn_row1.addWidget(btn_none)

        btn_row2 = QHBoxLayout()
        btn_row2.addWidget(btn_apply)
        btn_row2.addWidget(btn_cancel)

        btn_col.addLayout(btn_row1)
        btn_col.addLayout(btn_row2)

        container_layout.addWidget(btn_holder)

        layout.addWidget(container)
        panel.setLayout(layout)

        # 将自定义面板放进 QMenu
        wa = QWidgetAction(menu)
        wa.setDefaultWidget(panel)
        menu.addAction(wa)

        values = self._unique_values_for_column(logical_index)
        current_allowed = self.proxy.allowed_values.get(logical_index, None)
        for val in values:
            it = QListWidgetItem(str(val))
            it.setFlags(it.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            checked = (current_allowed is not None) and (val in current_allowed)
            it.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
            it.setData(Qt.ItemDataRole.UserRole, val)
            lst.addItem(it)
        
        def apply_search():
            q = search.text().strip().lower()
            for i in range(lst.count()):
                item = lst.item(i)
                item.setHidden(q not in item.text().lower())
        search.textChanged.connect(apply_search)

        def select_all():
            for i in range(lst.count()):
                if not lst.item(i).isHidden():
                    lst.item(i).setCheckState(Qt.CheckState.Checked)
        def select_none():
            for i in range(lst.count()):
                if not lst.item(i).isHidden():
                    lst.item(i).setCheckState(Qt.CheckState.Unchecked)

        btn_all.clicked.connect(select_all)
        btn_none.clicked.connect(select_none)

        def do_apply():
            selected = set()
            for i in range(lst.count()):
                it = lst.item(i)
                if it.checkState() == Qt.CheckState.Checked:
                    selected.add(it.data(Qt.ItemDataRole.UserRole))

                    # 如果没有勾选任何项，设为 None（显示全部）
            # 如果勾选了部分项，设为选中的集合（只显示这些）
            if len(selected) == 0:
                self.proxy.set_allowed_values(logical_index, None)
            else:
                self.proxy.set_allowed_values(logical_index, selected)
            menu.close()
            
        def do_cancel():
            menu.close()

        btn_apply.clicked.connect(do_apply)
        btn_cancel.clicked.connect(do_cancel)

        x = header.sectionPosition(logical_index)
        pt = header.mapToGlobal(QPoint(x, header.height()))
        font_metrics = QFontMetrics(self.table.font())
        min_width = font_metrics.horizontalAdvance("M") * 25  # 约 30 个字符宽度
        menu.setFixedWidth(max(min_width, header.sectionSize(logical_index)))
        menu.popup(pt)











