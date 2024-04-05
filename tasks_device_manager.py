from connection import *
from file_manager import *
from datetime import datetime
<<<<<<< HEAD
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
=======
from errors import ConexionFallida
from utils import logging
import os

def organizar_info_dispositivos(line):
    # Dividir la línea en partes utilizando el separador " - "
    parts = line.strip().split(" - ")
    logging.debug(parts)
    # Verificar que hay exactamente 5 partes en la línea
    if len(parts) == 5:
        # Retorna un objeto con atributos
        return {
            "nombreDistrito": parts[0],
            "nombreModelo": parts[1],
            "puntoMarcacion": parts[2],
            "ip": parts[3],
            "activo": parts[4]
        }
    else:
        # Si no hay exactamente 5 partes, retornar None
        return None

def obtener_info_dispositivos(filePath):
    # Obtiene la info de dispositivos de info_devices.txt
    dataList = cargar_desde_archivo(filePath)
    logging.debug(dataList)
    infoDevices = []
    # Itera los distintos dispositivos
    for data in dataList:
        # A la línea sin formatear, crea un objeto de dispositivo
        line = organizar_info_dispositivos(data)
        logging.debug(line)
        if line:
            # Anexa el dispositivo a la lista de dispositivos
            infoDevices.append(line)
        logging.debug(infoDevices)
    return infoDevices

def gestionar_marcaciones_dispositivos():
    # Obtiene la ubicación del archivo de texto
    filePath = os.path.join(os.path.abspath('.'), 'info_devices.txt')
    logging.debug(filePath)
    infoDevices = None
    try:
        # Obtiene todos los dispositivos en una lista formateada
        infoDevices = obtener_info_dispositivos(filePath)
    except Exception as e:
        logging.error(e)

    if infoDevices:
        # Itera a través de los dispositivos
        for infoDevice in infoDevices:
            try:
                # Si el dispositivo se encuentra activo...
                if eval(infoDevice["activo"]) == True:
                    conn = None
                    try:
                        conn = conectar(infoDevice["ip"], port=4370)
                    except Exception as e:
                        raise ConexionFallida(infoDevice["nombreModelo"], infoDevice["puntoMarcacion"], infoDevice["ip"]) from e
                    
                    if conn:
                        logging.info(f'Processing IP: {infoDevice["ip"]}')
                        actualizar_hora(conn)
                        attendances = obtener_marcaciones(conn)
                        logging.info(f'Attendances: {attendances}')
                        gestionar_marcaciones_individual(infoDevice, attendances)
                        gestionar_marcaciones_global(attendances)
                        finalizar_conexion(conn)
            except ConexionFallida as e:
                pass

def gestionar_marcaciones_individual(infoDevice, attendances):
    folderPath = crear_carpeta_y_devolver_ruta('devices', infoDevice["nombreDistrito"], infoDevice["nombreModelo"] + "-" + infoDevice["puntoMarcacion"])
    newtime = datetime.today().date()
    dateString = newtime.strftime("%Y-%m-%d")
    fileName = infoDevice["ip"]+'_'+dateString+'_file.cro'
    gestionar_guardado_de_marcaciones(attendances, folderPath, fileName)

def gestionar_marcaciones_global(attendances):
    folderPath = os.path.abspath('.')
    fileName = 'attendances_file.txt'
    gestionar_guardado_de_marcaciones(attendances, folderPath, fileName)

def gestionar_guardado_de_marcaciones(attendances, folderPath, fileName):
    destinyPath = os.path.join(folderPath, fileName)
    logging.debug(f'DestinyPath: {destinyPath}')
    guardar_marcaciones_en_archivo(attendances, destinyPath)

def actualizar_hora_dispositivos():
    # Obtiene la ubicación del archivo de texto
    filePath = os.path.join(os.path.abspath('.'), 'info_devices.txt')
    logging.debug(filePath)
    infoDevices = None
    try:
        # Obtiene todos los dispositivos en una lista formateada
        infoDevices = obtener_info_dispositivos(filePath)
    except Exception as e:
        logging.error(e)

    if infoDevices:
        # Itera a través de los dispositivos
        for infoDevice in infoDevices:
            try:
                # Si el dispositivo se encuentra activo...
                if eval(infoDevice["activo"]) == True:
                    conn = None
                    try:
                        conn = conectar(infoDevice["ip"], port=4370)
                    except Exception as e:
                        raise ConexionFallida(infoDevice["nombreModelo"], infoDevice["puntoMarcacion"], infoDevice["ip"]) from e

                    if conn:
                        logging.info(f'Processing IP: {infoDevice["ip"]}')
                        actualizar_hora(conn)
                        finalizar_conexion(conn)
            except ConexionFallida as e:
                pass
>>>>>>> dev
