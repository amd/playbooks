<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Обзор

Напишите GPU-ядро с нуля, скомпилируйте его, запустите на AMD GPU и наблюдайте за ростом утилизации. Этот сборник инструкций показывает, как на самом деле работают GPU-вычисления: напишите код ядра и выполните его параллельно на тысячах потоков.

> **Примечание**: Это достаточно сложный сборник инструкций, который может потребовать дополнительной отладки и модификаций.

## Что вы узнаете

<!-- @os:windows -->
- Как работают GPU-ядра: сетки, блоки, потоки и модель индексирования, которая сопоставляет их с данными
- Как стек AMD ROCm/HIP позволяет писать CUDA-подобный код, который работает на AMD GPU без изменений
- Как компилировать ядро во время выполнения с помощью `torch.cuda._compile_kernel`
- Как собрать нативное расширение C++ с помощью `CUDAExtension` + pybind11, импортируемое из Python
<!-- @os:end -->
<!-- @os:linux -->
- Как работают GPU-ядра: сетки, блоки, потоки и модель индексирования, которая сопоставляет их с данными
- Как стек AMD ROCm/HIP позволяет писать CUDA-подобный код, который работает на AMD GPU без изменений
- Как компилировать ядро во время выполнения с помощью `torch.cuda._compile_kernel`
- Как собрать нативное расширение C++ с помощью `CUDAExtension` + pybind11, импортируемое из Python
- Как измерять время выполнения ядра и отслеживать утилизацию GPU в реальном времени с помощью `amd-smi`
<!-- @os:end -->

---

Этот сборник инструкций охватывает два подхода к разработке ядер:

<!-- @os:windows -->
| Подход | Точка входа |
|---|---|
| **JIT-компиляция** | `torch.cuda._compile_kernel` — запишите ядро в виде строки Python без шага сборки |
| **Расширение C++** | `CUDAExtension` + pybind11: скомпилируйте файл `.cu` в нативный `.pyd` и импортируйте его |
<!-- @os:end -->
<!-- @os:linux -->
| Подход | Точка входа |
|---|---|
| **JIT-компиляция** | `torch.cuda._compile_kernel` — запишите ядро в виде строки Python без шага сборки |
| **Расширение C++** | `CUDAExtension` + pybind11: скомпилируйте файл `.cu` в нативный `.so` и импортируйте его |
<!-- @os:end -->

Оба подхода работают на AMD GPU. Это возможно благодаря тому, что сборка PyTorch с ROCm отображает весь API-интерфейс CUDA на HIP. Это означает, что `torch.cuda`, `CUDAExtension` и синтаксис CUDA-ядер прозрачно работают на оборудовании AMD.

---

## Основные сведения

### Что такое GPU-ядро?

GPU-ядро — это функция, которая выполняется параллельно на тысячах GPU-потоков одновременно. В отличие от функции CPU, которая выполняется один раз за вызов, ядро запускается с **сеткой** **блоков**, каждый из которых содержит множество **потоков**, выполняющих один и тот же код на разных данных.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### Модель индексирования потоков

При запуске ядра вы задаёте два измерения:

| Переменная | Значение |
|---|---|
| `gridDim` | Количество блоков в сетке |
| `blockDim` | Количество потоков в блоке |

Каждый поток имеет доступ к трём встроенным переменным только для чтения:

| Переменная | Значение |
|---|---|
| `blockIdx.x` | К какому блоку принадлежит данный поток |
| `blockDim.x` | Количество потоков в одном блоке |
| `threadIdx.x` | Индекс потока внутри его блока |

### Глобальный идентификатор потока

Эти переменные объединяются для вычисления глобально уникального индекса потока:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

Общее количество потоков = `gridDim.x * blockDim.x`. Каждый поток обрабатывает один элемент независимо. Это основа **параллелизма данных**. Одна и та же операция выполняется над множеством элементов одновременно без зависимостей между потоками.

---

### Модель выполнения GPU: волновые фронты

AMD GPU выполняют потоки группами по **32**, называемыми **волновыми фронтами**. Все потоки в волновом фронте выполняют одну и ту же инструкцию одновременно. Это влияет на выбор оптимального размера блока (256 потоков = 8 волновых фронтов = хорошая эффективность планирования).

### Программирование AMD GPU: HIP + ROCm

**ROCm** — это открытый стек GPU-вычислений AMD (драйверы, компиляторы, библиотеки, среда выполнения). **HIP** находится поверх него и разработан так, чтобы быть синтаксически идентичным CUDA. Сборка PyTorch с ROCm прозрачно отображает `torch.cuda.*` на HIP, поэтому один и тот же код работает на AMD GPU.

---

### PyTorch + AMD/HIP

PyTorch поставляется со сборкой ROCm, в которой API-интерфейс CUDA (`torch.cuda.*`) прозрачно поддерживается HIP. Это означает:

- `torch.cuda.is_available()` работает на AMD GPU с ROCm
- `tensor.to("cuda")` выделяет память на AMD GPU
- `torch.version.hip` предоставляет версию HIP

PyTorch также предоставляет `torch.cuda._compile_kernel()` — высокоуровневый ярлык для JIT-компиляции строки с исходным кодом ядра и получения вызываемого объекта без необходимости отдельного шага сборки.

---

<!-- @device:halo_box -->
## Проверка обновлений программного обеспечения

<!-- @require:software-update -->
<!-- @device:end -->

## Установка необходимых программных компонентов
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Предварительные требования — Windows
- Установите последнюю версию: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### Создание виртуальной среды

<!-- @os:linux -->
<!-- @device:halo_box -->
В Linux откройте терминал в выбранном каталоге и выполните команды для создания виртуальной среды с уже установленными ROCm и PyTorch.
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
**Предоставьте вашему пользователю доступ к GPU-устройствам** (для вступления в силу необходимо выйти из системы и войти снова):

```bash
sudo usermod -aG render,video $LOGNAME
```

В Linux откройте терминал в выбранном каталоге и выполните команды для создания виртуальной среды.
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
В Windows откройте терминал в выбранном каталоге и выполните команды для создания виртуальной среды.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **Совет**: Пользователям Windows может потребоваться изменить политику выполнения PowerShell (например,
> установить значение RemoteSigned или Unrestricted) перед выполнением некоторых команд PowerShell.

<!-- @os:end -->
### Установка основных зависимостей
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
> **Примечание:** Для данного руководства ROCm и PyTorch необходимо установить в виртуальное окружение даже на Ryzen AI Halo, поскольку компиляция пользовательских ядер требует полных заголовочных файлов разработки.

Установите ROCm:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

Установите PyTorch:
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

### Установка дополнительных зависимостей

<!-- @os:linux -->
Установите набор инструментов сборки Linux C/C++. Это зависимость системного уровня, необходимая для пошаговых инструкций по расширениям C++, поскольку `CUDAExtension` собирает нативные модули `.so` из файлов `.cu`.

Выполните эту команду один раз на Linux-машине, вне созданного виртуального окружения Python:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

После активации виртуального окружения `kernel-env` установите зависимости сборки Python:
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
Убедитесь, что установлена [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) или [более новая версия](https://visualstudio.microsoft.com/vs/community/) с рабочей нагрузкой **Разработка классических приложений на C++**.

> **Примечание**: Настройка среды Visual Studio C++ требуется только для подхода с **расширением C++**. Для подхода с JIT-компиляцией она не нужна.

Откройте терминал PowerShell и выполните следующие команды перед сборкой расширения C++.

**Шаг 1: Найдите установленную среду Visual Studio C++**

**(A) Найдите `vswhere.exe`, который устанавливается вместе с Visual Studio Installer**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) Найдите `vcvars64.bat` из Visual Studio 2022 или более новой версии с инструментами сборки C++**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(C) Выведите используемую среду Visual Studio C++**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**Шаг 2: Активируйте среду сборки Visual Studio C++**

**(A) Запустите `vcvars64.bat` и захватите устанавливаемые им переменные среды**

Это делает доступными `cl.exe`, `INCLUDE`, `LIB`, `LIBPATH` и пути Windows SDK.

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) Импортируйте переменные среды Visual Studio в текущий сеанс PowerShell**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**Шаг 3: Убедитесь, что компилятор Microsoft C++ доступен**

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

#### Установка переменных среды
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
Убедитесь, что AMD GPU виден, выполнив:
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

## Загрузка необходимых файлов

Создайте следующую структуру каталогов, создав **2 новые папки** и загрузив соответствующие файлы:

| Каталог | Файлы для загрузки | Описание |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| Файлы JIT и расширения C++ для ядра сложения векторов |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Файлы JIT и расширения C++ для ядра матричного умножения |


## Пошаговые инструкции

### Инструкция 1: Сложение векторов

#### Подход A: JIT-компиляция

JIT (Just-In-Time, компиляция «на лету») означает, что ядро записывается в виде строки C++ внутри Python и компилируется во время выполнения, без необходимости дополнительных шагов сборки.

Чтобы использовать [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py), убедитесь, что файл загружен, и выполните:
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**Ключевые фрагменты кода**
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
> **Совет**: Скрипт также запускает фоновый поток, который каждые 100 мс опрашивает `amd-smi` для записи пиковой и средней загрузки GPU во время выполнения ядра.
<!-- @os:end -->

> **Примечание**: **Почему размер блока равен 256?** <br>
> - Ядро использует **256 потоков на блок**, поскольку это хорошо согласуется с **моделью выполнения волновых фронтов AMD GPU**.
> - Напомним, что аппаратное обеспечение AMD выполняет потоки группами по 32, что даёт 8 волновых фронтов на блок. (8 волновых фронтов × 32 потока = 1 блок)


**Что делает рабочая нагрузка:**

Ядро искусственно добавляет дополнительную работу для демонстрации загрузки GPU:

- **100 000 000 элементов** в тензоре
- **Внутренний цикл выполняется 1 000 раз** на элемент за каждый запуск ядра  
- **200 запусков ядра** всего

**Математика:**  
- Каждый элемент: увеличивается на 1 × 1 000 итераций × 200 запусков = 200 000  
- Итоговый результат: 1,0 (начальное значение) + 200 000 (сложений) = 200 001,0

**Зачем нужен внутренний цикл?**  
- Без цикла `for (int i = 0; i < 1000; i++)` 200 запусков завершились бы мгновенно, и инструменты мониторинга не зафиксировали бы значимую загрузку GPU. Искусственная работа делает каждый запуск ядра достаточно долгим для измерения производительности инструментами мониторинга.

<!-- @os:linux -->
**Ожидаемый вывод:** [Показатели производительности могут отличаться]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Примечание**: В Windows `amd-smi` не поддерживается. Для отслеживания загрузки GPU можно использовать Диспетчер задач, в котором при запуске программы должен наблюдаться кратковременный всплеск загрузки.

**Ожидаемый вывод:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**Отлично! Вы только что запустили своё первое ядро GPU.**

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
#### Подход Б: Расширение C++

Второй подход более ручной: напишите ядро и привязку Python в один файл `.cu`, скомпилируйте его нативно с помощью системы сборки PyTorch и импортируйте в Python.

<!-- @os:windows -->
> **Примечание**: Подход с расширением C++ требует среды сборки Visual Studio C++, поскольку PyTorch компилирует исходный файл `.cu` в нативный модуль расширения `.pyd`. Сборка этого нативного расширения зависит от инструментария Microsoft C++ (компилятор, компоновщик и инструменты сборки), предоставляемого Visual Studio. Перед сборкой расширения выполните команды активации Visual Studio из раздела настройки.
<!-- @os:end -->

Загрузите следующие файлы, если вы ещё этого не сделали:
<!-- @os:windows -->
| Файл | Роль |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Ядро + запускатель + привязка pybind11, всё в одном файле |
| [setup.py](assets/Vector_Addition/setup.py) | Скрипт сборки, использует `CUDAExtension` для компиляции `.cu` в `.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Скрипт Python, запускающий собранные артефакты |
<!-- @os:end -->

<!-- @os:linux -->
| Файл | Роль |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Ядро + запускатель + привязка pybind11, всё в одном файле |
| [setup.py](assets/Vector_Addition/setup.py) | Скрипт сборки, использует `CUDAExtension` для компиляции `.cu` в `.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Скрипт Python, запускающий собранные артефакты |
<!-- @os:end -->

#### **Шаг 1: Ядро, запускатель и привязка** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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

>**Совет**: Зачем использовать `hipDeviceSynchronize()`? <br>
> - Запуски ядер GPU являются асинхронными. Когда CPU выполняет `add_one<<<grid_size, block_size>>>(data, n);`, он немедленно переходит к следующей инструкции, не дожидаясь завершения работы GPU. `hipDeviceSynchronize()` заставляет CPU ждать, пока ядро GPU не завершит выполнение.

#### **Шаг 2: Сборка**
```bash
pip install --no-build-isolation -v .
```
>**Примечание**: Эта команда ищет `setup.py` в текущем каталоге для сборки созданного нами файла .cu.


`CUDAExtension` — это вспомогательный инструмент сборки CUDA из `torch.utils.cpp_extension`. При использовании ROCm PyTorch **перенаправляет `CUDAExtension` на использование `hipcc`** вместо `nvcc`. ROCm перехватывает путь сборки и направляет его через компилятор HIP, портируя код CUDA на AMD.

В результате создаются следующие файлы:
<!-- @os:windows -->
- `build/`: каталог с файлами `.pyd`
- `add_one_kernel.hip`: источник HIP, сгенерированный путём hipify файла `.cu`; именно это компилирует `hipcc`
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: каталог с файлами `.so`
- `add_one_kernel.hip`: источник HIP, сгенерированный путём hipify файла `.cu`; именно это компилирует `hipcc`
<!-- @os:end -->

#### **Шаг 3: Использование из Python** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
Выполните этот скрипт, чтобы увидеть ядро в действии:
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**Ожидаемый вывод:**
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

### Пример 2: Матричное умножение

Матричное умножение вычисляет **C = A × B**, где:
- **A** имеет размер M×N (строки × столбцы)
- **B** имеет размер N×K  
- **C** имеет размер M×K (результат)

Каждый элемент результата определяется как:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

Каждый элемент C вычисляется независимо, что делает эту задачу идеальной для параллелизма на GPU.

#### Как это отображается на потоки GPU

В отличие от сложения векторов (1D), матричное умножение даёт **двумерный результат**, поэтому используется **двумерная сетка потоков**:

| | Сложение векторов | Матричное умножение |
|---|---|---|
| **Форма результата** | Одномерный массив | Двумерная матрица (M×K) |
| **Отображение потоков** | 1 поток → 1 элемент | 1 поток → 1 элемент результата |
| **Шаблон запуска** | Одномерная сетка: `(grid_x, 1, 1)` | Двумерная сетка: `(grid_x, grid_y, 1)` |
| **Размер блока** | `(256, 1, 1)` | `(16, 16, 1)` = 256 потоков |

Каждый поток вычисляет один элемент выходной матрицы C. Поток в позиции `(row, col)` вычисляет `C[row][col]`, умножая соответствующую строку A на соответствующий столбец B.

**Расположение в памяти**: Память GPU является плоской (одномерной), но матрицы хранятся построчно. Для доступа к `A[row][col]` ядро использует `A[row * N + col]`.


#### Подход А: JIT-компиляция:

Как и в примере 1, ядро записывается в виде строки C++ внутри Python и компилируется во время выполнения с помощью встроенного JIT PyTorch.


Чтобы использовать [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py), убедитесь, что файл загружен, и выполните:
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**Ключевые фрагменты кода**
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

Скрипт проверяет результат по сравнению с `torch.mm` с небольшим допуском. Арифметика с плавающей точкой на GPU может давать небольшие числовые отличия по сравнению с реализациями на CPU из-за порядка параллельной редукции.

<!-- @os:linux -->
**Ожидаемый вывод:** [Показатели производительности могут варьироваться]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Примечание**: В Windows `amd-smi` не поддерживается. Для отслеживания загрузки GPU можно использовать Диспетчер задач, в котором при запуске программы должен наблюдаться кратковременный всплеск загрузки.

**Ожидаемый вывод:**
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
#### Подход Б: Расширение C++

Второй подход более ручной: напишите ядро и привязку Python в один файл `.cu`, скомпилируйте его нативно с помощью системы сборки PyTorch и импортируйте в Python.

<!-- @os:windows -->
> **Примечание**: Подход с расширением C++ требует среды сборки Visual Studio C++, поскольку PyTorch компилирует исходный файл `.cu` в нативный модуль расширения `.pyd`. Сборка этого нативного расширения зависит от инструментальной цепочки Microsoft C++ (компилятор, компоновщик и инструменты сборки), предоставляемой Visual Studio. Перед сборкой расширения выполните команды активации Visual Studio из раздела настройки.
<!-- @os:end -->

Загрузите следующие файлы, если вы ещё этого не сделали:
<!-- @os:windows -->
| Файл | Роль |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Ядро + запускатель + привязка pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Скрипт сборки, использует `CUDAExtension` для компиляции `.cu` в `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Скрипт Python, запускающий собранные артефакты |
<!-- @os:end -->
<!-- @os:linux -->
| Файл | Роль |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Ядро + запускатель + привязка pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Скрипт сборки, использует `CUDAExtension` для компиляции `.cu` в `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Скрипт Python, запускающий собранные артефакты |
<!-- @os:end -->

#### **Шаг 1: Ядро, запускатель и привязка** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
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

По сравнению с `add_one_launcher` из Руководства 1, запускатель здесь:
- Принимает два входных тензора вместо одного
- Выводит все три измерения (M, N, K) из форм тензоров, без ручной передачи размеров из Python
- Выделяет и возвращает выходной тензор C, а не изменяет данные на месте
- Использует `dim3` как для сетки, так и для блока, чтобы задать двумерную форму запуска

#### **Шаг 2: Сборка**
```bash
pip install --no-build-isolation -v .
```
>**Примечание**: Эта команда ищет `setup.py` в текущем каталоге для сборки созданного нами файла `.cu`.


В результате создаются следующие файлы:
<!-- @os:windows -->
- `build/`: каталог с файлами `.pyd`
- `matmul_kernel.hip`: исходный код HIP, сгенерированный путём hipify файла `.cu`; именно его компилирует `hipcc`
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: каталог с файлами `.so`
- `matmul_kernel.hip`: исходный код HIP, сгенерированный путём hipify файла `.cu`; именно его компилирует `hipcc`
<!-- @os:end -->

#### **Шаг 3: Использование из Python** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
Выполните этот скрипт, чтобы увидеть ядро в действии:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**Ожидаемый вывод:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**Отлично! Вы только что реализовали матричное умножение на GPU.** Это важная веха, поскольку матричное умножение является основой современных операций машинного обучения, таких как:
- Слои нейронных сетей
- Механизмы внимания
- Эмбеддинги
- Трансформеры

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

## Следующие шаги

Вы научились писать, компилировать и запускать ядра GPU с использованием как JIT-компиляции, так и расширений C++ для базовых параллельных операций.

**Оптимизации производительности:**
- **Тайлинг с использованием разделяемой памяти** — кэширование блоков данных для уменьшения обращений к глобальной памяти
- **Коалесцирование памяти** — оптимизация паттернов доступа к памяти для увеличения пропускной способности

**Реальные алгоритмы:**
- **2D свёртка** — небольшой фильтр (ядро) скользит по изображению, вычисляя каждый выходной пиксель как взвешенную сумму соседних пикселей. Это вводит стенсильные вычисления и тайлинг с разделяемой памятью, при котором потоки повторно используют перекрывающиеся области изображения для уменьшения обращений к глобальной памяти.
- **Функция Softmax**: Softmax преобразует вектор чисел в вероятности, сумма которых равна 1, и широко используется в выходных слоях нейронных сетей. Эффективная реализация на GPU вводит параллельные редукции и методы численной стабильности при обработке больших векторов.

**Производственные соображения:**
- **Обработка ошибок** — проверка границ и управление устройствами
- **Интеграция с PyTorch** — пользовательские операторы с поддержкой autograd