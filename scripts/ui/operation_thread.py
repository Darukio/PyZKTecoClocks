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
from PyQt5.QtCore import QThread, pyqtSignal

class OperationThread(QThread):
    op_updated = pyqtSignal(dict)
    op_terminated = pyqtSignal(float)
    progress_updated = pyqtSignal(int, str, int, int)  # Signal for progress

    def __init__(self, op_func, selected_devices=None, parent=None):
        super().__init__(parent)
        self.op_func = op_func
        self.selected_devices = selected_devices

    def run(self):
        try:
            import time
            start_time = time.time()
            if self.selected_devices:
                self.result = self.op_func(self.selected_devices, emit_progress=self.emit_progress)
            else:
                self.result = self.op_func(emit_progress=self.emit_progress)
            if self.result is None:
                self.op_updated.emit({})
            else:
                self.op_updated.emit(self.result)
            self.op_terminated.emit(start_time)
        except Exception as e:
            logging.critical(e)

    def emit_progress(self, percent_progress=None, device_progress=None, processed_devices=None, total_devices=None):
        self.progress_updated.emit(percent_progress, device_progress, processed_devices, total_devices)  # Emit the progress signal