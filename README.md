# Firefox NewUser

Script para ejecutar una instancia de Firefox con un usuario temporal creado dinámicamente **exclusivamente en entornos Wayland**. El usuario y todos sus datos se eliminan automáticamente al cerrar el navegador, garantizando una sesión limpia y aislada.

## Características

- **Aislamiento total:** Crea un usuario de sistema (`firefox_newuser`) exclusivo para la sesión.
- **Limpieza automática:** Elimina el usuario, su grupo y su directorio `/home` tras la ejecución.
- **Sincronización de archivos:** Permite mover archivos descargados o creados durante la sesión a un directorio persistente antes de la eliminación.
- **Optimizado para Wayland:** Utiliza la gestión de sesiones nativa para entornos modernos.

## Requisitos

- Python >= 3.10
- Privilegios de **root** (el script los solicitará mediante `su` si se ejecuta como usuario normal).
- Firefox instalado.
- Herramientas de sistema: `useradd`, `userdel`, `xhost`, `pkill`.

## Instalación

Si utilizas Poetry:

```bash
poetry install
```

## Uso

El proyecto expone un punto de entrada principal:

```bash
firefox_newuser --sync /ruta/de/destino
```
*Por defecto, los archivos se sincronizan en `/root` si no se especifica `--sync`.*

### 2. Wayland
```bash
firefox_newuser_wayland --sync /ruta/de/destino
```

## Configuración de Sonido (X11)

Para que el audio funcione correctamente en la sesión aislada bajo X11, es necesario configurar PulseAudio para que acepte conexiones anónimas a través de un socket compartido. 

Añade o modifica la siguiente línea en tu archivo `/etc/pulse/default.pa`:

```text
load-module module-native-protocol-unix auth-anonymous=1 socket=/tmp/my-pulse-socket-name
```

## Desarrollo

El proyecto utiliza `poethepoet` para tareas comunes:

- **Traducir mensajes:** `poe translate`
- **Preparar release:** `poe release`

## Licencia

Este proyecto está bajo la licencia **GPL-3.0-only**. Consulta el archivo `LICENSE.txt` para más detalles.
