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
import threading
import time
from connection import *
from file_manager import *
from errors import ConexionFallida
from utils import logging
import configparser

# Para leer un archivo INI
config = configparser.ConfigParser()

def organizar_info_dispositivos(line):
    # Dividir la línea en partes utilizando el separador " - "
    parts = line.strip().split(" - ")
    logging.debug(parts)
    # Verificar que hay exactamente 6 partes en la línea
    if len(parts) == 6:
        # Retorna un objeto con atributos
        return {
            "nombreDistrito": parts[0],
            "nombreModelo": parts[1],
            "puntoMarcacion": parts[2],
            "ip": parts[3],
            "id": parts[4],
            "activo": parts[5]
        }
    else:
        # Si no hay exactamente 6 partes, retornar None
        return None

def obtener_info_dispositivos():
    # Obtiene la ubicación del archivo de texto
    filePath = os.path.join(os.path.abspath('.'), 'info_devices.txt')
    logging.debug(filePath)
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

'''
def reintentar_conexion(infoDevice):
    config.read('config.ini')
    intentos_maximos = config['Network_config']['retry_connection']
    conn = None
    logging.info(f'Retrying connection to device {infoDevice["ip"]}...')
    intentos = 0
    t_inicio_reintento_total = time.time()
    while intentos < intentos_maximos:  # Intenta conectar hasta 3 veces
        try:
            t_inicio_reintento = time.time()
            conn = conectar(infoDevice['ip'], port=4370)
            return conn
        except Exception as e:
            logging.warning(f'Failed to connect to device {infoDevice['ip']}. Retrying...')
            intentos += 1
        finally:
            time.sleep(1)
            t_reintento = finalizar_cronometro(t_inicio_reintento)
            logging.debug(f'Tiempo de reintento {intentos} de {infoDevice["ip"]}: {t_reintento}')
            logging.debug(conn)
            if conn or intentos == intentos_maximos:
                t_reintento_total = finalizar_cronometro(t_inicio_reintento_total)
                logging.debug(f'Tiempo total de reintento de {infoDevice["ip"]}: {t_reintento_total}')
    logging.error(f'Unable to connect to device {infoDevice['ip']} after {intentos} attempts.')
    raise ConexionFallida(infoDevice['nombreModelo'], infoDevice['puntoMarcacion'], infoDevice['ip'])

def finalizar_cronometro(tiempo_inicial):
    tiempo_final = time.time()
    return tiempo_final-tiempo_inicial
'''

async def ping_devices():
    infoDevices = None
    try:
        # Obtiene todos los dispositivos en una lista formateada
        infoDevices = obtener_info_dispositivos()
    except Exception as e:
        logging.error(e)

    results = {}
    if infoDevices:
        # Itera a través de los dispositivos
        for infoDevice in infoDevices:
            # Si el dispositivo se encuentra activo...
            if eval(infoDevice["activo"]):
                conn = None
                status = None
                    
                try:
                    conn = await conectar(infoDevice["ip"], port=4370)
                    status = "Conexión exitosa"
                    await finalizar_conexion(conn)
                except Exception as e:
                    status = "Conexión fallida"

                # Guardar la información en results
                results[infoDevice["ip"]] = {
                    "puntoMarcacion": infoDevice["puntoMarcacion"],
                    "nombreDistrito": infoDevice["nombreDistrito"],
                    "id": infoDevice["id"],
                    "status": status
                }

    return results

async def reintentar_operacion(op, args=(), kwargs={}, intentos_maximos=3):
    logging.debug('4')
    config.read('config.ini')
    intentos_maximos = int(config['Network_config']['retry_connection'])
    result = None
    
    for _ in range(intentos_maximos):
        try:
            logging.debug('5')
            result = await op(*args, **kwargs)
            logging.debug('6')
            logging.debug(result)
            return result
        except Exception as e:
            logging.warning(f"Failed attempt {_ + 1} of {intentos_maximos} for operation {op.__name__}: {e}")

    raise Exception
    