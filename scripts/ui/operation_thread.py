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

from typing import Callable
from PyQt5.QtCore import QThread, pyqtSignal
from scripts.common.utils.errors import BaseError

class OperationThread(QThread):
    op_terminate = pyqtSignal(dict)
    op_start_time = pyqtSignal(float)
    progress_updated = pyqtSignal(int, str, int, int)  # Signal for progress

    def __init__(self, op_func: Callable, selected_ips: list[str] = None, parent = None):
        """
        Initializes the OperationThread instance.

        Args:
            op_func (Callable): The operation function to be executed in the thread.
            selected_ips (list[str], optional): A list of selected IP addresses. Defaults to None.
            parent (QObject, optional): The parent object for the thread. Defaults to None.
        """
        super().__init__(parent)
        self.op_func: Callable = op_func
        self.selected_ips: list[str] = selected_ips
        self.result: dict = {}

    def run(self):
        """
        Executes the operation function (`op_func`) with the selected IPs or without them,
        handles the result, and emits appropriate signals.

        This method is designed to run in a separate thread to perform operations
        asynchronously. It captures any exceptions raised during execution and
        raises a `BaseError` with a specific error code and message.

        Attributes:
            selected_ips (list): A list of selected IP addresses to pass to the operation
                function. If not provided, the operation function is called without IPs.
            result (dict): The result of the operation function execution.

        Emits:
            op_terminate (dict): Signal emitted with the result of the operation function
                or an empty dictionary if the result is `None`.

        Raises:
            BaseError: If an exception occurs during the execution of the operation
                function, a `BaseError` is raised with error code 3000 and the exception
                message.
        """
        try:
            #import time
            #start_time: float = time.time()
            if self.selected_ips:
                self.result: dict = self.op_func(self.selected_ips, emit_progress=self.emit_progress)
            else:
                self.result: dict = self.op_func(emit_progress=self.emit_progress)
            if self.result is None:
                self.op_terminate.emit({})
            else:
                self.op_terminate.emit(self.result)
            #self.op_start_time.emit(start_time)
        except Exception as e:
            raise BaseError(3000, str(e), "critical")

    def emit_progress(self, percent_progress: int = None, device_progress: str = None, processed_devices: int = None, total_devices: int = None):
        """
        Emits a progress update signal with the provided progress details.

        Args:
            percent_progress (int, optional): The overall percentage of progress completed. Defaults to None.
            device_progress (str, optional): A string describing the progress of the current device. Defaults to None.
            processed_devices (int, optional): The number of devices that have been processed so far. Defaults to None.
            total_devices (int, optional): The total number of devices to be processed. Defaults to None.
        """
        self.progress_updated.emit(percent_progress, device_progress, processed_devices, total_devices)  # Emit the progress signal