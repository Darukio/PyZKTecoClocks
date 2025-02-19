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

import logging
import os
import eventlet
import configparser
config = configparser.ConfigParser()
from scripts.common.business_logic.connection import restart_device
from scripts.common.business_logic.device_manager import get_device_info, retry_network_operation
from scripts.common.business_logic.shared_state import SharedState
from scripts.common.utils.errors import ConnectionFailedError, NetworkError
from scripts.common.utils.file_manager import find_root_directory

def activate_all_devices():
    try:
        with open('info_devices.txt', 'r') as file:
            lines = file.readlines()

        new_lines = []
        for line in lines:
            parts = line.strip().split(' - ')
            parts[7] = "True"
            new_lines.append(' - '.join(parts) + '\n')

        with open('info_devices.txt', 'w') as file:
            file.writelines(new_lines)

        logging.debug("Estado activo actualizado correctamente.")
    except Exception as e:
        logging.error(f"Error al actualizar el estado activo: {e}")

def restart_devices(selected_devices=None, emit_progress=None):
    device_info = []
    try:
        # Get all devices in a formatted list
        device_info = get_device_info()
    except Exception as e:
        logging.error(e)

    if device_info:
        logging.debug("Iniciando reinicio de dispositivos...")
        gt = []
        active_devices = []
        config.read(os.path.join(find_root_directory(), 'config.ini'))
        coroutines_pool_max_size = int(config['Cpu_config']['coroutines_pool_max_size'])

        # Create a pool of green threads
        state = SharedState()
        pool = eventlet.GreenPool(coroutines_pool_max_size)
        
        if selected_devices:
            selected_ips = {device['ip'] for device in selected_devices}
            logging.debug(f"selected_ips: {selected_ips}")

            active_devices = [device for device in device_info if device['ip'] in selected_ips]
            logging.debug(f"active_devices: {active_devices}")

        # Set the total number of devices in the shared state
        state.set_total_devices(len(active_devices))
        
        for active_device in active_devices:
            try:
                gt.append(pool.spawn(restart_device_single, active_device, emit_progress, state))
            except Exception as e:
                pass

        devices_with_error = {}
            
        for active_device, g in zip(active_devices, gt):
            logging.debug(f'Processing {active_device}')
            try:
                g.wait()
            except NetworkError as e:
                devices_with_error[active_device["ip"]] = str(e)
                logging.error(e, e.__cause__)

        logging.debug('TERMINE REINICIO!')
            
        if len(devices_with_error) > 0:
            logging.debug(f"Error al reiniciar los siguientes dispositivos: {devices_with_error}")
            return devices_with_error
        return
        
def restart_device_single(info, emit_progress, state):
    try:
        retry_network_operation(restart_device, args=(info['ip'], 4370, info['communication'],))
    except ConnectionFailedError as e:
        raise NetworkError(info['model_name'], info['point'], info['ip'])
    except Exception as e:
        raise e
    finally:
        try:
            # Update the number of processed devices and progress
            processed_devices = state.increment_processed_devices()
            if emit_progress:
                progress = state.calculate_progress()
                emit_progress(percent_progress=progress, device_progress=info["ip"], processed_devices=processed_devices, total_devices=state.get_total_devices())
                logging.debug(f"processed_devices: {processed_devices}/{state.get_total_devices()}, progress: {progress}%")
        except Exception as e:
            logging.error(e)

    return