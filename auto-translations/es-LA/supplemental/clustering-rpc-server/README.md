<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Este playbook utiliza etiquetas especiales que GitHub no puede renderizar. Visita [amd.com/playbooks](https://amd.com/playbooks) para previsualizar correctamente este contenido.
<!-- @github-only:end -->

# Cómo agrupar dos Ryzen™ AI Halo con RPC

## Descripción general

Tu Ryzen™ AI Halo ya es capaz de ejecutar modelos de lenguaje grandes de forma local. La agrupación en clústeres lleva esto un paso más allá al combinar la memoria de la GPU de múltiples sistemas a través de una red local, dándote acceso a modelos aún más grandes con un razonamiento más sólido, mejor generación de código y una comprensión multilingüe más profunda, todo completamente en tu propio hardware.

Este playbook te enseña cómo agrupar dos sistemas Ryzen AI Halo usando el motor RPC de llama.cpp y ejecutar GLM 4.7, un modelo de 358B parámetros, en ambas máquinas con aceleración de AMD ROCm™.

## Qué aprenderás

- Cómo extender la asignación de VRAM en sistemas Ryzen AI Halo
- Instalación de llama.cpp con soporte para ROCm y RPC
- Configuración de un worker RPC y ejecución de inferencia distribuida en dos nodos
- Ejecución de un modelo de 358B parámetros en dos sistemas Ryzen AI Halo conectados en red

## Configuración de la memoria

> **Nota**: Completa este paso tanto en la Máquina 1 como en la Máquina 2.

<!-- @os:windows -->
En Windows, para ejecutar modelos más grandes que requieren mayor memoria, necesitamos usar la asignación de AMD Variable Graphics Memory (iGPU VRAM).

Esto se puede hacer abriendo el panel de control de AMD Software: Adrenalin Edition y navegando a: `Performance > Tuning > AMD Variable Graphics Memory`. Establece el valor en **96 GB**. Reinicia el sistema para que los cambios surtan efecto.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
En Linux, ROCm utiliza un pool de memoria compartida del sistema, y este pool está configurado por defecto a la mitad de la memoria del sistema.

Esta cantidad puede aumentarse cambiando la configuración de páginas del Translation Table Manager (TTM) del kernel, siguiendo las siguientes instrucciones. AMD recomienda establecer la VRAM dedicada mínima en el BIOS (0.5 GB).

* Instala la utilidad pipx y agrega la ruta de los wheels instalados por pipx a la ruta de búsqueda del sistema.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Instala el wheel amd-debug-tools desde PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Ejecuta la herramienta amd-ttm para consultar la configuración actual de memoria compartida.
  ```bash
  amd-ttm
  ```

* Reconfigura la configuración de memoria compartida a **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Reinicia el sistema para que los cambios surtan efecto.


<!-- @os:end -->
<!-- @device:halo_box -->
## Verificar actualizaciones de software

<!-- @require:software-update -->
<!-- @device:end -->
## Requisitos previos

### Hardware

Este playbook requiere dos unidades Ryzen AI Halo y un switch Ethernet, conectados en una topología en estrella con cada unidad cableada directamente al switch.

| Componente | Cantidad | Descripción |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Nodos de cómputo que forman el clúster |
| Switch Ethernet de 10 Gbps | 1 | Switch central que permite la comunicación multinodo de Ryzen AI Halo (al menos 2 puertos) |
| Cable Ethernet | 2 | Conecta cada unidad Halo al switch (se recomienda Cat 7 o superior) |

> **Nota**: Se requieren dos puertos de switch Ethernet para conectar las dos unidades Ryzen AI Halo. Se requiere un tercer puerto si accedes al modelo desde una máquina cliente separada en lugar de hacerlo desde una de las unidades Halo.

### Software
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Instala:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) con la carga de trabajo **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Configuración física del hardware

> **Nota**: Completa este paso tanto en la Máquina 1 como en la Máquina 2.

Conecta cada unidad Ryzen AI Halo al switch Ethernet usando un cable Cat 7 (o superior). Esto establece el enlace de 10 Gbps utilizado para la comunicación de alta velocidad entre los nodos.
<!-- @os:linux -->
### 1. Determinar las interfaces de red

En cada máquina, encuentra el nombre de su interfaz de red y anótalo (a continuación se hará referencia a él como `IFNAME`). Ejecuta:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Esto imprime el nombre de la interfaz directamente, por ejemplo:

```bash
enp191s0
```

### 2. Verificar las velocidades de enlace de red

Confirma que el enlace esté activo y funcionando a la velocidad máxima verificando la velocidad de tu interfaz:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Nota**: Reemplaza `<IFNAME>` con el nombre de la interfaz de salida de [1. Determinar las interfaces de red](#1-determine-network-interfaces)

Deberías ver una velocidad de `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Nota**: Si la velocidad es inferior a `10000Mb/s` o el enlace no se activa, verifica la conexión del cable y confirma que el puerto del switch esté configurado a 10 Gbps. Algunos switches requieren que se deshabilite la autonegociación y que la velocidad de enlace se establezca manualmente; consulta la documentación de tu switch.

<!-- @os:end -->

<!-- @os:windows -->
### Verificar la velocidad de enlace de red

En cada máquina, verifica la velocidad de enlace de tus interfaces de red:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Tu interfaz Ethernet debería estar `Up` y funcionando a `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Nota**: Si la velocidad es inferior a `10 Gbps` o el enlace no se activa, verifica la conexión del cable y confirma que el puerto del switch esté configurado a 10 Gbps. Algunos switches requieren que se deshabilite la autonegociación y que la velocidad de enlace se establezca manualmente; consulta la documentación de tu switch.

<!-- @os:end -->

## Instalación de llama.cpp

> **Nota**: Completa este paso tanto en la Máquina 1 como en la Máquina 2.

Hay dos opciones de instalación disponibles:

- [Opción 1: Lemonade SDK (recomendado)](#option-1-lemonade-sdk-recommended) - binarios prediseñados, configuración más rápida
- [Opción 2: Compilación manual desde el código fuente](#option-2-manual-source-build) - compila desde el código fuente con control total sobre los indicadores de compilación

### Opción 1: Lemonade SDK (recomendado)

Lemonade SDK proporciona compilaciones nocturnas de llama.cpp con aceleración de AMD ROCm 7, dirigidas a GPU como gfx1151 (Strix Halo / Ryzen AI Max+ 395) y otras arquitecturas Radeon recientes.

<!-- @os:windows -->
#### Paso 1: Descargar los binarios preconstruidos

Navega a la página de la última versión y descarga el archivo que corresponda a tu plataforma y GPU objetivo:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Descarga el archivo llamado `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (donde `xxxx` es el número de compilación).

#### Paso 2: Extraer los binarios

Descomprime el archivo descargado:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Este directorio ahora contiene compilaciones habilitadas para ROCm de `llama-cli.exe`, `llama-server.exe` y `rpc-server.exe`, precompiladas para tu sistema Ryzen AI Halo.

#### Paso 3: Verificar la detección de la GPU

```bash
.\llama-cli.exe --list-devices
```

Salida esperada:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### Paso 1: Descargar los binarios preconstruidos

Navega a la página de la última versión y descarga el archivo que corresponda a tu plataforma y GPU objetivo:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Descarga el archivo llamado `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (donde `xxxx` es el número de compilación).

#### Paso 2: Extraer y preparar los binarios

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Este directorio ahora contiene compilaciones habilitadas para ROCm de `llama-cli`, `llama-server` y `rpc-server`, precompiladas para tu sistema Ryzen AI Halo.

#### Paso 3: Verificar la detección de la GPU

```bash
./llama-cli --list-devices
```

Salida esperada:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
Con llama.cpp preparado en cada nodo, continúa con [Descargar el modelo](#downloading-the-model).

### Opción 2: Compilación manual desde el código fuente

<!-- @os:windows -->
#### Paso 1: Compilar llama.cpp

Abre el **x64 Native Tools Command Prompt** (instalado con Visual Studio Build Tools) y clona el repositorio:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Agrega HIP a tu PATH y compila con soporte para ROCm y RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Indicador de compilación | Propósito |
|-----------|---------|
| `-DGGML_HIP=ON` | Habilita el stack de software ROCm/HIP |
| `-DGGML_RPC=ON` | Habilita RPC para inferencia distribuida |
| `-DGPU_TARGETS=gfx1151` | Apunta a la GPU Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Utiliza el sistema de compilación Ninja |

#### Paso 2: Verificar la detección de la GPU

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

Salida esperada:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### Paso 3: Agregar HIP a tu PATH de usuario

El paso de compilación anterior estableció `%HIP_PATH%\bin` solo para la sesión actual. Para que las bibliotecas de HIP estén disponibles en cualquier terminal (no solo en el x64 Native Tools Command Prompt), agrégalo de forma permanente a tu `PATH` de usuario:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Con llama.cpp preparado en cada nodo, continúa con [Descargar el modelo](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Paso 1: Compilar llama.cpp

Clona el repositorio:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Compila con soporte para ROCm y RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Indicador de compilación | Propósito |
|-----------|---------|
| `-DGGML_HIP=ON` | Habilita el stack de software ROCm |
| `-DGGML_RPC=ON` | Habilita RPC para inferencia distribuida |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Habilita rocWMMA para un Flash Attention mejorado en GPU AMD |
| `-DAMDGPU_TARGETS="gfx1151"` | Apunta a la GPU Ryzen AI Halo (Radeon 8060s) |

Para más opciones de compilación, consulta la [documentación de compilación de llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Paso 2: Verificar la detección de la GPU

```bash
cd rocm/bin
./llama-cli --list-devices
```

Salida esperada:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

Con llama.cpp preparado en cada nodo, continúa con [Descargar el modelo](#downloading-the-model).
<!-- @os:end -->

## Descargar el modelo

Este playbook utiliza [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), un modelo de 358B parámetros en la cuantización `Q4_K_XL` de [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Con esta cuantización, el modelo requiere aproximadamente 205GB de almacenamiento y cabe dentro de la memoria GPU combinada de dos nodos Ryzen AI Halo.

Descarga los archivos GGUF usando la CLI de Hugging Face:
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

> **Nota**: La descarga del modelo debe completarse en la Máquina 1 (el controlador). Los nodos trabajadores de RPC no necesitan una copia local de los archivos del modelo.

## Iniciar el modelo en el clúster

El motor RPC (Remote Procedure Call) de llama.cpp permite que una sola instancia de llama.cpp delegue capas del modelo a trabajadores remotos a través de la red. Una máquina actúa como el **controlador** (Máquina 1), encargándose de la tokenización, la planificación y la orquestación. La otra máquina ejecuta un **servidor RPC** liviano (Máquina 2) que expone su memoria y capacidad de cómputo de GPU al controlador.

En el momento de la carga, llama.cpp divide el modelo entre ambos nodos. Una vez cargado, la inferencia procede como si se ejecutara en un solo acelerador. RPC gestiona las transferencias de tensores y la sincronización de manera transparente.

### Paso 1: Iniciar el servidor RPC (Máquina 2)

En la Máquina 2, inicia el servidor RPC para exponer sus recursos de GPU al controlador:
<!-- @os:linux -->
```bash
./rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| Indicador | Propósito |
|------|---------|
| `-p` | Puerto en el que se transmite el servidor RPC |
| `-c` | Habilita una caché local para tensores grandes, evitando transferencias de red repetidas durante la carga del modelo |
| `--host` | Dirección IP a la que se vincula el servidor RPC (`0.0.0.0` para todas las interfaces) |

Para más opciones, consulta la [documentación de RPC de llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Paso 2: Iniciar el modelo (Máquina 1)

Con el servidor RPC ejecutándose en la Máquina 2, inicia la inferencia desde la Máquina 1 usando `llama-cli` o `llama-server`.

#### llama-cli

`llama-cli` proporciona una interfaz basada en terminal para interactuar directamente con el modelo. Es ideal para pruebas de rendimiento, depuración y experimentación de bajo nivel.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --rpc <RPC_WORKER_IP>:50053
```

> **Cómo encontrar `<RPC_WORKER_IP>`**: En la Máquina 2, ejecuta `hostname -I | awk '{print $1}'` para encontrar su dirección IP local.
<!-- @os:end -->

<!-- @os:windows -->
> **Nota**: Ejecuta este comando en la Terminal (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **Cómo encontrar `<RPC_WORKER_IP>`**: En la Máquina 2, ejecuta `ipconfig | findstr /C:"IPv4"` en la Terminal (Powershell) para encontrar su dirección IP local.

<!-- @os:end -->

Una vez en ejecución, `llama-cli` muestra el progreso de carga del modelo e ingresa a un prompt interactivo donde puedes chatear directamente con el modelo:

![llama-cli ejecutando GLM 4.7 en dos nodos](assets/llama-cli-example.png)
#### llama-server

`llama-server` expone el mismo motor de inferencia a través de un proceso de servidor persistente con una interfaz web integrada y una API HTTP compatible con OpenAI. Esta es la interfaz preferida para implementaciones de mayor duración, acceso multiusuario e integración con herramientas externas.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_IP>:50053
```

> **Cómo encontrar `<RPC_WORKER_IP>`**: En la Máquina 2, ejecuta `hostname -I | awk '{print $1}'` para encontrar su dirección IP local.
<!-- @os:end -->

<!-- @os:windows -->
> **Nota**: Ejecuta este comando en Terminal (Powershell).

```powershell
.\llama-server.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **Cómo encontrar `<RPC_WORKER_IP>`**: En la Máquina 2, ejecuta `ipconfig | findstr /C:"IPv4"` en Terminal (Powershell) para encontrar su dirección IP local.
<!-- @os:end -->

Una vez iniciado, abre `http://<HOST_IP>:8081` en tu navegador para acceder a la interfaz web integrada. Esto proporciona una interfaz de chat basada en el navegador para interactuar con el modelo:

![Interfaz web de llama-server ejecutando GLM 4.7 en dos nodos](assets/llama-server-example.png)

<!-- @os:linux -->
> **Cómo encontrar `<HOST_IP>`**: En la Máquina 1, ejecuta `hostname -I | awk '{print $1}'` para encontrar su dirección IP local.
<!-- @os:end -->

<!-- @os:windows -->
> **Cómo encontrar `<HOST_IP>`**: En la Máquina 1, ejecuta `ipconfig | findstr /C:"IPv4"` en Terminal (Powershell) para encontrar su dirección IP local.
<!-- @os:end -->

#### Referencia de parámetros

| Marcador | Propósito |
|------|---------|
| `-m` | Ruta al archivo de modelo GGUF (usa el primer fragmento, `00001-of-00005`) |
| `-c` | Tamaño de contexto en tokens. Los valores más grandes usan más memoria |
| `-fa on` | Habilita rocWMMA Flash Attention para un mejor rendimiento en GPU de AMD |
| `-ngl 999` | Descarga todas las capas del modelo a la GPU |
| `--no-mmap` | Deshabilita el mapeo de memoria, reduciendo los tiempos de carga cuando el tamaño del modelo excede la RAM del sistema pero cabe en la VRAM |
| `--host` | IP a la que se enlaza `llama-server` (solo `llama-server`) |
| `--port` | Puerto en el que se sirve la API HTTP (solo `llama-server`) |
| `--rpc` | Lista separada por comas de puntos de conexión de los workers RPC (`IP:port`) |

Para conocer el uso completo de los parámetros, consulta la [documentación de llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) y la [documentación de llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Próximos pasos

- **Conectar aplicaciones de terceros**: `llama-server` expone una API compatible con OpenAI. Apunta cualquier aplicación compatible con OpenAI (como Open WebUI) a `http://<HOST_IP>:8081` con cualquier clave de API de marcador de posición (por ejemplo, `none`) para conectarte a tu clúster
- **Explorar otros modelos**: Explora los GGUF cuantizados en [Hugging Face](https://huggingface.co/models?search=gguf) para encontrar modelos que se ajusten a la memoria GPU combinada de tu clúster
- **Escalar a cuatro nodos**: Agrega dos sistemas Ryzen AI Halo adicionales como workers RPC adicionales para acceder a modelos a escala de un billón de parámetros. Pasa puntos de conexión adicionales a `--rpc` como una lista separada por comas (por ejemplo, `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)