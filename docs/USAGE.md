# Guía de Uso de PyZKTecoClocks

> ⚠️ **Nota / Note:**  
> Esta página está disponible _solo en Español_ temporalmente.  
> This page is currently available _in Spanish only_.

## Tabla de Contenidos

1. [Introducción](#introduccion)
2. [Interfaz de usuario](#interfaz-de-usuario)
3. [Programa Reloj de Asistencias](#programa-reloj-de-asistencias)
   - [Acciones principales](#acciones-principales)
     - [Lista de acciones](#lista-de-acciones)
     - [Modificar dispositivos](#modificar-dispositivos)
     - [Reiniciar dispositivos](#reiniciar-dispositivos)
     - [Probar conexiones](#probar-conexiones)
     - [Actualizar hora](#actualizar-hora)
     - [Obtener marcaciones](#obtener-marcaciones)
   - [Configuración en acciones principales](#configuracion-en-acciones-principales)
   - [Acciones de configuración del menú contextual](#acciones-de-configuracion-del-menu-contextual)
   - [Otras acciones](#otras-acciones)
4. [Servicio Reloj de Asistencias](#servicio-reloj-de-asistencias)
   - [Acciones principales del servicio](#acciones-principales-del-servicio)
   - [Configuración del servicio](#configuracion-del-servicio)
   - [Comportamiento del servicio](#comportamiento-del-servicio)
5. [Carpetas generadas](#carpetas-generadas)
6. [Archivos generados](#archivos-generados)
   - [Por el usuario](#por-el-usuario)
   - [Por el programa y el servicio](#por-el-programa-y-el-servicio)
   - [Logs](#logs)
7. [Archivo de configuración ](#archivo-de-configuracion-configini)[`config.ini`](#archivo-de-configuracion-configini)
   - [Resumen de parámetros](#resumen-de-parametros)
   - [Attendance\_status](#attendance_status)
   - [Cpu\_config](#cpu_config)
   - [Device\_config](#device_config)
   - [Program\_config](#program_config)
   - [Network\_config](#network_config)

---

## Introducción

Este documento describe cómo utilizar las herramientas **Programa Reloj de Asistencias** y **Servicio Reloj de Asistencias** del proyecto **PyZKTecoClocks**. Aquí encontrarás:

- Descripción de las interfaces de usuario.
- Detalle de cada acción disponible.
- Explicación de la configuración y de los archivos generados.
- Estructura de las carpetas y logs.

---

## Interfaz de usuario

El proyecto cuenta con dos aplicaciones independientes, cada uno con su propia interfaz de bandeja. Al hacer clic derecho sobre el ícono, se despliega un menú contextual con acciones propias del ejecutable.

Ver apartados [Programa Reloj de Asistencias](#programa-reloj-de-asistencias) y [Servicio Reloj de Asistencias](#servicio-reloj-de-asistencias) para más información.

## Programa Reloj de Asistencias

Para usar el programa, ejecutar `Programa Reloj de Asistencias.exe`. Para ello, asegúrese de tener en el directorio raíz donde se encuentran los ejecutables, los archivos `config.ini` (ver [Archivo de configuración](#archivo-de-configuracion-configini)) y `info_devices.txt` (ver [Archivos generados por el usuario](#por-el-usuario)).

### Acciones principales

El menú contextual del programa ofrece cinco acciones principales que abren ventanas con tablas interactivas y controles de ejecución.

#### Lista de acciones

| Acción                                            | Descripción breve                                                 |
| ------------------------------------------------- | ----------------------------------------------------------------- |
| [Modificar dispositivos](#modificar-dispositivos) | Edita `info_devices.txt` desde una tabla interactiva.             |
| [Reiniciar dispositivos](#reiniciar-dispositivos) | Envía comando de reinicio y muestra progreso con barra y alertas. |
| [Probar conexiones](#probar-conexiones)           | Verifica conexión, marcaciones, serie, plataforma y firmware.     |
| [Actualizar hora](#actualizar-hora)               | Sincroniza la hora de los dispositivos seleccionados.             |
| [Obtener marcaciones](#obtener-marcaciones)       | Descarga registros y sincroniza hora, con gestión de errores.     |

Cada acción incluye **Tiempo de Espera** y **Reintentos** (ver [Configuración en acciones principales](#configuracion-en-acciones-principales)) y utiliza variables de `config.ini` (ver [Archivo de configuración](#archivo-de-configuracion-configini)). Además, genera archivos de log mensuales en la carpeta `logs/` (ver [Carpetas generadas](#carpetas-generadas)).

#### Modificar dispositivos

Abre una ventana en la que permite modificar el archivo `info_devices.txt` a través de una tabla que contiene los dispositivos configurados para las acciones de:

- Reiniciar dispositivos
- Probar conexiones
- Actualizar hora
- Obtener marcaciones

La tabla es interactiva: al hacer doble clic sobre cualquier campo, se habilita la edición in situ, pero **no** se guardan los cambios en tiempo real en el archivo.

**Botones disponibles:**

- **Cargar**: recarga desde `info_devices.txt` todos los dispositivos y actualiza la tabla.
- **Modificar**: guarda en `info_devices.txt` los cambios realizados en la tabla.
- **Agregar**: abre un formulario para incluir un nuevo dispositivo; solicita:
    - Distrito  
    - Modelo  
    - Punto de marcación  
    - IP  
    - Tipo de comunicación (TCP o UDP)
- **Activar todo**: marca la casilla "Activo" para **todos** los dispositivos listados, de modo que aparezcan y estén disponibles en las demás ventanas de acciones.
- **Desactivar todo**: desmarca la casilla "Activo" para **todos** los dispositivos listados, de modo que queden ocultos y no se incluyan en las demás acciones.

#### Reiniciar dispositivos
Abre una ventana con:

- **Inputs**:
    - Tiempo de Espera  
    - Reintentos
    
    (Ver [Configuración en acciones principales](#configuracion-en-acciones-principales)).
    
- **Tabla interactiva** de dispositivos activos (selección mediante clic izquierdo).
- **Botones disponibles:**
    - **Reiniciar dispositivos**: envía el comando de reinicio a cada dispositivo seleccionado; se muestra:
        - Barra de progreso verde indicando avance.  
        - Conteo “dispositivos finalizados / total activos”.
        - Al finalizar, ventana emergente con listado de dispositivos cuya conexión falló.
    - **Seleccionar todo**: marca todos los dispositivos para reinicio.  
    - **Deseleccionar todo**: desmarca todos.

Esta acción utiliza las variables del `config.ini`:

- `threads_pool_max_size`  
- `retry_connection`  
- `timeout`

(Ver [Archivo de configuración](#archivo-de-configuracion-configini)).

#### Probar conexiones

Abre una ventana con:

- **Inputs**:
    - Tiempo de Espera  
    - Reintentos
    
    (Ver [Configuración en acciones principales](#configuracion-en-acciones-principales)).
    
- **Tabla interactiva** de dispositivos activos (selección mediante clic izquierdo).
- **Botones disponibles:**
    - **Probar conexiones**: envía comandos a cada dispositivo seleccionado; despliega:
        - Barra de progreso verde y conteo “finalizados / total”.
        - Al completar, la tabla añade las columnas:
            - **Estado de Conexión**: "Conectado" o "Error".  
            - **Cant. de Marcaciones**: número de registros ("No aplica" si 0).  
            - **Número de Serie**  
            - **Plataforma**  
            - **Firmware**  
        - Coloreado de celdas:
            - Verde si el valor fue obtenido correctamente.  
            - Gris con leyenda "No aplica" si el campo no corresponde.  
            - Rojo si hubo fallo de conexión o de obtención.
    - **Seleccionar todo** / **Deseleccionar todo**.

Esta acción utiliza las variables del `config.ini`:

- `threads_pool_max_size`  
- `retry_connection`  
- `size_ping_test_connection`  
- `timeout`

(Ver [Archivo de configuración](#archivo-de-configuracion-configini)).

#### Actualizar hora

Abre una ventana con:

- **Inputs**:
    - Tiempo de Espera  
    - Reintentos
    
    (Ver [Configuración en acciones principales](#configuracion-en-acciones-principales)).
    
- **Tabla interactiva** de dispositivos activos (selección mediante clic izquierdo).
- **Botones disponibles:**
    - **Actualizar hora**: envía comando a cada dispositivo seleccionado; muestra barra de progreso.
    - **Seleccionar todo** / **Deseleccionar todo**.

    - Al finalizar, la tabla añade:
        - **Estado de Conexión**: "Conectado" (verde) o "Error" (rojo).
        - **Estado de Pila**: 
          - "Pila funcionando" (verde)  
          - "Pila fallando" (rojo)  
          - "No aplica" (gris) si hubo error de conexión.

Esta acción utiliza las variables del `config.ini`:

- `threads_pool_max_size`  
- `retry_connection`  
- `timeout`

(Ver [Archivo de configuración](#archivo-de-configuracion-configini)).

#### Obtener marcaciones

Abre una ventana con:

- **Inputs**:
    - Tiempo de Espera  
    - Reintentos
    
    (Ver [Configuración en acciones principales](#configuracion-en-acciones-principales)).

- **Tabla interactiva** de dispositivos activos (selección mediante clic izquierdo).
- **Botones disponibles:**
    - **Obtener marcaciones**: envía comandos para descargar marcaciones, sincronizar la hora, actualizar el modelo en el nombre de las carpetas ubicadas en `devices/{distrito}/`; muestra barra de progreso con conteo.
    - **Seleccionar todo** / **Deseleccionar todo**.
    - **Reintentar todos** / **Reintentar fallidos** (aparecen si hubo fallos).

Al terminar, se agrega:

- **Cant. de Marcaciones**: número de marcaciones descargadas (verde con cantidad) o "Conexión fallida" (rojo).

**Gestión de errores de formato:**

- Dispositivos con registros fuera de rango (más de 3 meses antiguos o fechas futuras al día de hoy) mostrarán hipervínculos a sus archivos.
- Si "Eliminar marcaciones" está activo, permite forzar eliminación en próxima ejecución; luego se deshabilita.
- Si no, solo listará enlaces a archivos afectados.

Archivos de salida diarios: `devices/{distrito}/{modelo}-{punto_de_marcacion}/` y `%ProgramData%/.../Backup/devices/{distrito}/{modelo}-{punto_de_marcacion}/` (ver [Carpetas generadas](#carpetas-generadas)).

### Configuración en acciones principales

- **Tiempo de Espera**: modifica `timeout` (segundos) en `config.ini`.
- **Reintentos**: modifica `retry_connection` (intentos) en `config.ini`.

### Acciones de configuración del menú contextual

- **Eliminar marcaciones**: edita `clear_attendance` en `config.ini`.
- **Iniciar automáticamente**: registra programa en inicio del sistema.

### Otras acciones

- **Salir**: cierra el programa.

---

## Servicio Reloj de Asistencias

El servicio se compone de 2 ejecutables: `schedulerService.exe` y `Servicio Reloj de Asistencias.exe`.

  - `schedulerService.exe` es el servicio automático per se.
  - `Servicio Reloj de Asistencias.exe` es el gestor del servicio. Con él, se pueden hacer las acciones tabuladas en la siguiente sección.

Para usar el servicio, ejecutar `Servicio Reloj de Asistencias.exe`. Para ello, asegúrese de tener en el directorio raíz donde se encuentran los ejecutables, los archivos `config.ini` (ver [Archivo de configuración](#archivo-de-configuracion-configini)), `info_devices.txt` y `schedule.txt` (ver [Archivos generados por el usuario](#por-el-usuario)).

### Acciones principales del servicio

| Acción               | Descripción                             |
| -------------------- | --------------------------------------- |
| Iniciar servicio     | Arranca el servicio manualmente.        |
| Detener servicio     | Detiene la ejecución del servicio.      |
| Reiniciar servicio   | Detiene y vuelve a iniciar el servicio. |
| Reinstalar servicio  | Reinstala el servicio en el sistema.    |
| Desinstalar servicio | Elimina el servicio del sistema.        |

### Configuración del servicio

- **Eliminar marcaciones**: edita `clear_attendance_service` en `config.ini`.
- **Iniciar automáticamente**: registra servicio en inicio del sistema.

### Comportamiento del servicio

- Arranca automáticamente al ejecutar el ejecutable.
- Permanece activo tras cerrar la app, siguiendo `schedule.txt`.
- Usa dispositivos activos en `info_devices.txt`.
- No elimina marcaciones erróneas; el programa las procesa en la próxima ejecución de “Obtener marcaciones”.

---

## Carpetas generadas

| Ruta                                                   | Descripción                                          |
| ------------------------------------------------------ | ---------------------------------------------------- |
| `devices/{distrito}/{modelo}-{punto_de_marcacion}/`                   | Marcaciones organizadas por distrito y modelo / punto de marcación. |
| `logs/{año-mes}/`                                      | Logs mensuales de programa y servicio.               |
| `%ProgramData%/.../Backup/devices/{distrito}/{modelo}` | Copia de seguridad de archivos de asistencia.        |

---

## Archivos generados

### Por el usuario

- **schedule.txt**: define horarios de tareas (*no modificar títulos*).

  ```
  # Hours for gestionar_marcaciones_dispositivos
    ...
  # Hours for actualizar_hora_dispositivos
    ...
  ```

- **info\_devices.txt**: lista de dispositivos:

  ```
  DISTRITO - MODELO - PUNTO - IP - ID - TCP/UDP - Activado (True/False)
  ```

### Por el programa y el servicio

- `{name_attendances_file}.txt`: archivo global de marcaciones.
- `ip_date_file.cro`: registros por dispositivo y fecha en `devices/{distrito}/{modelo}-{punto_de_marcacion}/`.

### Logs

- **programa\_reloj\_de\_asistencias\_{VERSION}\_debug.log**: mensajes de depuración e info.
- **programa\_reloj\_de\_asistencias\_{VERSION}\_error.log**: advertencias y errores.
- **console\_log.txt**: logs de consola.
- **servicio\_reloj\_de\_asistencias\_{VERSION}\_debug.txt** y **\_error.txt**: logs del servicio.
- **icono\_reloj\_de\_asistencias\_{VERSION}\_{tipo}.txt**: logs del icono del servicio.

---

## Archivo de configuración `config.ini`

### Resumen de parámetros

| Sección            | Parámetro                    | Tipo     | Descripción                                                   |
| ------------------ | ---------------------------- | -------- | ------------------------------------------------------------- |
| Attendance\_status | IDs de tipo de marcación     | Entero   | Relaciona ID con tipo de marcación (face, fingerprint, card). |
| Cpu\_config        | threads\_pool\_max\_size     | Entero   | Máximo de conexiones paralelas en acciones de red.            |
| Device\_config     | clear\_attendance            | Booleano | Elimina marcaciones en ejecución manual.                      |
|                    | clear\_attendance\_service   | Booleano | Elimina marcaciones en servicio programado.                   |
|                    | disable\_device              | Booleano | Bloqueo del dispositivo al acceder (no recomendado).          |
| Program\_config    | name\_attendances\_file      | Cadena   | Nombre del archivo global de marcaciones.                     |
| Network\_config    | retry\_connection            | Entero   | Cantidad de reintentos en operaciones de red.                 |
|                    | size\_ping\_test\_connection | Entero   | Paquetes enviados en test de conexión.                        |
|                    | timeout                      | Entero   | Segundos antes de considerar caída de conexión.               |

### Attendance\_status

Asocia IDs con tipos de marcación.

Ejemplo en `config.ini`:

```ini
[Attendance_status]
status_face = 2
status_fingerprint = 1
status_card = 3
```

### Cpu\_config

- `threads_pool_max_size`: conexiones paralelas.

Ejemplo en `config.ini`:

```ini
[Cpu_config]
threads_pool_max_size = 50
```

### Device\_config

- `clear_attendance`: elimina marcaciones manuales.
- `clear_attendance_service`: elimina marcaciones en el servicio.
- `disable_device`: bloquea dispositivo al acceder (no recomendado).

Ejemplo en `config.ini`:

```ini
[Device_config]
clear_attendance = False
force_clear_attendance = False
clear_attendance_service = False
disable_device = False
```

### Program\_config

- `name_attendances_file`: nombre del archivo global de marcaciones.

Ejemplo en `config.ini`:

```ini
[Program_config]
name_attendances_file = attendances_file
```

### Network\_config

- `retry_connection`: reintentos en operaciones de red.
- `size_ping_test_connection`: paquetes en test de conexión.
- `timeout`: segundos de espera.

Ejemplo en `config.ini`:

```ini
[Network_config]
retry_connection = 3
size_ping_test_connection = 5
timeout = 15
```

---

*Fin de la documentación.*