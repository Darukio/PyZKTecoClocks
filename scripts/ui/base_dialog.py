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

from PyQt5.QtWidgets import QDialog, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from scripts.common.utils.errors import BaseError
from scripts.common.utils.file_manager import find_marker_directory
import os

class BaseDialog(QDialog):
    def __init__(self, parent=None, window_title=""):
        """
        Initializes the base dialog window with the specified parent and window title.
        Args:
            parent (QWidget, optional): The parent widget for the dialog. Defaults to None.
            window_title (str, optional): The title of the dialog window. Defaults to an empty string.
        Raises:
            BaseError: If an exception occurs during initialization, it raises a BaseError with code 3501
                       and the exception message.
        """
        try:
            super().__init__(parent)
            self.setWindowTitle(window_title)

            # Set window icon
            self.file_path_resources = os.path.join(find_marker_directory("resources"), "resources")
            self.file_path_icon = os.path.join(self.file_path_resources, "fingerprint.ico")
            self.setWindowIcon(QIcon(self.file_path_icon))
            
            # Allow minimizing the window
            self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
            # Allow maximizing the window
            self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

            self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        except Exception as e:
            raise BaseError(3501, str(e))

    def init_ui(self):
        pass

    def adjust_size_to_table(self):
        """
        Adjusts the size of the dialog window to fit the content of the table widget.
        This method resizes the columns of the table widget to fit their contents and calculates
        the required width and height of the table based on its content. It ensures that the
        dialog window does not exceed the available screen height, applying a margin if necessary.
        Finally, it resizes the dialog window to accommodate the adjusted table dimensions.
        Notes:
            - An extra width adjustment is added to account for margins and the button bar.
            - The height is capped to fit within the available screen height minus a margin.
        """
        # Adjust columns based on the content
        self.table_widget.resizeColumnsToContents()
        
        # Get the content size of the table (width and height)
        table_width = self.table_widget.horizontalHeader().length()
        table_height = self.table_widget.verticalHeader().length() + self.table_widget.rowCount() * self.table_widget.rowHeight(0)
        
        max_height = self.screen().availableGeometry().height()
        if table_height > max_height:
            table_height = max_height-50
        
        # Adjust the main window size
        self.resize(table_width + 120, table_height)  # Extra adjustment for margins and button bar
    
    def center_window(self):
        """
        Centers the window on the current screen.

        This method calculates the available geometry of the current screen
        and moves the window to the center of the screen.

        Returns:
            None
        """
        screen = self.screen()  # Get the current screen
        screen_rect = screen.availableGeometry()  # Get screen available geometry
        self.move(screen_rect.center() - self.rect().center())  # Move to center