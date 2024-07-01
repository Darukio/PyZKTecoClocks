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

from connection import *
from device_manager import *
from file_manager import *
from datetime import datetime
from errors import *
from utils import logging
import os
import configparser
import asyncio

# Para leer un archivo INI
config = configparser.ConfigParser()

async def gestionar_marcaciones_dispositivos():
    infoDevices = None
    try:
        # Obtiene todos los dispositivos en una lista formateada
        infoDevices = obtener_info_dispositivos()
    except Exception as e:
        logging.error(e)

    if infoDevices:
        tasks = []
        resultados = []

        # Itera a través de los dispositivos
        for infoDevice in infoDevices:
            # Si el dispositivo se encuentra activo...
            if eval(infoDevice["activo"]):
                tasks.append(gestionar_marcaciones_dispositivo(infoDevice))
        
        # Ejecuta todas las tareas asíncronas y espera sus resultados
        resultados = await asyncio.gather(*tasks, return_exceptions=True)

        # Maneja los resultados y excepciones
        for resultado in resultados:
            if isinstance(resultado, Exception):
                logging.error(f"Error en la tarea: {resultado}")

async def gestionar_marcaciones_dispositivo(infoDevice):
    conn = None
                    
    try:
        conn = await reintentar_operacion(conectar, args=(infoDevice["ip"], 4370))

        attendances = await reintentar_operacion(obtener_marcaciones, args=(conn))
        attendances = format_attendances(attendances, infoDevice["id"])
        logging.info(f'{infoDevice["ip"]} - Attendances: {attendances}')
        await gestionar_marcaciones_individual(infoDevice, attendances)
        await gestionar_marcaciones_global(attendances)

        await finalizar_conexion(conn)

        await actualizar_hora_dispositivo(infoDevice)
    except ConexionFallida as e:
        raise ConexionFallida(infoDevice['nombreModelo'], infoDevice['puntoMarcacion'], infoDevice['ip']) from e
    except Exception as e:
        pass

    return

def format_attendances(attendances, id):
    formatted_attendances = []
    for attendance in attendances:
        formatted_timestamp = attendance.timestamp.strftime("%d/%m/%Y %H:%M") # Formatea el timestamp a DD/MM/YYYY hh:mm, ejemplo: 21/07/2023 05:28
        attendance_formatted = {
            "user_id": attendance.user_id,
            "timestamp": formatted_timestamp,
            "id": id,
            "status": attendance.status
        }
        formatted_attendances.append(attendance_formatted)
    return formatted_attendances

async def gestionar_marcaciones_individual(infoDevice, attendances):
    folderPath = crear_carpeta_y_devolver_ruta('devices', infoDevice["nombreDistrito"], infoDevice["nombreModelo"] + "-" + infoDevice["puntoMarcacion"])
    newtime = datetime.today().date()
    dateString = newtime.strftime("%Y-%m-%d")
    fileName = infoDevice["ip"]+'_'+dateString+'_file.cro'
    await gestionar_guardado_de_marcaciones(attendances, folderPath, fileName)

async def gestionar_marcaciones_global(attendances):
    folderPath = os.path.abspath('.')
    fileName = 'attendances_file.txt'
    await gestionar_guardado_de_marcaciones(attendances, folderPath, fileName)

async def gestionar_guardado_de_marcaciones(attendances, folderPath, fileName):
    destinyPath = os.path.join(folderPath, fileName)
    logging.debug(f'DestinyPath: {destinyPath}')
    guardar_marcaciones_en_archivo(attendances, destinyPath)

async def obtener_cantidad_marcaciones_dispositivos():
    infoDevices = None
    try:
        # Obtiene todos los dispositivos en una lista formateada
        infoDevices = obtener_info_dispositivos()
    except Exception as e:
        logging.error(e)

    if infoDevices:
        cantidad_marcaciones = {}
        tasks = []
        resultados = []

        # Itera a través de los dispositivos
        for infoDevice in infoDevices:
            # Si el dispositivo se encuentra activo...
            if eval(infoDevice["activo"]) == True:
                tasks.append(obtener_cantidad_marcaciones_dispositivo(infoDevice))
            else:
                infoDevices.remove(infoDevice)
        
        # Ejecuta todas las tareas asíncronas y espera sus resultados
        resultados = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Asigna los resultados a sus respectivos dispositivos
        for infoDevice, resultado in zip(infoDevices, resultados):
            if isinstance(resultado, Exception):
                cantidad_marcaciones[infoDevice["ip"]] = 'Conexión fallida'
            else:
                cantidad_marcaciones[infoDevice["ip"]] = resultado

    return cantidad_marcaciones

async def obtener_cantidad_marcaciones_dispositivo(infoDevice):
    conn = None
                    
    try:
        conn = await reintentar_operacion(conectar, args=(infoDevice["ip"], 4370))

        try:
            await reintentar_conexion(asyncio.to_thread(conn.get_attendance()))
            return await reintentar_conexion(asyncio.to_thread(conn.records))
        except Exception as e:
            pass

        await finalizar_conexion(conn)
    except ConexionFallida as e:
        raise ConexionFallida(infoDevice['nombreModelo'], infoDevice['puntoMarcacion'], infoDevice['ip']) from e
    except Exception as e:
        raise e