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

import logging
import os
import sys
import time
from scripts.business_logic.device_manager import activate_all_devices
from scripts.common.utils.add_to_startup import add_to_startup, is_startup_entry_exists, remove_from_startup
from scripts.common.utils.errors import BaseError
from scripts.common.utils.file_manager import find_marker_directory, find_root_directory
from scripts.ui.device_attendance_count_dialog import DeviceAttendancesCountDialog
from scripts.ui.device_attendance_dialog import DeviceAttendancesDialog
from scripts.ui.logs_dialog import LogsDialog
from scripts.ui.modify_device_dialog import ModifyDevicesDialog
from scripts.ui.ping_devices_dialog import PingDevicesDialog
from scripts.ui.restart_devices_dialog import RestartDevicesDialog
from scripts import config
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QSystemTrayIcon, QMenu, QAction, QMessageBox
from PyQt5.QtCore import pyqtSlot
from scripts.ui.update_time_device_dialog import UpdateTimeDeviceDialog
from scripts.common.utils.system_utils import exit_duplicated_instance, verify_duplicated_instance

config.read(os.path.join(find_root_directory(), 'config.ini'))  # Read the config.ini configuration file

class MainWindow(QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            self.is_running = False  # Variable to indicate if the application is running
            self.checked_clear_attendance = eval(config['Device_config']['clear_attendance'])  # State of the clear attendance checkbox
            self.checked_automatic_init = is_startup_entry_exists("Programa Reloj de Asistencias")

            self.tray_icon = None  # Variable to store the QSystemTrayIcon
            self.__init_ui()  # Initialize the user interface

            # Set the initial tray icon to loading.png
            file_path = os.path.join(find_marker_directory("resources"), "resources", "system_tray", "loading.png")  # Icon file path
            logging.debug(file_path)
            self.tray_icon.setIcon(QIcon(file_path))

            """ if not is_user_admin():
                run_as_admin()
            """

            if verify_duplicated_instance(sys.argv[0]):
                exit_duplicated_instance()

            activate_all_devices()  # Activate all devices

            # Change the tray icon to program-icon.png after all initializations
            file_path = os.path.join(find_marker_directory("resources"), "resources", "system_tray", "program-icon.png")  # Icon file path
            logging.debug(file_path)
            self.tray_icon.setIcon(QIcon(file_path))
        except Exception as e:
            raise BaseError(3501, str(e), "critical")

    def __init_ui(self):
        # Create and configure the system tray icon
        self.__create_tray_icon()  # Create the system tray icon        

    def __create_tray_icon(self):
        '''
        Create a system tray icon with a custom context menu
        '''
        try:
            file_path = os.path.join(find_marker_directory("resources"), "resources", "system_tray", "loading.png")  # Icon file path
            logging.debug(file_path)
            self.tray_icon = QSystemTrayIcon(QIcon(), self)  # Create QSystemTrayIcon with the icon and associated main window
            self.tray_icon.showMessage("Notificación", 'Iniciando la aplicación', QSystemTrayIcon.Information)
            self.tray_icon.setToolTip("Programa Reloj de Asistencias")  # Tooltip text

            # Create a custom context menu
            menu = QMenu()
            menu.addAction(self.__create_action("Modificar dispositivos...", lambda: self.__opt_modify_devices()))  # Action to modify devices
            menu.addAction(self.__create_action("Reiniciar dispositivos...", lambda: self.__opt_restart_devices()))  # Action to restart devices    
            menu.addAction(self.__create_action("Probar conexiones...", lambda: self.__opt_test_connections()))  # Action to test connections
            menu.addAction(self.__create_action("Actualizar hora...", lambda: self.__opt_update_devices_time()))  # Action to update device time
            menu.addAction(self.__create_action("Obtener marcaciones...", lambda: self.__opt_fetch_devices_attendances()))  # Action to fetch device attendances
            menu.addAction(self.__create_action("Obtener cantidad de marcaciones...", lambda: self.__opt_show_attendances_count()))  # Action to show attendance count
            menu.addSeparator()  # Context menu separator
            # Checkbox as QAction with checkable state
            clear_attendance_action = QAction("Eliminar marcaciones", menu)
            clear_attendance_action.setCheckable(True)  # Make the QAction checkable
            clear_attendance_action.setChecked(self.checked_clear_attendance)  # Set initial checkbox state
            clear_attendance_action.triggered.connect(self.__opt_toggle_checkbox_clear_attendance)  # Connect action to toggle checkbox state
            menu.addAction(clear_attendance_action)  # Add action to the menu
            logging.debug(f'checked_automatic_init: {self.checked_automatic_init}')
            # Action to toggle the checkbox state
            automatic_init_action = QAction('Iniciar automáticamente', menu)
            automatic_init_action.setCheckable(True)
            automatic_init_action.setChecked(self.checked_automatic_init)
            automatic_init_action.triggered.connect(self.__opt_toggle_checkbox_automatic_init)
            menu.addAction(automatic_init_action)
            menu.addSeparator()  # Context menu separator
            menu.addAction(self.__create_action("Ver errores...", lambda: self.__opt_show_logs()))  # Action to show logs
            menu.addAction(self.__create_action("Salir", lambda: self.__opt_exit_icon()))  # Action to exit the application
            self.tray_icon.setContextMenu(menu)  # Assign context menu to the icon
            
            self.tray_icon.show()  # Show the system tray icon
        except Exception as e:
            raise BaseError(3500, str(e), "critical")

    def __create_action(self, text, function):
        """
        Create an action for the context menu.
        
        Args:
            text (str): Action text.
            function (function): Function to be executed when the action is triggered.
            
        Returns:
            QAction: Created action.
        """
        action = QAction(text, self)  # Create QAction with the text and associated main window
        action.triggered.connect(function)  # Connect the action to the provided function
        return action  # Return the created action
    
    def __set_icon_color(self, icon, color):
        """
        Change the color of the system tray icon.

        Args:
            icon (QSystemTrayIcon): System tray icon to modify.
            color (str): Color to set ('red', 'yellow', 'green').
        """
        self.color_icon = color  # Update the icon color
        file_path = os.path.join(find_marker_directory("resources"), "resources", "system_tray", f"circle-{self.color_icon}.png")  # Icon file path with the new color
        icon.setIcon(QIcon(file_path))  # Set the new icon with the specified color

    def start_timer(self):
        """
        Start the timer and return the current time.

        Returns:
            float: Current time in seconds.
        """
        return time.time()  # Return the current time in seconds

    def stop_timer(self, start_time):
        """
        Stop the timer, calculate the elapsed time, and show a notification.

        Args:
            start_time (float): Start time obtained when starting the timer.
        """
        end_time = self.start_timer()  # Get the end time
        elapsed_time = end_time - start_time  # Calculate the elapsed time
        logging.debug(f'La tarea finalizo en {elapsed_time:.2f} segundos')
        self.tray_icon.showMessage("Notificacion", f'La tarea finalizo en {elapsed_time:.2f} segundos', QSystemTrayIcon.Information)  # Show notification with the elapsed time

    def __show_message_information(self, title, text):
        """
        Show a dialog box with a message.

        Args:
            title (str): Dialog box title.
            text (str): Message text.
        """
        msg_box = QMessageBox()  # Create QMessageBox instance
        msg_box.setWindowTitle(title)  # Set the dialog box title
        msg_box.setText(text)  # Set the message text
        msg_box.setIcon(QMessageBox.Information)  # Set the dialog box icon (information)
        file_path = os.path.join(find_marker_directory("resources"), "resources", "fingerprint.ico")
        msg_box.setWindowIcon(QIcon(file_path))
        msg_box.exec_()  # Show the dialog box

        # Once the QMessageBox is closed, show the context menu again
        if self.tray_icon:
            self.tray_icon.contextMenu().setVisible(True)

    @pyqtSlot()
    def __opt_modify_devices(self):
        """
        Option to modify devices.
        """
        try:
            device_dialog = ModifyDevicesDialog()
            device_dialog.exec_()
            # Once the QDialog is closed, show the context menu again
            if self.tray_icon:
                self.tray_icon.contextMenu().setVisible(True)
        except Exception as e:
            BaseError(3500, str(e))

    @pyqtSlot()
    def __opt_show_logs(self):
        """
        Option to show logs.
        """
        try:
            error_log_dialog = LogsDialog()
            error_log_dialog.exec_()
            # Once the QDialog is closed, show the context menu again
            if self.tray_icon:
                self.tray_icon.contextMenu().setVisible(True)
        except Exception as e:
            BaseError(3500, str(e))

    @pyqtSlot()
    def __opt_restart_devices(self):
        """
        Option to restart devices.
        """
        try:
            restart_devices_dialog = RestartDevicesDialog()
            restart_devices_dialog.exec_()
            # Once the QDialog is closed, show the context menu again
            if self.tray_icon:
                self.tray_icon.contextMenu().setVisible(True)
        except Exception as e:
            BaseError(3500, str(e))

    @pyqtSlot()
    def __opt_test_connections(self):
        """
        Option to test device connections.
        """
        try:
            device_status_dialog = PingDevicesDialog()  # Get device status
            device_status_dialog.exec_()
            # Once the QDialog is closed, show the context menu again
            if self.tray_icon:
                self.tray_icon.contextMenu().setVisible(True)
        except Exception as e:
            BaseError(3500, str(e))

    @pyqtSlot()
    def __opt_update_devices_time(self):
        """
        Option to update the time on devices.
        """
        try:
            update_time_device_dialog = UpdateTimeDeviceDialog()
            update_time_device_dialog.exec_()
            # Once the QDialog is closed, show the context menu again
            if self.tray_icon:
                self.tray_icon.contextMenu().setVisible(True)
        except Exception as e:
            BaseError(3500, str(e))

    @pyqtSlot()
    def __opt_fetch_devices_attendances(self):
        """
        Option to fetch device attendances.
        """
        try:
            device_attendances_dialog = DeviceAttendancesDialog()
            device_attendances_dialog.op_terminated.connect(self.stop_timer)
            device_attendances_dialog.exec_()
            # Once the QDialog is closed, show the context menu again
            if self.tray_icon:
                self.tray_icon.contextMenu().setVisible(True)
        except Exception as e:
            BaseError(3500, str(e))

    @pyqtSlot()
    def __opt_show_attendances_count(self):
        """
        Option to show the number of attendances per device.
        """
        try:
            device_attendances_count_dialog = DeviceAttendancesCountDialog()
            device_attendances_count_dialog.op_terminated.connect(self.stop_timer)
            device_attendances_count_dialog.exec_()
            # Once the QDialog is closed, show the context menu again
            if self.tray_icon:
                self.tray_icon.contextMenu().setVisible(True)
        except Exception as e:
            BaseError(3500, str(e))

    @pyqtSlot()
    def __opt_toggle_checkbox_clear_attendance(self):
        """
        Option to toggle the state of the clear attendance checkbox.
        """
        self.checked_clear_attendance = not self.checked_clear_attendance  # Invert the current checkbox state
        logging.debug(f"Status checkbox: {self.checked_clear_attendance}")  # Debug log: current checkbox state
        # Modify the value of the desired field in the configuration file
        config['Device_config']['clear_attendance'] = str(self.checked_clear_attendance)
        # Write the changes back to the configuration file
        try:
            with open('config.ini', 'w') as config_file:
                config.write(config_file)
        except Exception as e:
            BaseError(3001, str(e))

    @pyqtSlot()
    def __opt_toggle_checkbox_automatic_init(self):
        """
        Option to toggle the state of the run at startup checkbox.
        """
        import sys
        try:
            if getattr(sys, 'frozen', False):
                self.checked_automatic_init = not self.checked_automatic_init  # Invert the current checkbox state
                logging.debug(f"Status checkbox: {self.checked_automatic_init}")  # Debug log: current checkbox state

                if self.checked_automatic_init:
                    logging.debug('add_to_startup')
                    add_to_startup("Programa Reloj de Asistencias")
                else:
                    logging.debug('remove_from_startup')
                    remove_from_startup("Programa Reloj de Asistencias")
        except Exception as e:
            BaseError(3000, str(e))

    @pyqtSlot()
    def __opt_exit_icon(self):
        """
        Option to exit the application.
        """
        if self.tray_icon:
            self.tray_icon.hide()  # Hide the system tray icon
            QApplication.quit()  # Exit the application