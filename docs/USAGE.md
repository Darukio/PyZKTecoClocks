# PyZKTecoClocks
## Ejecutables del proyecto
El proyecto contiene 2 ejecutables, "Programa Reloj de Asistencias" y "Servicio Reloj de Asistencias".

## Interfaz de ejecutables
Tanto el ejecutable del programa como el del servicio agregan un ícono en la bandeja del sistema. Al hacer clic derecho sobre este ícono, se despliega un menú contextual con distintas acciones, organizadas según su procedencia (del programa o del servicio).
    
## "Programa Reloj de Asistencias"
### Acciones principales del menú contextual
El menú contextual del programa incluye cinco acciones:

- Modificar dispositivos
- Reiniciar dispositivos
- Probar conexiones
- Actualizar hora
- Obtener marcaciones
Cada una de estas acciones abre una ventana emergente con una estructura similar.

#### Modificar dispositivos
Abre una ventana en la que permite modificar el archivo info_devices.txt a través de una tabla, la cual contiene aquellos dispositivos que se conectarán al presionar las acciones "Reiniciar dispositivos", "Probar conexiones", "Actualizar hora" u "Obtener marcaciones".

La tabla en la que se encuentran los dispositivos es interactiva, al presionar 2 veces sobre un campo permite editarlo. Sin embargo, esto NO edita el archivo info_devices.txt en tiempo real.

La interfaz posee los siguientes botones:

- Cargar: Actualiza la tabla con los dispositivos que se encuentren cargados en info_devices.txt.
- Modificar: Guarda los cambios realizados sobre los dispositivos de la tabla en el archivo info_devices.txt.
- Agregar: Abre una ventana para poder añadir un nuevo dispositivo a la tabla. Solicita: Distrito, Modelo, Punto de marcación, IP y cuál es la forma de Comunicación (TCP o UDP).
- Activar todo: Tilda la casilla de activación de todos los dispositivos de la tabla. "Activado" implica que el dispositivo será visualizable (y podrá ser usable) en el resto de ventanas de acciones principales.
- Desactivar todo: Destilda la casilla de activación de todos los dispositivos de la tabla. "Desactivado" implica que el dispositivo no será visualizable (ni usable) en el resto de ventanas de acciones principales.

#### Reiniciar dispositivos
Abre una ventana que contiene 2 inputs a ingresar: "Tiempo de Espera" y "Reintentos" (ver apartado "Configuración en acciones principales" para más información); una tabla interactiva que muestra los dispositivos activos —seleccionables presionando clic derecho—; y un conjunto de acciones dispuesta en botones:

- Reiniciar dispositivos: Envía un comando de reinicio para cada uno de los dispositivos seleccionados en la tabla. Se podrá visualizar el progreso de la operación mediante una barra verde que simboliza el progreso, la cantidad de dispositivos finalizados / la cantidad de dispositivos activos en total.
Tras finalizar, informa por medio de una ventana emergente los dispositivos cuya conexión falló.
- Seleccionar todo: Selecciona todas las celdas de dispositivos para su posterior conexión en "Reiniciar dispositivos".
- Deseleccionar todo

Esta ación hace uso de las variables "threads_pool_max_size", "retry_connection" y "timeout" del archivo config.ini (ver apartado "Archivo de configuración config.ini" para más información).

Esta acción genera archivos separados por meses en la carpeta logs/ (ver apartados "Archivos generados" y/o "Carpetas generadas" para más información).

#### Probar conexiones
Abre una ventana que contiene 2 inputs a ingresar: "Tiempo de Espera" y "Reintentos" (ver apartado "Configuración en acciones principales" para más información); una tabla interactiva que muestra los dispositivos activos —seleccionables presionando clic derecho—; y un conjunto de acciones dispuesta en botones:

- Probar conexiones: Envía comandos para obtener información acerca de la conexión y del dispositivo conectado, para cada uno de los seleccionados en la tabla. Se podrá visualizar el progreso de la operación mediante una barra verde que simboliza el progreso, la cantidad de dispositivos finalizados / la cantidad de dispositivos activos en total.
Tras finalizar, actualiza la tabla interactiva añadiendo las columnas "Estado de Conexión", "Cant. de Marcaciones", "Número de Serie", "Plataforma" y "Firmware".
Si la conexión no falla (y no falla para cada obtención de información), se mostrará el valor con la celda pintada de verde. Si el valor de la columna es 0, aplicará la leyenda "No aplica" y el color gris.
En caso contrario, si la conexión falla, la celda se pintará de rojo y el resto de columnas nuevas tendrán la leyenda "No aplica" y el color gris.
- Seleccionar todo: Selecciona todas las celdas de dispositivos para su posterior conexión en "Reiniciar dispositivos".
- Deseleccionar todo

Esta ación hace uso de las variables "threads_pool_max_size", "retry_connection", "size_ping_test_connection" y "timeout" del archivo config.ini (ver apartado "Archivo de configuración config.ini" para más información).

Esta acción genera archivos separados por meses en la carpeta logs/ (ver apartados "Archivos generados" y/o "Carpetas generadas" para más información).

#### Actualizar hora
Abre una ventana que contiene 2 inputs a ingresar: "Tiempo de Espera" y "Reintentos" (ver apartado "Configuración en acciones principales" para más información); una tabla interactiva que muestra los dispositivos activos —seleccionables presionando clic derecho—; y un conjunto de acciones dispuesta en botones:

- Actualizar hora: Envía un comando que actualizará la hora de cada uno de los dispositivos seleccionados en la tabla. Se podrá visualizar el progreso de la operación mediante una barra verde que simboliza el progreso, la cantidad de dispositivos finalizados / la cantidad de dispositivos activos en total.
Tras finalizar, actualiza la tabla interactiva añadiendo las columnas "Estado de Conexión" y "Estado de Pila".
Si la conexión no falla, se mostrará el valor con la celda pintada de verde. El estado de pila puede ser "Pila funcionando" (celda pintada de verde) o "Pila fallando" (celda pintada de rojo)
En caso contrario, si la conexión falla, la celda se pintará de rojo y el estado de pila tendrá la leyenda "No aplica" y el color gris.
- Seleccionar todo: Selecciona todas las celdas de dispositivos para su posterior conexión en "Reiniciar dispositivos".
- Deseleccionar todo

Esta ación hace uso de las variables "threads_pool_max_size", "retry_connection" y "timeout" del archivo config.ini (ver apartado "Archivo de configuración config.ini" para más información).

Esta acción genera archivos separados por meses en la carpeta logs/ (ver apartados "Archivos generados" y/o "Carpetas generadas" para más información).

#### Obtener marcaciones
Abre una ventana que contiene 2 inputs a ingresar: "Tiempo de Espera" y "Reintentos" (ver apartado "Configuración en acciones principales" para más información); una tabla interactiva que muestra los dispositivos activos —seleccionables presionando clic derecho—; y un conjunto de acciones dispuesta en botones:

- Obtener marcaciones: Envía un comando de obtención de marcaciones y de actualización de hora para cada uno de los dispositivos seleccionados en la tabla. Se podrá visualizar el progreso de la operación mediante una barra verde que simboliza el progreso, la cantidad de dispositivos finalizados / la cantidad de dispositivos activos en total.
Tras finalizar, actualiza la tabla interactiva añadiendo la columna "Cant. de Marcaciones".
Si la conexión no falla, se mostrará el valor con la celda pintada de verde.
En caso contrario, si la conexión falla, la celda se pintará de rojo y tendrá la leyenda "Conexión fallida".
- Seleccionar todo: Selecciona todas las celdas de dispositivos para su posterior conexión en "Reiniciar dispositivos".
- Deseleccionar todo

En el caso de que hayan conexiones que hayan fallado, se habilitan los botones "Reintentar todos" o "Reintentar fallidos".

Esta ación hace uso de las variables "status_face", "status_fingerprint", "status_card", "threads_pool_max_size", "clear_attendance", "force_clear_attendance", "name_attendances_file", "retry_connection" y "timeout" del archivo config.ini (ver apartado "Archivo de configuración config.ini" para más información).

- Puede eliminar marcaciones dependiendo de si se encuentra activado la acción "Eliminar marcaciones" del menú contextual.
- Si se traen marcaciones con formato erróneo, NO se eliminarán las marcaciones de ese dispositivo. Serán almacenadas y, al finalizar, se recorrerán todos los archivos individuales (de asistencias) con la leyenda del día de hoy, y se abrirá una ventana emergente que mostrará las ips de los dispositivos con marcaciones erróneas (fecha incorrecta, ya sea con marcaciones pasadas a 3 meses a partir de hoy, o futuras al día de hoy), y con hipervínculos a los archivos correspondientes.
Si se tiene habilitado el eliminado de marcaciones, preguntará al usuario si desea forzar el eliminado de marcaciones para que, en su próxima corrida, se eliminen las marcaciones de ese dispositivo. Luego de dicha corrida, se deshabilitará automáticamente el forzado de eliminación de marcaciones hasta la próxima vez que se encuentren marcaciones erróneas y esté habilitado el eliminado de marcaciones.
Si NO se tiene habilitado el eliminado de marcaciones, solamente mostrará los hipervínculos de los dispositivos con marcaciones erróneas.

Esta acción genera archivos separados por meses en la carpeta logs/, y archivos separados por días en las carpetas devices/{distrito}/{modelo}-{punto_de_marcacion}/ y %ProgramData%/Gestor Reloj de Asistencias Backup/devices/{distrito}/{modelo}-{punto_de_marcacion}/ (ver apartado "Archivo de configuración config.ini" para más información).

### Configuración en acciones principales
- "Tiempo de Espera": Este parámetro modifica el valor de "timeout" del archivo config.ini. Especifica la cantidad de tiempo en segundos que se esperará por cada conexión para considerarla como caída.
- "Reintentos": Luego de considerar caída una conexión, este parámetro entra en acción, el cual modifica el valor de "retry_connection" del archivo config.ini. Especifica la cantidad de reintentos que se realizarán por dispositivo hasta considerarlo como inaccesible.

### Acciones de configuración del menú contextual
- Eliminar marcaciones: Edita el parámetro "clear_attendance" del archivo config.ini. Si está tildado, se eliminarán las marcaciones. Sino, no.
- Iniciar automáticamente: Edita el registro del sistema para que el programa pueda iniciarse automáticamente cuando el sistema arranca. Si está tildado, iniciará automáticamente. Sino, no.

### Otras acciones del menú contextual
- Salir: Termina la ejecución del programa.

## "Servicio Reloj de Asistencias"
### Acciones principales del menú contextual
Hay 3 acciones en el menú contextual asociadas al servicio:

- Iniciar servicio
- Detener servicio
- Reiniciar servicio
- Reinstalar servicio
- Desinstalar servicio

### Acciones de configuración
- Eliminar marcaciones: Edita el parámetro "clear_attendance_service" del archivo config.ini. Si está tildado, se eliminarán las marcaciones. Sino, no.
- Iniciar automáticamente: Edita el registro del sistema para que el servicio pueda iniciarse automáticamente cuando el sistema arranca. Si está tildado, iniciará automáticamente. Sino, no.

### Comportamiento del servicio
-   El servicio automático se inicia cuando el ejecutable del servicio ("Servicio Reloj de Asistencias") se ejecuta.
-   Cuando se cierra la aplicación, el servicio NO se detiene, continúa ejecutando su rutina de tareas programadas en el archivo schedule.txt.
-   El servicio SIEMPRE hace uso de todos los dispositivos activos en info_devices.txt, es decir, aquellos que estén con la columna de activo en alguno de los siguientes: 'true', '1', 'yes', 'verdadero' o 'si'. No respeta case-sensitive.
-   Si se encuentran marcaciones erróneas, como en el caso del programa, el procedimiento del programa es NO eliminar las marcaciones. La próxima que se ejecute la operación "Obtener marcaciones" del programa, al finalizar, recorrerá los archivos en búsqueda de aquellas marcaciones erróneas en el día.

### Configuración del servicio
-   El parámetro "clear_attendance_service" de la sección "Device_config" del archivo config.ini indica si el servicio va a eliminar marcaciones cuando ejecuta la tarea programada "gestionar_marcaciones_dispositivos".

## Carpetas generadas
-   devices/{distrito}/{modelo}-{punto_de_marcacion}/ proporciona una jerarquía organizada para localizar fácilmente los diferentes distritos y, dentro de cada distrito, los diversos modelos según los puntos de marcación.
-   logs/{año}-{mes} contiene todos los archivos logs de la aplicación y el servicio.
-   %ProgramData%/Gestor Reloj de Asistencias Backup/devices/{distrito}/{modelo}-{punto_de_marcacion}/ corresponde a un backup de los archivos individuales de asistencias, con el fin de mantener la información en caso de fallo humano.

## Archivos generados

### Por el usuario
-   Con schedule.txt se configura el horario de ejecución de las tareas programadas "gestionar_marcaciones_dispositivos" y "actualizar_hora_dispositivos". NO MODIFICAR LOS TÍTULOS # Hours for gestionar_marcaciones_dispositivos - # Hours for actualizar_hora_dispositivos.
-   Con info_devices.txt se configuran los dispositivos que el programa va a iterar para la ejecución de las tareas de "actualizar_hora_dispositivo" o "gestionar_marcaciones_dispositivos". El archivo .txt posee el siguiente formato:
    
        DISTRITO - MODELO - PUNTO DE MARCACIÓN - IP - ID DE DISPOSITIVO - TIPO DE CONEXIÓN (TCP o UDP) - ACTIVACIÓN DEL DISPOSITIVO (True o False)
    Cualquier valor que sea true, 1, yes, verdadero o si se tomará como válido. No respeta case-sensitive. Cualquier otro valor se toma como default en False.
    Si se configura el booleano en True, el dispositivo se incluirá en la selección de dispositivos en las ventanas de acciones principales (programa) o en las operaciones automatizadas del servicio. Sino, no.

#### Archivo de configuración config.ini
En el archivo config.ini se pueden hallar varias secciones de configuración (y sus respectivos parámetros), las cuales son:

- Attendance_status: En cada parámetro, relaciona un id con la forma de marcar (status_face, status_fingerprint, status_card). Tipo de dato: Entero.
- Cpu_config: En esta sección hay parámetros útiles para la configuración de la cpu en tiempos de ejecución.
    - El parámetro "threads_pool_max_size" indica cuántas conexiones de dispositivos se deben realizar a la vez cuando se está ejecutando alguna acción de red. Tipo de dato: Entero.
- Device_config: En esta sección hay parámetros útiles para la configuración al momento de acceder a un dispositivo.
    - El parámetro "clear_attendance" indica si se debe eliminar las marcaciones del dispositivo cuando se obtengan a través de la ejecución manual (presionar la acción "Obtener marcaciones"). Tipo de dato: Booleano (True o False).
    - El parámetro "clear_attendance_service" indica si se debe eliminar las marcaciones del dispositivo cuando se obtengan a través del servicio (gobernado por schedule.txt). Tipo de dato: Booleano (True o False).
    - El parámetro "disable_device" indica si se debe bloquear el dispositivo cuando se acceda a este. NO RECOMENDADO, si está activo puede conectarse, bloquear y perder la conexión, el dispositivo queda bloqueado indefinidamente hasta que se lo reinicie. Tipo de dato: Booleano (True o False).
- Program_config: En esta sección hay parámetros útiles para la ejecución del programa.
    - El parámetro "name_attendances_file" establece cuál va a ser el nombre del archivo de marcaciones global cuando este sea generado. Tipo de dato: Cadena.
- Network_config: En esta sección hay parámetros útiles para la configuración de operaciones de red.
    - El parámetro "retry_connection" indica cuántas veces la aplicación va a intentar reconectar y realizar alguna operación de red. Tipo de dato: Entero.
    - El parámetro "size_ping_test_connection" indica cuántos paquetes van a ser enviados para realizar el test de conexión en la acción "Probar conexiones". Tipo de dato: Entero.
    - El parámetro "timeout" indica la cantidad de tiempo en segundos que se esperará por cada conexión para considerarla como caída. Tipo de dato: Entero.

### Por el programa
-   {name_attendances_file}.txt es un archivo global en donde se guardan todas las marcaciones, independiente del distrito, modelo o ip del dispositivo.
-   ip_date_file.cro es un archivo donde se guardan todas las marcaciones de un dispositivo (según ip) y fecha de marcación. Se encuentra ubicado en devices/{distrito}/{modelo}-{punto_de_marcacion}/. El formato del archivo es:

        Legajo Fecha Hora Status Punch
        24 22/03/2024 10:41 1 0

#### Logs
-   En programa_reloj_de_asistencias_{PROGRAM_VERSION}_debug.log se establecen mensajes de depuración, información, advertencias, errores comunes y críticos del programa.
-   En programa_reloj_de_asistencias_{PROGRAM_VERSION}_error.log se establecen mensajes de advertencias, errores comunes y críticos del programa.
-   En console_log.txt se guardan los mensajes de la consola (incluyendo excepciones no controladas) que está ejecutando el programa.
-   En servicio_reloj_de_asistencias_{SERVICE_VERSION}_debug.txt se establecen mensajes de depuración, información, advertencias, errores comunes y críticos del servicio.
-   En servicio_reloj_de_asistencias_{SERVICE_VERSION}_error.txt se establecen mensajes de advertencias, errores comunes y críticos del servicio.
-   En icono_reloj_de_asistencias_{SERVICE_VERSION}_debug.txt se establecen mensajes de depuración, información, advertencias, errores comunes y críticos del ejecutable del servicio.
-   En icono_reloj_de_asistencias_{SERVICE_VERSION}_error.txt se establecen mensajes de advertencias, errores comunes y críticos del ejecutable del servicio.