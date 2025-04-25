# PyZKTecoClocks
[![Docs](https://img.shields.io/badge/docs-online-blue.svg)](https://darukio.github.io/PyZKTecoClocks/)

## English

**Library and applications to manage ZKTeco attendance clocks from Python.**

### Features

- **Attendance Clock Program**: Desktop interface for manual operations (restart devices, test connections, synchronize time, and download attendance records).
- **Attendance Clock Service**: Executable to schedule and automate attendance tasks in the background.
- Flexible configuration using `config.ini`, `schedule.txt` and `info_devices.txt`.
- Detailed logging and data backup capabilities in `%ProgramData%`.

### Installation

#### Prerequisites

- Python 3.7+
- Windows 10 or later

#### Dependencies

All required packages are listed in `requirements.txt`.

```bash
# Run in cmd or PowerShell as administrator
Set-ExecutionPolicy RemoteSigned
# If needed, navigate to the project directory
git clone <repo-url> && cd PyZKTecoClocks
python install.py  # Installs dependencies globally
```

#### Building Executables
**Program:**
Run the following command in a Command Prompt or PowerShell window with administrator privileges.
```bash
pyinstaller.exe --noconsole --clean --onefile \
  --version-file version_info.txt \
  --hidden-import=eventlet.hubs.epolls \
  --hidden-import=eventlet.hubs.kqueue \
  --hidden-import=eventlet.hubs.selects \
  --hidden-import=dns \
  --hidden-import=dns.dnssec \
  --hidden-import=dns.e164 \
  --hidden-import=dns.hash \
  --hidden-import=dns.namedict \
  --hidden-import=dns.tsigkeyring \
  --hidden-import=dns.update \
  --hidden-import=dns.version \
  --hidden-import=dns.zone \
  --hidden-import=dns.versioned \
  -n "Programa Reloj de Asistencias" \
  -i "resources/fingerprint.ico" \
  --add-data "json/errors.json;json/" \
  --add-data "resources/window/*;resources/window" \
  --add-data "resources/system_tray/*;resources/system_tray" \
  --add-data "resources/fingerprint.ico;resources/" \
  --noupx \
  --log-level=INFO \
  --debug all \
  main.py
```

### Project Structure
```
.
├───docs                                # Documentation for MkDocs (includes USAGE.md)
│   └───mkdocs
│       └───docs                        # Actual Markdown files used by MkDocs
│                                       # (index, usage, installation, etc.)
├───json                                # JSON files used as data persistence
├───resources                           # Visual and UI resources
│   ├───system_tray                     # Icons and assets used in the system tray
│   └───window                          # Files related to application windows
└───scripts                             # Main source code of the program
    ├───business_logic                  # Core business logic of the application
    │                                   # Data processing, validation, business rules
    ├───common                          # Shared code between the main program and the service
    │   ├───business_logic              # Reusable business logic
    │   │   └───models                  # Common data models (e.g. Attendance, Device)
    │   ├───connection                  # Modules for connecting to devices
    │   │   └───zk                      # Specific implementation for ZKTeco devices
    │   └───utils                       # Utility functions, helpers, validators, logging, etc.
    └───ui
        └───components                  # UI components (widgets, windows, dialogs)
```

### Usage

For detailed installation and usage instructions, see the [Usage Guide](https://darukio.github.io/PyZKTecoClocks/USAGE/). Key sections include:

- [Introduction](https://darukio.github.io/PyZKTecoClocks/USAGE/#introduccion)
- [User Interface](https://darukio.github.io/PyZKTecoClocks/USAGE/#interfaz-de-usuario)
- [Attendance Clock Program](https://darukio.github.io/PyZKTecoClocks/USAGE/#programa-reloj-de-asistencias)
- [Attendance Clock Service](https://darukio.github.io/PyZKTecoClocks/USAGE/#servicio-reloj-de-asistencias)
- [Configuration File](https://darukio.github.io/PyZKTecoClocks/USAGE/#archivo-de-configuracion-configini)

---

*This README provides a high-level overview; for in-depth guidance, consult `docs/USAGE.md`.*

## Español

**Librería y aplicaciones para gestionar relojes de asistencia ZKTeco desde Python.**

### Características

- **Programa Reloj de Asistencias**: Interfaz de escritorio para operaciones manuales (reiniciar dispositivos, probar conexiones, sincronizar hora y descargar marcaciones).
- **Servicio Reloj de Asistencias**: Ejecutable para programar y automatizar tareas de marcaciones en segundo plano.
- Configuración flexible mediante `config.ini`, `schedule.txt` e `info_devices.txt`.
- Registro detallado (logs) y capacidad de copia de seguridad de datos en `%ProgramData%`.

### Instalación

#### Prerrequisitos

- Python 3.7+
- Windows 10 o superior

#### Dependencias

Todos los paquetes necesarios están listados en `requirements.txt`.

```bash
# Ejecutar en cmd o PowerShell con permisos de administrador
Set-ExecutionPolicy RemoteSigned
# Si es necesario, navegar al directorio del proyecto
git clone <url-del-repositorio> && cd PyZKTecoClocks
python install.py  # Instala las dependencias de forma global
```

#### Creación de ejecutables

**Programa:**
Ejecutar el siguiente comando en cmd o PowerShell con permisos de admin.
```bash
pyinstaller.exe --noconsole --clean --onefile \
  --version-file version_info.txt \
  --hidden-import=eventlet.hubs.epolls \
  --hidden-import=eventlet.hubs.kqueue \
  --hidden-import=eventlet.hubs.selects \
  --hidden-import=dns \
  --hidden-import=dns.dnssec \
  --hidden-import=dns.e164 \
  --hidden-import=dns.hash \
  --hidden-import=dns.namedict \
  --hidden-import=dns.tsigkeyring \
  --hidden-import=dns.update \
  --hidden-import=dns.version \
  --hidden-import=dns.zone \
  --hidden-import=dns.versioned \
  -n "Programa Reloj de Asistencias" \
  -i "resources/fingerprint.ico" \
  --add-data "json/errors.json;json/" \
  --add-data "resources/window/*;resources/window" \
  --add-data "resources/system_tray/*;resources/system_tray" \
  --add-data "resources/fingerprint.ico;resources/" \
  --noupx \
  --log-level=INFO \
  --debug all \
  main.py
```

### Estructura del proyecto

```
.
├───docs                                # Documentación para MkDocs (incluye USAGE.md)
│   └───mkdocs
│       └───docs                        # Archivos Markdown reales usados por MkDocs
│                                       # (índice, uso, instalación, etc.)
├───json                                # Archivos JSON usados como persistencia de datos
├───resources                           # Recursos visuales y de interfaz gráfica
│   ├───system_tray                     # Iconos y recursos usados en la bandeja del sistema
│   └───window                          # Archivos relacionados con las ventanas de la aplicación
└───scripts                             # Código fuente principal del programa
    ├───business_logic                  # Lógica de negocio principal de la aplicación
    │                                   # Procesamiento de datos, validación, reglas de negocio
    ├───common                          # Código compartido entre el programa principal y el servicio
    │   ├───business_logic              # Lógica de negocio reutilizable
    │   │   └───models                  # Modelos de datos comunes (p. ej. Attendance, Device)
    │   ├───connection                  # Módulos para conectar con dispositivos
    │   │   └───zk                      # Implementación específica para dispositivos ZKTeco
    │   └───utils                       # Funciones utilitarias, helpers, validadores, logging, etc.
    └───ui
        └───components                  # Componentes de la interfaz (widgets, ventanas, diálogos)
```

### Uso

Para instrucciones detalladas de instalación y uso, consulte la [Guía de Uso](https://darukio.github.io/PyZKTecoClocks/USAGE/). Secciones destacadas:

- [Introducción](https://darukio.github.io/PyZKTecoClocks/USAGE/#introduccion)
- [Interfaz de usuario](https://darukio.github.io/PyZKTecoClocks/USAGE/#interfaz-de-usuario)
- [Programa Reloj de Asistencias](https://darukio.github.io/PyZKTecoClocks/USAGE/#programa-reloj-de-asistencias)
- [Servicio Reloj de Asistencias](https://darukio.github.io/PyZKTecoClocks/USAGE/#servicio-reloj-de-asistencias)
- [Archivo de configuración](https://darukio.github.io/PyZKTecoClocks/USAGE/#archivo-de-configuracion-configini)
