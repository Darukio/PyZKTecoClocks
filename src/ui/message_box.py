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

import os
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon
from src.common.utils.errors import BaseError
from src.common.utils.file_manager import find_marker_directory

# Subclass for the device status dialog
class MessageBox(QMessageBox):
    def __init__(self, icon, text, parent=None):
        """
        Initializes the custom message box with the specified icon, text, and optional parent widget.

        Args:
            icon (QMessageBox.Icon): The icon to display in the message box.
            text (str): The text message to display in the message box.
            parent (QWidget, optional): The parent widget of the message box. Defaults to None.
            
        Raises:
            BaseError: If an error occurs during initialization, a BaseError with code 3501 is raised.
        """
        try:
            super().__init__(icon, 'Programa Reloj de Asistencias', text, parent)

            file_path = os.path.join(find_marker_directory("resources"), "resources", "fingerprint.ico")
            self.setWindowIcon(QIcon(file_path))
        except Exception as e:
            raise BaseError(3501, str(e))