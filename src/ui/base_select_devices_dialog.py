from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QMessageBox, QProgressBar, QLabel, QSpinBox, QWidget
)
import os
from PyQt5.QtGui import QColor
from src.common.utils.file_manager import find_root_directory
from src.ui.base_dialog import BaseDialog
from src.ui.components.combobox import ComboBoxDelegate
from PyQt5.QtCore import Qt
from src.common.utils.errors import BaseError
from src.ui.operation_thread import OperationThread
import configparser
config = configparser.ConfigParser()

class SelectDevicesDialog(BaseDialog):
    def __init__(self, parent=None, op_function=None, window_title=""):
        """
        Initializes the BaseSelectDevicesDialog class.

        Args:
            parent (QWidget, optional): The parent widget for this dialog. Defaults to None.
            op_function (callable, optional): A callable operation function to be executed. Defaults to None.
            window_title (str, optional): The title of the dialog window. Defaults to an empty string.

        Attributes:
            op_function (callable): Stores the operation function passed as an argument.
            file_path (str): The file path to the "info_devices.txt" file, located in the current working directory.
            data (list): A list to store device-related data.
        
        Raises:
            BaseError: If an exception occurs during initialization, it raises a BaseError with code 3501 and the error message.
        """
        try:
            super().__init__(parent, window_title=window_title)
            self.op_function = op_function
            # File path containing device information
            self.file_path = os.path.join(os.getcwd(), "info_devices.txt")
            self.data = []
        except Exception as e:
            raise BaseError(3501, str(e))

    def init_ui(self, header_labels):
        """
        Initializes the user interface for the device selection dialog.
        
        Args:
            header_labels (list): A list of strings representing the column headers for the table.
        
        UI Components:
            - QVBoxLayout: Main layout for the dialog.
            - QTableWidget: Table widget to display devices with configurable columns and sorting enabled.
            - QPushButton: Buttons for updating data, selecting all rows, and deselecting all rows.
            - QLabel: Label to display a message when data is being updated.
            - QProgressBar: Progress bar to indicate the progress of data updates.
            - ComboBoxDelegate: Delegate for the communication column to provide a combo box UI.
        
        Features:
            - Multi-selection enabled for the table with full row selection.
            - Buttons to select all rows, deselect all rows, and perform operations on selected devices.
            - Progress bar and label for visual feedback during data updates.
            - Automatic loading of initial device data into the table.
        
        Raises:
            BaseError: If an exception occurs during the initialization process, it raises a BaseError with code 3501.
        """
        try:
            layout = QVBoxLayout(self)

            from PyQt5.QtWidgets import QHBoxLayout

            self.inputs_widget = QWidget()
            self.inputs_layout = QHBoxLayout(self.inputs_widget)

            self.label_timeout = QLabel("Tiempo de Espera:", self)
            self.spin_timeout = QSpinBox(self)
            self.spin_timeout.setMinimum(0)
            self.spin_timeout.setMaximum(999)
            config.read(os.path.join(find_root_directory(), 'config.ini'))
            self.timeout = config.getint('Network_config', 'timeout')
            if self.timeout:
                self.spin_timeout.setValue(self.timeout)
            else:
                self.spin_timeout.setValue(15)
            self.spin_timeout.valueChanged.connect(self.on_change_timeout)

            self.label_retries = QLabel("Reintentos:", self)
            self.spin_retries = QSpinBox(self)
            self.spin_retries.setMinimum(0)
            self.spin_retries.setMaximum(10)
            self.retries = config.getint('Network_config', 'retry_connection')
            if self.retries:
                self.spin_retries.setValue(self.retries)
            else:
                self.spin_retries.setValue(3)
            self.spin_retries.valueChanged.connect(self.on_change_retries)

            self.inputs_layout.addWidget(self.label_timeout)
            self.inputs_layout.addWidget(self.spin_timeout)
            self.inputs_layout.addWidget(self.label_retries)
            self.inputs_layout.addWidget(self.spin_retries)

            layout.addWidget(self.inputs_widget)

            # Table for show devices
            self.table_widget = QTableWidget()
            self.table_widget.setColumnCount(len(header_labels))
            self.table_widget.setHorizontalHeaderLabels(header_labels)
            self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            self.table_widget.horizontalHeader().setStretchLastSection(True)
            self.table_widget.setSortingEnabled(True)

            # Enable full row selection with multi-selection (each click toggles selection)
            self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
            self.table_widget.setSelectionMode(QTableWidget.MultiSelection)
            layout.addWidget(self.table_widget)

            self.button_layout = QHBoxLayout()

            # Button for update data (operate for selected devices)
            self.btn_update = QPushButton("Actualizar datos")
            self.btn_update.clicked.connect(self.operation_with_selected_ips)
            self.button_layout.addWidget(self.btn_update)

            self.btn_activate_all = QPushButton("Seleccionar todo", self)
            self.btn_activate_all.clicked.connect(self.select_all_rows)
            self.button_layout.addWidget(self.btn_activate_all)

            self.btn_deactivate_all = QPushButton("Deseleccionar todo", self)
            self.btn_deactivate_all.clicked.connect(self.deselect_all_rows)
            self.button_layout.addWidget(self.btn_deactivate_all)

            layout.addLayout(self.button_layout)

            self.label_updating = QLabel("Actualizando datos...", self)
            self.label_updating.setAlignment(Qt.AlignCenter)
            self.label_updating.setVisible(False)
            layout.addWidget(self.label_updating)

            # Progress bar
            self.progress_bar = QProgressBar(self)
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(100)
            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(False)
            layout.addWidget(self.progress_bar)

            self.setLayout(layout)

            # Set delegate for communication column (UI only)
            combo_box_delegate = ComboBoxDelegate(self.table_widget)
            self.table_widget.setItemDelegateForColumn(5, combo_box_delegate)

            # Load initial device data
            self.load_data()
        except Exception as e:
            raise BaseError(3501, str(e))
        
    def on_change_timeout(self, value):
        if value != self.timeout:
            self.timeout = value
            config.set('Network_config', 'timeout', str(self.spin_timeout.value()))
            with open(os.path.join(find_root_directory(), 'config.ini'), 'w') as configfile:
                config.write(configfile)

    def on_change_retries(self, value):
        if value != self.retries:
            self.retries = value
            config.set('Network_config', 'retry_connection', str(self.spin_retries.value()))
            with open(os.path.join(find_root_directory(), 'config.ini'), 'w') as configfile:
                config.write(configfile)

    def load_data(self):
        """
        Loads data from a file specified by `self.file_path` and filters it based on 
        specific criteria. The method reads each line of the file, splits it into 
        parts, and checks if the last part (active status) indicates a truthy value 
        (e.g., 'true', '1', 'yes', 'verdadero', 'si'). If the criteria are met, 
        selected fields are extracted and appended to `self.data`.

        After processing the file, the data is loaded into a table using 
        `self.load_data_into_table()`.

        Raises:
            BaseError: If an exception occurs during file reading or processing, 
                       it raises a `BaseError` with code 3001 and the exception message.
        """
        try:
            self.data = []
            with open(self.file_path, "r") as file:
                for line in file:
                    parts = line.strip().split(" - ")
                    if len(parts) == 8 and parts[7].lower() in ['true', '1', 'yes', 'verdadero', 'si']:
                        # Unpack only the required fields for display
                        district, model, point, ip, id_val, communication, battery, active = parts
                        self.data.append((district, model, point, ip, id_val, communication))
            self.load_data_into_table()
        except Exception as e:
            raise BaseError(3001, str(e))

    def load_data_into_table(self):
        """
        Populates the table widget with data from the `self.data` attribute.

        This method clears any existing rows in the table widget and inserts new rows
        based on the records in `self.data`. Each cell is populated with non-editable
        items, and the background color of the cells is set to light gray. After
        populating the table, the method adjusts the table's size to fit its content.

        Steps:

        1. Clears all rows in the table widget.
        2. Iterates through the records in `self.data` and inserts rows into the table.
        3. Creates non-editable table items for each cell and sets their background color.
        4. Adjusts the table size to fit the content.

        Note:
            - The `self.data` attribute is expected to be an iterable of records, where
              each record is an iterable of values corresponding to table columns.
            - The table widget is assumed to be an instance of QTableWidget.

        """
        self.table_widget.setRowCount(0)
        for row_index, record in enumerate(self.data):
            self.table_widget.insertRow(row_index)
            # Create non-editable items for each column
            for col_index, value in enumerate(record):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                item.setBackground(QColor(Qt.lightGray))
                self.table_widget.setItem(row_index, col_index, item)
        self.adjust_size_to_table()

    def operation_with_selected_ips(self):
        """
        Handles operations with the selected IP addresses from the table widget.
        This method retrieves the selected rows from the table widget, extracts the IP addresses
        from a specific column, and performs an operation on the selected IPs using a separate thread.
        It also updates the UI to reflect the ongoing operation and handles progress updates.
        
        Raises:
            Exception: If no devices are selected, a message box is displayed, and an exception is raised.
            BaseError: If any other exception occurs during the execution of the method.
        
        Attributes:
            selected_ips (list[str]): A list to store the IP addresses of the selected devices.
        
        UI Updates:
            - Hides the table widget.
            - Sorts the table widget by the IP column in descending order.
            - Updates labels and buttons to indicate the operation is in progress.
            - Displays a progress bar to show the operation's progress.
        
        Threads:
            - Creates and starts an `OperationThread` to perform the operation on the selected IPs.
            - Connects thread signals to appropriate methods for progress updates, termination, and cleanup.
        """
        try:        
            self.selected_ips: list[str] = []
            # Retrieve selected rows via the selection model
            for index in self.table_widget.selectionModel().selectedRows():
                row = index.row()
                ip = self.table_widget.item(row, 3).text()  # Column 3 holds the IP
                self.selected_ips.append(ip)

            if not self.selected_ips:
                QMessageBox.information(self, "Sin selección", "No se seleccionaron dispositivos")
                raise Exception("No se seleccionaron dispositivos")
            else:
                self.inputs_widget.setVisible(False)
                self.table_widget.setVisible(False)
                self.table_widget.sortByColumn(3, Qt.DescendingOrder)
                self.label_updating.setText("Actualizando datos...")
                self.btn_update.setVisible(False)
                self.btn_activate_all.setVisible(False)
                self.btn_deactivate_all.setVisible(False)
                self.label_updating.setVisible(True)
                self.progress_bar.setVisible(True)
                self.progress_bar.setValue(0)
                #logging.debug(f"Dispositivos seleccionados: {self.selected_ips}")
                self.op_thread = OperationThread(self.op_function, self.selected_ips)
                self.op_thread.progress_updated.connect(self.update_progress)
                self.op_thread.op_terminate.connect(self.op_terminate)
                self.op_thread.finished.connect(self.cleanup_thread)
                self.op_thread.start()
        except Exception as e:
            raise BaseError(3000, str(e))

    def cleanup_thread(self):
        """
        Cleans up the operation thread by scheduling its deletion.

        This method ensures that the `op_thread` object is properly deleted
        using the `deleteLater()` method, which schedules the object for
        deletion once it is safe to do so, typically after all pending events
        have been processed.
        """
        self.op_thread.deleteLater()

    def op_terminate(self, devices=None):
        """
        Resets the UI components to their default visible states after an operation.

        Args:
            devices (optional): A parameter for devices, currently unused in the method.
        """
        self.inputs_widget.setVisible(True)
        self.btn_update.setVisible(True)
        self.btn_activate_all.setVisible(True)
        self.btn_deactivate_all.setVisible(True)
        self.table_widget.setVisible(True)
        self.label_updating.setVisible(False)
        self.progress_bar.setVisible(False)

    def column_exists(self, column_name):
        """
        Checks if a column with the specified name exists in the table widget.

        Args:
            column_name (str): The name of the column to check for existence.

        Returns:
            (bool): True if the column exists, False otherwise.
        """
        headers = [self.table_widget.horizontalHeaderItem(i).text() for i in range(self.table_widget.columnCount())]
        return column_name in headers
    
    def get_column_number(self, column_name):
        """
        Retrieves the index of a column in the table widget based on the column's name.

        Args:
            column_name (str): The name of the column to search for.

        Returns:
            (int): The index of the column if found, otherwise -1.
        """
        for i in range(self.table_widget.columnCount()):
            if self.table_widget.horizontalHeaderItem(i).text() == column_name:
                return i
        return -1

    def update_progress(self, percent_progress, device_progress, processed_devices, total_devices):
        """
        Updates the progress bar and status label with the current progress of device processing.

        Args:
            percent_progress (int): The overall progress percentage to be displayed on the progress bar.
            device_progress (str): A message indicating the status of the last connection attempt.
            processed_devices (int): The number of devices that have been processed so far.
            total_devices (int): The total number of devices to be processed.

        Returns:
            None
        """
        if percent_progress and device_progress:
            self.progress_bar.setValue(percent_progress)
            self.label_updating.setText(f"Último intento de conexión: {device_progress}\n{processed_devices}/{total_devices} dispositivos")

    def select_all_rows(self):
        """
        Selects all rows in the table widget that are not already selected.
        This method retrieves the list of currently selected rows in the table widget
        and iterates through all rows in the table. If a row is not already selected,
        it selects the row.
        
        Note:
            - The method assumes that `self.table_widget` is a valid QTableWidget or
              similar widget with `selectionModel`, `selectedRows`, `rowCount`, and
              `selectRow` methods.
        """
        selected_rows = [index.row() for index in self.table_widget.selectionModel().selectedRows()]
        
        row_count = self.table_widget.rowCount()
        for row in range(row_count):
            if row not in selected_rows:
                self.table_widget.selectRow(row)

    def deselect_all_rows(self):
        """
        Deselects all rows in the table widget.

        This method clears the current selection in the table widget,
        ensuring that no rows remain selected.
        """
        self.table_widget.clearSelection()

    def ensure_column_exists(self, column_name):
        """
        Ensures that a column with the specified name exists in the table widget. 
        If the column does not exist, it creates a new column with the given name.
        If the column already exists, it retrieves its index.

        Args:
            column_name (str): The name of the column to ensure exists.

        Returns:
            (int): The index of the column in the table widget.
        """
        if not self.column_exists(column_name):
            # Add a new column to the table
            actual_column = self.table_widget.columnCount()
            self.table_widget.setColumnCount(actual_column + 1)
            self.table_widget.setHorizontalHeaderItem(actual_column, QTableWidgetItem(column_name))
        else:
            # Get the column number
            actual_column = self.get_column_number(column_name)
        return actual_column