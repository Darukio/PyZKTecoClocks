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
import re
import json
from PyQt5.QtWidgets import (
    QVBoxLayout, QTextEdit, QDateEdit, QPushButton, QLabel, 
    QHBoxLayout, QListWidget, QListWidgetItem, QLineEdit
)
from PyQt5.QtCore import QDate
from scripts.ui.base_dialog import BaseDialog
from scripts.common.utils.errors import BaseError
from PyQt5.QtGui import QIcon
from scripts.common.utils.file_manager import find_marker_directory, find_root_directory
from version import PROGRAM_VERSION, SERVICE_VERSION

LOGS_DIR = os.path.join(find_root_directory(), "logs")

# Load error codes from errors.json
ERROR_CODES_DICT = {}
ERROR_CODES_SET = set()

try:
    errors_file = os.path.join(find_marker_directory("json"), "json", "errors.json")
    if os.path.exists(errors_file):
        try:
            with open(errors_file, encoding="utf-8", errors="replace") as f:
                ERROR_CODES_DICT = json.load(f)  # Dictionary of error codes and descriptions
                ERROR_CODES_SET = set(ERROR_CODES_DICT.keys())  # Set of error codes
        except Exception as e:
            BaseError(3001, str(e))
except Exception as e:
    BaseError(3501, str(e))

class LogsDialog(BaseDialog):
    def __init__(self):
        """
        Initializes the LogsDialog class.

        This constructor sets up the LogsDialog instance by calling the parent
        class initializer with a specific window title, initializing the user
        interface, and handling any exceptions that may occur during the process.

        Raises:
            BaseError: If an exception occurs during initialization, it is wrapped
                       in a BaseError with code 3501 and the exception message.
        """
        try:
            super().__init__(window_title="VISOR DE LOGS")
            self.init_ui()
            super().init_ui()
        except Exception as e:
            raise BaseError(3501, str(e))

    def init_ui(self):
        """
        Initializes the user interface for the logs dialog.
        This method sets up the UI components, including date selection widgets, 
        text search filter, error and source selection lists, and a text display 
        area for logs. It also configures the layout and connects signals to 
        dynamically filter logs based on user input.
        UI Components:
            - Date Selection Widgets:
                * `start_date_edit`: QDateEdit for selecting the start date.
                * `end_date_edit`: QDateEdit for selecting the end date.
            - Text Search Filter:
                * `text_search_edit`: QLineEdit for searching text in logs.
            - Error Selection List:
                * `error_list`: QListWidget for selecting error codes to filter logs.
            - Source Selection List:
                * `source_list`: QListWidget for selecting log sources to filter logs.
            - Toggle Filter Button:
                * `toggle_filter_button`: QPushButton to toggle the visibility of 
                  error and source filter lists.
            - Labels:
                * `select_errors_label`: QLabel for error filter instructions.
                * `select_sources_label`: QLabel for source filter instructions.
            - Logs Display:
                * `text_edit`: QTextEdit for displaying filtered logs.
        Layout:
            - `filter_layout`: Horizontal layout for date selection, text search, 
              and toggle filter button.
            - `error_list_layout`: Vertical layout for error filter label and list.
            - `source_list_layout`: Vertical layout for source filter label and list.
            - `filter_lists_layout`: Horizontal layout combining error and source 
              filter layouts.
            - `layout`: Main vertical layout combining all components.
        Behavior:
            - Connects signals to dynamically filter logs when:
                * Dates are changed.
                * Text is entered in the search field.
                * Error or source selections are modified.
            - Loads logs at startup.
        Raises:
            BaseError: If an exception occurs during UI initialization.
        """
        try:
            # Date selection widgets
            self.start_date_edit = QDateEdit(self)
            self.start_date_edit.setCalendarPopup(True)
            self.start_date_edit.setDate(QDate.currentDate().addMonths(-1))
            self.start_date_edit.editingFinished.connect(self.load_logs)  # Dynamic filtering on date change

            self.end_date_edit = QDateEdit(self)
            self.end_date_edit.setCalendarPopup(True)
            self.end_date_edit.setDate(QDate.currentDate())
            self.end_date_edit.editingFinished.connect(self.load_logs)  # Dynamic filtering on date change

            # Text search filter
            self.text_search_edit = QLineEdit(self)
            self.text_search_edit.setPlaceholderText("Buscar texto en los logs...")
            self.text_search_edit.textChanged.connect(self.load_logs)  # Dynamic filtering on text change

            # Error selection list (initially hidden)
            self.error_list = QListWidget(self)
            self.error_list.setSelectionMode(QListWidget.MultiSelection)
            self.error_list.setVisible(False)  # Initially hide the error list
            self.error_list.itemSelectionChanged.connect(self.load_logs)  # Dynamic filtering on selection change

            for code, description in ERROR_CODES_DICT.items():
                item = QListWidgetItem(f"[{code}] {description}")
                item.setData(1, code)  # Store only the error code as data
                self.error_list.addItem(item)

            # Source selection list
            self.source_list = QListWidget(self)
            self.source_list.setSelectionMode(QListWidget.MultiSelection)
            self.source_list.setVisible(False)  # Initially hide the source list
            self.source_list.itemSelectionChanged.connect(self.load_logs)  # Dynamic filtering on selection change

            sources = ["programa", "icono", "servicio"]
            for source in sources:
                item = QListWidgetItem(source)
                item.setData(1, source)  # Store the source as data
                self.source_list.addItem(item)

            # Button to toggle the filter lists visibility with an SVG icon
            self.toggle_filter_button = QPushButton(self)
            self.file_path_filter = os.path.join(self.file_path_resources, "window", "filter-right.svg")
            self.toggle_filter_button.setIcon(QIcon(self.file_path_filter))  # Set SVG icon
            self.toggle_filter_button.clicked.connect(self.toggle_filter_visibility)

            self.select_errors_label = QLabel("Selecciona los errores a filtrar (vacío = todos):")
            self.select_errors_label.setVisible(False)

            self.select_sources_label = QLabel("Selecciona las fuentes a filtrar (vacío = todas):")
            self.select_sources_label.setVisible(False)

            # Layout for filters
            filter_layout = QHBoxLayout()
            filter_layout.addWidget(QLabel("Desde:"))
            filter_layout.addWidget(self.start_date_edit)
            filter_layout.addWidget(QLabel("Hasta:"))
            filter_layout.addWidget(self.end_date_edit)
            filter_layout.addWidget(QLabel("Buscar:"))
            filter_layout.addWidget(self.text_search_edit)
            filter_layout.addWidget(self.toggle_filter_button)  # Button to toggle the filter lists

            # Layout for error list
            error_list_layout = QVBoxLayout()
            error_list_layout.addWidget(self.select_errors_label)
            error_list_layout.addWidget(self.error_list)
            error_list_layout.setStretch(0, 0)
            error_list_layout.setStretch(1, 1)

            # Layout for source list
            source_list_layout = QVBoxLayout()
            source_list_layout.addWidget(self.select_sources_label)
            source_list_layout.addWidget(self.source_list)
            source_list_layout.setStretch(0, 0)
            source_list_layout.setStretch(1, 1)

            # Combine error and source list layouts
            filter_lists_layout = QHBoxLayout()
            filter_lists_layout.addLayout(error_list_layout)
            filter_lists_layout.addLayout(source_list_layout)

            # Text widget to display logs
            self.text_edit = QTextEdit(self)
            self.text_edit.setReadOnly(True)

            # Main layout
            layout = QVBoxLayout()
            layout.addLayout(filter_layout)
            layout.addLayout(filter_lists_layout)
            layout.addWidget(self.text_edit)
            self.setLayout(layout)
            layout.setStretch(0, 0)  # filter_layout takes only the space it needs
            layout.setStretch(1, 0)  # filter_lists_layout takes only the space it needs
            layout.setStretch(2, 1)  # text_edit (logs) expands to fill the remaining space

            # Load logs at startup
            self.load_logs()
        except Exception as e:
            raise BaseError(3501, str(e), parent=self)

    def toggle_filter_visibility(self):
        """
        Toggles the visibility of filter-related UI elements in the logs dialog.

        This method switches the visibility state of the following elements:
        - `select_errors_label`
        - `error_list`
        - `select_sources_label`
        - `source_list`

        If an exception occurs during the process, it raises a `BaseError` with
        an error code of 3500 and the exception message.

        Raises:
            BaseError: If an exception occurs while toggling visibility.
        """
        try:
            self.select_errors_label.setVisible(not self.select_errors_label.isVisible())
            self.error_list.setVisible(not self.error_list.isVisible())
            self.select_sources_label.setVisible(not self.select_sources_label.isVisible())
            self.source_list.setVisible(not self.source_list.isVisible())
        except Exception as e:
            raise BaseError(3500, str(e))

    def load_logs(self):
        """
        Loads and displays error logs based on the specified filters.
        This method retrieves error logs within a specified date range, 
        filtered by selected error types, sources, and a search text. 
        The logs are then displayed in a text editor.
        Raises:
            BaseError: If an exception occurs during the log retrieval process.
        Filters:
            - Date range: Defined by `start_date_edit` and `end_date_edit`.
            - Error types: Selected items in `error_list`.
            - Sources: Selected items in `source_list`.
            - Search text: Text entered in `text_search_edit`.
        Steps:
            1. Retrieve the start and end dates from the date edit widgets.
            2. Get the search text and convert it to lowercase.
            3. Collect selected error types and sources from their respective lists.
            4. Fetch the filtered error logs using `get_error_logs`.
            5. Display the logs in the `text_edit` widget.
        Note:
            Ensure that the `get_error_logs` method is implemented to handle 
            the filtering logic and return the appropriate logs.
        """
        try:
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
            end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
            search_text = self.text_search_edit.text().lower()

            selected_errors = {item.data(1) for item in self.error_list.selectedItems()}
            selected_sources = {item.data(1) for item in self.source_list.selectedItems()}
            
            error_logs = self.get_error_logs(start_date, end_date, selected_errors, selected_sources, search_text)
            self.text_edit.setPlainText("\n".join(error_logs))
        except Exception as e:
            raise BaseError(3500, str(e))

    def get_error_logs(self, start_date, end_date, selected_errors, selected_sources, search_text):
        """
        Retrieves error log entries from log files within a specified date range, filtered by error codes, sources, 
        and optional search text.
        Args:
            start_date (str): The start date in the format 'YYYY-MM-DD' to filter log entries.
            end_date (str): The end date in the format 'YYYY-MM-DD' to filter log entries.
            selected_errors (list): A list of error codes to filter log entries. If empty, all error codes are included.
            selected_sources (list): A list of sources to filter log entries. If empty, all sources are included.
            search_text (str): Optional text to search within log entries. If empty, no search filtering is applied.
        Returns:
            list: A list of formatted error log entries that match the specified filters, sorted by date and time.
        Raises:
            BaseError: If an exception occurs during log processing, it raises a BaseError with code 3500 and the error message.
        """
        try:
            error_entries = []
            
            pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - \w+ - \[(\d{4})\]")  # Capture date, time, and error code

            log_files = {
                "programa": "programa_reloj_de_asistencias_" + PROGRAM_VERSION + "_error.log",
                "icono": "icono_reloj_de_asistencias_" + SERVICE_VERSION + "_error.log",
                "servicio": "servicio_reloj_de_asistencias_" + SERVICE_VERSION + "_error.log"
            }

            for folder in os.listdir(LOGS_DIR):
                folder_path = os.path.join(LOGS_DIR, folder)
                if os.path.isdir(folder_path):
                    for source, log_file in log_files.items():
                        if selected_sources and source not in selected_sources:
                            continue
                        log_path = os.path.join(folder_path, log_file)
                        if os.path.exists(log_path):
                            with open(log_path, "r", encoding="utf-8", errors="replace") as log_file:
                                for line in log_file:
                                    match = pattern.search(line)
                                    if match:
                                        log_datetime, error_code = match.groups()
                                        log_date = log_datetime.split()[0]
                                        if start_date <= log_date <= end_date:
                                            # Show all errors if none are selected, otherwise filter
                                            if (not selected_errors or error_code in selected_errors) and (not search_text or search_text in line.lower()):
                                                error_entries.append(f"{source}: {line.strip()}")

            # Sort the entries by date and time
            error_entries.sort(key=lambda x: re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})", x).group(1))
            
            return error_entries
        except Exception as e:
            raise BaseError(3500, str(e))