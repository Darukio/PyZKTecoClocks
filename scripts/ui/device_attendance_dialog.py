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

# Subclass for the device status dialog
from datetime import datetime
import logging
import os
import re

import urllib
from scripts.common.business_logic.attendances_manager import is_in_the_future, is_three_months_old, manage_device_attendances
from scripts.business_logic.device_manager import activate_all_devices
from scripts.common.utils.errors import BaseError
from scripts.common.utils.file_manager import find_root_directory
from scripts.ui.base_device_dialog import BaseDeviceDialog
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QLabel, QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

class DeviceAttendancesDialog(BaseDeviceDialog):
    def __init__(self, parent=None):
        try:
            super().__init__(parent, manage_device_attendances, "OBTENER MARCACIONES")
            self.__init_ui()
            self.op_thread.progress_updated.connect(self.update_progress)  # Connect the progress signal
        except Exception as e:
            raise BaseError(3501, str(e))

    def __init_ui(self):
        try:
            header_labels = ["IP", "Punto de Marcación", "Nombre de Distrito", "ID", "Cant. de Marcaciones"]
            super().init_ui(header_labels)
            self.btn_update.setText("Obtener marcaciones")
            
            button_layout = QHBoxLayout()

            self.btn_retry_all_connection = QPushButton("Reintentar todos", self)
            self.btn_retry_all_connection.clicked.connect(self.on_retry_all_connection_clicked)
            button_layout.addWidget(self.btn_retry_all_connection)
            self.btn_retry_all_connection.setVisible(False)

            self.btn_retry_failed_connection = QPushButton("Reintentar fallidos", self)
            self.btn_retry_failed_connection.clicked.connect(self.on_retry_failed_connection_clicked)
            button_layout.addWidget(self.btn_retry_failed_connection)
            self.btn_retry_failed_connection.setVisible(False)

            self.layout().addLayout(button_layout)

            self.setLayout(self.layout())

            self.label_total_marcaciones = QLabel("Total de Marcaciones: 0", self)
            self.label_total_marcaciones.setAlignment(Qt.AlignCenter)
            self.layout().addWidget(self.label_total_marcaciones)
            self.label_total_marcaciones.setVisible(False)
        except Exception as e:
            raise BaseError(3501, str(e))

    def update_progress(self, percent_progress, device_progress, processed_devices, total_devices):
        if percent_progress and device_progress:
            self.progress_bar.setValue(percent_progress)  # Update the progress bar value
            self.label_updating.setText(f"Último intento de conexión: {device_progress}\n{processed_devices}/{total_devices} dispositivos")
        
    def update_table(self, device_status=None):
        try:
            self.total_marcaciones = 0
            super().update_table(device_status)
            self.center_window()
            self.check_attendance_files()
            self.show_btn_retry_failed_connection()
            self.label_total_marcaciones.setText(f"Total de Marcaciones: {self.total_marcaciones}")
            self.label_total_marcaciones.setVisible(True)
        except Exception as e:
            raise BaseError(3500, str(e))

    def parse_attendance(self, line):
        parts = line.split()
        if len(parts) < 3:
            return None  # Línea mal formada
        try:
            date_str, time_str = parts[1], parts[2]
            timestamp = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
            return timestamp
        except ValueError:
            return None

    def check_attendance_files(self):
        today_str = datetime.now().strftime("%Y-%m-%d")
        devices_path = os.path.join(find_root_directory(), "devices")
        
        if not os.path.isdir(devices_path):
            raise BaseError(3000, "No se encontró la carpeta 'devices'")
        
        devices_with_error = []
        with os.scandir(devices_path) as entries:
            for subfolder in entries:
                if not subfolder.is_dir():
                    continue
                
                attendance_with_error = False
                subfolder_path = os.path.join(devices_path, subfolder.name)
                with os.scandir(subfolder_path) as sub_entries:
                    for sub_entry in sub_entries:
                        if not sub_entry.is_dir():
                            continue

                        with os.scandir(sub_entry.path) as files:
                            for file in files:
                                if today_str in file.name and file.name.endswith(".cro"):
                                    with open(file.path, "r", encoding="utf-8") as f:
                                        for line in f:
                                            timestamp = self.parse_attendance(line)
                                            if timestamp and (is_three_months_old(timestamp) or is_in_the_future(timestamp)):
                                                attendance_with_error = True
                                                break
                                    if attendance_with_error:
                                        devices_with_error.append({"ip": self.extract_ip(file.name), "date": self.extract_date(file.name), "file_path": self.format_file_uri(file.path)})
                                        break
        
        if len(devices_with_error) > 0:
            error_info = "<html>" + "<br>" + "<br>".join(
                [f"- <a href='{device['file_path']}'>{device['date']}: {device['ip']}</a>"
                for device in devices_with_error]
            ) + "</html>"
            
            error = BaseError(2003, error_info)
            error.show_message_box_html(parent=self)

    def format_file_uri(self, file_path):
        """Converts a Windows file path to a properly formatted file URI."""
        file_path = os.path.abspath(file_path)
        file_uri = urllib.parse.urljoin('file:', urllib.parse.quote(file_path.replace("\\", "/")))
        logging.debug(file_uri)
        return file_uri

    def extract_ip(self, filename):
        match = re.match(r"^(\d+\.\d+\.\d+\.\d+)_\d{4}-\d{2}-\d{2}_file\.cro$", filename)
        return match.group(1) if match else None
    
    def extract_date(self, filename):
        match = re.match(r"^\d+\.\d+\.\d+\.\d+_(\d{4}-\d{2}-\d{2})_file\.cro$", filename)
        return match.group(1) if match else None

    def show_btn_retry_failed_connection(self):
        try:
            self.btn_retry_all_connection.setVisible(True)
            
            has_failed_connection = any(
                device["attendance_count"] == "Conexión fallida" for device in self.op_thread.result.values()
                )
            if has_failed_connection:
                self.btn_retry_failed_connection.setVisible(True)
        except Exception as e:
            raise BaseError(3500, str(e))

    def update_last_column(self, row, device_info):
        try:
            status_item = QTableWidgetItem(device_info.get("attendance_count", ""))
            if device_info.get("attendance_count") == "Conexión fallida":
                status_item.setBackground(QColor(Qt.red))
            else:
                status_item.setBackground(QColor(Qt.green))
            
            self.table_widget.setItem(row, 4, status_item)
            try:
                self.total_marcaciones += int(device_info.get("attendance_count", 0))
                logging.debug(f'Total attendances: {self.total_marcaciones}')
            except ValueError:
                pass
        except Exception as e:
            raise BaseError(3500, str(e))
    
    def on_retry_all_connection_clicked(self):
        try:
            self.label_total_marcaciones.setVisible(False)
            self.label_updating.setText("Reintentando conexiones...")

            activate_all_devices()
            self.update_data()
        
            self.btn_retry_failed_connection.setVisible(False)  # Hide the button after clicking
            self.btn_retry_all_connection.setVisible(False)  # Hide the button after clicking
        except Exception as e:
            raise BaseError(3500, str(e))
    
    def on_retry_failed_connection_clicked(self):
        try:
            self.label_total_marcaciones.setVisible(False)
            self.label_updating.setText("Reintentando conexiones...")

            with open('info_devices.txt', 'r') as file:
                lines = file.readlines()

            new_lines = []
            for line in lines:
                parts = line.strip().split(' - ')
                ip = parts[3]
                if ip in self.op_thread.result and self.op_thread.result[ip]["attendance_count"] == "Conexión fallida":
                    parts[7] = "True"
                else:
                    parts[7] = "False"
                new_lines.append(' - '.join(parts) + '\n')

            with open('info_devices.txt', 'w') as file:
                file.writelines(new_lines)

            logging.debug("Estado activo actualizado correctamente.")

            self.update_data()

            self.btn_retry_all_connection.setVisible(False)  # Hide the button after clicking
            self.btn_retry_failed_connection.setVisible(False)  # Hide the button after clicking
        except Exception as e:
            raise BaseError(3500, str(e))