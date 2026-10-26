<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducción automática.** Esta página fue traducida automáticamente del inglés y no ha sido revisada por un humano. Puede contener errores, y ciertas instrucciones, comandos, descargas, disponibilidad de productos u otro contenido pueden variar según el idioma o la región. En caso de cualquier incoherencia o discrepancia, la versión original en inglés del playbook prevalecerá y será la que rija.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Desarrollo remoto con AMD Sync

## Descripción general

**AMD Sync** convierte tu laptop en una cabina de mando remota para la AMD Ryzen™ AI Halo. Evita la configuración manual de SSH, claves e IDE — instala AMD Sync y obtén acceso con un clic a una terminal remota, VS Code, JupyterLab y un panel en vivo de GPU/CPU/memoria en la Ryzen AI Halo.

Tu máquina local se mantiene familiar; cada comando, notebook y modelo se ejecuta en la Ryzen AI Halo.

> **Consejo**: Esta página contendrá cualquier actualización nueva de AMDSync. 

## Lo que aprenderás

- Habilitar SSH en la Ryzen AI Halo y conectarte a ella desde AMD Sync
- Iniciar VS Code, Terminal, JupyterLab y Live Metrics contra la Ryzen AI Halo con un clic
- Organizar el trabajo remoto usando las carpetas de proyecto administradas de AMD Sync

---

## Conceptos clave

AMD Sync tiene dos lados: un **cliente** (tu laptop, ejecutando la aplicación AMD Sync) y un **servidor** (la Ryzen AI Halo, ejecutando un servidor SSH al que AMD Sync se conecta mediante túnel). Todo lo que inicies desde AMD Sync — VS Code, una terminal, un notebook — se abre localmente pero se ejecuta en la Ryzen AI Halo.

> **Clientes compatibles:** Windows 11 y Linux. macOS no es compatible.

---

## Paso 1 — Habilitar SSH en la Ryzen AI Halo


> **Nota:** En Windows, la Ryzen AI Halo viene con el servidor SSH *deshabilitado de forma predeterminada*. En Linux, viene con el servidor SSH *habilitado de forma predeterminada*.

1. En la Ryzen AI Halo, abre el **AMD Ryzen™ AI Developer Center**.
2. Ve a la pestaña **Remote**.
3. Activa **SSH Server**.
4. Anota la **IP Address**, el **Port** y el **Username** que se muestran en **Server Information** — los pegarás en AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Nota:** Este es el AMD Developer Center para Windows. El de Linux puede tener una interfaz diferente, pero una funcionalidad remota similar.

> **Consejo:** AMD Sync solicita la **contraseña de inicio de sesión del sistema operativo** de ese usuario, no una contraseña del Developer Center.

---

## Paso 2 — Instalar AMD Sync en tu cliente

AMD Sync funciona en Windows 11 y Linux. Descarga el instalador para tu sistema operativo y sigue los pasos a continuación. Después de la instalación, haz clic en **Accept & Install** en la pantalla **Get Started** — AMD Sync se inicia automáticamente al finalizar.

### Windows

[Descargar AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Haz doble clic en `AMDSyncInstaller.exe`.
2. Haz clic en **Accept & Install**.

> Si el Firewall de Windows te lo solicita, permite el acceso de red a AMD Sync para que pueda comunicarse con la Ryzen AI Halo a través de SSH.

### Linux

Haz clic en el enlace para descargar tu formato preferido:

| Formato | Descarga | Comando de instalación |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Nota:** El Centro de Aplicaciones de Ubuntu puede marcar un `.deb` abierto localmente como *"Potencialmente inseguro."* Esa es la advertencia estándar para cualquier instalador local de terceros. Si al hacer doble clic en el `.deb` falla, usa el comando de terminal anterior.

---

## Paso 3 — Conectarte a tu Ryzen AI Halo

En el primer inicio, AMD Sync muestra el formulario **Add a Remote Device**. Complétalo usando los valores de la pestaña **Remote** del Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Campo | Notas |
|-------|-------|
| **Device Name** *(opcional)* | Una etiqueta amigable como `Ryzen AI Halo`. Por defecto es `Device 1`, `Device 2`, … |
| **Hostname or IP** | De la pestaña Remote |
| **SSH Port** | De la pestaña Remote (solo números) |
| **Username** | El nombre de tu cuenta de sistema operativo en la Ryzen AI Halo |
| **Password** | Tu contraseña de inicio de sesión del sistema operativo — oculta mientras escribes |

Haz clic en **Add Device**. Después de una breve pantalla de carga, verás **"Connection Successful"** y llegarás a la vista principal, que reside en tu bandeja del sistema. Haz clic fuera de la ventana para cerrarla; AMD Sync sigue ejecutándose y está a un clic de distancia.

> **Si la conexión falla,** AMD Sync vuelve al formulario con tus valores conservados. Las causas habituales son que SSH esté deshabilitado en la Ryzen AI Halo, una contraseña incorrecta, o que los dos dispositivos estén en redes diferentes.

---

## Paso 4 — Iniciar tu primera herramienta remota

La vista principal te ofrece cinco componentes de un clic — todos disponibles sin importar qué sistema operativo estén ejecutando el cliente y la Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Componente | Qué hace |
|-----------|--------------|
| **Directory** | Selecciona la carpeta en la Ryzen AI Halo en la que se abrirán VS Code, Terminal y JupyterLab. Por defecto es un espacio de trabajo administrado `Documents/AMD_Sync`. |
| **VS Code** | Abre VS Code localmente con un túnel SSH hacia la carpeta seleccionada. |
| **Terminal** | Abre una terminal local conectada mediante SSH a la Ryzen AI Halo, en la carpeta seleccionada. |
| **JupyterLab** | Inicia un proyecto de notebook conectado mediante SSH a la Ryzen AI Halo, delimitado a la carpeta seleccionada. |
| **Live Metrics** | Vista en tiempo real del uso de GPU, memoria y CPU en la Ryzen AI Halo. |

### Prueba VS Code

Para tu primer inicio, prueba **VS Code**. Las siguientes instrucciones son para Linux, pero la experiencia en Windows es similar.

1. Deja **Directory** en el valor predeterminado `~/Documents/AMD_Sync`.
2. Haz clic en **VS Code**.
3. AMD Sync crea `Documents/AMD_Sync/Project_1` en la Ryzen AI Halo y abre VS Code localmente, con un túnel hacia esa carpeta.

Ahora estás editando archivos que residen en la Ryzen AI Halo con tu configuración local de VS Code. Crea `helloworld.py`, agrega `print("hello world")`, abre la terminal integrada (`` Ctrl + ` ``) y ejecútalo:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

La barra de estado muestra **SSH: Linux** — prueba de que tu código se está ejecutando en la Ryzen AI Halo, no en tu laptop.
### Prueba la Terminal

Haz clic en **Terminal** para entrar por SSH a la misma carpeta sin soltar el teclado.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

En Windows, la terminal predeterminada es **PowerShell**; cámbiala a **Windows Command Prompt** desde el menú Settings si lo prefieres. En Linux, AMD Sync usa la terminal predeterminada de tu sistema.

---

## Cómo funciona el Directory

El menú desplegable **Directory** es el control individual más importante de AMD Sync: decide dónde aterriza en el Ryzen AI Halo cada herramienta que lances.

- **`~/Documents/AMD_Sync` (predeterminado)** — Lanzar VS Code o JupyterLab desde aquí crea automáticamente una carpeta de proyecto nueva (`Project_1`, `Project_2`, … para VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … para JupyterLab).
- **Carpetas de proyecto existentes** — Cualquier subcarpeta directa de `AMD_Sync` (incluidas las que crees manualmente en el Ryzen AI Halo) aparece en el menú desplegable. La última carpeta que usaste se convierte en la predeterminada la próxima vez.
- **Rutas personalizadas** — Escribe cualquier ruta absoluta para abrir una carpeta en otro lugar del Ryzen AI Halo. AMD Sync solo la *abre*: no creará carpetas fuera de `AMD_Sync`, y las rutas personalizadas no se guardan entre sesiones.

Si una ruta personalizada no funciona, AMD Sync te indica por qué: sintaxis inválida, la carpeta no existe, o la ruta apunta a un archivo.

---

## Live Metrics y JupyterLab

- **Live Metrics** — Un panel en vivo del uso de GPU, memoria y CPU. La forma más rápida de confirmar que una ejecución de entrenamiento remota realmente está utilizando el hardware.
- **JupyterLab** — Un proyecto de notebook completo conectado por SSH al Ryzen AI Halo, con su propia terminal integrada para combinar celdas de notebook y comandos de shell sin salir de la interfaz.

---

## Settings y múltiples dispositivos

El menú **Settings** tiene tres pestañas:

| Pestaña | Qué abarca |
|-----|----------------|
| **Devices** | Enumera todos los Ryzen AI Halo a los que te has conectado exitosamente. Reconéctate, edita credenciales o agrega un nuevo dispositivo. |
| **Information** | Enlaces a documentación y soporte en el foro. |
| **Customize** | Reposiciona la app en tu escritorio, cambia el tipo de terminal (solo Windows) y verifica si hay actualizaciones de AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Tipo de terminal (Windows)** — Elige entre **PowerShell** (predeterminado) y **Windows Command Prompt**.
- **Tipo de terminal (Linux)** — Solo está disponible la terminal predeterminada del sistema.
- **Actualizaciones de la app** — Esta pestaña es el lugar indicado para buscar e instalar nuevas versiones de AMD Sync desde dentro de la interfaz; no se necesita un actualizador aparte.

> Un dispositivo solo aparece en **Devices** después de una primera conexión exitosa, por lo que los intentos fallidos no saturarán la lista.

---

## Solución de problemas

- **La conexión falla de inmediato** — Confirma que el servidor SSH esté habilitado en la pestaña **Remote** del Developer Center del Ryzen AI Halo.
- **Error de contraseña incorrecta** — Usa tu **contraseña de inicio de sesión del sistema operativo** en el Ryzen AI Halo, no contraseñas tomadas del Developer Center.
- **El botón de VS Code no hace nada** — Instala VS Code en tu máquina cliente desde [code.visualstudio.com](https://code.visualstudio.com).
- **Falta el ícono de bandeja de AMD Sync (Linux/GNOME)** — Instala y habilita la extensión AppIndicator.
- **El `.deb` no abre desde el administrador de archivos** — Usa `sudo apt install ./AMDSyncInstaller.deb` desde una terminal.
- **La configuración vuelve a aparecer en cada inicio (Linux)**: desbloquea tu llavero de inicio de sesión, o inicia con `--password-store=gnome-libsecret`, y luego repite la configuración una vez.

---