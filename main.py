import sys
import win32serviceutil
import pyuac
from icon_manager import create_tray_icon
from service import MyService
from global_variables import logPath

@pyuac.main_requires_admin
def main():
    with open(logPath, 'a') as logFile:
        logFile.write('Script executing...\n')

    logFilePath = 'console_log.txt'

    # Redirigir salida estándar y de error al archivo de registro
    sys.stdout = open(logFilePath, 'a')
    sys.stderr = open(logFilePath, 'a')

    if len(sys.argv) == 1:
        tray_icon = create_tray_icon()
        tray_icon.run()
        # servicemanager.Initialize()
        # servicemanager.PrepareToHostSingle(MyService)
        # servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(MyService)

if __name__ == '__main__':
    main()