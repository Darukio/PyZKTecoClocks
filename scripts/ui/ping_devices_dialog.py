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
from PyQt5.QtCore import Qt
from scripts.business_logic.program_manager import ConnectionsInfo
from scripts.common.utils.errors import BaseError, BaseErrorWithMessageBox
from scripts.ui.base_select_devices_dialog import SelectDevicesDialog

class PingDevicesDialog(SelectDevicesDialog):
    def __init__(self, parent=None):
        """
        Initializes the PingDevicesDialog class.

        This constructor sets up the dialog window for testing device connections.
        It initializes the user interface and sets the operation function to obtain
        connection information.

        Args:
            parent (QWidget, optional): The parent widget for this dialog. Defaults to None.

        Raises:
            BaseError: If an exception occurs during initialization, it raises a BaseError
                       with code 3501 and the exception message.
        """
        try:
            connection_info = ConnectionsInfo()
            super().__init__(parent, op_function=connection_info.obtain_connections_info, window_title="PROBAR CONEXIONES")
            self.init_ui()
        except Exception as e:
            raise BaseError(3501, str(e))

    def init_ui(self):
        """
        Initializes the user interface for the ping devices dialog.

        This method sets up the table headers and updates the text of the 
        update button to "Probar conexiones" (Test connections).

        Header Labels:
            - Distrito: Represents the district or region.
            - Modelo: Represents the device model.
            - Punto de Marcación: Represents the marking point.
            - IP: Represents the IP address of the device.
            - ID: Represents the device identifier.
            - Comunicación: Represents the communication status.

        Overrides:
            This method overrides the `init_ui` method from the parent class
            and passes the custom header labels to it.
        """
        header_labels = ["Distrito", "Modelo", "Punto de Marcación", "IP", "ID", "Comunicación"]
        super().init_ui(header_labels=header_labels)
        self.btn_update.setText("Probar conexiones")

    def op_terminate(self, devices=None):
        """
        Updates the table widget with the connection status and device information for a list of devices.
        This method iterates through the rows of the table widget and updates the columns with information
        such as connection status, attendance count, serial number, platform, and firmware version for each device.
        The information is retrieved from the `devices` dictionary, which maps IP addresses to device data.
        Args:
            devices (dict, optional): A dictionary where keys are IP addresses (str) and values are dictionaries
                                      containing device information. Each device dictionary may include:
                                      - "connection_failed" (bool): Indicates if the connection failed.
                                      - "device_info" (dict): Contains device-specific information such as:
                                          - "attendance_count" (int or str): The number of attendance records.
                                          - "serial_number" (str): The serial number of the device.
                                          - "platform" (str): The platform of the device.
                                          - "firmware_version" (str): The firmware version of the device.
        Raises:
            BaseErrorWithMessageBox: If an exception occurs during the operation, it raises a custom error
                                     with a message box displaying the error details.
        Notes:
            - The method ensures that specific columns ("Estado de Conexión", "Cant. de Marcaciones",
              "Número de Serie", "Plataforma", "Firmware") exist in the table widget before updating.
            - The background color of each cell is updated based on the device's connection status and
              availability of information.
            - The table widget is resized and sorted by the 6th column in descending order after updates.
            - All rows are deselected at the end of the operation.
        """
        try:
            #logging.debug(devices)

            # Ensure the "Estado de Conexión" column exists
            connection_column = self.ensure_column_exists("Estado de Conexión")
            attendance_count_column = self.ensure_column_exists("Cant. de Marcaciones")            
            serial_number_column = self.ensure_column_exists("Número de Serie")            
            platform_column = self.ensure_column_exists("Plataforma")
            firmware_version_column = self.ensure_column_exists("Firmware")

            for row in range(self.table_widget.rowCount()):
                ip_selected = self.table_widget.item(row, 3).text()  # Column 3 holds the IP
                connection_item = QTableWidgetItem("")
                attendance_count_item = QTableWidgetItem("")
                serial_number_item = QTableWidgetItem("")
                platform_item = QTableWidgetItem("")
                firmware_version_item = QTableWidgetItem("")
                
                if ip_selected not in self.selected_ips:
                    connection_item.setBackground(QColor(Qt.white))
                    attendance_count_item.setBackground(QColor(Qt.white))
                    serial_number_item.setBackground(QColor(Qt.white))
                    platform_item.setBackground(QColor(Qt.white))
                    firmware_version_item.setBackground(QColor(Qt.white))
                else:
                    device = devices[ip_selected]
                    
                    if device:
                        if device.get("connection_failed"):
                            connection_item.setText("Conexión fallida")
                            connection_item.setBackground(QColor(Qt.red))
                        else:
                            connection_item.setText("Conexión exitosa")
                            connection_item.setBackground(QColor(Qt.green))
                        
                        #logging.debug(str(device))
                        #logging.debug(str(device.get("device_info", "")))
                        if not device.get("device_info") or not device["device_info"].get("attendance_count"):
                            attendance_count_item.setText("No aplica")
                            attendance_count_item.setBackground(QColor(Qt.gray))
                        else:
                            attendance_count_item.setText(str(device.get("device_info", "").get("attendance_count", "")))
                            attendance_count_item.setBackground(QColor(Qt.green))
                        
                        if not device.get("device_info") or not device["device_info"].get("serial_number"):
                            serial_number_item.setText("No aplica")
                            serial_number_item.setBackground(QColor(Qt.gray))
                        else:
                            serial_number_item.setText(str(device.get("device_info", "").get("serial_number", "")))
                            serial_number_item.setBackground(QColor(Qt.green))
                        
                        if not device.get("device_info") or not device["device_info"].get("platform"):
                            platform_item.setText("No aplica")
                            platform_item.setBackground(QColor(Qt.gray))
                        else:
                            platform_item.setText(str(device.get("device_info", "").get("platform", "")))
                            platform_item.setBackground(QColor(Qt.green))
                        
                        if not device.get("device_info") or not device["device_info"].get("firmware_version"):
                            firmware_version_item.setText("No aplica")
                            firmware_version_item.setBackground(QColor(Qt.gray))
                        else:
                            firmware_version_item.setText(str(device.get("device_info", "").get("firmware_version", "")))
                            firmware_version_item.setBackground(QColor(Qt.green))
                        
                connection_item.setFlags(connection_item.flags() & ~Qt.ItemIsEditable)
                attendance_count_item.setFlags(attendance_count_item.flags() & ~Qt.ItemIsEditable)
                serial_number_item.setFlags(serial_number_item.flags() & ~Qt.ItemIsEditable)
                platform_item.setFlags(platform_item.flags() & ~Qt.ItemIsEditable)
                firmware_version_item.setFlags(firmware_version_item.flags() & ~Qt.ItemIsEditable)
                
                self.table_widget.setItem(row, connection_column, connection_item)
                self.table_widget.setItem(row, attendance_count_column, attendance_count_item)
                self.table_widget.setItem(row, serial_number_column, serial_number_item)
                self.table_widget.setItem(row, platform_column, platform_item)
                self.table_widget.setItem(row, firmware_version_column, firmware_version_item)

            self.adjust_size_to_table()

            self.table_widget.setSortingEnabled(True)
            self.table_widget.sortByColumn(6, Qt.DescendingOrder)  

            self.deselect_all_rows()
            super().op_terminate()
        except Exception as e:
            raise BaseErrorWithMessageBox(3500, str(e), parent=self)