import os
import pyuac
import subprocess
from pystray import MenuItem as item
from pystray import Icon, Menu
from PIL import Image
from service import is_service_running
from tasks_device_manager import actualizar_hora_dispositivos, cargar_marcaciones_dispositivos

# Crear ícono en la bandeja del sistema
def create_tray_icon():
    initial_color = "green" if is_service_running() else "red"
    filePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", f"circle-{initial_color}.png")
    image = Image.open(filePath)

    icon = Icon("MyService", image, "Gestor de Reloj de Asistencias", menu=Menu(
        item('Iniciar', start_service),
        item('Detener', stop_service),
        item('Reiniciar', restart_service),
        item('Actualizar hora', actualizar_hora_dispositivos),
        item('Obtener marcaciones', cargar_marcaciones_dispositivos),
        item('Salir', exit_icon)
    ))

    return icon

def exit_icon(icon, item):
    stop_service(icon)
    icon.stop()

def start_service(icon):
    if pyuac.isUserAdmin():
        set_icon_color(icon, "green")
        subprocess.run(["net", "start", "MyService"], shell=True)

def stop_service(icon):
    set_icon_color(icon, "red")
    subprocess.run(["net", "stop", "MyService"], shell=True)

def restart_service(icon):
    stop_service(icon)
    start_service(icon)

def set_icon_color(icon, color):
    # Función para cambiar el color del ícono
    filePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", f"circle-{color}.png")
    image = Image.open(filePath)
    icon.update_menu()
    icon.icon = image