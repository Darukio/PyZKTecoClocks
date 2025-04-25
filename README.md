# PyZKTecoClocks

## Instalación

### Archivos necesarios para instalación
-   En requirements.txt se encuentran las dependencias necesarias para la ejecución del proyecto.

### Instalación de dependencias
```bash
# Ejecutar en cmd o PowerShell con permisos de admin
Set-ExecutionPolicy RemoteSigned
# Si es necesario, hacer cd carpeta-de-proyecto
python install.py # Instala las dependencias de forma global
```

### Instalación de servicio .exe
```bash
# Ejecutar en cmd o PowerShell con permisos de admin
pyinstaller --noconsole --onefile --hidden-import=eventlet.hubs.epolls --hidden-import=eventlet.hubs.kqueue --hidden-import=eventlet.hubs.selects --hidden-import=dns --hidden-import=dns.dnssec --hidden-import=dns.e164 --hidden-import=dns.hash --hidden-import=dns.namedict --hidden-import=dns.tsigkeyring --hidden-import=dns.update --hidden-import=dns.version --hidden-import=dns.zone --hidden-import=dns.versioned schedulerService.py
```

### Instalación de aplicación .exe
```bash
# Ejecutar en cmd o PowerShell con permisos de admin
pyinstaller.exe --noconsole --clean --onefile --version-file version_info.txt --hidden-import=eventlet.hubs.epolls --hidden-import=eventlet.hubs.kqueue --hidden-import=eventlet.hubs.selects --hidden-import=dns --hidden-import=dns.dnssec --hidden-import=dns.e164 --hidden-import=dns.hash --hidden-import=dns.namedict --hidden-import=dns.tsigkeyring --hidden-import=dns.update --hidden-import=dns.version --hidden-import=dns.zone --hidden-import=dns.versioned -n "Programa Reloj de Asistencias" -i "resources/fingerprint.ico" --add-data "json/errors.json;json/" --add-data "resources/window/*;resources/window" --add-data "resources/system_tray/*;resources/system_tray" --add-data "resources/fingerprint.ico;resources/" --noupx --log-level=INFO --debug all main.py
```

### Jerarquía de carpetas y módulos
.
├───resources/
│   └───system_tray/
└───scripts/
    ├───business_logic/
    │	├───attendances_manager.py
    │   ├───connection.py
    │   ├───device_manager.py
    │   └───hour_manager.py
    ├───ui/
    │	├───icon_manager.py
    │   ├───message_box.py
    │   └───window_manager.py
    └───utils/
     	├───add_to_startup.py
        ├───errors.py
        ├───file_manager.py
        └───logging.py