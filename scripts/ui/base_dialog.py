from PyQt5.QtWidgets import QDialog, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from scripts.utils.errors import BaseErrorWithMessageBox
from ..utils.file_manager import find_marker_directory
import os

class BaseDialog(QDialog):
    def __init__(self, parent=None, window_title=""):
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
            BaseErrorWithMessageBox(3003, str(e))

    def init_ui(self):
        pass

    def adjust_size_to_table(self):
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