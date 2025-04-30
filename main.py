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

import eventlet
eventlet.monkey_patch()
from src.common.utils.errors import BaseError
from src.common.utils.system_utils import is_user_admin
from PyQt5.QtWidgets import QApplication
from src.ui.icon_manager import MainWindow
from src.common.utils.logging import config_log, logging
from src.common.utils.file_manager import find_root_directory
from version import PROGRAM_VERSION
import sys
import os


# To read an INI file
from src import config
config.read(os.path.join(find_root_directory(), 'config.ini'))

def main():
    """
    Main function to initialize and run the attendance clock program.
    This function sets up logging, determines the mode of operation (User or Developer),
    and initializes the main application window. It also handles any exceptions that
    occur during the execution of the program.

    Steps performed:
    1. Configures logging with a filename based on the program version.
    2. Logs the start of the script execution.
    3. Configures console logging.
    4. Determines the mode of operation (User or Developer) based on the runtime environment.
    5. Logs and prints the program version and mode.
    6. Prints copyright information.
    7. Initializes the QApplication and the main window.
    8. Handles any exceptions by logging a critical error.

    Raises:
        Exception: If an error occurs during the execution of the application.
    """
    config_log("programa_reloj_de_asistencias_" + PROGRAM_VERSION)

    logging.debug('Script ejecutandose...')
    # logging.debug(f'ADMIN: {is_user_admin()}')

    config_log_console()
        
    MODE = 'User' if getattr(sys, 'frozen', False) else 'Developer'
    msg_init = f"Program version: {PROGRAM_VERSION} - Mode: {MODE}"
    logging.info(msg_init)
    print(msg_init)
    print_copyright()

    # config_content()
    # logging.debug(sys.argv)
    
    try:
        app = QApplication(sys.argv)
        MainWindow()
        sys.exit(app.exec_())
    except Exception as e:
        BaseError(3000, str(e), "critical")

def config_content():
    """
    Logs the sections and their corresponding key-value pairs from a configuration object.

    This function iterates through all sections of a configuration object (`config`),
    logging each section name and the key-value pairs within that section.

    Logging Levels:
    - Logs the section names at the DEBUG level.
    - Logs the keys and their corresponding values within each section at the DEBUG level.

    Note:
    - Assumes that `config` is a pre-defined configuration object with methods `sections()` 
      and `items(section)`.

    Raises:
    - No exceptions are explicitly handled within this function.
    """
    for section in config.sections():
        logging.debug(f'Seccion: {section}')
        # Iterate over the keys and values within each section
        for key, value in config.items(section):
            logging.debug(f'Sub-seccion: {key}, Valor: {value}')

def config_log_console():
    """
    Configures logging to redirect standard output and error streams to a log file.
    This function performs the following tasks:
    - Determines the log file path by combining the root directory, 'logs' folder, and 'console_log.txt'.
    - Ensures the existence of the log file and its parent directory, creating them if necessary.
    - Redirects `sys.stdout` and `sys.stderr` to the log file for capturing console output and errors.
    - Enables fault handler to dump stack traces in case of a program crash.
    Note:
    - The `find_root_directory` function is expected to return the root directory of the project.
    - The log file is appended to if it already exists.
    """
    log_file_path = os.path.join(find_root_directory(), 'logs', 'console_log.txt')
    # logging.debug(find_root_directory())
    # logging.debug(sys.executable)
    
    # Ensure the log file and its directory exist
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    if not os.path.exists(log_file_path):
        with open(log_file_path, 'w') as f:
            pass  # Create the file if it doesn't exist

    # Redirect standard output and error to the log file
    sys.stdout = open(log_file_path, 'a')
    sys.stderr = open(log_file_path, 'a')

    import faulthandler
    faulthandler.enable()  # Activate stack trace dumping in case of failure

def print_copyright():
    """
    Prints and logs the copyright information for the PyZKTecoClocks program.
    This function outputs the copyright details, including licensing information,
    to the console and logs it using the logging module.
    """
    copyright_text = """
PyZKTecoClocks: GUI for managing ZKTeco clocks. 
Copyright (C) 2024 Paulo Sebastian Spaciuk (Darukio)

This software is licensed under the GNU General Public License v3.0 or later.
It comes without warranty. See <https://www.gnu.org/licenses/> for details."""
    print(copyright_text)
    logging.info(copyright_text)

if __name__ == '__main__':
    main()