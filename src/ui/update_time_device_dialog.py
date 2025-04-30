# PyZKTecoClocks: GUI for managing ZKTeco clocks, enabling clock 
# time synchronization and attendance data retrieval.
# Copyright (C) 2024  Paulo Sebastian Spaciuk (Darukio)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from PyQt5.QtWidgets import (
    QTableWidgetItem
)
from src.business_logic.program_manager import HourManager
from src.common.business_logic import hour_manager
from src.common.business_logic.models.device import Device
from src.common.utils.errors import BaseError, BaseErrorWithMessageBox
from src.ui.base_select_devices_dialog import SelectDevicesDialog
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
import logging

class UpdateTimeDeviceDialog(SelectDevicesDialog):
    def __init__(self, parent = None):
        """
        Initializes the UpdateTimeDeviceDialog class.

        Args:
            parent (Optional[QWidget]): The parent widget for this dialog. Defaults to None.

        Attributes:
            device_info (dict[str, bool]): A dictionary containing device information loaded from `load_device_info()`.

        Raises:
            BaseError: If an exception occurs during initialization, it raises a BaseError with code 3501 and the exception message.
        """
        try:
            hour_manager = HourManager()
            super().__init__(parent, op_function=hour_manager.manage_hour_devices, window_title="ACTUALIZAR HORA")
            self.device_info: dict[str, bool] = self.load_device_info()
            self.init_ui()
        except Exception as e:
            raise BaseError(3501, str(e))
        
    def init_ui(self):
        """
        Initializes the user interface for the update time device dialog.

        This method sets up the table headers with predefined labels and updates
        the text of the update button to "Actualizar hora".

        Header Labels:
            - Distrito
            - Modelo
            - Punto de Marcación
            - IP
            - ID
            - Comunicación
        """
        header_labels: list[str] = ["Distrito", "Modelo", "Punto de Marcación", "IP", "ID", "Comunicación"]
        super().init_ui(header_labels=header_labels)
        self.btn_update.setText("Actualizar hora")

    def load_device_info(self):
        """
        Loads device information from a file and returns it as a dictionary.

        The method reads the file "info_devices.txt" line by line, extracts the IP address
        and battery status from each line, and stores them in a dictionary. The IP address
        is used as the key, and the battery status (a boolean) is used as the value.

        Returns:
            (dict[str, bool]): A dictionary where the keys are IP addresses (str) and the
                            values are battery statuses (bool).

        Raises:
            BaseErrorWithMessageBox: If an error occurs while reading the file, an exception
            is raised with an error code and the exception message.
        """
        device_info: dict[str, bool] = {}
        try:
            with open("info_devices.txt", "r") as file:
                for line in file:
                    parts: list[str] = line.strip().split(" - ")
                    if len(parts) == 8:
                        ip: str = parts[3]
                        battery_status: bool = parts[6] == "True"
                        device_info[ip] = battery_status
        except Exception as e:
            raise BaseErrorWithMessageBox(3001, str(e), parent=self)
        return device_info

    def op_terminate(self, devices_errors: dict[str, dict[str, bool]] = None):
        """
        Updates the table widget with the connection and battery status of devices.
        This method processes the `devices_errors` dictionary to update the table widget
        with the connection and battery status for each device. It ensures that the required
        columns exist in the table, updates the rows with the appropriate status and colors,
        and adjusts the table's size and sorting.

        Args:
            devices_errors (dict[str, dict[str, bool]], optional): A dictionary where the keys
                are device IP addresses, and the values are dictionaries containing error
                statuses for the device. The inner dictionary can have the following keys:

                - "connection failed" (bool): Indicates if the connection to the device failed.
                - "battery failing" (bool): Indicates if the device's battery is failing.

                Defaults to None.
                
        Raises:
            BaseErrorWithMessageBox: If an exception occurs during the operation, it raises
                a custom error with a message box displaying the error details.
        """
        #logging.debug(devices_errors)
        try:
            connection_column = self.ensure_column_exists("Estado de Conexión")
            battery_column = self.ensure_column_exists("Estado de Pila")
            
            for row in range (self.table_widget.rowCount()):
                ip_selected: str = self.table_widget.item(row, 3).text()  # Column 3 holds the IP
                connection_item: QTableWidgetItem = QTableWidgetItem("")
                battery_item: QTableWidgetItem = QTableWidgetItem("")
                if ip_selected not in self.selected_ips:
                    connection_item.setBackground(QColor(Qt.white))
                    battery_item.setBackground(QColor(Qt.white))
                else:
                    device: dict[str, bool] = devices_errors.get(ip_selected)
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
                            battery_failing: bool = device.get("battery failing") or not self.device_info.get(ip_selected, True)
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
            raise BaseErrorWithMessageBox(3500, str(e), parent=self)