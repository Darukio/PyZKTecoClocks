import schedule
import time
import os
import subprocess
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
from tasks_device_manager import cargar_marcaciones_dispositivos
from file_manager import cargar_desde_archivo
from global_variables import logPath

class MyService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'MyService'
    _svc_display_name_ = 'My Service'

    def __init__(self, args):
        with open(logPath, 'a') as logFile:
            logFile.write("Service initiated...\n")
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_alive = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_alive = False

    def SvcDoRun(self):
        with open(logPath, 'a') as logFile:
            logFile.write("Service started...\n")
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STARTED, (self._svc_name_, ''))
        self.main()

    def main(self):
        configurar_schedule()
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STARTED, (self._svc_name_, ''))
        while self.is_alive:
            
            with open(logPath, 'a') as logFile:
                logFile.write("Service executing...\n")
            schedule.run_pending()
            time.sleep(1)

def is_service_running():
    # Comando para verificar si el servicio está en ejecución
    result = subprocess.run(["sc", "query", "MyService"], capture_output=True, text=True)
    return "STATE" in result.stdout or "ESTADO" in result.stdout and "RUNNING" in result.stdout

def configurar_schedule():
    '''
    Configura las tareas programadas en base a las horas cargadas desde el archivo.
    '''

    # Lee las horas de ejecución desde el archivo de texto
    filePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schedule.txt')
    hoursToPerform = cargar_desde_archivo(filePath)
        
    # Itera las horas de ejecución
    for hourToPerform in hoursToPerform:
        '''
        Ejecuta la tarea de actualizar hora y guardar las 
        marcaciones en archivos (individual y en conjunto)
        en la hora especificada en .at
        '''

        schedule.every().day.at(hourToPerform).do(cargar_marcaciones_dispositivos)