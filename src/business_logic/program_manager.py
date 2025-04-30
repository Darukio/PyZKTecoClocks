# PyZKTecoClocks: GUI for managing ZKTeco clocks, enabling clock 
# time synchronization and attendance data retrieval.
# Copyright (C) 2024  Paulo Sebastian Spaciuk (Darukio)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from src.common.business_logic.models.attendance import Attendance
from PyQt5.QtWidgets import QMessageBox
from src.common.business_logic.operation_manager import OperationManager
import configparser
import logging
from logging import config
import os
from typing import Callable
from src.common.business_logic.attendances_manager import AttendancesManagerBase
from src.common.business_logic.connection_manager import ConnectionManager
from src.common.business_logic.models.device import Device
from src.common.business_logic.hour_manager import HourManagerBase
from src.common.business_logic.shared_state import SharedState
from src.common.business_logic.types import ConnectionInfo, DeviceInfo
from src.common.utils.errors import BatteryFailingError, NetworkError, ConnectionFailedError, BaseError, ObtainAttendancesError, OutdatedTimeError
from src.common.utils.file_manager import find_marker_directory, find_root_directory
config = configparser.ConfigParser()

class ProgressTracker:
    def __init__(self, state: SharedState, emit_progress: Callable):
        """
        Initializes the ProgramManager instance.

        Args:
            state (SharedState): The shared state object used to manage and share data across components.
            emit_progress (Callable): A callable function used to emit progress updates.
        """
        self.state: SharedState = state
        self.emit_progress: Callable = emit_progress

    def update(self, device: Device):
        """
        Updates the progress of processing a device and emits progress information if applicable.

        Args:
            device (Device): The device object being processed.

        Behavior:
            - Increments the count of processed devices in the current state.
            - Calculates the progress percentage based on the total devices.
            - Emits progress information including:
                - Percent progress.
                - IP address of the device being processed.
                - Number of processed devices.
                - Total number of devices.
            - Logs the progress details for debugging purposes.

        Exceptions:
            - Catches any exception that occurs during the update process and raises a `BaseError`
              with an error code of 3000 and a descriptive message.
        """
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
        """
        Initializes the ProgramManager instance.

        This constructor sets up the initial state of the ProgramManager by
        creating a new instance of SharedState and passing it to the parent
        class initializer.

        Attributes:
            state (SharedState): The shared state object used to manage
            program-wide data and operations.
        """
        self.state = SharedState()
        super().__init__(self.state)

    def manage_devices_attendances(self, selected_ips: list[str], emit_progress: Callable = None):
        """
        Manages the attendance records for the specified devices.
        This method processes attendance data for the devices with the given IPs.
        It also handles configuration settings related to clearing attendance data
        and updates the configuration file if necessary.

        Args:
            selected_ips (list[str]): A list of IP addresses of the devices to manage.
            emit_progress (Callable, optional): A callable function to emit progress updates. Defaults to None.
        
        Returns:
            (int): The count of attendances processed.

        Side Effects:
            - Reads configuration settings from 'config.ini'.
            - Resets the internal state before processing.
            - Updates the 'force_clear_attendance' setting in 'config.ini' if it was set to True.
        """
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
        """
        Manages the attendance data for a single device.
        This method handles the connection to a device, retrieves attendance data, processes it,
        and updates the device's state and attendance records. It also manages error handling
        and ensures proper cleanup of resources.

        Args:
            device (Device): The device object representing the attendance device to be managed.

        Workflow:
            1. Establishes a connection to the device using `ConnectionManager`.
            2. Retrieves attendance data from the device.
            3. Formats the attendance data and handles any errors during formatting.
            4. Clears attendance data on the device based on the `clear_attendance` flag.
            5. Updates the device's model name if possible.
            6. Processes individual and global attendance records.
            7. Synchronizes the device's time and handles time-related errors.
            8. Updates the attendance count for the device in a shared dictionary.
            9. Ensures proper disconnection from the device and updates progress tracking.

        Exceptions:
            - Handles `NetworkError` and `ObtainAttendancesError` during connection and data retrieval.
            - Raises `ConnectionFailedError` if the connection to the device fails.
            - Catches and re-raises other exceptions as `BaseError` with a specific error code.
            - Handles time synchronization errors such as `OutdatedTimeError` and updates the battery status.
        
        Logging:
            - Logs debug information for connection initiation, attendance processing, and cleanup.
            - Logs errors and warnings for failed connections and other issues.
        
        Returns:
            None
        """
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
                BatteryFailingError(device.model_name, device.point, device.ip)

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
        """
        Initializes the ProgramManager instance.

        This constructor sets up the initial state of the ProgramManager by
        creating a new instance of SharedState and passing it to the parent
        class initializer.

        Attributes:
            state (SharedState): The shared state object used to manage
            program-wide state and data.
        """
        self.state = SharedState()
        super().__init__(self.state)

    def manage_hour_devices(self, selected_ips: list[str], emit_progress: Callable = None):
        """
        Synchronizes the time on a list of devices identified by their IP addresses.

        Args:
            selected_ips (list[str]): A list of IP addresses of the devices to update.
            emit_progress (Callable, optional): A callback function to emit progress updates. Defaults to None.

        Returns:
            (Any): The result of the `update_devices_time` method from the superclass.
        """
        self.emit_progress: Callable = emit_progress
        self.state.reset()
        return super().update_devices_time(selected_ips)

    def update_device_time_of_one_device(self, device: Device):
        """
        Updates the device time for a single device.

        This method attempts to connect to the specified device, update its time, 
        and handle any errors that may occur during the process. It also updates 
        the device's error status and progress tracking.

        Args:
            device (Device): The device object containing information such as 
                             IP address, communication type, model name, and point.

        Raises:
            ConnectionFailedError: If the connection to the device fails.
            BatteryFailingError: If the device's battery is failing and its time 
                                 cannot be updated.
            BaseError: For any other unexpected errors, with error code 3000.

        Notes:
            - Uses a lock to ensure thread-safe updates to the `devices_errors` dictionary.
            - Updates the battery status if an outdated time error occurs.
            - Ensures the connection is properly closed in the `finally` block.
            - Tracks progress using the `ProgressTracker` class.
        """
        logging.debug(f"Iniciando {device.ip}")
        try:
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
                HourManager().update_battery_status(device.ip)
                raise BatteryFailingError(device.model_name, device.point, device.ip)
        except ConnectionFailedError as e:
            pass
        except BatteryFailingError as e:
            pass
        except Exception as e:
            BaseError(3000, str(e))
        finally:
            if conn_manager.is_connected():
                conn_manager.disconnect()
            ProgressTracker(self.state, self.emit_progress).update(device)
            logging.debug(f"Finalizando {device.ip}")
        return

class RestartManager(OperationManager):
    def __init__(self):
        """
        Initializes the ProgramManager instance.

        This constructor sets up the shared state and initializes a dictionary
        to track device errors. It also calls the superclass initializer with
        the shared state.

        Attributes:
            state (SharedState): An instance of SharedState to manage shared data.
            devices_errors (dict[str, dict[str, bool]]): A dictionary to store
                error states for devices, where the keys are device identifiers
                and the values are dictionaries mapping error types to their
                boolean statuses.
        """
        self.state = SharedState()
        self.devices_errors: dict[str, dict[str, bool]] = {}
        super().__init__(self.state)

    def restart_devices(self, selected_ips: list[str], emit_progress: Callable = None):
        """
        Restarts the devices specified by their IP addresses.
        This method clears any existing device errors, resets the state, and manages
        threads to restart the specified devices. If any errors occur during the 
        restart process, they are collected and returned.
        
        Args:
            selected_ips (list[str]): A list of IP addresses of the devices to restart.
            emit_progress (Callable, optional): A callable function to emit progress updates. 
                Defaults to None.
        
        Returns:
            (dict): A dictionary containing errors encountered during the restart process, 
                    if any. If no errors occur, an empty dictionary is returned.
        """
        self.devices_errors.clear()
        self.emit_progress: Callable = emit_progress
        self.state.reset()
        super().manage_threads_to_devices(selected_ips=selected_ips, function=self.restart_device)

        if len(self.devices_errors) > 0:
            return self.devices_errors
        
    def restart_device(self, device: Device):
        """
        Restart the specified device by establishing a connection, sending a restart command, 
        and handling any potential errors during the process.

        Args:
            device (Device): The device object containing details such as IP address, 
                             communication type, and model information.

        Raises:
            ConnectionFailedError: If the connection to the device fails.
            BaseError: For any other unexpected errors during the restart process.

        Notes:
            - Uses a connection manager to handle the device connection and restart operation.
            - Updates the device error state in a thread-safe manner using a lock.
            - Ensures the connection is properly closed in the `finally` block.
            - Tracks progress using the `ProgressTracker` class.
        """
        try:
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
        except ConnectionFailedError as e:
            pass
        except Exception as e:
            BaseError(3000, str(e))
        finally:
            if conn_manager.is_connected():
                conn_manager.disconnect()
            ProgressTracker(self.state, self.emit_progress).update(device)
        return

class ConnectionsInfo(OperationManager):
    def __init__(self):
        """
        Initializes the ProgramManager instance.

        This constructor sets up the shared state and initializes a dictionary
        to store connection information. It also calls the superclass initializer
        with the shared state.

        Attributes:
            state (SharedState): An instance of SharedState to manage shared resources.
            connections_info (dict[str, ConnectionInfo]): A dictionary mapping connection
                identifiers to their respective ConnectionInfo objects.
        """
        self.state = SharedState()
        self.connections_info: dict[str, ConnectionInfo] = {}
        super().__init__(self.state)

    def obtain_connections_info(self, selected_ips: list[str], emit_progress: Callable = None):
        """
        Obtains connection information for a list of selected IPs and manages the threading process 
        to retrieve this information from devices.
        
        Args:
            selected_ips (list[str]): A list of IP addresses to connect to and retrieve information from.
            emit_progress (Callable, optional): A callable function to emit progress updates during 
                the operation. Defaults to None.
        
        Returns:
            (dict): A dictionary containing connection information for the devices if any connections 
                    were successfully established. Returns an empty dictionary if no connections were made.
        """
        self.connections_info.clear()
        self.emit_progress: Callable = emit_progress
        self.state.reset()

        super().manage_threads_to_devices(selected_ips=selected_ips, function=self.obtain_connection_info)

        if len(self.connections_info) > 0:
            return self.connections_info
        
    def obtain_connection_info(self, device: Device):
        """
        Establishes a connection to a device, retrieves its connection information, 
        and updates the connection status.

        Args:
            device (Device): The device object containing information such as IP, 
                             communication type, and model name.

        Raises:
            ConnectionFailedError: If the connection to the device fails due to a 
                                   network error.
            BaseError: If any other unexpected exception occurs during the process.

        Workflow:
            1. Initializes a connection manager for the device using its IP and 
               communication type.
            2. Attempts to connect to the device with retries.
            3. Pings the device to verify connectivity.
            4. If the ping is successful, retrieves device information and updates 
               the connection info.
            5. If the ping fails or a network error occurs, marks the connection 
               as failed and raises a ConnectionFailedError.
            6. Updates the shared connection information dictionary with the 
               device's connection status.
            7. Ensures the connection is properly disconnected in the `finally` block.
            8. Updates the progress tracker and logs the completion of the process.

        Note:
            This method uses a lock to ensure thread-safe updates to the shared 
            `connections_info` dictionary.
        """
        try:
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
        except ConnectionFailedError:
            pass
        except Exception as e:
            BaseError(3000, str(e))
        finally:
            if conn_manager.is_connected():
                conn_manager.disconnect()
            ProgressTracker(self.state, self.emit_progress).update(device)
            logging.debug(f"Finalizando {device.ip}")
        return