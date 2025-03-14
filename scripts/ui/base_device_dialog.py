"""
    PyZKTecoClocks: GUI for managing ZKTeco clocks, enabling clock 
    time synchronization and attendance data retrieval.
    Copyright (C) 2024  Paulo Sebastian Spaciuk (Darukio)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from scripts import config
from scripts.common.utils.errors import BaseError
from scripts.ui.operation_thread import OperationThread
from PyQt5.QtWidgets import QProgressBar, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QHeaderView, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
import logging

from scripts.ui.base_dialog import BaseDialog

# Definition of the common base class
class BaseDeviceDialog(BaseDialog):
    op_terminated = pyqtSignal(float)

    def __init__(self, parent=None, op_function=None, window_title=""):
        try:
            super().__init__(parent, window_title)
            
            self.op_thread = OperationThread(op_function)
            self.op_thread.op_updated.connect(self.update_table)
            self.op_thread.op_terminated.connect(self.terminate_op)
        except Exception as e:
            raise BaseError(3501, str(e))
    
    def terminate_op(self, start_time):
        logging.debug(f'start time: {start_time:.2f}')
        self.op_terminated.emit(start_time)
    
    def init_ui(self, header_labels):
        try:
            layout = QVBoxLayout(self)

            self.table_widget = QTableWidget()
            self.table_widget.setVisible(False)
            self.table_widget.setColumnCount(5)
            self.table_widget.setHorizontalHeaderLabels(header_labels)
            self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
            self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            self.table_widget.horizontalHeader().setStretchLastSection(True)
            self.table_widget.setSortingEnabled(True)

            layout.addWidget(self.table_widget)

            self.btn_update = QPushButton("Actualizar", self)
            self.btn_update.clicked.connect(self.update_data)
            layout.addWidget(self.btn_update, alignment=Qt.AlignCenter)

            self.label_updating = QLabel("Actualizando datos...", self)
            self.label_updating.setAlignment(Qt.AlignCenter)
            self.label_updating.setVisible(False)
            layout.addWidget(self.label_updating)

            self.label_no_active_device = QLabel("No hay dispositivo activo", self)
            self.label_no_active_device.setAlignment(Qt.AlignCenter)
            self.label_no_active_device.setVisible(False)
            layout.addWidget(self.label_no_active_device)

            # Progress bar
            self.progress_bar = QProgressBar(self)
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(100)
            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(False)  # Hide the progress bar initially
            layout.addWidget(self.progress_bar)
        except Exception as e:
            raise BaseError(3501, str(e))

    def update_data(self):
        try:
            self.label_no_active_device.setVisible(False)
            self.btn_update.setVisible(False)
            self.label_updating.setVisible(True)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.table_widget.setSortingEnabled(False)
            self.table_widget.setRowCount(0)
            self.op_thread.start()
        except Exception as e:
            raise BaseError(3500, str(e))

    def update_table(self, device_status=None):
        try:
            self.table_widget.setVisible(True)
            self.label_updating.setVisible(False)
            self.progress_bar.setVisible(False)  # Hide the progress bar when the update is complete
            logging.debug(device_status)

            if not device_status:
                self.label_no_active_device.setVisible(True)
                return

            # Insert data into the table
            for row, (ip, device_info) in enumerate(device_status.items()):
                self.table_widget.insertRow(row)
                self.table_widget.setItem(row, 0, QTableWidgetItem(ip))
                self.table_widget.setItem(row, 1, QTableWidgetItem(device_info.get("point", "")))
                self.table_widget.setItem(row, 2, QTableWidgetItem(device_info.get("district_name", "")))
                self.table_widget.setItem(row, 3, QTableWidgetItem(device_info.get("id", "")))
                self.update_last_column(row, device_info)

            self.adjust_size_to_table()

            self.table_widget.setSortingEnabled(True)
            self.table_widget.sortByColumn(4, Qt.DescendingOrder)            
        except Exception as e:
            raise BaseError(3500, str(e))

    def update_last_column(self, row, device_info):
        raise NotImplementedError("Subclasses should implement this method")

    def reject(self):
        self.op_thread.terminate()
        super().reject()