# PyZKTecoClocks

> ⚠️ **Nota / Note:**  
> Esta página está disponible _solo en Español_ temporalmente.  
> This page is currently available _in Spanish only_.

## ¿Qué es PyZKTecoClocks?

Librería y aplicaciones para gestionar relojes de asistencia ZKTeco desde Python:

- **Programa Reloj de Asistencias**: GUI de escritorio para reiniciar dispositivos, probar conexiones, sincronizar hora y descargar marcaciones.  
- **Servicio Reloj de Asistencias**: Demonio programable en segundo plano para automatizar tareas de asistencia.

## Instalación rápida

**1. Prerrequisitos**

    - Python 3.7+  
    - Windows 10 o superior

**2. Clona e instala**

```bash
git clone <repo-url> && cd PyZKTecoClocks
python install.py
```

**3. Construir ejecutables**

Ejecuta en PowerShell (como administrador):

**3.1. Programa:**

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

**3.2. Ejecutable del Servicio:**

```bash
pyinstaller --noconsole --clean --version-file version_info.txt --onefile --hidden-import=eventlet.hubs.epolls --hidden-import=eventlet.hubs.kqueue --hidden-import=eventlet.hubs.selects --hidden-import=dns --hidden-import=dns.dnssec --hidden-import=dns.e164 --hidden-import=dns.hash --hidden-import=dns.namedict --hidden-import=dns.tsigkeyring --hidden-import=dns.update --hidden-import=dns.version --hidden-import=dns.zone --hidden-import=dns.versioned --add-data "json/errors.json;json/" --noupx --log-level=INFO --debug all schedulerService.py
```

**3.3. GUI del servicio:**

```bash
pyinstaller.exe --noconsole --clean --version-file version_info.txt --onefile --hidden-import=eventlet.hubs.epolls --hidden-import=eventlet.hubs.kqueue --hidden-import=eventlet.hubs.selects --hidden-import=dns --hidden-import=dns.dnssec --hidden-import=dns.e164 --hidden-import=dns.hash --hidden-import=dns.namedict --hidden-import=dns.tsigkeyring --hidden-import=dns.update --hidden-import=dns.version --hidden-import=dns.zone --hidden-import=dns.versioned -n "Servicio Reloj de Asistencias" -i "resources/24-7.png" --add-data "resources/system_tray/*;resources/system_tray" --add-data "resources/24-7.png;resources/" --add-data "json/errors.json;json/" --noupx --log-level=INFO --uac-admin --debug all main.py
```

## Características

- Configuración flexible mediante `config.ini`, `schedule.txt` e `info_devices.txt`.  
- Logs detallados en `logs/` y backups en `%ProgramData%/`.  
- Interfaz de bandeja de sistema con menú contextual.

## Estructura del proyecto

```plaintext
.
├───docs        # MkDocs (USAGE.md, guías, referencias)
├───json        # Persistencia de datos
├───resources   # Iconos y assets UI
└───src         # Código fuente (business_logic, common, ui)
```

## Enlaces útiles

- [Guía de Uso completa](USAGE.md)  
- [Configuración (`config.ini`)](USAGE.md#archivo-de-configuracion-configini)  
- [Estructura detallada de carpetas y logs](USAGE.md#carpetas-generadas)