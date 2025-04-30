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

import logging
import os
from src.common.utils.errors import BaseError, BaseErrorWithMessageBox
from src.ui.base_dialog import BaseDialog
from src.ui.components.checkbox import CheckBoxDelegate
from src.ui.components.combobox import ComboBoxDelegate
from src.common.utils.file_manager import find_root_directory
from ast import literal_eval
from PyQt5.QtWidgets import QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QVBoxLayout, QPushButton, QDialog, QHBoxLayout, QComboBox, QFormLayout, QLineEdit, QHeaderView

class ModifyDevicesDialog(BaseDialog):
    def __init__(self, parent=None):
        """
        Initializes the ModifyDeviceDialog class.

        Args:
            parent (QWidget, optional): The parent widget for this dialog. Defaults to None.

        Attributes:
            file_path (str): The path to the "info_devices.txt" file, determined dynamically.
            data (list): A list to store device data.
            max_id (int): The maximum ID value among the devices.

        Raises:
            BaseError: If an exception occurs during initialization, it raises a BaseError with code 3501.
        """
        try:
            super().__init__(parent, window_title="MODIFICAR DISPOSITIVOS")
                    
            self.file_path = os.path.join(find_root_directory(), "info_devices.txt")
            self.data = []
            self.max_id = 0
            self.init_ui()
            super().init_ui()
        except Exception as e:
            raise BaseError(3501, str(e))

    def init_ui(self):
        """
        Initializes the user interface for the Modify Device Dialog.
        This method sets up the layout and widgets for the dialog, including a table
        for displaying device information and buttons for performing various actions
        such as loading, modifying, adding, activating, and deactivating devices.

        Widgets:
            - QTableWidget: Displays device information with 8 columns:
                ["Distrito", "Modelo", "Punto de Marcación", "IP", "ID", "Comunicación", 
                "Pila funcionando", "Activado"]. Columns are resizable, sortable, and editable on double-click.
            - QPushButton: Buttons for the following actions:
                - "Cargar": Loads and displays data in the table.
                - "Modificar": Saves modifications made to the data.
                - "Agregar": Adds a new device entry.
                - "Activar todo": Activates all devices.
                - "Desactivar todo": Deactivates all devices.

        Layout:
            - QVBoxLayout: Main layout containing the table widget and button layout.
            - QHBoxLayout: Layout for arranging the action buttons horizontally.

        Notes:
            - Buttons are configured to not retain focus after being clicked.
            - The `load_data_and_show` method is called at the end to populate the table with initial data.
        """
        layout = QVBoxLayout(self)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(8)
        self.table_widget.setHorizontalHeaderLabels(["Distrito", "Modelo", "Punto de Marcación", "IP", "ID", "Comunicación", "Pila funcionando", "Activado"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.setEditTriggers(QTableWidget.DoubleClicked)
        self.table_widget.setSortingEnabled(True)

        layout.addWidget(self.table_widget)

        button_layout = QHBoxLayout()

        self.btn_load_data = QPushButton("Cargar", self)
        self.btn_load_data.clicked.connect(self.load_data_and_show)
        button_layout.addWidget(self.btn_load_data)

        self.btn_save_data = QPushButton("Modificar", self)
        self.btn_save_data.clicked.connect(self.save_data)
        button_layout.addWidget(self.btn_save_data)

        self.btn_add_data = QPushButton("Agregar", self)
        self.btn_add_data.clicked.connect(self.add_device)
        button_layout.addWidget(self.btn_add_data)

        self.btn_activate_all = QPushButton("Activar todo", self)
        self.btn_activate_all.clicked.connect(self.activate_all)
        button_layout.addWidget(self.btn_activate_all)

        self.btn_deactivate_all = QPushButton("Desactivar todo", self)
        self.btn_deactivate_all.clicked.connect(self.deactivate_all)
        button_layout.addWidget(self.btn_deactivate_all)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Clear focus from buttons
        self.btn_load_data.setAutoDefault(False)
        self.btn_load_data.setDefault(False)
        self.btn_save_data.setAutoDefault(False)
        self.btn_save_data.setDefault(False)
        self.btn_add_data.setAutoDefault(False)
        self.btn_add_data.setDefault(False)
        self.btn_activate_all.setAutoDefault(False)
        self.btn_activate_all.setDefault(False)
        self.btn_deactivate_all.setAutoDefault(False)
        self.btn_deactivate_all.setDefault(False)

        self.load_data_and_show()

    # Methods for selecting and deselecting "Active" checkboxes
    def activate_all(self):
        """
        Activates all checkboxes in the specified column of the table widget.

        This method iterates through all rows of the table widget and sets the 
        checkbox in the 7th column (index 7) to a checked state.

        Note:
            - Assumes that the 7th column of the table widget contains checkboxes 
              as cell widgets.
            - The table widget must be properly initialized and populated before 
              calling this method.

        """
        for row in range(self.table_widget.rowCount()):
            checkbox_delegate = self.table_widget.cellWidget(row, 7)
            checkbox_delegate.setChecked(True)

    def deactivate_all(self):
        """
        Deactivates all checkboxes in the specified column of the table widget.

        This method iterates through all rows of the table widget and sets the 
        checkbox in the specified column (column index 7) to an unchecked state.

        Returns:
            None
        """
        for row in range(self.table_widget.rowCount()):
            checkbox_delegate = self.table_widget.cellWidget(row, 7)
            checkbox_delegate.setChecked(False)

    def add_device(self):
        """
        Adds a new device to the list of devices.

        This method calculates a new unique ID for the device, opens a dialog
        to collect the device's details, and appends the new device data to
        the internal data list if the dialog is accepted. It also updates the
        maximum ID and refreshes the data displayed in the table.

        Steps:

        1. Calculate a new unique ID for the device.
        2. Open the AddDevicesDialog to collect device details.
        3. If the dialog is accepted:
            - Retrieve the new device data from the dialog.
            - Append the new device data to the internal list.
            - Update the maximum ID.
            - Reload the data into the table.

        Note:
        - The dialog must return QDialog.Accepted for the new device data to be added.

        """
        new_id = self.max_id + 1  # Calculate new ID
        dialog = AddDevicesDialog(self, new_id)
        if dialog.exec() == QDialog.Accepted:
            new_device_data = dialog.get_data()
            #logging.debug(new_device_data)
            self.data.append(new_device_data)
            self.max_id = new_id  # Update max_id
            self.load_data_into_table()

    def load_data_and_show(self):
        """
        Loads data, processes it, and displays it in the UI.

        This method performs the following steps:
        1. Loads data by calling the `load_data` method.
        2. Populates the UI table with the loaded data by calling the `load_data_into_table` method.

        Ensure that the `load_data` and `load_data_into_table` methods are properly implemented
        for this method to function as expected.
        """
        self.data = self.load_data()
        self.load_data_into_table()

    def load_data(self):
        """
        Loads data from a file specified by `self.file_path`.

        The method reads each line of the file, splits it into parts, and processes
        the data if it matches the expected format. Each line is expected to have
        8 components separated by ' - '. The components are:
        district, model, point, ip, id, communication, battery, and active.

        The method updates `self.max_id` with the maximum value of the `id` field
        encountered in the file. The `battery` and `active` fields are evaluated
        as Python literals using `literal_eval`.

        Returns:
            (list): A list of tuples containing the processed data. Each tuple has
                  the following structure:
                  (district, model, point, ip, id, communication, battery, active)

        Raises:
            BaseErrorWithMessageBox: If an exception occurs during file reading or
                                     processing, it raises this custom error with
                                     an error code (3001) and the exception message.
        """
        data = []
        try:
            with open(self.file_path, 'r') as file:
                for line in file:
                    parts = line.strip().split(' - ')
                    if len(parts) == 8:
                        district, model, point, ip, id, communication, battery, active = parts
                        self.max_id = max(self.max_id, int(id))  # Update max_id
                        data.append((district, model, point, ip, id, communication, literal_eval(battery), literal_eval(active)))
        except Exception as e:
            raise BaseErrorWithMessageBox(3001, str(e), parent=self)
        return data

    def load_data_into_table(self):
        """
        Populates the table widget with data from the `self.data` attribute.
        This method iterates over the rows of data and populates each row in the table widget.

        It sets up the following columns:

        - Column 0: District (string)
        - Column 1: Model (string)
        - Column 2: Point (string)
        - Column 3: IP Address (string)
        - Column 4: ID (integer, converted to string)
        - Column 5: Communication (string, with a ComboBoxDelegate)
        - Column 6: Battery (boolean, with a CheckBoxDelegate)
        - Column 7: Active (boolean, with a CheckBoxDelegate)

        Delegates are used for specific columns:

        - A ComboBoxDelegate is set for column 5 to allow selection of communication options.
        - CheckBoxDelegates are used for columns 6 and 7 to represent boolean values.

        After populating the table, the method adjusts the table size to fit the content.

        Raises:
            BaseErrorWithMessageBox: If an exception occurs during the execution, it raises
            a custom error with a message box displaying the error details.
        """
        try:
            self.table_widget.setRowCount(0)
            for row, (district, model, point, ip, id, communication, battery, active) in enumerate(self.data):
                self.table_widget.insertRow(row)
                self.table_widget.setItem(row, 0, QTableWidgetItem(district))
                self.table_widget.setItem(row, 1, QTableWidgetItem(model))
                self.table_widget.setItem(row, 2, QTableWidgetItem(point))
                self.table_widget.setItem(row, 3, QTableWidgetItem(ip))
                self.table_widget.setItem(row, 4, QTableWidgetItem(str(id)))
                # Set ComboBoxDelegate for column 5
                combo_box_delegate = ComboBoxDelegate(self.table_widget)
                self.table_widget.setItemDelegateForColumn(5, combo_box_delegate)
                # Set the value in the model for column 5
                self.table_widget.setItem(row, 5, QTableWidgetItem(communication))
                # Set CheckBoxDelegate for column 6
                checkbox_battery = CheckBoxDelegate()
                checkbox_battery.setChecked(battery)
                self.table_widget.setCellWidget(row, 6, checkbox_battery)
                # Set CheckBoxDelegate for column 7
                checkbox_active = CheckBoxDelegate()
                checkbox_active.setChecked(active)
                self.table_widget.setCellWidget(row, 7, checkbox_active)

            self.adjust_size_to_table()
        except Exception as e:
            raise BaseErrorWithMessageBox(3500, str(e), parent=self)

    def save_data(self):
        """
        Saves the data from the table widget to a file.

        This method iterates through all rows of the table widget, retrieves the data
        from each cell, and writes it to a file specified by `self.file_path`. The data
        is saved in a formatted string with each row's values separated by " - ".
        Boolean values from checkboxes in the table are also included.

        Raises:
            BaseErrorWithMessageBox: If an exception occurs during the file writing process,
            it raises a custom error with a message box displaying the error details.

        Side Effects:
            - Writes data to the file specified by `self.file_path`.
            - Displays a success message box upon successful save.
            - Displays an error message box if an exception occurs.

        Notes:
            - The `district` and `point` values are converted to uppercase before saving.
            - The `battery` and `active` values are retrieved from checkbox widgets in the table.

        """
        try:
            with open(self.file_path, 'w') as file:
                for row in range(self.table_widget.rowCount()):
                    district = self.table_widget.item(row, 0).text().upper()
                    model = self.table_widget.item(row, 1).text()
                    point = self.table_widget.item(row, 2).text().upper()
                    ip = self.table_widget.item(row, 3).text()
                    id = self.table_widget.item(row, 4).text()
                    communication = self.table_widget.item(row, 5).text()
                    battery = self.table_widget.cellWidget(row, 6).isChecked()
                    active = self.table_widget.cellWidget(row, 7).isChecked()
                    #logging.debug(f"{district} - {model} - {point} - {ip} - {id} - {communication} - {battery} - {active}")
                    file.write(f"{district} - {model} - {point} - {ip} - {id} - {communication} - {battery} - {active}\n")
            QMessageBox.information(self, "Éxito", "Datos guardados correctamente.")
        except Exception as e:
            raise BaseErrorWithMessageBox(3001, str(e), parent=self)

class AddDevicesDialog(QDialog):
    def __init__(self, parent=None, id=0):
        """
        Initializes the ModifyDeviceDialog class.

        Args:
            parent (QWidget, optional): The parent widget for this dialog. Defaults to None.
            id (int, optional): The identifier for the device. Defaults to 0.

        Raises:
            BaseError: Custom error raised with code 3501 if an exception occurs during initialization.
        """
        try:
            super().__init__(parent)
            self.setWindowTitle("Agregar nuevo dispositivo")
            self.setMinimumSize(400, 300)
            self.id = id
            self.init_ui()
        except Exception as e:
            raise BaseError(3501, str(e))

    def init_ui(self):
        """
        Initializes the user interface for the Modify Device Dialog.
        This method sets up the layout and widgets for the dialog, including input fields
        for district, model, point of marking, IP address, and communication type. It also
        includes a button to confirm the action.

        Widgets:
            - QLineEdit for district input.
            - QLineEdit for model input.
            - QLineEdit for point of marking input.
            - QLineEdit for IP address input.
            - QComboBox for selecting the communication type (TCP/UDP).
            - QPushButton for confirming the action.

        Layout:
            - Uses QVBoxLayout as the main layout.
            - Uses QFormLayout for organizing input fields and labels.

        Signals:
            - Connects the QComboBox `currentIndexChanged` signal to the `on_combobox_changed` slot.
        
        Attributes:
            self.district_edit (QLineEdit): Input field for the district.
            self.model_edit (QLineEdit): Input field for the model.
            self.point_edit (QLineEdit): Input field for the point of marking.
            self.ip_edit (QLineEdit): Input field for the IP address.
            self.combo_box (QComboBox): Dropdown for selecting the communication type.
            self.communication (str): Stores the current communication type selected in the combo box.
            self.active (bool): Indicates if the device is active (default is True).
            self.battery (bool): Indicates if the device has a battery (default is True).
            self.btn_add (QPushButton): Button to confirm and accept the dialog.
        """
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        
        self.district_edit = QLineEdit(self)
        self.model_edit = QLineEdit(self)
        self.point_edit = QLineEdit(self)
        self.ip_edit = QLineEdit(self)
        # Create a QComboBox
        self.combo_box = QComboBox()
        # Add items to the QComboBox
        self.combo_box.addItem("TCP")
        self.combo_box.addItem("UDP")
        # Connect the QComboBox signal to a slot
        self.combo_box.currentIndexChanged.connect(self.on_combobox_changed)
        self.communication = self.combo_box.currentText()
        
        self.active = True
        self.battery = True

        form_layout.addRow("Distrito:", self.district_edit)
        form_layout.addRow("Modelo:", self.model_edit)
        form_layout.addRow("Punto de Marcación:", self.point_edit)
        form_layout.addRow("IP:", self.ip_edit)
        form_layout.addRow("Comunicación:", self.combo_box)
        
        layout.addLayout(form_layout)

        self.btn_add = QPushButton("Agregar", self)
        self.btn_add.clicked.connect(self.accept)
        layout.addWidget(self.btn_add)

        self.setLayout(layout)
        
    def on_combobox_changed(self, index):
        """
        Handles the event triggered when the selected index of the combo box changes.

        Args:
            index (int): The index of the newly selected item in the combo box.

        Side Effects:
            Updates the `self.communication` attribute with the text of the currently selected option
            in the combo box.
        """
        # Get the text of the selected option
        self.communication = self.combo_box.currentText()
        #logging.debug(self.communication)

    def get_data(self):
        """
        Retrieves and returns the data from the dialog fields.

        Returns:
            (tuple): A tuple containing the following elements:

                - str: The district name in uppercase (from `district_edit`).
                - str: The model name (from `model_edit`).
                - str: The point name in uppercase (from `point_edit`).
                - str: The IP address (from `ip_edit`).
                - Any: The device ID (`self.id`).
                - Any: The communication type or status (`self.communication`).
                - Any: The battery status (`self.battery`).
                - Any: The active status (`self.active`).
        """
        return (
            self.district_edit.text().upper(),
            self.model_edit.text(),
            self.point_edit.text().upper(),
            self.ip_edit.text(),
            self.id,
            self.communication,
            self.battery,
            self.active
        )