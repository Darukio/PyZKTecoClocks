from connection import *
from file_manager import *
from datetime import datetime
import os
from global_variables import logPath

def cargar_marcaciones_dispositivos():
    # Lee las IPs desde el archivo de texto
    filePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'file_ips.txt')
    ips = cargar_desde_archivo(filePath)
        
    # Itera a través de las IPs
    for ipDevice in ips:
        conn = None
        try:
            with open(logPath, 'a') as logFile:
                logFile.write(f'Service connecting with device {ipDevice}...\n')
            conn = conectar(ipDevice, port=4370)
        except Exception as e:
            folderPath = crear_carpeta_y_devolver_ruta(ipDevice)
            newtime = datetime.today().date()
            dateString = newtime.strftime("%Y-%m-%d")
            fileName = ipDevice+'_'+dateString+'_logs.txt'
            filePath = os.path.join(folderPath, fileName)
            with open(filePath, 'a') as file:
                file.write(f'Connection failed with device {ipDevice}: ', e)

        if conn:
            # FECHA
            newtime = datetime.today().date()
            dateString = newtime.strftime("%Y-%m-%d")
            print(f'Processing IP: {ipDevice}, Date: {dateString}')
            actualizar_hora(conn)

            # CARPETA
            folderPath = crear_carpeta_y_devolver_ruta(ipDevice)
                
            # MARCACIONES
            fileName = ipDevice+'_'+dateString+'_file.cro'
            destinyPath = os.path.join(folderPath, fileName)
            attendances = obtener_marcaciones(conn)
            print('Attendances: ', attendances)
            guardar_marcaciones_en_archivo(attendances, destinyPath)

            fileName = 'attendances_file.txt'
            folderPath = os.path.dirname(os.path.abspath(__file__))
            destinyPath = os.path.join(folderPath, fileName)
            guardar_marcaciones_en_archivo(attendances, destinyPath)

            print('Enabling device...')
            conn.enable_device()
            print('Disconnecting device...')
            conn.disconnect()

def actualizar_hora_dispositivos(icon, item):
    # Lee las IPs desde el archivo de texto
    filePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'file_ips.txt')
    ips = cargar_desde_archivo(filePath)
        
    # Itera a través de las IPs
    for ipDevice in ips:
        conn = None
        with open(logPath, 'a') as logFile:
            logFile.write(f'Service trying to connect with device {ipDevice}...\n')
        try:
            conn = conectar(ipDevice, port=4370)
        except Exception as e:
            folderPath = crear_carpeta_y_devolver_ruta(ipDevice)
            newtime = datetime.today().date()
            dateString = newtime.strftime("%Y-%m-%d")
            fileName = ipDevice+'_'+dateString+'_logs.txt'
            filePath = os.path.join(folderPath, fileName)
            with open(filePath, 'a') as file:
                file.write(f'Connection failed with device {ipDevice}: {e.args}')
        if conn:
            # FECHA
            newtime = datetime.today().date()
            dateString = newtime.strftime("%Y-%m-%d")
            print(f'Processing IP: {ipDevice}, Date: {dateString}')
            actualizar_hora(conn)

            print('Enabling device...')
            conn.enable_device()
            print('Disconnecting device...')
            conn.disconnect()