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

import sys
import os
import time
import schedule
import configparser
import tkinter as tk
import threading
from tkinter import messagebox
from pystray import MenuItem as item
from pystray import Icon, Menu
from PIL import Image
from ..conn.attendances_manager import *
from ..conn.hour_manager import *
from ..file_manager import cargar_desde_archivo
from ..utils import logging

# Para leer un archivo INI
config = configparser.ConfigParser()
config.read('config.ini')

class TrayApp:
    def __init__(self):
        logging.debug('hola')
        self.is_running = False
        self.schedule_thread = None
        self.colorIcon = "red"
        logging.debug('hola')
        self.checked = eval(config['Device_config']['clear_attendance'])
        logging.debug('hola')
        self.icon = self.create_tray_icon()
        logging.debug('hola')
        self.configurar_schedule(self.icon)

    def start_execution(self, icon):
        self.is_running = True
        self.set_icon_color(icon, "green")
        # Inicia un hilo para ejecutar run_pending() en segundo plano
        try:
            self.schedule_thread = threading.Thread(target=self.run_schedule)
            logging.debug('Hilo iniciado...')
            self.schedule_thread.start()
        except Exception as e:
            logging.critical(e)

    def run_schedule(self):
        # Función para ejecutar run_pending() en segundo plano
        try:
            while self.is_running:
                logging.debug('Hilo en ejecucion...')
                schedule.run_pending()
                time.sleep(1)
        except Exception as e:
            logging.error(e)

    def stop_execution(self, icon):
        self.is_running = False
        if self.schedule_thread and self.schedule_thread.is_alive():
            self.schedule_thread.join()  # Esperar a que el hilo termine
        logging.debug('Hilo detenido...')
        # schedule.clear()
        self.set_icon_color(icon, "red")

    def restart_execution(self, icon):
        # Función para reiniciar el servicio
        self.stop_execution(icon)
        self.start_execution(icon)

    def create_tray_icon(self):
        '''
            Crear ícono en la bandeja del sistema
        '''
        logging.debug(getattr(sys, 'frozen', False))
        filePath = os.path.join(self.directorio_de_ejecucion(), "resources", "system tray", f"circle-{self.colorIcon}.png")
        image = Image.open(filePath)
        
        try:
            icon = Icon("GestorRelojAsistencias", image, "Gestor Reloj de Asistencias", menu=Menu(
                item('Iniciar', self.start_execution),
                item('Detener', self.stop_execution),
                item('Reiniciar', self.restart_execution),
                item('Probar conexiones', self.opc_probar_conexiones),
                item('Actualizar hora', self.opc_actualizar_hora_dispositivos),
                item('Obtener marcaciones', self.opc_marcaciones_dispositivos),
                item('Obtener cantidad de marcaciones', self.opc_mostrar_cantidad_marcaciones),
                item('Eliminar marcaciones', self.toggle_checkbox_clear_attendance, checked=lambda item: self.checked, radio=True),
                item('Salir', self.exit_icon)
                )
            )
        except Exception as e:
            logging.error(e)

        return icon

    def opc_probar_conexiones(self, icon):
        ping_devices()
        return
    
    def opc_actualizar_hora_dispositivos(self, icon):
        tiempo_inicial = self.iniciar_cronometro()
        actualizar_hora_dispositivos()
        self.finalizar_cronometro(icon, tiempo_inicial)
        return
    
    def iniciar_cronometro(self):
        return time.time()
    
    def finalizar_cronometro(self, icon, tiempo_inicial):
        tiempo_final = self.iniciar_cronometro()
        tiempo_transcurrido = tiempo_final - tiempo_inicial
        icon.notify(f'La tarea finalizó en {tiempo_transcurrido:.2f} segundos')
        return

    def opc_marcaciones_dispositivos(self, icon):
        tiempo_inicial = self.iniciar_cronometro()
        gestionar_marcaciones_dispositivos()
        self.finalizar_cronometro(icon, tiempo_inicial)
        return

    # Definir una función para cambiar el estado de la checkbox
    def toggle_checkbox_clear_attendance(self, icon, item):
        self.checked = not item.checked
        logging.debug(f"Status checkbox: {self.checked}")
        # Modificar el valor del campo deseado
        config['Device_config']['clear_attendance'] = str(self.checked)
        # Escribir los cambios de vuelta al archivo de configuración
        with open('config.ini', 'w') as config_file:
            config.write(config_file)
    
    def opc_mostrar_cantidad_marcaciones(self, icon, item):
        # Crear una ventana emergente de tkinter
        root = tk.Tk()
        root.withdraw()  # Ocultar la ventana principal
        cantidad_marcaciones = obtener_cantidad_marcaciones()
        cantidad_marcaciones_str = "\n".join([f"{ip}: {cantidad}" for ip, cantidad in cantidad_marcaciones.items()])

        # Mostrar un cuadro de diálogo con la información
        messagebox.showinfo("Marcaciones por dispositivo", cantidad_marcaciones_str)

        # Cerrar la ventana emergente de tkinter
        #self.root.quit()

        # Cerrar la ventana emergente de tkinter
        #root.after(0, root.destroy)  # Programar la destrucción de la ventana para después de que termine mainloop

    def set_icon_color(self, icon, color):
        # Función para cambiar el color del ícono
        self.colorIcon = color
        filePath = os.path.join(self.directorio_de_ejecucion(), "resources", "system tray", f"circle-{self.colorIcon}.png")
        image = Image.open(filePath)
        icon.update_menu()
        icon.icon = image
    
    def directorio_de_ejecucion(self):
        # Obtener la ruta del directorio del script
        root_dir = os.path.dirname(os.path.abspath(__file__))
        while os.path.basename(root_dir) != "PyZKTecoClocks":
            root_dir = os.path.dirname(root_dir)
        # Verificar si el script se está ejecutando desde un ejecutable de PyInstaller
        
        if getattr(sys, 'frozen', False):
            os.path.join(root_dir, os.path.basename(sys.argv[0]))
        logging.debug(root_dir)
        return root_dir

    def exit_icon(self, icon, item):
        # Función para salir del programa
        try:
            logging.debug(schedule.get_jobs())
            if len(schedule.get_jobs()) >= 1:
                self.stop_execution(icon)
            icon.stop()
        except Exception as e:
            logging.critical(e)

    def configurar_schedule(self, icon):
        '''
        Configura las tareas programadas en base a las horas cargadas desde el archivo.
        '''

        # Lee las horas de ejecución desde el archivo de texto
        filePath = os.path.join(os.path.abspath('.'), 'schedule.txt')
        hoursToPerform = None
        try:
            hoursToPerform = cargar_desde_archivo(filePath)
        except Exception as e:
            logging.error(e)

        if hoursToPerform: 
            # Itera las horas de ejecución
            for hourToPerform in hoursToPerform:
                '''
                Ejecuta la tarea de actualizar hora y guarda las 
                marcaciones en archivos (individual y en conjunto)
                en la hora especificada en schedule.txt
                '''

                schedule.every().day.at(hourToPerform).do(gestionar_marcaciones_dispositivos)