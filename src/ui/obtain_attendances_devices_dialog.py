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

import configparser
config = configparser.ConfigParser()
config.read('config.ini')
from datetime import datetime
import logging
import os
import re
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QLabel, QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import urllib.parse
from src.business_logic.program_manager import AttendancesManager
from src.common.business_logic.models.attendance import Attendance
from src.common.utils.errors import BaseError, BaseErrorWithMessageBox
from src.common.utils.file_manager import find_root_directory
from src.ui.base_select_devices_dialog import SelectDevicesDialog
from src.ui.operation_thread import OperationThread
from PyQt5.QtWidgets import QMessageBox

class ObtainAttendancesDevicesDialog(SelectDevicesDialog):
    def __init__(self, parent=None):
        """
        Initializes the ObtainAttendancesDevicesDialog class.

        Args:
            parent (Optional[QWidget]): The parent widget for this dialog. Defaults to None.

        Attributes:
            failed_devices (list[str]): A list to store devices that failed during the operation.
            attendances_manager (AttendancesManager): An instance of AttendancesManager to handle attendance management.

        Raises:
            BaseError: If an exception occurs during initialization, it raises a BaseError with code 3501 and the exception message.
        """
        try:
            self.failed_devices: list[str] = []
            self.attendances_manager = AttendancesManager()
            super().__init__(parent, op_function=self.attendances_manager.manage_devices_attendances, window_title="OBTENER MARCACIONES")
            self.init_ui()
        except Exception as e:
            raise BaseError(3501, str(e))

    def init_ui(self):
        """
        Initializes the user interface for the attendance devices dialog.

        This method sets up the UI components, including labels, buttons, and layouts,
        to display and manage attendance device information. It also configures event
        handlers for user interactions.

        Raises:
            BaseError: If an exception occurs during the initialization process, it
                       raises a BaseError with code 3501 and the exception message.

        UI Components:
            - Header Labels: ["Distrito", "Modelo", "Punto de Marcación", "IP", "ID", "Comunicación"]
            - QPushButton: A button to retry failed connections, initially hidden.
            - QPushButton: A button to update and obtain attendance records, with updated text.
            - QLabel: A label to display the total number of attendances, initially hidden.
        """
        try:
            header_labels = ["Distrito", "Modelo", "Punto de Marcación", "IP", "ID", "Comunicación"]
            super().init_ui(header_labels=header_labels)
            self.btn_retry_failed_connection = QPushButton("Reintentar fallidos", self)
            self.btn_retry_failed_connection.clicked.connect(self.on_retry_failed_connection_clicked)
            self.button_layout.addWidget(self.btn_retry_failed_connection)
            self.btn_retry_failed_connection.setVisible(False)
            self.btn_update.setText("Obtener marcaciones")
            self.label_total_attendances = QLabel("Total de Marcaciones: 0", self)
            self.label_total_attendances.setAlignment(Qt.AlignCenter)
            self.layout().addWidget(self.label_total_attendances)
            self.label_total_attendances.setVisible(False)
        except Exception as e:
            raise BaseError(3501, str(e))
        
    def operation_with_selected_ips(self):
        """
        Executes an operation with the selected IP addresses.

        This method hides the retry button and the total attendances label before
        attempting to perform the operation. It calls the parent class's 
        `operation_with_selected_ips` method to execute the operation. If an 
        exception occurs during the execution, it displays the retry button 
        for failed connections.

        Exceptions:
            Exception: Catches any exception that occurs during the operation 
            and triggers the display of the retry button.
        """
        self.btn_retry_failed_connection.setVisible(False)
        self.label_total_attendances.setVisible(False)
        try:
            super().operation_with_selected_ips()
        except Exception as e:
            self.show_btn_retry_failed_connection()
        return

    def op_terminate(self, devices: dict[str, dict[str, str]] = None):
        """
        Finalizes the operation of obtaining attendance data from devices and updates the UI accordingly.
        
        Args:
            devices (dict[str, dict[str, str]]): A dictionary where the keys are device IPs and the values are dictionaries 
                containing device-specific information, such as "connection failed" status and "attendance count".
        
        Functionality:
            - Iterates through the rows of the table widget to update attendance data for each device.
            - Checks if the device IP is in the list of selected IPs and updates the corresponding table cell:
                - Marks devices with failed connections in red and adds them to the failed devices list.
                - Updates the attendance count for devices with successful connections and marks them in green.
            - Ensures the "Cant. de Marcaciones" column exists in the table and updates it with attendance data.
            - Calculates the total number of attendances across all devices.
            - Adjusts the table size, enables sorting, and sorts the table by a specific column in descending order.
            - Deselects all rows in the table and centers the window.
            - Attempts to check attendance files and handles any exceptions with a warning-level error.
            - Displays a retry button for failed connections and updates the total attendance label.
        
        Raises:
            BaseErrorWithMessageBox: If an unexpected exception occurs during the operation, it is raised with an error message box.
        """
        try:
            self.failed_devices = []
            #logging.debug(f'selected devices: {self.selected_ips} - devices from operation: {devices} - failed devices: {self.failed_devices}')

            actual_column = self.ensure_column_exists("Cant. de Marcaciones")

            total_marcaciones = 0
            for row in range (self.table_widget.rowCount()):
                ip_selected = self.table_widget.item(row, 3).text()  # Column 3 holds the IP
                attendances_count_item = QTableWidgetItem("")
                if ip_selected not in self.selected_ips:
                    attendances_count_item.setBackground(QColor(Qt.white))
                else:
                    device = devices.get(ip_selected)
                    if device:
                        if device.get("connection failed", False):
                            attendances_count_item.setText("Conexión fallida")
                            attendances_count_item.setBackground(QColor(Qt.red))
                            self.failed_devices.append(ip_selected)
                        else:
                            attendance_count = device.get("attendance count")
                            try:
                                total_marcaciones += int(attendance_count)
                            except ValueError:
                                attendance_count = 0
                                BaseError(3500, f"Error al obtener la cantidad de marcaciones del dispositivo {ip_selected}")
                            attendances_count_item.setText(str(attendance_count))
                            attendances_count_item.setBackground(QColor(Qt.green))
                attendances_count_item.setFlags(attendances_count_item.flags() & ~Qt.ItemIsEditable)
                self.table_widget.setItem(row, actual_column, attendances_count_item)
            self.adjust_size_to_table()
            self.table_widget.setSortingEnabled(True)
            self.table_widget.sortByColumn(6, Qt.DescendingOrder)  
            self.deselect_all_rows()

            self.center_window()
            try:
                self.check_attendance_files()
            except Exception as e:
                BaseError(3000, str(e), level="warning")
            self.show_btn_retry_failed_connection()
            self.label_total_attendances.setText(f"Total de Marcaciones: {total_marcaciones}")
            self.label_total_attendances.setVisible(True)
            super().op_terminate()
        except Exception as e:
            raise BaseErrorWithMessageBox(3500, str(e), parent=self)

    def parse_attendance(self, line: str):
        """
        Parses a line of attendance data and extracts the timestamp.

        Args:
            line (str): A string containing attendance data, expected to have at least
                        three parts separated by spaces, where the second and third parts
                        represent the date and time respectively.

        Returns:
            (datetime or None): A datetime object representing the parsed timestamp if the
                              line is well-formed and the date and time are valid.
                              Returns None if the line is malformed or the date/time
                              cannot be parsed.
        """
        parts = line.split()
        if len(parts) < 3:
            return None
        try:
            date_str, time_str = parts[1], parts[2]
            timestamp: datetime = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
            return timestamp
        except ValueError:
            return None

    def check_attendance_files(self):
        """
        Checks attendance files in the "devices" directory for errors.
        A daily record (in a temporary file) is kept of each already reported incorrect check‑in,
        so that new ones are only reported once. For reporting, information is grouped by file,
        displaying each error only once (by file_path) as in the original version.

        Raises:
            BaseError: if the 'devices' folder is not found or if attendance errors are detected.
        """
        import tempfile
        from datetime import timedelta

        # Get today's and yesterday's dates
        today_str = datetime.now().strftime("%Y-%m-%d")
        yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        devices_path = os.path.join(find_root_directory(), "devices")
        temp_dir = tempfile.gettempdir()
        # logging.debug(f"Directorio temporal: {temp_dir}")

        # Temporary file for today and yesterday
        temp_file_path = os.path.join(
            temp_dir,
            f"reported_incorrect_attendances_{today_str}.tmp"
        )
        temp_file_yesterday = os.path.join(
            temp_dir,
            f"reported_incorrect_attendances_{yesterday_str}.tmp"
        )

        # Remove yesterday's file if it exists
        if os.path.exists(temp_file_yesterday):
            try:
                os.remove(temp_file_yesterday)
            except Exception as e:
                logging.warning(f"No se pudo eliminar el archivo de ayer: {e}")

        # Load errors already reported today: each line is a unique error identifier (file_path + line)
        reported_errors = set()
        if os.path.exists(temp_file_path):
            with open(temp_file_path, "r", encoding="utf-8") as tf:
                for line in tf:
                    reported_errors.add(line.strip())

        new_reported = set()            # Newly found errors (by line)
        files_with_new_errors = {}      # Grouped by file: key = file.path, value = info for report

        if not os.path.isdir(devices_path):
            raise BaseError(3000, "No se encontró la carpeta 'devices'", level="warning")

        # Traverse the devices directory
        with os.scandir(devices_path) as entries:
            for subfolder in entries:
                if not subfolder.is_dir():
                    continue

                subfolder_path = os.path.join(devices_path, subfolder.name)
                with os.scandir(subfolder_path) as sub_entries:
                    for sub_entry in sub_entries:
                        if not sub_entry.is_dir():
                            continue

                        with os.scandir(sub_entry.path) as files:
                            for file in files:
                                if today_str in file.name and file.name.endswith(".cro"):
                                    file_has_new_error = False  # Flag for new errors in this file

                                    with open(file.path, "r", encoding="utf-8") as f:
                                        # Check each line for attendance errors
                                        for line_number, line in enumerate(f, start=1):
                                            attendance = Attendance(timestamp=self.parse_attendance(line))
                                            if attendance is not None and (
                                                attendance.is_three_months_old() or attendance.is_in_the_future()
                                            ):
                                                # Create a unique identifier for this error line
                                                error_id = str(line)
                                                if error_id in reported_errors:
                                                    continue  # This error was already reported

                                                # New error found
                                                new_reported.add(error_id)
                                                file_has_new_error = True
                                                # To continue scanning the file for all new errors (even though only one link per file is shown),
                                                # do not break here. Uncomment the next line to only report the first occurrence per file.
                                                # break

                                    if file_has_new_error:
                                        # Add one entry per file, as in the original version
                                        if file.path not in files_with_new_errors:
                                            files_with_new_errors[file.path] = {
                                                "ip": self.extract_ip(file.name),
                                                "date": self.extract_date(file.name),
                                                "file_path": self.format_file_uri(file.path)
                                            }

        # Append newly found errors to the temporary file
        if new_reported:
            with open(temp_file_path, "a", encoding="utf-8") as tf:
                for err in new_reported:
                    tf.write(err + "\n")

        # Build report from files that have new errors
        devices_with_error = list(files_with_new_errors.values())
        if devices_with_error:
            error_info = (
                "<html><br>" +
                "<br>".join(
                    [f"- <a href='{device['file_path']}'>{device['date']}: {device['ip']}</a>"
                    for device in devices_with_error]
                ) +
                "</html>"
            )
            error_code = 2003
            error = BaseError(error_code, error_info)

            config.read(os.path.join(find_root_directory(), 'config.ini'))
            clear_attendance: bool = config.getboolean('Device_config', 'clear_attendance')
            if clear_attendance:
                self.ask_force_clear_attendances(error_code, error_info, parent=self)
            else:
                error.show_message_box_html(parent=self)

    def ask_force_clear_attendances(self, error_code, error_info, parent):
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(f"Error {error_code}")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(error_info)
        msg_box.setInformativeText("¿Desea habilitar el forzado de eliminado de marcaciones en su proxima obtencion de marcaciones?")
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        result = msg_box.exec_()
        if result == QMessageBox.Ok:
            config['Device_config']['force_clear_attendance'] = 'True'

            # Write the changes back to the configuration file
            try:
                with open('config.ini', 'w') as config_file:
                    config.write(config_file)
            except Exception as e:
                BaseError(3001, str(e))
            
            logging.info("Se ha habilitado el forzado de eliminacion de marcaciones")

    def format_file_uri(self, file_path: str):
        """
        Converts a local file path to a file URI.

        This method takes a file path as input, replaces backslashes with forward slashes
        (to ensure compatibility across different operating systems), and encodes special
        characters to make the path safe for use in a URI. It then constructs a file URI
        by prefixing the encoded path with 'file:'.

        Args:
            file_path (str): The local file path to be converted into a file URI.

        Returns:
            (str): The formatted file URI.
        """
        file_url = urllib.parse.urljoin('file:', urllib.parse.quote(file_path.replace("\\", "/")))
        # logging.debug(file_url)
        return file_url

    def extract_ip(self, filename: str):
        """
        Extracts an IP address from a given filename.

        The method uses a regular expression to match filenames that follow the
        pattern: `<IP_ADDRESS>_<DATE>_file.cro`, where:

        - `<IP_ADDRESS>` is a valid IPv4 address (e.g., 192.168.1.1).
        - `<DATE>` is in the format YYYY-MM-DD.

        Args:
            filename (str): The filename to extract the IP address from.

        Returns:
            (str): The extracted IP address if the filename matches the pattern, 
                 otherwise None.
        """
        match = re.match(r"^(\d+\.\d+\.\d+\.\d+)_\d{4}-\d{2}-\d{2}_file\.cro$", filename)
        return match.group(1) if match else None
    
    def extract_date(self, filename: str):
        """
        Extracts a date string from a given filename if it matches a specific pattern.

        The method uses a regular expression to identify filenames that follow the
        pattern: `<IP_ADDRESS>_<YYYY-MM-DD>_file.cro`, where:

        - `<IP_ADDRESS>` is a sequence of four groups of digits separated by dots.
        - `<YYYY-MM-DD>` is a date in the format year-month-day.

        Args:
            filename (str): The filename to extract the date from.

        Returns:
            (str or None): The extracted date string in the format 'YYYY-MM-DD' if the
                        filename matches the pattern; otherwise, None.
        """
        match = re.match(r"^\d+\.\d+\.\d+\.\d+_(\d{4}-\d{2}-\d{2})_file\.cro$", filename)
        return match.group(1) if match else None

    def show_btn_retry_failed_connection(self):
        """
        Displays the "Retry Failed Connection" button if there are failed devices.

        This method checks if the `failed_devices` attribute exists and contains 
        one or more entries. If so, it makes the `btn_retry_failed_connection` 
        button visible. If an exception occurs during execution, it raises a 
        `BaseError` with an appropriate error code and message.

        Raises:
            BaseError: If an exception occurs, it is wrapped in a `BaseError` 
                       with code 3500 and the exception message.
        """
        try:            
            if self.failed_devices and len(self.failed_devices) > 0:
                self.btn_retry_failed_connection.setVisible(True)
        except Exception as e:
            raise BaseError(3500, str(e))
    
    def on_retry_failed_connection_clicked(self):
        """
        Handles the retry action for failed device connections.

        This method is triggered when the "Retry Failed Connection" button is clicked.
        It attempts to reconnect to the devices that previously failed to connect and
        updates the UI to reflect the retry process. A separate thread is used to manage
        the reconnection attempts and progress updates.

        Steps performed:

        - Hides certain UI elements (e.g., table widget, buttons) and updates labels.
        - Initializes and starts an `OperationThread` to handle the reconnection logic.
        - Connects thread signals to appropriate methods for progress updates and cleanup.
        - Hides the retry button after it is clicked.

        Raises:
            BaseError: If an exception occurs during the execution of the method.

        Attributes:
            self.failed_devices (list): List of devices that failed to connect.
            self.attendances_manager (object): Manager responsible for handling device attendances.
        """
        try:
            self.table_widget.setVisible(False)
            self.table_widget.sortByColumn(3, Qt.DescendingOrder)
            self.label_total_attendances.setVisible(False)
            self.label_updating.setText("Reintentando conexiones...")
            self.btn_update.setVisible(False)
            self.btn_activate_all.setVisible(False)
            self.btn_deactivate_all.setVisible(False)
            self.label_updating.setVisible(True)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            # logging.debug(f"Dispositivos seleccionados: {self.failed_devices}")
            self.op_thread = OperationThread(self.attendances_manager.manage_devices_attendances, self.failed_devices)
            self.op_thread.progress_updated.connect(self.update_progress)
            self.op_thread.op_terminate.connect(self.op_terminate)
            self.op_thread.finished.connect(self.cleanup_thread)
            self.op_thread.start()
            self.btn_retry_failed_connection.setVisible(False)  # Hide the button after clicking
        except Exception as e:
            raise BaseError(3500, str(e))