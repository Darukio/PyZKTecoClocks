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
    QMessageBox
)
from scripts.business_logic.device_manager import restart_devices
from scripts.common.utils.errors import BaseError
from scripts.ui.base_select_devices_dialog import SelectDevicesDialog

class RestartDevicesDialog(SelectDevicesDialog):
    def __init__(self, parent=None):
        try:
            super().__init__(parent, op_function=restart_devices, window_title="REINICIAR DISPOSITIVOS")
            self.init_ui()
        except Exception as e:
            raise BaseError(3501, str(e))

    def init_ui(self):
        header_labels = ["Distrito", "Modelo", "Punto de Marcación", "IP", "ID", "Comunicación"]
        super().init_ui(header_labels=header_labels)
        self.btn_update.setText("Reiniciar dispositivos")

    def op_terminate(self, devices=None):
        if len(devices) > 0:
            error = BaseError(2002, f"{', '.join(devices.keys())}", parent=self)
            error.show_message_box()
        else:
            QMessageBox.information(self, "Éxito", "Dispositivos reiniciados correctamente.")
        super().op_terminate()