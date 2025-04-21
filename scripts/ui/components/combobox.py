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

from PyQt5.QtWidgets import QStyledItemDelegate, QComboBox

class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        """
        Initializes the ComboBox instance.

        Args:
            parent (QWidget, optional): The parent widget of the ComboBox. Defaults to None.
        """
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        """
        Creates and configures a QComboBox editor for a cell in the view.

        Args:
            parent (QWidget): The parent widget for the QComboBox.
            option (QStyleOptionViewItem): Provides style options for the item.
            index (QModelIndex): The index of the item in the model.

        Returns:
            QComboBox: A configured QComboBox with predefined items ("UDP" and "TCP").
        """
        combo_box = QComboBox(parent)
        combo_box.addItem("UDP")
        combo_box.addItem("TCP")
        return combo_box

    def setEditorData(self, editor, index):
        """
        Sets the data for the editor widget based on the given model index.

        This method retrieves the data from the specified index in the model
        and sets it as the current text of the editor widget, if the data is not None.

        Args:
            editor (QWidget): The editor widget where the data will be set.
            index (QModelIndex): The model index containing the data to be set in the editor.
        """
        value = index.data()
        if value is not None:
            editor.setCurrentText(value)

    def setModelData(self, editor, model, index):
        """
        Updates the model with the data from the editor at the specified index.

        Args:
            editor (QWidget): The editor widget, typically a QComboBox, 
                              from which the current text will be retrieved.
            model (QAbstractItemModel): The data model to be updated.
            index (QModelIndex): The index in the model where the data should be set.

        """
        model.setData(index, editor.currentText())