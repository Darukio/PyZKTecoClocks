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
from PyQt5.QtWidgets import (
    QMessageBox
)
from scripts.business_logic.program_manager import RestartManager
from scripts.common.utils.errors import BaseError
from scripts.ui.base_select_devices_dialog import SelectDevicesDialog

class RestartDevicesDialog(SelectDevicesDialog):
    def __init__(self, parent=None):
        """
        Initializes the RestartDevicesDialog class.

        Args:
            parent (QWidget, optional): The parent widget for this dialog. Defaults to None.

        Raises:
            BaseError: If an exception occurs during initialization, it raises a BaseError
                       with code 3501 and the exception message.
        """
        try:
            restart_manager: RestartManager = RestartManager()
            super().__init__(parent, op_function=restart_manager.restart_devices, window_title="REINICIAR DISPOSITIVOS")
            self.init_ui()
        except Exception as e:
            raise BaseError(3501, str(e))

    def init_ui(self):
        """
        Initializes the user interface for the restart devices dialog.

        This method sets up the table headers with predefined labels and updates
        the text of the update button to indicate its purpose as restarting devices.

        Header Labels:
            - "Distrito": Represents the district information.
            - "Modelo": Represents the device model.
            - "Punto de Marcación": Represents the marking point.
            - "IP": Represents the IP address of the device.
            - "ID": Represents the device ID.
            - "Comunicación": Represents the communication status of the device.
        """
        header_labels: list[str] = ["Distrito", "Modelo", "Punto de Marcación", "IP", "ID", "Comunicación"]
        super().init_ui(header_labels=header_labels)
        self.btn_update.setText("Reiniciar dispositivos")

    def op_terminate(self, devices_errors: dict[str, dict[str, bool]] = None):
        """
        Handles the termination operation for devices, displaying appropriate messages
        based on the presence of errors.

        Args:
            devices_errors (dict[str, dict[str, bool]]): A dictionary containing device error
                information. The keys are device identifiers, and the values are dictionaries
                with error details. Defaults to None.

        Behavior:
            - If `devices_errors` contains entries, an error message box is displayed with
              the list of problematic devices.
            - If `devices_errors` is empty or None, an information message box is displayed
              indicating successful device restarts.
            - Logs the `devices_errors` dictionary for debugging purposes.
            - Calls the parent class's `op_terminate` method after handling the operation.

        Exceptions:
            - Logs any exceptions that occur during the execution of the method.
        """
        try:
            #logging.debug(devices_errors)
            if len(devices_errors) > 0:
                error: BaseError = BaseError(2002, f"{', '.join(devices_errors.keys())}")
                error.show_message_box(parent=self)
            else:
                QMessageBox.information(self, "Éxito", "Dispositivos reiniciados correctamente")
            super().op_terminate()
        except Exception as e:
            logging.error(e)