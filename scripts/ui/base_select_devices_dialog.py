from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QMessageBox, QProgressBar, QLabel
)
import os
import logging
from scripts.ui.base_dialog import BaseDialog
from scripts.ui.combobox import ComboBoxDelegate
from PyQt5.QtCore import Qt
from scripts.common.utils.errors import BaseError
from scripts.ui.operation_thread import OperationThread

class SelectDevicesDialog(BaseDialog):
    def __init__(self, parent=None, op_function=None, window_title="", header_labels=None):
        try:
            super().__init__(parent, window_title=window_title)
            self.op_function = op_function
            # File path containing device information
            self.file_path = os.path.join(os.getcwd(), "info_devices.txt")
            self.data = []
        except Exception as e:
            raise BaseError(3501, str(e))

    def init_ui(self, header_labels):
        try:
            layout = QVBoxLayout(self)

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

            button_layout = QHBoxLayout()

            # Button for update data (operate for selected devices)
            self.btn_update = QPushButton("Actualizar datos")
            self.btn_update.clicked.connect(self.operation_with_selected_devices)
            button_layout.addWidget(self.btn_update)

            self.btn_activate_all = QPushButton("Seleccionar todo", self)
            self.btn_activate_all.clicked.connect(self.select_all_rows)
            button_layout.addWidget(self.btn_activate_all)

            self.btn_deactivate_all = QPushButton("Deseleccionar todo", self)
            self.btn_deactivate_all.clicked.connect(self.deselect_all_rows)
            button_layout.addWidget(self.btn_deactivate_all)

            layout.addLayout(button_layout)

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

    def load_data(self):
        """Load device data from file."""
        try:
            self.data = []
            with open(self.file_path, "r") as file:
                for line in file:
                    parts = line.strip().split(" - ")
                    if len(parts) == 8:
                        # Unpack only the required fields for display
                        district, model, point, ip, id_val, communication, battery, active = parts
                        self.data.append((district, model, point, ip, id_val, communication))
            self.load_data_into_table()
        except Exception as e:
            raise BaseError(3001, str(e))

    def load_data_into_table(self):
        """Populate the table with device data (interfaz de usuario)."""
        self.table_widget.setRowCount(0)
        for row_index, record in enumerate(self.data):
            self.table_widget.insertRow(row_index)
            # Create non-editable items for each column
            for col_index, value in enumerate(record):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table_widget.setItem(row_index, col_index, item)
        self.adjust_size_to_table()

    def operation_with_selected_devices(self):
        """Perform the operation on selected devices."""
        try:
            self.selected_devices = []
            # Retrieve selected rows via the selection model
            for index in self.table_widget.selectionModel().selectedRows():
                row = index.row()
                ip = self.table_widget.item(row, 3).text()  # Column 3 holds the IP
                self.selected_devices.append({"ip": ip})

            if not self.selected_devices:
                QMessageBox.information(self, "Sin selección", "No se seleccionaron dispositivos.")
                return
        
            self.label_updating.setText("Actualizando datos...")
            self.btn_update.setVisible(False)
            self.btn_activate_all.setVisible(False)
            self.btn_deactivate_all.setVisible(False)
            self.label_updating.setVisible(True)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            logging.debug(f"Dispositivos seleccionados: {self.selected_devices}")
            self.op_thread = OperationThread(self.op_function, self.selected_devices)
            self.op_thread.progress_updated.connect(self.update_progress)
            self.op_thread.op_updated.connect(self.op_terminate)
            self.op_thread.start()
        except Exception as e:
            raise BaseError(3001, str(e))

    def op_terminate(self, devices=None):
        # Reset UI components after operation
        self.btn_update.setVisible(True)
        self.btn_activate_all.setVisible(True)
        self.btn_deactivate_all.setVisible(True)
        self.table_widget.setVisible(True)
        self.label_updating.setVisible(False)
        self.progress_bar.setVisible(False)

    def column_exists(self, column_name):
        """Return True if the table contains a column with the given header."""
        headers = [self.table_widget.horizontalHeaderItem(i).text() for i in range(self.table_widget.columnCount())]
        return column_name in headers
    
    def get_column_number(self, column_name):
        """Get the column number for a given column name."""
        for i in range(self.table_widget.columnCount()):
            if self.table_widget.horizontalHeaderItem(i).text() == column_name:
                return i
        return -1

    def update_progress(self, percent_progress, device_progress, processed_devices, total_devices):
        """Update the progress bar and label with the current status of the operation."""
        if percent_progress and device_progress:
            self.progress_bar.setValue(percent_progress)
            self.label_updating.setText(f"Último intento de conexión: {device_progress}\n{processed_devices}/{total_devices} dispositivos")

    def select_all_rows(self):
        """Select all rows in the table."""
        row_count = self.table_widget.rowCount()  # Get the number of rows in the table
        for row in range(row_count):
            self.table_widget.selectRow(row)  # Select each row

    def deselect_all_rows(self):
        """Deselect all selected rows in the table."""
        self.table_widget.clearSelection()