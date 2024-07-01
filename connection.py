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

from zk import ZK
from datetime import datetime
from utils import logging
import configparser
import asyncio
from errors import ConexionFallida

# Para leer un archivo INI
config = configparser.ConfigParser()

async def conectar(ip, port):
    logging.debug(f'8 {ip}...')
    config.read('config.ini')
    conn = None
    try:
        logging.debug(f'9 {ip}...')
        omit_ping = eval(config['Network_config']['omit_ping'])
        ping_packages_size = int(config['Network_config']['ping_packages_size'])
        latency_limit = int(config['Network_config']['latency_limit'])
        package_loss_limit = int(config['Network_config']['package_loss_limit'])
        zk = await asyncio.to_thread(ZK, ip, port, omit_ping, 
        ping_packages_size, 
        latency_limit, 
        package_loss_limit)
        logging.info(f'Connecting to device {ip}...')
        logging.debug(f'10 {ip}...')
        conn = await asyncio.to_thread(zk.connect)
        #conn = zk.connect()
        logging.debug(f'11 {ip}...')
        #logging.info('Disabling device...')
        #conn.disable_device()
        logging.info(f'Successfully connected to device {ip}.')
        logging.debug(conn)
        logging.debug(conn.get_platform())
        logging.debug(conn.get_device_name())
        #conn.test_voice(index=10)
    except Exception as e:
        logging.error(e)
        raise ConexionFallida from e
    return conn

async def finalizar_conexion(conn):
    try:
        #logging.info('Enabling device...')
        #conn.enable_device()
        logging.info(f'{conn.get_network_params()["ip"]} - Disconnecting device...')
        await asyncio.to_thread(conn.disconnect)
    except Exception as e:
        raise e

async def actualizar_hora(conn):
    try:
        zktime = await asyncio.to_thread(conn.get_time)
        logging.debug(f'{conn.get_network_params()["ip"]} - Date and hour device: {zktime} - Date and hour machine: {datetime.today()}')
    except Exception as e:
        raise e

    try:
        try:
            validar_hora(zktime)
        except Exception as e:
            pass
        newtime = datetime.today()
        await asyncio.to_thread(conn.set_time, newtime)
    except Exception as e:
        raise e

def validar_hora(zktime):
    newtime = datetime.today()
    if (abs(zktime.hour - newtime.hour) > 0 or
    abs(zktime.minute - newtime.minute) >= 5 or
    zktime.day != newtime.day or
    zktime.month != newtime.month or
    zktime.year != newtime.year):
        raise Exception('Hours or date between device and machine doesn\'t match')
    
async def obtener_marcaciones(conn, intentos=0):
    attendances = []
    try:
        ip = conn.get_network_params()['ip']
        records = conn.records
        logging.info(f'{ip} - Getting attendances...')
        attendances = await asyncio.to_thread(conn.get_attendance())
        if records != len(attendances):
            if intentos < 3:
                logging.warning(f"{ip} - Records mismatch. Retrying... Attempt {intentos+1}")
                return await obtener_marcaciones(conn, intentos + 1)
            else:
                logging.error(f"{ip} - Failed to retrieve attendances after 3 attempts.")
        else:
            config.read('config.ini')
            logging.debug(f'clear_attendance: {config['Device_config']['clear_attendance']}')
            if eval(config['Device_config']['clear_attendance']):
                logging.debug(f'{ip} - Clearing attendances...')
                await asyncio.to_thread(conn.clear_attendance())
            logging.debug(f'{ip} - Length of attendances from device: {records}, Length of attendances: {len(attendances)}')
    except Exception as e:
        raise e
    return attendances