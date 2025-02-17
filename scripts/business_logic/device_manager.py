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
import eventlet
from scripts import config

def activate_all_devices():
    try:
        with open('info_devices.txt', 'r') as file:
            lines = file.readlines()

        new_lines = []
        for line in lines:
            parts = line.strip().split(' - ')
            parts[7] = "True"
            new_lines.append(' - '.join(parts) + '\n')

        with open('info_devices.txt', 'w') as file:
            file.writelines(new_lines)

        logging.debug("Estado activo actualizado correctamente.")
    except Exception as e:
        logging.error(f"Error al actualizar el estado activo: {e}")