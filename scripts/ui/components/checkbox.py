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

from PyQt5.QtWidgets import QWidget, QCheckBox, QHBoxLayout
from PyQt5.QtCore import Qt

class CheckBoxDelegate(QWidget):
    def __init__(self, parent=None):
        """
        Initializes a custom checkbox widget.

        Args:
            parent (QWidget, optional): The parent widget for this checkbox. Defaults to None.

        Attributes:
            checkbox (QCheckBox): The QCheckBox instance contained within this widget.
        """
        super().__init__(parent)
        layout = QHBoxLayout(self)
        self.checkbox = QCheckBox(self)
        layout.addWidget(self.checkbox)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def isChecked(self):
        """
        Check if the checkbox is currently checked.

        Returns:
            bool: True if the checkbox is checked, False otherwise.
        """
        return self.checkbox.isChecked()

    def setChecked(self, state):
        """
        Sets the checked state of the checkbox.

        Args:
            state (bool): The desired checked state of the checkbox. 
                          True to check the checkbox, False to uncheck it.
        """
        self.checkbox.setChecked(state)