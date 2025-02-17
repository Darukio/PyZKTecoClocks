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

from PyQt5.QtWidgets import (
    QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QMessageBox
)
import os
import logging

from scripts.common.business_logic.connection import restart_device
from scripts.common.business_logic.device_manager import retry_network_operation
from scripts.ui.base_dialog import BaseDialog
from scripts.ui.checkbox import CheckBoxDelegate
from scripts.ui.combobox import ComboBoxDelegate
from PyQt5.QtCore import Qt

from scripts.common.utils.errors import BaseError, BaseErrorWithMessageBox, ConnectionFailedError

class RestartDevicesDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__(parent, window_title="Reiniciar dispositivos")

        # Path to the file with device information
        self.file_path = os.path.join(os.getcwd(), "info_devices.txt")
        self.data = []
        self.init_ui()
        super().init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Table to display devices
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(7)
        self.table_widget.setHorizontalHeaderLabels(["Distrito", "Modelo", "Punto de Marcación", "IP", "ID", "Comunicación", "Seleccionar reinicio"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table_widget)

        # Button to restart selected devices
        self.btn_restart = QPushButton("Reiniciar dispositivos")
        self.btn_restart.clicked.connect(self.restart_selected_devices)
        layout.addWidget(self.btn_restart)

        self.setLayout(layout)

        # Load initial data
        self.load_data()

    def load_data(self):
        """Load devices from the file and display them in the table."""
        try:
            self.data = []
            with open(self.file_path, "r") as file:
                for line in file:
                    parts = line.strip().split(" - ")
                    if len(parts) == 8:
                        district, model, point, ip, id, communication, battery, active = parts
                        self.data.append((district, model, point, ip, id, communication))
            self.load_data_into_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar la información: {e}")

    def load_data_into_table(self):
        """Fill the table with device data."""
        self.table_widget.setRowCount(0)

        for row, (district, model, point, ip, id, communication) in enumerate(self.data):
            self.table_widget.insertRow(row)

            # Create non-editable cells
            item_district = QTableWidgetItem(district)
            item_district.setFlags(item_district.flags() & ~Qt.ItemIsEditable)
            self.table_widget.setItem(row, 0, item_district)

            item_model = QTableWidgetItem(model)
            item_model.setFlags(item_model.flags() & ~Qt.ItemIsEditable)
            self.table_widget.setItem(row, 1, item_model)

            item_point = QTableWidgetItem(point)
            item_point.setFlags(item_point.flags() & ~Qt.ItemIsEditable)
            self.table_widget.setItem(row, 2, item_point)

            item_ip = QTableWidgetItem(ip)
            item_ip.setFlags(item_ip.flags() & ~Qt.ItemIsEditable)
            self.table_widget.setItem(row, 3, item_ip)

            item_id = QTableWidgetItem(str(id))
            item_id.setFlags(item_id.flags() & ~Qt.ItemIsEditable)
            self.table_widget.setItem(row, 4, item_id)

            # Configure ComboBoxDelegate for column 5 but disable editing
            combo_box_delegate = ComboBoxDelegate(self.table_widget)
            self.table_widget.setItemDelegateForColumn(5, combo_box_delegate)

            # Display the value as text, not editable
            item_communication = QTableWidgetItem(communication)
            item_communication.setFlags(item_communication.flags() & ~Qt.ItemIsEditable)
            self.table_widget.setItem(row, 5, item_communication)

            # Configure CheckBox in column 6 (interactive)
            checkbox = CheckBoxDelegate()
            checkbox.setChecked(False)
            self.table_widget.setCellWidget(row, 6, checkbox)

        self.adjust_size_to_table()

    def restart_selected_devices(self):
        """Restart selected devices."""
        selected_devices = []
        for row in range(self.table_widget.rowCount()):
            checkbox = self.table_widget.cellWidget(row, 6)
            if checkbox and checkbox.isChecked():
                ip = self.table_widget.item(row, 3).text()
                communication = self.table_widget.item(row, 5).text()
                selected_devices.append((ip, communication))

        if not selected_devices:
            QMessageBox.information(self, "Sin selección", "No se seleccionaron dispositivos para reiniciar.")
            return

        for ip, communication in selected_devices:

            try:
                retry_network_operation(restart_device, args=(ip, 4370, communication,))
                QMessageBox.information(self, "Éxito", "Dispositivos reiniciados correctamente.")
                logging.info(f"Dispositivo IP: {ip} reiniciado correctamente.")
            except ConnectionFailedError as e:
                BaseErrorWithMessageBox(2002, str(e))
            except Exception as e:
                BaseError(0000, str(e))