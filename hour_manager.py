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
from errors import HoraDesactualizada
from utils import logging
import asyncio

async def actualizar_hora_dispositivos():
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
                tasks.append(actualizar_hora_dispositivo(infoDevice))

        # Ejecuta todas las tareas asíncronas y espera sus resultados
        resultados = await asyncio.gather(*tasks, return_exceptions=True)

        # Maneja los resultados y excepciones
        for resultado in resultados:
            if isinstance(resultado, Exception):
                logging.error(f"Error en la tarea: {resultado}")

async def actualizar_hora_dispositivo(infoDevice):
    conn = None
                    
    try:
        conn = await reintentar_operacion(conectar, args=(infoDevice["ip"], 4370))

        try:
            await reintentar_operacion(actualizar_hora, args=(conn))
        except Exception as e:
            raise HoraDesactualizada(infoDevice["nombreModelo"], infoDevice["puntoMarcacion"], infoDevice["ip"]) from e
        
        await finalizar_conexion(conn)
    except ConexionFallida as e:
        raise ConexionFallida(infoDevice['nombreModelo'], infoDevice['puntoMarcacion'], infoDevice['ip']) from e
    except HoraDesactualizada as e:
        pass

    return