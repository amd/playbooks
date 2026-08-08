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

## Descripción general

Escribe un kernel de GPU desde cero, compílalo, ejecútalo en una GPU AMD y observa cómo se dispara la utilización. Este playbook muestra cómo funciona realmente el cómputo en GPU: escribes el código del kernel y lo ejecutas en paralelo a través de miles de hilos.

> **Nota**: Este es un playbook bastante complejo, que puede requerir algo de depuración y modificaciones adicionales.

## Qué aprenderás

<!-- @os:windows -->
- Cómo funcionan los kernels de GPU: grids, bloques, hilos y el modelo de indexación que los mapea a los datos
- Cómo la pila AMD ROCm/HIP permite escribir código estilo CUDA que se ejecuta en GPUs AMD sin modificaciones
- Cómo compilar un kernel en tiempo de ejecución usando `torch.cuda._compile_kernel`
- Cómo construir una extensión de kernel en C++ nativo con `CUDAExtension` + pybind11, importable desde Python
<!-- @os:end -->
<!-- @os:linux -->
- Cómo funcionan los kernels de GPU: grids, bloques, hilos y el modelo de indexación que los mapea a los datos
- Cómo la pila AMD ROCm/HIP permite escribir código estilo CUDA que se ejecuta en GPUs AMD sin modificaciones
- Cómo compilar un kernel en tiempo de ejecución usando `torch.cuda._compile_kernel`
- Cómo construir una extensión de kernel en C++ nativo con `CUDAExtension` + pybind11, importable desde Python
- Cómo medir el tiempo de ejecución del kernel y monitorear en vivo la utilización de la GPU con `amd-smi`
<!-- @os:end -->

---

Este playbook cubre dos enfoques para el desarrollo de kernels:

<!-- @os:windows -->
| Enfoque | Punto de entrada |
|---|---|
| **Compilación JIT** | `torch.cuda._compile_kernel`, escribe un kernel como una cadena de Python, sin paso de compilación |
| **Extensión en C++** | `CUDAExtension` + pybind11: compila un archivo `.cu` en un `.pyd` nativo e impórtalo |
<!-- @os:end -->
<!-- @os:linux -->
| Enfoque | Punto de entrada |
|---|---|
| **Compilación JIT** | `torch.cuda._compile_kernel`, escribe un kernel como una cadena de Python, sin paso de compilación |
| **Extensión en C++** | `CUDAExtension` + pybind11: compila un archivo `.cu` en un `.so` nativo e impórtalo |
<!-- @os:end -->

Ambos enfoques se ejecutan en GPUs AMD. Esto es posible porque la compilación ROCm de PyTorch mapea toda la superficie de la API de CUDA a HIP. Esto significa que `torch.cuda`, `CUDAExtension`, y la sintaxis de kernels CUDA funcionan todos de forma transparente en hardware AMD.

---

## Antecedentes

### ¿Qué es un Kernel de GPU?

Un kernel de GPU es una función que se ejecuta en paralelo a través de miles de hilos de GPU simultáneamente. A diferencia de una función de CPU que se ejecuta una vez por llamada, un kernel se lanza con una **grid** de **bloques**, cada uno conteniendo muchos **hilos**, todos ejecutando el mismo código sobre datos diferentes.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### Modelo de Indexación de Hilos

Al lanzar un kernel especificas dos dimensiones:

| Variable | Significado |
|---|---|
| `gridDim` | Número de bloques en la grid |
| `blockDim` | Número de hilos por bloque |

Cada hilo tiene acceso a tres variables integradas de solo lectura:

| Variable | Significado |
|---|---|
| `blockIdx.x` | A qué bloque pertenece este hilo |
| `blockDim.x` | Número de hilos en un bloque |
| `threadIdx.x` | Índice del hilo dentro de su bloque |

### ID Global del Hilo

Estas variables se combinan para calcular un índice de hilo globalmente único:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

Total de hilos = `gridDim.x * blockDim.x`. Cada hilo procesa un elemento de forma independiente. Esta es la base del **paralelismo de datos**. La misma operación se ejecuta sobre muchos elementos a la vez, sin dependencia entre hilos.

---

### Modelo de Ejecución de GPU: Wavefronts

Las GPUs AMD ejecutan hilos en grupos de **32** llamados **wavefronts**. Todos los hilos en un wavefront ejecutan la misma instrucción simultáneamente. Esto afecta las decisiones óptimas de tamaño de bloque (256 hilos = 8 wavefronts = buena eficiencia de programación).

### Programación de GPU AMD: HIP + ROCm

**ROCm** es la pila de cómputo de GPU de código abierto de AMD (drivers, compiladores, bibliotecas, runtime). **HIP** se sitúa encima, diseñado para ser sintácticamente idéntico a CUDA. La compilación ROCm de PyTorch mapea de forma transparente `torch.cuda.*` a HIP, de modo que el mismo código funciona en GPUs AMD.

---

### PyTorch + AMD/HIP

PyTorch ofrece una compilación ROCm donde la superficie de la API de CUDA (`torch.cuda.*`) está respaldada de forma transparente por HIP. Esto significa que:

- `torch.cuda.is_available()` funciona en GPUs AMD con ROCm
- `tensor.to("cuda")` asigna memoria en la GPU AMD
- `torch.version.hip` expone la versión de HIP

PyTorch también expone `torch.cuda._compile_kernel()`, un atajo de alto nivel para compilar en JIT una cadena de kernel en bruto y obtener de vuelta un objeto invocable, sin necesitar un paso de compilación separado.

---

<!-- @device:halo_box -->
## Verificar actualizaciones de software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalación de requisitos previos de software
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Requisitos previos - Windows
- Instala la última versión: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### Crear un Entorno Virtual

<!-- @os:linux -->
<!-- @device:halo_box -->
En Linux, abre una terminal en el directorio de tu elección y sigue los comandos para crear un venv con ROCm+Pytorch ya instalados.
<!-- @test:id=create-venv timeout=60 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv kernel-env --system-site-packages
source kernel-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source kernel-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Otorga a tu usuario acceso a los dispositivos GPU** (cierra sesión y vuelve a iniciarla para que esto tenga efecto):

```bash
sudo usermod -aG render,video $LOGNAME
```

En Linux, abre una terminal en el directorio de tu elección y sigue los comandos para crear un venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv kernel-env
source kernel-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source kernel-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
En Windows, abre una terminal en el directorio de tu elección y sigue los comandos para crear un venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **Consejo**: Es posible que los usuarios de Windows necesiten modificar su Política de Ejecución de PowerShell (por ejemplo,
> configurándola como RemoteSigned o Unrestricted) antes de ejecutar algunos comandos de PowerShell.

<!-- @os:end -->
### Instalando Dependencias Básicas
<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
<!-- @require:rocm,pytorch -->
<!-- @device:end -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver,rocm,pytorch -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver,rocm,pytorch -->
<!-- @device:end -->

<!-- @device:halo_box -->
> **Nota:** Para este playbook, ROCm y PyTorch deben instalarse en el entorno virtual incluso en el Ryzen AI Halo, ya que la compilación de kernels personalizados requiere los encabezados de desarrollo completos.

Instalar ROCm:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

Instalar PyTorch:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "torch==2.11.0+rocm7.13.0" "torchvision==0.26.0+rocm7.13.0" "torchaudio==2.11.0+rocm7.13.0"
```
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=verify-installed-package-versions timeout=60 hidden=True setup=activate-venv -->
```bash
python -m pip list | grep -E '^(rocm|rocm-sdk|torch|torchvision|torchaudio)' || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=verify-installed-package-versions timeout=60 hidden=True setup=activate-venv -->
```powershell
python -m pip list | Select-String "rocm|torch|torchvision|torchaudio"
```
<!-- @test:end -->
<!-- @os:end -->
---

### Instalando Dependencias Adicionales

<!-- @os:linux -->
Instala la cadena de herramientas de compilación C/C++ de Linux. Esta es una dependencia a nivel de sistema y se requiere para los recorridos de extensión en C++ porque `CUDAExtension` compila módulos `.so` nativos a partir de archivos `.cu`.

Ejecuta esto una vez en la máquina Linux, fuera del entorno virtual de Python creado:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

Después de activar el entorno virtual `kernel-env`, instala las dependencias de compilación de Python:
<!-- @test:id=install-deps timeout=60 setup=activate-venv -->
```bash
python -m pip install "setuptools<82" wheel ninja
```
<!-- @test:end -->

<!-- @os:linux -->
<!-- @test:id=verify-linux-build-tools timeout=60 hidden=True -->
```bash
set -euo pipefail

command -v gcc
command -v g++
gcc --version
g++ --version

echo "OK: Linux C/C++ build toolchain is available."
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
Asegúrate de tener instalado [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) o [una versión más reciente](https://visualstudio.microsoft.com/vs/community/) con la carga de trabajo **Desktop development with C++**.

> **Nota**: Esta configuración del entorno C++ de Visual Studio solo se requiere para el enfoque de **C++ Extension**. No se requiere para el enfoque de JIT Compilation.

Abre una terminal de PowerShell y ejecuta los siguientes comandos antes de compilar la extensión C++.

**Paso 1: Encontrar el entorno C++ de Visual Studio instalado**

**(A) Localiza `vswhere.exe`, que se instala junto con el Visual Studio Installer**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) Encuentra `vcvars64.bat` de Visual Studio 2022 o una versión más reciente con las herramientas de compilación C++**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(C) Imprime el entorno C++ de Visual Studio que se está usando**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**Paso 2: Activar el entorno de compilación C++ de Visual Studio**

**(A) Ejecuta `vcvars64.bat` y captura el entorno que configura**

Esto hace que `cl.exe`, `INCLUDE`, `LIB`, `LIBPATH` y las rutas del SDK de Windows estén disponibles.

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) Importa las variables de entorno de Visual Studio en esta sesión de PowerShell**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**Paso 3: Verificar que el compilador C++ de Microsoft esté disponible**

```powershell
where.exe cl
```

<!-- @test:id=verify-visual-studio-community timeout=60 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
Write-Host "Detected Visual Studio installations:"
& $VsWhere -all -products * -format table | Out-Host

$VcvarsList = & $VsWhere `
  -all `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat"
if (-not $VcvarsList) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
$Vcvars = $VcvarsList | Select-Object -First 1
if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
Write-Host "Using vcvars64.bat from Visual Studio C++ environment: $Vcvars"

$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE
if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}

$VsEnv | Select-String "Developer Command Prompt|Environment initialized|cl.exe" | Out-Host
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}

where.exe cl

Write-Host "OK: Visual Studio C++ build environment is available."
```
<!-- @test:end -->
<!-- @os:end -->

#### Establecer Variables de Entorno
<!-- @os:linux -->
<!-- @test:id=set-env-variables-linux timeout=300 setup=activate-venv -->
```bash
rocm-sdk init # Initialize the devel libraries

# Get the active Python version (e.g. "3.13") so the path works with any Python release
PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
export ROCM_HOME="$VIRTUAL_ENV/lib/python${PY_MM}/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH="$ROCM_HOME/lib:$LD_LIBRARY_PATH"
export PATH="$ROCM_HOME/bin:$PATH"

# Set compiler and build settings
export CC=clang
export CXX=clang
export DISTUTILS_USE_SDK=1
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=set-env-variables-windows timeout=300 setup=activate-venv -->
```powershell
rocm-sdk init # Initialize the devel libraries

$ROCM_ROOT = (rocm-sdk path --root).Trim()
$ROCM_BIN = (rocm-sdk path --bin).Trim()

$RocmPathEntries = @(
  $ROCM_BIN,
  "$ROCM_ROOT\bin",
  "$ROCM_ROOT\lib",
  "$ROCM_ROOT\lib\llvm\bin"
) | Where-Object { $_ -and (Test-Path $_) }

$env:PATH = (($RocmPathEntries + @($env:PATH)) -join ";")

$env:ROCM_HOME = $ROCM_ROOT
$env:HIP_PATH = $ROCM_ROOT
$env:ROCM_BIN = $ROCM_BIN
$env:HIP_PLATFORM = "amd"

# Set compiler and build settings
$env:CC = "clang-cl"
$env:CXX = "clang-cl"
$env:DISTUTILS_USE_SDK = "1"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
Verifica que la GPU de AMD sea visible con:
<!-- @test:id=amd-smi-linux timeout=60 setup=activate-venv -->
```bash
amd-smi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=env-setup-rocm-pytorch-linux timeout=300 hidden=True setup=activate-venv -->
```bash
set -euo pipefail

rocm-sdk init

PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
export ROCM_HOME="$VIRTUAL_ENV/lib/python${PY_MM}/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH="$ROCM_HOME/lib:${LD_LIBRARY_PATH:-}"
export PATH="$ROCM_HOME/bin:$PATH"

export CC=clang
export CXX=clang
export DISTUTILS_USE_SDK=1

echo "Installed ROCm/PyTorch packages:"
python -m pip list | grep -E '^(rocm|rocm-sdk|torch|torchvision|torchaudio)' || true

test -d "$ROCM_HOME"
test -d "$ROCM_HOME/bin"
test -d "$ROCM_HOME/lib"

test -f "$ROCM_HOME/lib/libhiprtc.so" || ls "$ROCM_HOME/lib"/libhiprtc.so*
test -f "$ROCM_HOME/lib/libroctx64.so" || ls "$ROCM_HOME/lib"/libroctx64.so*

hipcc --version >/dev/null
rocminfo >/dev/null

python - <<'PY'
import torch

print("torch:", torch.__version__)
print("HIP:", torch.version.hip)
print("CUDA available via HIP:", torch.cuda.is_available())

if torch.version.hip is None:
    raise SystemExit("PyTorch is not a ROCm/HIP build.")

if not torch.cuda.is_available():
    raise SystemExit("torch.cuda.is_available() is False. AMD GPU is not available through HIP.")

print("Device:", torch.cuda.get_device_name(0))
print("OK: ROCm PyTorch environment is ready")
PY
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=env-setup-rocm-pytorch-windows timeout=300 hidden=True setup=activate-venv -->
```powershell
$ErrorActionPreference = "Stop"

rocm-sdk init

$ROCM_ROOT = (rocm-sdk path --root).Trim()
$ROCM_BIN = (rocm-sdk path --bin).Trim()

$RocmPathEntries = @(
  $ROCM_BIN,
  "$ROCM_ROOT\bin",
  "$ROCM_ROOT\lib",
  "$ROCM_ROOT\lib\llvm\bin"
) | Where-Object { $_ -and (Test-Path $_) }
$env:PATH = (($RocmPathEntries + @($env:PATH)) -join ";")

$env:ROCM_HOME = $ROCM_ROOT
$env:HIP_PATH = $ROCM_ROOT
$env:ROCM_BIN = $ROCM_BIN
$env:HIP_PLATFORM = "amd"
$env:CC = "clang-cl"
$env:CXX = "clang-cl"
$env:DISTUTILS_USE_SDK = "1"

Write-Host "ROCM_ROOT=$ROCM_ROOT"
Write-Host "ROCM_BIN=$ROCM_BIN"

Write-Host "Installed ROCm/PyTorch packages:"
python -m pip list | Select-String "rocm|torch|torchvision|torchaudio"

Get-ChildItem -Path $ROCM_ROOT -Recurse -Filter "hiprtc*.dll" | Select-Object -First 10 FullName | Out-Host

hipcc --version | Out-Host
hipinfo | Out-Host

$code = @'
import os
import sys
import torch

if sys.platform == "win32":
    for key in ("ROCM_HOME", "HIP_PATH"):
        root = os.environ.get(key)
        if root:
            for subdir in ("bin", "lib", r"lib\llvm\bin"):
                path = os.path.join(root, subdir)
                if os.path.isdir(path):
                    os.add_dll_directory(path)

    rocm_bin = os.environ.get("ROCM_BIN")
    if rocm_bin and os.path.isdir(rocm_bin):
        os.add_dll_directory(rocm_bin)

print("torch:", torch.__version__)
print("HIP:", torch.version.hip)
print("CUDA available via HIP:", torch.cuda.is_available())

if torch.version.hip is None:
    raise SystemExit("PyTorch is not a ROCm/HIP build.")

if not torch.cuda.is_available():
    raise SystemExit("torch.cuda.is_available() is False. AMD GPU is not available through HIP.")

print("Device:", torch.cuda.get_device_name(0))
print("OK: ROCm PyTorch environment is ready")
'@

$code | python -
```
<!-- @test:end --> 
<!-- @os:end -->

---

## Descargar los Archivos Requeridos

Crea la siguiente estructura de directorios creando las **2 nuevas carpetas** y descargando los archivos correspondientes:

| Directorio | Archivos a Descargar | Descripción |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| Archivos JIT y de extensión C++ para el kernel de suma de vectores |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Archivos JIT y de extensión C++ para el kernel de multiplicación de matrices |


## Recorridos Guiados

### Recorrido Guiado 1: Suma de Vectores

#### Enfoque A: Compilación JIT

La compilación JIT (Just-In-Time) significa que el kernel se escribe como una cadena de texto en C++ sin procesar dentro de Python y se compila en tiempo de ejecución, sin necesidad de pasos de compilación adicionales.

Para usar [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py), asegúrate de que esté descargado y ejecuta:
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**Fragmentos de Código Clave**
```python
import torch

# Snippet 1: Kernel source as a string
KERNEL_SOURCE = """
extern "C"
__global__ void add_one(float* data, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        for (int i = 0; i < 1000; i++)
            data[idx] += 1.0f;
    }
}
"""


# Snippet 2: Compile the kernel string. PyTorch calls hipcc under the hood with ROCm
add_one_kernel = torch.cuda._compile_kernel(KERNEL_SOURCE, "add_one")

x = torch.ones(100_000_000, dtype=torch.float32, device="cuda")
n = x.numel()
block_size = 256
grid_size = (n + block_size - 1) // block_size


# Snippet 3: Launch: specify the grid/block dimensions and pass tensor arguments directly
for _ in range(200):
    add_one_kernel(
        grid=(grid_size, 1, 1),
        block=(block_size, 1, 1),
        args=[x, n],
    )


# Snippet 4: Test the output
print("First 5 elements:", x[:5].cpu()) 
#Expected output: tensor([200001., 200001., 200001., 200001., 200001.])
```
<!-- @os:linux -->
> **Consejo**: El script también genera un hilo en segundo plano que consulta `amd-smi` cada 100ms para registrar el uso máximo y promedio de la GPU durante la ejecución del kernel.
<!-- @os:end -->

> **Nota**: **¿Por qué el tamaño de bloque es 256?** <br>
> - El kernel usa **256 hilos por bloque** porque se alinea bien con el **modelo de ejecución de wavefronts de las GPU de AMD**.
> - Recuerda que el hardware de AMD ejecuta hilos en grupos de 32 hilos, lo que resulta en 8 wavefronts por bloque. (8 wavefronts x 32 hilos = 1 bloque)


**Qué hace la carga de trabajo:**

El kernel agrega trabajo adicional artificialmente para demostrar el uso de la GPU:

- **100,000,000 elementos** en el tensor
- **El bucle interno se ejecuta 1,000 veces** por elemento por lanzamiento de kernel
- **200 lanzamientos de kernel** en total

**Matemática:**  
- Cada elemento: se incrementa en 1 × 1,000 iteraciones × 200 lanzamientos = 200,000
- Resultado final: 1.0 (valor inicial) + 200,000 (adiciones) = 200,001.0

**¿Por qué el bucle interno?**  
- Sin el bucle `for (int i = 0; i < 1000; i++)`, los 200 lanzamientos terminarían instantáneamente y las herramientas de monitoreo no capturarían un uso significativo de la GPU. El trabajo artificial hace que cada ejecución del kernel dure lo suficiente como para que las herramientas de monitoreo puedan medir el rendimiento.

<!-- @os:linux -->
**Salida esperada:**[Los números de rendimiento variarán]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Nota**: En Windows, `amd-smi` no es compatible. Para monitorear el uso de la GPU, puedes usar el Administrador de Tareas, donde deberías ver un breve pico de uso cuando ejecutes el programa.

**Salida esperada:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**¡Buen trabajo! Acabas de ejecutar tu primer kernel de GPU.**

<!-- @os:linux -->
<!-- @test:id=vector-addition-jit-linux timeout=300 hidden=True setup=activate-venv -->
```bash
set -euo pipefail

rocm-sdk init

PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
export ROCM_HOME="$VIRTUAL_ENV/lib/python${PY_MM}/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH="$ROCM_HOME/lib:${LD_LIBRARY_PATH:-}"
export PATH="$ROCM_HOME/bin:$PATH"

export CC=clang
export CXX=clang
export DISTUTILS_USE_SDK=1

python - <<'PY'
import torch

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

kernel_source = r'''
extern "C"
__global__ void add_one(float* data, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        data[idx] += 1.0f;
    }
}
'''

kernel = torch.cuda._compile_kernel(kernel_source, "add_one")

x = torch.ones(1024, dtype=torch.float32, device="cuda")
n = x.numel()
block = 256
grid = (n + block - 1) // block

kernel(
    grid=(grid, 1, 1),
    block=(block, 1, 1),
    args=[x, n],
)

torch.cuda.synchronize()

if not torch.allclose(x, torch.full_like(x, 2.0)):
    raise SystemExit(f"Vector JIT output mismatch. First values: {x[:5].cpu()}")

print("OK: vector addition JIT kernel compiled and ran correctly")
PY
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=vector-addition-jit-windows timeout=300 hidden=True setup=activate-venv -->
```powershell
$ErrorActionPreference = "Stop"

rocm-sdk init

$ROCM_ROOT = (rocm-sdk path --root).Trim()
$ROCM_BIN = (rocm-sdk path --bin).Trim()

$RocmPathEntries = @(
  $ROCM_BIN,
  "$ROCM_ROOT\bin",
  "$ROCM_ROOT\lib",
  "$ROCM_ROOT\lib\llvm\bin"
) | Where-Object { $_ -and (Test-Path $_) }

$env:PATH = (($RocmPathEntries + @($env:PATH)) -join ";")

$env:ROCM_HOME = $ROCM_ROOT
$env:HIP_PATH = $ROCM_ROOT
$env:ROCM_BIN = $ROCM_BIN
$env:HIP_PLATFORM = "amd"

$code = @'
import os
import sys

if sys.platform == "win32":
    for key in ("ROCM_HOME", "HIP_PATH"):
        root = os.environ.get(key)
        if root:
            for subdir in ("bin", "lib", r"lib\llvm\bin"):
                path = os.path.join(root, subdir)
                if os.path.isdir(path):
                    os.add_dll_directory(path)

    rocm_bin = os.environ.get("ROCM_BIN")
    if rocm_bin and os.path.isdir(rocm_bin):
        os.add_dll_directory(rocm_bin)

import torch

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

kernel_source = r"""
extern "C"
__global__ void add_one(float* data, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        data[idx] += 1.0f;
    }
}
"""

kernel = torch.cuda._compile_kernel(kernel_source, "add_one")

x = torch.ones(1024, dtype=torch.float32, device="cuda")
n = x.numel()
block = 256
grid = (n + block - 1) // block

kernel(
    grid=(grid, 1, 1),
    block=(block, 1, 1),
    args=[x, n],
)

torch.cuda.synchronize()

if not torch.allclose(x, torch.full_like(x, 2.0)):
    raise SystemExit(f"Vector JIT output mismatch. First values: {x[:5].cpu()}")

print("OK: vector addition JIT kernel compiled and ran correctly")
'@

$code | python -
```
<!-- @test:end -->
<!-- @os:end -->

---
#### Enfoque B: Extensión de C++

El segundo enfoque es más manual: escribir el kernel y el binding de Python en un único archivo `.cu`, compilarlo de forma nativa usando el sistema de compilación de PyTorch e importarlo en Python.

<!-- @os:windows -->
> **Nota**: El enfoque de extensión de C++ requiere el entorno de compilación de Visual Studio C++ porque PyTorch compila el archivo fuente `.cu` en un módulo de extensión nativo `.pyd`. Compilar esa extensión nativa depende de la cadena de herramientas de Microsoft C++ (compilador, enlazador y herramientas de compilación) provistas por Visual Studio. Ejecuta los comandos de activación de Visual Studio de la sección de configuración antes de compilar la extensión.
<!-- @os:end -->

Descarga los siguientes archivos si aún no lo has hecho:
<!-- @os:windows -->
| Archivo | Función |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + lanzador + binding pybind11, todo en un solo archivo |
| [setup.py](assets/Vector_Addition/setup.py) | Script de compilación, usa `CUDAExtension` para compilar el `.cu` en un `.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Script de Python que ejecuta los artefactos compilados |
<!-- @os:end -->

<!-- @os:linux -->
| Archivo | Función |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + lanzador + binding pybind11, todo en un solo archivo |
| [setup.py](assets/Vector_Addition/setup.py) | Script de compilación, usa `CUDAExtension` para compilar el `.cu` en un `.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Script de Python que ejecuta los artefactos compilados |
<!-- @os:end -->

#### **Paso 1: El kernel, el lanzador y el binding** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
```cpp
#include <torch/extension.h>
#include <hip/hip_runtime.h>
// GPU kernel, one thread per element
__global__ void add_one(float* data, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) data[idx] += 1.0f;
}

// Launcher, bridges torch::Tensor to raw pointer, sets grid/block, runs kernel
void add_one_launcher(torch::Tensor tensor) {
    int n = tensor.numel();
    float* data = tensor.data_ptr<float>();
    int block_size = 256;
    int grid_size = (n + block_size - 1) / block_size;
    add_one<<<grid_size, block_size>>>(data, n);
    hipDeviceSynchronize();
}

// Python binding, exposes add_one_launcher as add_one_ext.add_one
PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) {
    m.def("add_one", &add_one_launcher, "Add one kernel (HIP)");
}
```

>**Consejo**: ¿Por qué usar `hipDeviceSynchronize()`? <br>
> - Los lanzamientos de kernel en la GPU son asíncronos. Cuando la CPU ejecuta `add_one<<<grid_size, block_size>>>(data, n);`, ejecutaría inmediatamente la siguiente instrucción sin esperar a la GPU. `hipDeviceSynchronize()` obliga a la CPU a esperar hasta que el kernel de la GPU se complete.

#### **Paso 2: Compilar**
```bash
pip install --no-build-isolation -v .
```
>**Nota**: Este comando busca `setup.py` en el directorio actual para compilar el archivo .cu que hemos creado.


`CUDAExtension` es un asistente de compilación de CUDA de `torch.utils.cpp_extension`. Con ROCm, PyTorch **redirige `CUDAExtension` para usar `hipcc`** en lugar de `nvcc`. ROCm intercepta la ruta de compilación y la enruta a través del compilador HIP, portando el código CUDA a AMD.

Esto produce los siguientes archivos:
<!-- @os:windows -->
- `build/`:  directorio con los archivos `.pyd`
- `add_one_kernel.hip`:  la fuente HIP generada al aplicar hipify al archivo `.cu`; esto es lo que `hipcc` realmente compiló
<!-- @os:end -->

<!-- @os:linux -->
- `build/`:  directorio con los archivos `.so`
- `add_one_kernel.hip`:  la fuente HIP generada al aplicar hipify al archivo `.cu`; esto es lo que `hipcc` realmente compiló
<!-- @os:end -->

#### **Paso 3: Usar desde Python** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
Ejecuta este script para ver el kernel en acción:
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**Salida esperada:**
```
Before: tensor([1., 1., 1., 1., 1., 1., 1., 1., 1., 1.], device='cuda:0')
After: tensor([2., 2., 2., 2., 2., 2., 2., 2., 2., 2.], device='cuda:0')
```

<!-- @os:linux -->
<!-- @test:id=vector-extension-linux timeout=600 hidden=True setup=activate-venv -->
```bash
set -euo pipefail

rocm-sdk init

PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
export ROCM_HOME="$VIRTUAL_ENV/lib/python${PY_MM}/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH="$ROCM_HOME/lib:${LD_LIBRARY_PATH:-}"
export PATH="$ROCM_HOME/bin:$PATH"

cd Vector_Addition

python -m pip install --no-build-isolation -v .

python - <<'PY'
import torch
import add_one_ext

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

x = torch.ones(16, dtype=torch.float32, device="cuda")
add_one_ext.add_one(x)
torch.cuda.synchronize()

expected = torch.full_like(x, 2.0)
if not torch.allclose(x, expected):
    raise SystemExit(f"Vector extension output mismatch. Got: {x.cpu()}")

print("OK: vector addition C++ extension built, imported, and ran correctly")
PY
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=vector-extension-windows timeout=600 hidden=True setup=activate-venv -->
```powershell
$ErrorActionPreference = "Stop"

$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}

$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1
if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
Write-Host "Using Visual Studio C++ environment: $Vcvars"

$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE
if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
$VsEnv | Select-String "Developer Command Prompt|Environment initialized|cl.exe" | Out-Host
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {[System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')}
}
where.exe cl

rocm-sdk init

$ROCM_ROOT = (rocm-sdk path --root).Trim()
$ROCM_BIN = (rocm-sdk path --bin).Trim()

$RocmPathEntries = @(
  $ROCM_BIN,
  "$ROCM_ROOT\bin",
  "$ROCM_ROOT\lib",
  "$ROCM_ROOT\lib\llvm\bin"
) | Where-Object { $_ -and (Test-Path $_) }

$env:PATH = (($RocmPathEntries + @($env:PATH)) -join ";")

$env:ROCM_HOME = $ROCM_ROOT
$env:HIP_PATH = $ROCM_ROOT
$env:ROCM_BIN = $ROCM_BIN
$env:HIP_PLATFORM = "amd"

$env:CC = "clang-cl"
$env:CXX = "clang-cl"
$env:DISTUTILS_USE_SDK = "1"

Push-Location "Vector_Addition"
try {
  python -m pip install --no-build-isolation -v .

  $code = @'
import os
import sys

if sys.platform == "win32":
    for key in ("ROCM_HOME", "HIP_PATH"):
        root = os.environ.get(key)
        if root:
            for subdir in ("bin", "lib", r"lib\llvm\bin"):
                path = os.path.join(root, subdir)
                if os.path.isdir(path):
                    os.add_dll_directory(path)

    rocm_bin = os.environ.get("ROCM_BIN")
    if rocm_bin and os.path.isdir(rocm_bin):
        os.add_dll_directory(rocm_bin)

import torch
import add_one_ext

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

x = torch.ones(16, dtype=torch.float32, device="cuda")
add_one_ext.add_one(x)
torch.cuda.synchronize()

expected = torch.full_like(x, 2.0)
if not torch.allclose(x, expected):
    raise SystemExit(f"Vector extension output mismatch. Got: {x.cpu()}")

print("OK: vector addition C++ extension built, imported, and ran correctly")
'@

  $code | python -
}
finally {
  Pop-Location
}
```
<!-- @test:end --> 
<!-- @os:end -->

---

### Recorrido 2: Multiplicación de matrices

La multiplicación de matrices calcula **C = A × B** donde:
- **A** es M×N (filas × columnas)
- **B** es N×K  
- **C** es M×K (el resultado)

Cada elemento de salida se define como:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

Cada elemento de C se calcula de forma independiente, lo que hace que esto sea perfecto para el paralelismo de GPU.

#### Cómo se mapea a los hilos de la GPU

A diferencia de la suma de vectores (1D), la multiplicación de matrices produce una **salida 2D**, por lo que usamos una **cuadrícula de hilos 2D**:

| | Suma de vectores | Multiplicación de matrices |
|---|---|---|
| **Forma de salida** | Arreglo 1D | Matriz 2D (M×K) |
| **Mapeo de hilos** | 1 hilo → 1 elemento | 1 hilo → 1 elemento de salida |
| **Patrón de lanzamiento** | Cuadrícula 1D: `(grid_x, 1, 1)` | Cuadrícula 2D: `(grid_x, grid_y, 1)` |
| **Tamaño de bloque** | `(256, 1, 1)` | `(16, 16, 1)` = 256 hilos |

Cada hilo calcula un elemento de la matriz de salida C. El hilo en la posición `(row, col)` calcula `C[row][col]` multiplicando la fila correspondiente de A con la columna correspondiente de B.

**Distribución de memoria**: La memoria de la GPU es plana (1D), pero las matrices se almacenan fila por fila. Para acceder a `A[row][col]`, el kernel usa `A[row * N + col]`.


#### Enfoque A: Compilación JIT:

Al igual que en el Recorrido 1, el kernel se escribe como una cadena de C++ sin procesar dentro de Python y se compila en tiempo de ejecución mediante el JIT integrado de PyTorch.


Para usar [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py), asegúrate de haberlo descargado y ejecuta:
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**Fragmentos de código clave**
```python
import torch

# Snippet 1: Kernel source as a string
KERNEL_SOURCE = """
extern "C"
__global__ void matmul(float* A, float* B, float* C, int M, int N, int K) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;

    if (row < M && col < K) {
        float sum = 0.0f;
        for (int n = 0; n < N; n++) {
            sum += A[row * N + n] * B[n * K + col];
        }
        C[row * K + col] = sum;
    }
}
"""

# Snippet 2: Creating the Matrix - 2D indexing to map threads onto the M×K output matrix
# Inputs: A is M x N, B is N x K, C is M x K
M, N, K = 1024, 512, 768

A = torch.randn(M, N, dtype=torch.float32, device="cuda")
B = torch.randn(N, K, dtype=torch.float32, device="cuda")
C = torch.zeros(M, K, dtype=torch.float32, device="cuda")

BLOCK = 16
grid_x = (K + BLOCK - 1) // BLOCK
grid_y = (M + BLOCK - 1) // BLOCK


# Snippet 3: Compile the kernel string
matmul_kernel = torch.cuda._compile_kernel(KERNEL_SOURCE, "matmul")


# Snippet 4:. Launch with a 2D grid, grid_x covers columns (K), grid_y covers rows (M)
BLOCK = 16
matmul_kernel(
    grid=(grid_x, grid_y, 1),
    block=(BLOCK, BLOCK, 1),
    args=[A, B, C, M, N, K],
)

C_ref = torch.mm(A, B)
max_err = (C - C_ref).abs().max().item()
print(f"Max error vs torch.mm: {max_err:.6f}")
```

El script verifica el resultado contra `torch.mm` con una pequeña tolerancia. La aritmética de punto flotante en las GPU puede producir pequeñas diferencias numéricas en comparación con las implementaciones en CPU debido al orden de reducción paralela.

<!-- @os:linux -->
**Salida esperada:**[Los números de rendimiento variarán]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Nota**: En Windows, `amd-smi` no es compatible. Para monitorear la utilización de la GPU, puedes usar el Administrador de Tareas, donde deberías ver un breve pico de utilización cuando ejecutas el programa.

**Salida esperada:**
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
No GPU Usage captured.
```
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=matmul-jit-linux timeout=300 hidden=True setup=activate-venv -->
```bash
set -euo pipefail

rocm-sdk init

PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
export ROCM_HOME="$VIRTUAL_ENV/lib/python${PY_MM}/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH="$ROCM_HOME/lib:${LD_LIBRARY_PATH:-}"
export PATH="$ROCM_HOME/bin:$PATH"

export CC=clang
export CXX=clang
export DISTUTILS_USE_SDK=1

python - <<'PY'
import torch

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

kernel_source = r'''
extern "C"
__global__ void matmul(float* A, float* B, float* C, int M, int N, int K) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;

    if (row < M && col < K) {
        float sum = 0.0f;
        for (int n = 0; n < N; n++) {
            sum += A[row * N + n] * B[n * K + col];
        }
        C[row * K + col] = sum;
    }
}
'''

M, N, K = 32, 16, 24
A = torch.randn(M, N, dtype=torch.float32, device="cuda")
B = torch.randn(N, K, dtype=torch.float32, device="cuda")
C = torch.zeros(M, K, dtype=torch.float32, device="cuda")

kernel = torch.cuda._compile_kernel(kernel_source, "matmul")

BLOCK = 16
grid_x = (K + BLOCK - 1) // BLOCK
grid_y = (M + BLOCK - 1) // BLOCK

kernel(
    grid=(grid_x, grid_y, 1),
    block=(BLOCK, BLOCK, 1),
    args=[A, B, C, M, N, K],
)

torch.cuda.synchronize()

C_ref = torch.mm(A, B)
max_err = (C - C_ref).abs().max().item()

if max_err > 1e-3:
    raise SystemExit(f"Matmul JIT max error too high: {max_err}")

print(f"OK: matmul JIT kernel compiled and ran correctly; max_err={max_err:.6f}")
PY
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=matmul-jit-windows timeout=300 hidden=True setup=activate-venv -->
```powershell
$ErrorActionPreference = "Stop"

rocm-sdk init

$ROCM_ROOT = (rocm-sdk path --root).Trim()
$ROCM_BIN = (rocm-sdk path --bin).Trim()

$RocmPathEntries = @(
  $ROCM_BIN,
  "$ROCM_ROOT\bin",
  "$ROCM_ROOT\lib",
  "$ROCM_ROOT\lib\llvm\bin"
) | Where-Object { $_ -and (Test-Path $_) }

$env:PATH = (($RocmPathEntries + @($env:PATH)) -join ";")

$env:ROCM_HOME = $ROCM_ROOT
$env:HIP_PATH = $ROCM_ROOT
$env:ROCM_BIN = $ROCM_BIN
$env:HIP_PLATFORM = "amd"

$code = @'
import os
import sys

if sys.platform == "win32":
    for key in ("ROCM_HOME", "HIP_PATH"):
        root = os.environ.get(key)
        if root:
            for subdir in ("bin", "lib", r"lib\llvm\bin"):
                path = os.path.join(root, subdir)
                if os.path.isdir(path):
                    os.add_dll_directory(path)

    rocm_bin = os.environ.get("ROCM_BIN")
    if rocm_bin and os.path.isdir(rocm_bin):
        os.add_dll_directory(rocm_bin)

import torch

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

kernel_source = r"""
extern "C"
__global__ void matmul(float* A, float* B, float* C, int M, int N, int K) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;

    if (row < M && col < K) {
        float sum = 0.0f;
        for (int n = 0; n < N; n++) {
            sum += A[row * N + n] * B[n * K + col];
        }
        C[row * K + col] = sum;
    }
}
"""

M, N, K = 32, 16, 24
A = torch.randn(M, N, dtype=torch.float32, device="cuda")
B = torch.randn(N, K, dtype=torch.float32, device="cuda")
C = torch.zeros(M, K, dtype=torch.float32, device="cuda")

kernel = torch.cuda._compile_kernel(kernel_source, "matmul")

BLOCK = 16
grid_x = (K + BLOCK - 1) // BLOCK
grid_y = (M + BLOCK - 1) // BLOCK

kernel(
    grid=(grid_x, grid_y, 1),
    block=(BLOCK, BLOCK, 1),
    args=[A, B, C, M, N, K],
)

torch.cuda.synchronize()

C_ref = torch.mm(A, B)
max_err = (C - C_ref).abs().max().item()

if max_err > 1e-3:
    raise SystemExit(f"Matmul JIT max error too high: {max_err}")

print(f"OK: matmul JIT kernel compiled and ran correctly; max_err={max_err:.6f}")
'@

$code | python -
```
<!-- @test:end --> 
<!-- @os:end -->

---
#### Enfoque B: Extensión de C++

El segundo enfoque es más manual: escribir el kernel y el binding de Python en un único archivo `.cu`, compilarlo de forma nativa usando el sistema de compilación de PyTorch, e importarlo en Python.

<!-- @os:windows -->
> **Nota**: El enfoque de Extensión de C++ requiere el entorno de compilación de Visual Studio C++, ya que PyTorch compila el archivo fuente `.cu` en un módulo de extensión nativo `.pyd`. La compilación de esa extensión nativa depende del conjunto de herramientas de Microsoft C++ (compilador, enlazador y herramientas de compilación) proporcionado por Visual Studio. Ejecuta los comandos de activación de Visual Studio de la sección de configuración antes de compilar la extensión.
<!-- @os:end -->

Descarga los siguientes archivos si aún no lo has hecho:
<!-- @os:windows -->
| Archivo | Función |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + launcher + binding de pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Script de compilación, usa `CUDAExtension` para compilar el `.cu` en un `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Script de Python que ejecuta los artefactos compilados |
<!-- @os:end -->
<!-- @os:linux -->
| Archivo | Función |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + launcher + binding de pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Script de compilación, usa `CUDAExtension` para compilar el `.cu` en un `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Script de Python que ejecuta los artefactos compilados |
<!-- @os:end -->

#### **Paso 1: El kernel, launcher, y binding** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
```cpp
#include <torch/extension.h>
#include <hip/hip_runtime.h>
#define BLOCK 16

// GPU kernel, one thread per output element of C
__global__ void matmul(float* A, float* B, float* C, int M, int N, int K) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;

    if (row < M && col < K) {
        float sum = 0.0f;
        for (int n = 0; n < N; n++) {
            sum += A[row * N + n] * B[n * K + col];
        }
        C[row * K + col] = sum;
    }
}

// Launcher, extracts dims from torch::Tensor, allocates C, sets 2D grid/block
torch::Tensor matmul_launcher(torch::Tensor A, torch::Tensor B) {
    int M = A.size(0), N = A.size(1), K = B.size(1);
    auto C = torch::zeros({M, K}, A.options());

    dim3 block(BLOCK, BLOCK);
    dim3 grid((K + BLOCK - 1) / BLOCK, (M + BLOCK - 1) / BLOCK);

    matmul<<<grid, block>>>(A.data_ptr<float>(), B.data_ptr<float>(),
                            C.data_ptr<float>(), M, N, K);
    hipDeviceSynchronize();
    return C;
}

// Python binding, exposes matmul_launcher as matmul_ext.matmul
PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) {
    m.def("matmul", &matmul_launcher, "Naive matmul kernel (HIP): A(M,N) @ B(N,K) -> C(M,K)");
}
```

En comparación con `add_one_launcher` en el Recorrido 1, el launcher aquí:
- Toma dos tensores de entrada en lugar de uno
- Deriva las tres dimensiones (M, N, K) a partir de las formas de los tensores, sin pasar tamaños manualmente desde Python
- Asigna y devuelve el tensor de salida C, en lugar de mutarlo en el lugar
- Usa `dim3` tanto para el grid como para el block para expresar la forma de lanzamiento 2D

#### **Paso 2: Compilar**
```bash
pip install --no-build-isolation -v .
```
>**Nota**: Este comando busca `setup.py` en el directorio actual para compilar el archivo .cu que hemos creado.


Esto produce los siguientes archivos:
<!-- @os:windows -->
- `build/`: directorio con los archivos `.pyd`
- `matmul_kernel.hip`: el código fuente HIP generado al hipificar el archivo `.cu`; esto es lo que `hipcc` realmente compiló
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: directorio con los archivos `.so`
- `matmul_kernel.hip`: el código fuente HIP generado al hipificar el archivo `.cu`; esto es lo que `hipcc` realmente compiló
<!-- @os:end -->

#### **Paso 3: Usar desde Python** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
Ejecuta este script para ver el kernel en acción:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**Resultado esperado:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**¡Excelente! Acabas de implementar la multiplicación de matrices en la GPU.** Este es un hito importante porque la multiplicación de matrices es la columna vertebral de las operaciones modernas de machine learning como:
- Capas de redes neuronales
- Mecanismos de atención
- Embeddings
- Transformers

<!-- @os:linux -->
<!-- @test:id=matmul-extension-linux timeout=600 hidden=True setup=activate-venv -->
```bash
set -euo pipefail

rocm-sdk init

PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
export ROCM_HOME="$VIRTUAL_ENV/lib/python${PY_MM}/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH="$ROCM_HOME/lib:${LD_LIBRARY_PATH:-}"
export PATH="$ROCM_HOME/bin:$PATH"

cd Matrix_Multiplication

python -m pip install --no-build-isolation -v .

python - <<'PY'
import torch
import matmul_ext

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

A = torch.randn(32, 16, dtype=torch.float32, device="cuda")
B = torch.randn(16, 24, dtype=torch.float32, device="cuda")

C = matmul_ext.matmul(A, B)
torch.cuda.synchronize()

C_ref = torch.mm(A, B)
max_err = (C - C_ref).abs().max().item()

if max_err > 1e-3:
    raise SystemExit(f"Matmul extension max error too high: {max_err}")

print(f"OK: matmul C++ extension built, imported, and ran correctly; max_err={max_err:.6f}")
PY
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=matmul-extension-windows timeout=600 hidden=True setup=activate-venv -->
```powershell
$ErrorActionPreference = "Stop"

$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}

$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1
if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
Write-Host "Using Visual Studio C++ environment: $Vcvars"

$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE
if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
$VsEnv | Select-String "Developer Command Prompt|Environment initialized|cl.exe" | Out-Host
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {[System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')}
}
where.exe cl

rocm-sdk init

$ROCM_ROOT = (rocm-sdk path --root).Trim()
$ROCM_BIN = (rocm-sdk path --bin).Trim()

$RocmPathEntries = @(
  $ROCM_BIN,
  "$ROCM_ROOT\bin",
  "$ROCM_ROOT\lib",
  "$ROCM_ROOT\lib\llvm\bin"
) | Where-Object { $_ -and (Test-Path $_) }

$env:PATH = (($RocmPathEntries + @($env:PATH)) -join ";")

$env:ROCM_HOME = $ROCM_ROOT
$env:HIP_PATH = $ROCM_ROOT
$env:ROCM_BIN = $ROCM_BIN
$env:HIP_PLATFORM = "amd"

$env:CC = "clang-cl"
$env:CXX = "clang-cl"
$env:DISTUTILS_USE_SDK = "1"

Push-Location "Matrix_Multiplication"
try {
  python -m pip install --no-build-isolation -v .

  $code = @'
import os
import sys

if sys.platform == "win32":
    for key in ("ROCM_HOME", "HIP_PATH"):
        root = os.environ.get(key)
        if root:
            for subdir in ("bin", "lib", r"lib\llvm\bin"):
                path = os.path.join(root, subdir)
                if os.path.isdir(path):
                    os.add_dll_directory(path)

    rocm_bin = os.environ.get("ROCM_BIN")
    if rocm_bin and os.path.isdir(rocm_bin):
        os.add_dll_directory(rocm_bin)

import torch
import matmul_ext

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

A = torch.randn(32, 16, dtype=torch.float32, device="cuda")
B = torch.randn(16, 24, dtype=torch.float32, device="cuda")

C = matmul_ext.matmul(A, B)
torch.cuda.synchronize()

C_ref = torch.mm(A, B)
max_err = (C - C_ref).abs().max().item()

if max_err > 1e-3:
    raise SystemExit(f"Matmul extension max error too high: {max_err}")

print(f"OK: matmul C++ extension built, imported, and ran correctly; max_err={max_err:.6f}")
'@

  $code | python -
}
finally {
  Pop-Location
}
```
<!-- @test:end --> 
<!-- @os:end -->

---

## Próximos pasos

Has aprendido a escribir, compilar y lanzar kernels de GPU usando tanto la compilación JIT como extensiones de C++ para operaciones paralelas básicas.

**Optimizaciones de rendimiento:**
- **Shared memory tiling**: almacenar en caché bloques de datos para reducir el acceso a la memoria global
- **Coalescencia de memoria**: optimizar los patrones de acceso a memoria para el ancho de banda

**Algoritmos del mundo real:**
- **Convolución 2D**: un pequeño filtro (kernel) se desliza sobre una imagen, calculando cada píxel de salida a partir de una suma ponderada de los píxeles vecinos. Esto introduce cálculos de tipo stencil y shared memory tiling, donde los threads reutilizan regiones de imagen superpuestas para reducir el acceso a la memoria global.
- **Función Softmax**: Softmax convierte un vector de números en probabilidades que suman 1, comúnmente usado en las salidas de redes neuronales. Implementarlo de manera eficiente en la GPU introduce reducciones paralelas y técnicas de estabilidad numérica al procesar vectores grandes.

**Consideraciones de producción:**
- **Manejo de errores**: verificación de límites y gestión de dispositivos
- **Integración con PyTorch**: operadores personalizados con soporte para autograd