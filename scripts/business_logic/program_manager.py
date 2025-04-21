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

from scripts.common.business_logic.models.attendance import Attendance
from PyQt5.QtWidgets import QMessageBox
from scripts.common.business_logic.operation_manager import OperationManager
import configparser
import logging
from logging import config
import os
from typing import Callable
from scripts.common.business_logic.attendances_manager import AttendancesManagerBase
from scripts.common.business_logic.connection_manager import ConnectionManager
from scripts.common.business_logic.models.device import Device
from scripts.common.business_logic.hour_manager import HourManagerBase
from scripts.common.business_logic.shared_state import SharedState
from scripts.common.business_logic.types import ConnectionInfo, DeviceInfo
from scripts.common.utils.errors import BatteryFailingError, NetworkError, ConnectionFailedError, BaseError, ObtainAttendancesError, OutdatedTimeError
from scripts.common.utils.file_manager import find_marker_directory, find_root_directory
config = configparser.ConfigParser()

class ProgressTracker:
    def __init__(self, state: SharedState, emit_progress: Callable):
        self.state: SharedState = state
        self.emit_progress: Callable = emit_progress

    def update(self, device: Device):
        try:
            if self.state:
                processed_devices: int = self.state.increment_processed_devices()
                if self.emit_progress:
                    progress: int = self.state.calculate_progress()
                    self.emit_progress(
                        percent_progress=progress,
                        device_progress=device.ip,
                        processed_devices=processed_devices,
                        total_devices=self.state.get_total_devices()
                    )
                    logging.debug(f"Processed: {processed_devices}/{self.state.get_total_devices()}, Progress: {progress}%")
        except Exception as e:
            BaseError(3000, f'Error actualizando el progreso: {str(e)}')
        return

class AttendancesManager(AttendancesManagerBase):
    def __init__(self):
        self.state = SharedState()
        config.read(os.path.join(find_root_directory(), 'config.ini'))
        self.clear_attendance: bool = config.getboolean('Device_config', 'clear_attendance')
        super().__init__(self.state)

    def manage_devices_attendances(self, selected_ips: list[str], emit_progress: Callable = None):
        self.emit_progress: Callable = emit_progress
        config.read(os.path.join(find_root_directory(), 'config.ini'))
        self.clear_attendance: bool = config.getboolean('Device_config', 'clear_attendance')
        self.force_clear_attendance: bool = config.getboolean('Device_config', 'force_clear_attendance')
        logging.debug(f'force_clear_attendance: {self.force_clear_attendance}')
        self.state.reset()
        attendances_count = super().manage_devices_attendances(selected_ips)
        if self.force_clear_attendance:
            self.force_clear_attendance = False
            config['Device_config']['force_clear_attendance'] = 'False'

            with open('config.ini', 'w') as configfile:
                config.write(configfile)
        return attendances_count

    def manage_attendances_of_one_device(self, device: Device):
        logging.debug(f"Iniciando {device.ip}")
        try:
            try:
                conn_manager = ConnectionManager(device.ip, 4370, device.communication)
                #import time
                #start_time = time.time()
                conn_manager.connect_with_retry()
                #end_time = time.time()
                #logging.debug(f'{device.ip} - Tiempo de conexión total: {(end_time - start_time):2f}')
                attendances: list[Attendance] = conn_manager.get_attendances()
                #logging.info(f'{device.ip} - PREFORMATEO - Longitud marcaciones: {len(attendances)} - Marcaciones: {attendances}')
                attendances, attendances_with_error = self.format_attendances(attendances, device.id)
                if len(attendances_with_error) > 0:
                    if not self.force_clear_attendance:
                        self.clear_attendance = False
                        logging.debug(f'No se eliminaran las marcaciones correspondientes al dispositivo {device.ip}')
                #logging.info(f'{device.ip} - POSTFORMATEO - Longitud marcaciones: {len(attendances)} - Marcaciones: {attendances}')
                logging.debug(f'clear_attendance: {self.clear_attendance}')
                conn_manager.clear_attendances(self.clear_attendance)
            except (NetworkError, ObtainAttendancesError) as e:
                with self.lock:
                    self.attendances_count_devices[device.ip] = {
                        "connection failed": True
                    }
                raise ConnectionFailedError(device.model_name, device.point, device.ip)
            except Exception as e:
                raise BaseError(3000, str(e)) from e
                        
            try:
                device.model_name = conn_manager.update_device_name()
            except Exception as e:
                pass

            self.manage_individual_attendances(device, attendances)
            self.manage_global_attendances(attendances)

            try:
                conn_manager.update_time()
            except NetworkError as e:
                NetworkError(f'{device.model_name}, {device.point}, {device.ip}')
            except OutdatedTimeError as e:
                HourManager().update_battery_status(device.ip)

            with self.lock:
                self.attendances_count_devices[device.ip] = {
                    "attendance count": str(len(attendances))
                }
        except Exception as e:
            pass
        finally:
            if conn_manager.is_connected():
                conn_manager.disconnect()
            ProgressTracker(self.state, self.emit_progress).update(device)
            logging.debug(f"Finalizando {device.ip}")
            return
        
class HourManager(HourManagerBase):
    def __init__(self):
        self.state = SharedState()
        super().__init__(self.state)

    def manage_hour_devices(self, selected_ips: list[str], emit_progress: Callable = None):
        self.emit_progress: Callable = emit_progress
        self.state.reset()
        return super().update_devices_time(selected_ips)

    def update_device_time_of_one_device(self, device: Device):
        logging.debug(f"Iniciando {device.ip}")
        try:
            conn_manager: ConnectionManager = ConnectionManager(device.ip, 4370, device.communication)
            conn_manager.connect_with_retry()
            with self.lock:
                self.devices_errors[device.ip] = { "connection failed": False }
            conn_manager.update_time()
            with self.lock:
                self.devices_errors[device.ip] = { "battery failing": False }
        except NetworkError as e:
            with self.lock:
                self.devices_errors[device.ip] = { "connection failed": True }
            raise ConnectionFailedError(device.model_name, device.point, device.ip)
        except OutdatedTimeError as e:
            with self.lock:
                self.devices_errors[device.ip] = { "battery failing": True }
            raise BatteryFailingError(device.model_name, device.point, device.ip)
        except Exception as e:
            raise BaseError(3000, str(e)) from e
        finally:
            if conn_manager.is_connected():
                conn_manager.disconnect()
            ProgressTracker(self.state, self.emit_progress).update(device)
            logging.debug(f"Finalizando {device.ip}")
        return

class RestartManager(OperationManager):
    def __init__(self):
        self.state = SharedState()
        self.devices_errors: dict[str, dict[str, bool]] = {}
        super().__init__(self.state)

    def restart_devices(self, selected_ips: list[str], emit_progress: Callable = None):
        self.devices_errors.clear()
        self.emit_progress: Callable = emit_progress
        self.state.reset()
        super().manage_threads_to_devices(selected_ips=selected_ips, function=self.restart_device)

        if len(self.devices_errors) > 0:
            return self.devices_errors
        
    def restart_device(self, device: Device):
        try:
            conn_manager: ConnectionManager = ConnectionManager(device.ip, 4370, device.communication)
            conn_manager.connect_with_retry()
            with self.lock:
                self.devices_errors[device.ip] = { "connection failed": False }
            conn_manager.restart_device()
        except NetworkError as e:
            with self.lock:
                self.devices_errors[device.ip] = { "connection failed": True }
            raise ConnectionFailedError(device.model_name, device.point, device.ip)
        except Exception as e:
            raise BaseError(3000, str(e))
        finally:
            if conn_manager.is_connected():
                conn_manager.disconnect()
            ProgressTracker(self.state, self.emit_progress).update(device)

class ConnectionsInfo(OperationManager):
    def __init__(self):
        self.state = SharedState()
        self.connections_info: dict[str, ConnectionInfo] = {}
        super().__init__(self.state)

    def obtain_connections_info(self, selected_ips: list[str], emit_progress: Callable = None):
        self.connections_info.clear()
        self.emit_progress: Callable = emit_progress
        self.state.reset()

        super().manage_threads_to_devices(selected_ips=selected_ips, function=self.obtain_connection_info)

        if len(self.connections_info) > 0:
            return self.connections_info
        
    def obtain_connection_info(self, device: Device):
        try:
            logging.debug(f"Iniciando {device.ip}")
            conn_manager: ConnectionManager = ConnectionManager(device.ip, 4370, device.communication)
            connection_info: ConnectionInfo = ConnectionInfo()
            conn_manager.connect_with_retry()
            test_ping_connection: bool = conn_manager.ping_device()
            if test_ping_connection:
                device_info: DeviceInfo = conn_manager.obtain_device_info()
                connection_info.update({
                    "connection_failed": False,
                    "device_info": device_info
                })
            else:
                connection_info.update({
                    "connection_failed": True,
                })
            with self.lock:
                self.connections_info[device.ip] = connection_info
        except NetworkError as e:
            connection_info.update({
                "connection_failed": True
            })
            with self.lock:
                self.connections_info[device.ip] = connection_info
            raise ConnectionFailedError(device.model_name, device.point, device.ip)
        except Exception as e:
            raise BaseError(3000, str(e))
        finally:
            if conn_manager.is_connected():
                conn_manager.disconnect()
            ProgressTracker(self.state, self.emit_progress).update(device)
            logging.debug(f"Finalizando {device.ip}")