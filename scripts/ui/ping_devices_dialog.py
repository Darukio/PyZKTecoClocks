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
    QTableWidgetItem
)
from PyQt5.QtGui import QColor
import logging
from scripts.business_logic.device_manager import ping_devices
from PyQt5.QtCore import Qt
from scripts.common.utils.errors import BaseError, BaseErrorWithMessageBox
from scripts.ui.base_select_devices_dialog import SelectDevicesDialog

class PingDevicesDialog(SelectDevicesDialog):
    def __init__(self, parent=None):
        try:
            super().__init__(parent, op_function=ping_devices, window_title="PROBAR CONEXIONES")
            self.init_ui()
        except Exception as e:
            raise BaseError(3501, str(e))

    def init_ui(self):
        header_labels = ["Distrito", "Modelo", "Punto de Marcación", "IP", "ID", "Comunicación"]
        super().init_ui(header_labels=header_labels)
        self.btn_update.setText("Probar conexiones")

    def op_terminate(self, devices=None):
        try:
            logging.debug(devices)

            if not self.column_exists("Estado de Conexión"):
                # Add a new column to the table
                actual_column = self.table_widget.columnCount()
                self.table_widget.setColumnCount(actual_column + 1)
                self.table_widget.setHorizontalHeaderItem(actual_column, QTableWidgetItem("Estado de Conexión"))
            else:
                # Get the column number
                actual_column = self.get_column_number("Estado de Conexión")

            selected_ips = {device["ip"] for device in self.selected_devices}
            for row in range (self.table_widget.rowCount()):
                ip_selected = self.table_widget.item(row, 3).text()  # Column 3 holds the IP
                connection_item = QTableWidgetItem("")
                if ip_selected not in selected_ips:
                    connection_item.setBackground(QColor(Qt.white))
                else:
                    device = devices.get(ip_selected)
                    if device:
                        if device.get("connection failed"):
                            connection_item.setText("Conexión fallida")
                            connection_item.setBackground(QColor(Qt.red))
                        else:
                            connection_item.setText("Conexión exitosa")
                            connection_item.setBackground(QColor(Qt.green))
                connection_item.setFlags(connection_item.flags() & ~Qt.ItemIsEditable)
                self.table_widget.setItem(row, actual_column, connection_item)

            self.adjust_size_to_table()

            self.table_widget.setSortingEnabled(True)
            self.table_widget.sortByColumn(6, Qt.DescendingOrder)  

            self.deselect_all_rows()
            super().op_terminate()
        except Exception as e:
            raise BaseErrorWithMessageBox(3500, str(e), parent=self)