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

import asyncio
from icon_manager import MainWindow
from utils import logging
import sys
import configparser
import threading
from qasync import QEventLoop, QApplication as QAsyncApplication

# Versión del programa
VERSION = "v1.0.0-beta"

# Para leer un archivo INI
config = configparser.ConfigParser()
config.read('config.ini')

def main():
    logging.debug('Script executing...')
    logging.info(f"Version del programa: {VERSION}")

    log_config()

    logFilePath = 'console_log.txt'

    # Redirigir salida estándar y de error al archivo de registro
    sys.stdout = open(logFilePath, 'a')
    sys.stderr = open(logFilePath, 'a')

    if len(sys.argv) == 1:
        try:
            app = QAsyncApplication(sys.argv)

            # Integrar asyncio con PyQt usando qasync
            loop = QEventLoop(app)
            asyncio.set_event_loop(loop)

            main_window = MainWindow()

            with loop:
                sys.exit(loop.run_forever())            
        except Exception as e:
            logging.error(e)

def log_config():
    for section in config.sections():
        logging.info(f'Section: {section}')
        # Iterar sobre las claves y valores dentro de cada sección
        for key, value in config.items(section):
            logging.info(f'Subsection: {key}, Value: {value}')

if __name__ == '__main__':
    main()