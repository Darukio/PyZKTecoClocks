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
from scripts.common.business_logic.hour_manager import update_devices_time
from scripts.common.utils.errors import BaseError, BaseErrorWithMessageBox
from scripts.ui.base_select_devices_dialog import SelectDevicesDialog
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
import logging

class UpdateTimeDeviceDialog(SelectDevicesDialog):
    def __init__(self, parent=None):
        try:
            super().__init__(parent, op_function=update_devices_time, window_title="ACTUALIZAR HORA")
            self.device_info = self.load_device_info()
            self.init_ui()
        except Exception as e:
            raise BaseError(3501, str(e))
        
    def init_ui(self):
        header_labels = ["Distrito", "Modelo", "Punto de Marcación", "IP", "ID", "Comunicación"]
        super().init_ui(header_labels=header_labels)
        self.btn_update.setText("Actualizar hora")

    def load_device_info(self):
        """Load device information from the file."""
        device_info = {}
        try:
            with open("info_devices.txt", "r") as file:
                for line in file:
                    parts = line.strip().split(" - ")
                    if len(parts) == 8:
                        ip = parts[3]
                        battery_status = parts[6] == "True"
                        device_info[ip] = battery_status
        except Exception as e:
            raise BaseErrorWithMessageBox(3001, str(e), parent=self)
        return device_info

    def op_terminate(self, devices=None):
        try:
            self.table_widget.setVisible(False)
            self.table_widget.sortByColumn(3, Qt.DescendingOrder)

            if not self.column_exists("Estado de Conexión"):
                # Add a new column to the table
                connection_column = self.table_widget.columnCount()
                self.table_widget.setColumnCount(connection_column + 1)
                self.table_widget.setHorizontalHeaderItem(connection_column, QTableWidgetItem("Estado de Conexión"))
            else:
                # Get the column number
                connection_column = self.get_column_number("Estado de Conexión")

            if not self.column_exists("Estado de Pila"):
                # Add a new column to the table
                battery_column = self.table_widget.columnCount()
                self.table_widget.setColumnCount(battery_column + 1)
                self.table_widget.setHorizontalHeaderItem(battery_column, QTableWidgetItem("Estado de Pila"))
            else:
                # Get the column number
                battery_column = self.get_column_number("Estado de Pila")

            selected_ips = {device["ip"] for device in self.selected_devices}
            
            for row in range (self.table_widget.rowCount()):
                ip_selected = self.table_widget.item(row, 3).text()  # Column 3 holds the IP
                connection_item = QTableWidgetItem("")
                battery_item = QTableWidgetItem("")
                if ip_selected not in selected_ips:
                    connection_item.setBackground(QColor(Qt.white))
                    battery_item.setBackground(QColor(Qt.white))
                else:
                    connection_item.setBackground(QColor(Qt.blue))
                    battery_item.setBackground(QColor(Qt.blue))
                    logging.debug(devices)
                    device = devices.get(ip_selected)
                    if device:
                        if device.get("connection failed"):
                            connection_item.setText("Conexión fallida")
                            connection_item.setBackground(QColor(Qt.red))
                        else:
                            connection_item.setText("Conexión exitosa")
                            connection_item.setBackground(QColor(Qt.green))
                        if device.get("connection failed"):
                            battery_item.setText("No aplica")
                            battery_item.setBackground(QColor(Qt.gray))
                        else:
                            logging.debug(f"Device: {device}")
                            battery_failing = device.get("battery failing") or not self.device_info.get(ip_selected, True)
                            if battery_failing:
                                battery_item.setText("Pila fallando")
                                battery_item.setBackground(QColor(Qt.red))
                            else:
                                battery_item.setText("Pila funcionando")
                                battery_item.setBackground(QColor(Qt.green))
                connection_item.setFlags(connection_item.flags() & ~Qt.ItemIsEditable)
                self.table_widget.setItem(row, connection_column, connection_item)
                battery_item.setFlags(battery_item.flags() & ~Qt.ItemIsEditable)
                self.table_widget.setItem(row, battery_column, battery_item)

            self.adjust_size_to_table()

            self.table_widget.setSortingEnabled(True)
            self.table_widget.sortByColumn(6, Qt.DescendingOrder)    

            self.deselect_all_rows()
            super().op_terminate()
            self.table_widget.setVisible(True)
        except Exception as e:
            logging.error(e)
            raise BaseErrorWithMessageBox(3500, str(e), parent=self)