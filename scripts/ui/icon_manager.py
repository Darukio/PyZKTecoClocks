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
from scripts.common.utils.add_to_startup import add_to_startup, is_startup_entry_exists, remove_from_startup
from scripts.common.utils.errors import BaseError
from scripts.common.utils.file_manager import find_marker_directory, find_root_directory
from scripts.ui.logs_dialog import LogsDialog
from scripts.ui.modify_device_dialog import ModifyDevicesDialog
from scripts.ui.obtain_attendances_devices_dialog import ObtainAttendancesDevicesDialog
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
        """
        Initializes the IconManager class.
        This constructor sets up the initial state of the application, including
        the system tray icon, configuration settings, and application startup behavior.
        It also handles potential duplicate instances of the application.
        Attributes:
            is_running (bool): Indicates if the application is currently running.
            checked_clear_attendance (bool): State of the "clear attendance" checkbox,
                retrieved from the configuration file.
            checked_automatic_init (bool): Indicates if the application is set to start
                automatically on system startup.
            tray_icon (QSystemTrayIcon): The system tray icon for the application.
        Raises:
            BaseError: If an exception occurs during initialization, it raises a
                BaseError with an error code, message, and severity level.
        """
        try:
            super().__init__()
            self.is_running = False  # Variable to indicate if the application is running
            self.checked_clear_attendance = eval(config['Device_config']['clear_attendance'])  # State of the clear attendance checkbox
            self.checked_automatic_init = is_startup_entry_exists("Programa Reloj de Asistencias")

            self.tray_icon: QSystemTrayIcon = None  # Variable to store the QSystemTrayIcon
            self.__init_ui()  # Initialize the user interface

            # Set the initial tray icon to loading.png
            file_path = os.path.join(find_marker_directory("resources"), "resources", "system_tray", "loading.png")  # Icon file path
            # logging.debug(file_path)
            self.tray_icon.setIcon(QIcon(file_path))

            """ if not is_user_admin():
                run_as_admin()
            """

            #if verify_duplicated_instance(sys.argv[0]):
            #    exit_duplicated_instance()

            # Change the tray icon to program-icon.png after all initializations
            file_path = os.path.join(find_marker_directory("resources"), "resources", "system_tray", "program-icon.png")  # Icon file path
            # logging.debug(file_path)
            self.tray_icon.setIcon(QIcon(file_path))
        except Exception as e:
            raise BaseError(3501, str(e), "critical")

    def __init_ui(self):
        """
        Initializes the user interface components for the application.

        This method is responsible for setting up and configuring the system tray icon
        by invoking the necessary helper methods. It ensures that the system tray icon
        is properly created and ready for use.
        """
        # Create and configure the system tray icon
        self.__create_tray_icon()  # Create the system tray icon        

    def __create_tray_icon(self):
        """
        Creates and configures the system tray icon for the application.
        This method initializes a QSystemTrayIcon with a tooltip and a custom context menu
        containing various actions for interacting with the application. The context menu
        includes options for modifying devices, restarting devices, testing connections,
        updating device time, fetching attendances, and toggling specific settings. It also
        provides options to view logs and exit the application.
        The tray icon displays a notification message upon initialization and is shown in
        the system tray.
        Raises:
            BaseError: If an exception occurs during the creation or configuration of the
                       system tray icon, it raises a BaseError with an error code and message.
        """
        try:
            file_path = os.path.join(find_marker_directory("resources"), "resources", "system_tray", "loading.png")  # Icon file path
            # logging.debug(file_path)
            self.tray_icon = QSystemTrayIcon(QIcon(file_path), self)  # Create QSystemTrayIcon with the icon and associated main window
            self.tray_icon.showMessage("Notificación", 'Iniciando la aplicación', QSystemTrayIcon.Information)
            self.tray_icon.setToolTip("Programa Reloj de Asistencias")  # Tooltip text

            # Create a custom context menu
            menu = QMenu()
            menu.addAction(self.__create_action("Modificar dispositivos...", lambda: self.__opt_modify_devices()))  # Action to modify devices
            menu.addAction(self.__create_action("Reiniciar dispositivos...", lambda: self.__opt_restart_devices()))  # Action to restart devices    
            menu.addAction(self.__create_action("Probar conexiones...", lambda: self.__opt_test_connections()))  # Action to test connections
            menu.addAction(self.__create_action("Actualizar hora...", lambda: self.__opt_update_devices_time()))  # Action to update device time
            menu.addAction(self.__create_action("Obtener marcaciones...", lambda: self.__opt_fetch_devices_attendances()))  # Action to fetch device attendances
            menu.addSeparator()  # Context menu separator
            # Checkbox as QAction with checkable state
            clear_attendance_action = QAction("Eliminar marcaciones", menu)
            clear_attendance_action.setCheckable(True)  # Make the QAction checkable
            clear_attendance_action.setChecked(self.checked_clear_attendance)  # Set initial checkbox state
            clear_attendance_action.triggered.connect(self.__opt_toggle_checkbox_clear_attendance)  # Connect action to toggle checkbox state
            menu.addAction(clear_attendance_action)  # Add action to the menu
            # logging.debug(f'checked_automatic_init: {self.checked_automatic_init}')
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
        Creates a QAction with the specified text and associates it with a function.

        Args:
            text (str): The display text for the action.
            function (callable): The function to be executed when the action is triggered.

        Returns:
            QAction: The created action with the specified text and connected function.
        """
        action = QAction(text, self)  # Create QAction with the text and associated main window
        action.triggered.connect(function)  # Connect the action to the provided function
        return action  # Return the created action
    
    def start_timer(self):
        """
        Starts a timer by returning the current time in seconds.

        Returns:
            float: The current time in seconds since the epoch.
        """
        return time.time()  # Return the current time in seconds

    def stop_timer(self, start_time):
        """
        Stops the timer and calculates the elapsed time since the provided start time.

        Args:
            start_time (float): The starting time in seconds since the epoch.

        Returns:
            None

        Logs:
            Logs the elapsed time in seconds to the application log.

        Side Effects:
            Displays a system tray notification with the elapsed time.
        """
        end_time = self.start_timer()  # Get the end time
        elapsed_time = end_time - start_time  # Calculate the elapsed time
        logging.info(f'La tarea finalizo en {elapsed_time:.2f} segundos')
        self.tray_icon.showMessage("Notificacion", f'La tarea finalizo en {elapsed_time:.2f} segundos', QSystemTrayIcon.Information)  # Show notification with the elapsed time

    def __show_message_information(self, title, text):
        """
        Displays an informational message dialog with a specified title and text.
        This method creates a QMessageBox instance to show an informational message
        to the user. It sets the title, text, and icon of the dialog box. Additionally,
        it customizes the window icon using a specified `.ico` file. After the dialog
        box is closed, it ensures that the tray icon's context menu is made visible again.
        Args:
            title (str): The title of the message dialog box.
            text (str): The informational text to display in the dialog box.
        Side Effects:
            - Displays a QMessageBox with the specified title and text.
            - Sets the window icon of the QMessageBox using a custom `.ico` file.
            - Ensures the tray icon's context menu is visible after the dialog box is closed.
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
        Handles the modification of devices through a dialog interface.

        This method creates and displays a `ModifyDevicesDialog` for modifying device settings.
        Once the dialog is closed, it ensures that the tray icon's context menu is visible again.
        Any exceptions encountered during the process are logged using the `BaseError` class.

        Raises:
            BaseError: If an exception occurs during the execution of the method, it is wrapped
                       and logged with an error code of 3500.
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
        Displays the logs dialog and ensures the system tray context menu is visible after the dialog is closed.

        This method attempts to create and display a `LogsDialog` instance. Once the dialog is closed, 
        it ensures that the system tray icon's context menu is made visible again. If an exception occurs 
        during this process, it is handled by logging the error using the `BaseError` class.

        Raises:
            Exception: If an error occurs while creating or displaying the `LogsDialog`.
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
        Handles the restart devices operation by displaying a dialog to the user.

        This method creates and executes a `RestartDevicesDialog` to allow the user
        to restart devices. Once the dialog is closed, it ensures that the tray icon's
        context menu is made visible again. If an exception occurs during the process,
        it logs the error using the `BaseError` class.

        Raises:
            Exception: If an error occurs during the execution of the dialog or
                       while handling the tray icon's context menu.
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
        Handles the testing of device connections by opening a dialog to ping devices.

        This method creates and displays a `PingDevicesDialog` to check the status of devices.
        Once the dialog is closed, it ensures that the tray icon's context menu is visible again.
        If an exception occurs during the process, it logs the error using the `BaseError` class.

        Raises:
            Exception: If an error occurs during the execution of the method.
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
        Handles the process of updating the time on devices.

        This method creates and displays a dialog for updating the time on devices.
        Once the dialog is closed, it ensures that the context menu of the tray icon
        is made visible again if it exists. Any exceptions raised during the process
        are caught and logged using the BaseError class.

        Exceptions:
            Exception: Catches any exception that occurs during the execution and
                       logs it with an error code and message.
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
        Handles the process of fetching attendance data from devices.

        This method creates and displays a dialog for obtaining attendance data
        from devices. Once the dialog is closed, it ensures that the tray icon's
        context menu is made visible again. Any exceptions encountered during the
        process are captured and logged using the BaseError class.

        Raises:
            BaseError: If an exception occurs during the execution of the method.
        """
        try:
            device_attendances_dialog = ObtainAttendancesDevicesDialog()
            #device_attendances_dialog.op_terminated.connect(self.stop_timer)
            device_attendances_dialog.exec_()
            # Once the QDialog is closed, show the context menu again
            if self.tray_icon:
                self.tray_icon.contextMenu().setVisible(True)
        except Exception as e:
            BaseError(3500, str(e))

    @pyqtSlot()
    def __opt_toggle_checkbox_clear_attendance(self):
        """
        Toggles the state of the 'clear attendance' checkbox and updates the configuration file accordingly.

        This method inverts the current state of the `checked_clear_attendance` attribute, updates the 
        corresponding value in the configuration file under the 'Device_config' section, and writes the 
        changes back to the file. If an error occurs during the file write operation, it raises a 
        `BaseError` with an appropriate error code and message.

        Raises:
            BaseError: If an exception occurs while writing to the configuration file.
        """
        self.checked_clear_attendance = not self.checked_clear_attendance  # Invert the current checkbox state
        # logging.debug(f"Status checkbox: {self.checked_clear_attendance}")  # Debug log: current checkbox state
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
        Toggles the state of the "automatic initialization" checkbox and updates the system's startup configuration
        accordingly. This method is intended to be used in a frozen Python application (e.g., packaged with PyInstaller).
        When the checkbox is toggled:
        - If enabled, the application is added to the system's startup programs.
        - If disabled, the application is removed from the system's startup programs.
        Exceptions are caught and logged using the `BaseError` class.
        Raises:
            BaseError: If an exception occurs during the process, it is wrapped and raised with an error code (3000).
        Notes:
            - The `add_to_startup` and `remove_from_startup` functions are assumed to handle the actual system-level
              operations for managing startup programs.
            - This method only functions correctly in a frozen Python environment (e.g., when `sys.frozen` is True).
        """
        import sys
        try:
            if getattr(sys, 'frozen', False):
                self.checked_automatic_init = not self.checked_automatic_init  # Invert the current checkbox state
                # logging.debug(f"Status checkbox: {self.checked_automatic_init}")  # Debug log: current checkbox state

                if self.checked_automatic_init:
                    # logging.debug('add_to_startup')
                    add_to_startup("Programa Reloj de Asistencias")
                else:
                    # logging.debug('remove_from_startup')
                    remove_from_startup("Programa Reloj de Asistencias")
        except Exception as e:
            BaseError(3000, str(e))

    @pyqtSlot()
    def __opt_exit_icon(self):
        """
        Handles the exit operation for the application.

        This method hides the system tray icon, if it exists, and then quits the application.

        Returns:
            None
        """
        if self.tray_icon:
            self.tray_icon.hide()  # Hide the system tray icon
            QApplication.quit()  # Exit the application