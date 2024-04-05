<<<<<<< HEAD
import sys
import win32serviceutil
import pyuac
from icon_manager import create_tray_icon
from service import MyService
from global_variables import logPath

@pyuac.main_requires_admin
=======

import sys
import pyuac
from icon_manager import TrayApp
from utils import logging

#@pyuac.main_requires_admin
>>>>>>> dev
def main():
    logging.debug('Script executing...')

    logFilePath = 'console_log.txt'

    # Redirigir salida estándar y de error al archivo de registro
    sys.stdout = open(logFilePath, 'a')
    sys.stderr = open(logFilePath, 'a')

    if len(sys.argv) == 1:
        try:
            app = TrayApp()
            app.icon.run()
        except Exception as e:
            logging.error(e)

if __name__ == '__main__':
    main()