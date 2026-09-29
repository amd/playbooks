<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Машинный перевод.** Эта страница была автоматически переведена с английского языка и не прошла проверку человеком. Она может содержать ошибки, а некоторые инструкции, команды, файлы для загрузки, сведения о доступности продуктов или иное содержимое могут отличаться в зависимости от языка или региона. В случае каких-либо несоответствий или расхождений преимущественную силу имеет оригинальная версия playbook на английском языке.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Обзор

Напишите GPU-ядро (kernel) с нуля, скомпилируйте его, запустите на GPU AMD и понаблюдайте за резким ростом загрузки. Этот playbook показывает, как на самом деле работают вычисления на GPU: вы пишете код ядра и выполняете его параллельно на тысячах потоков.

> **Примечание**: это довольно сложный playbook, который может потребовать дополнительной отладки и доработок.

## Чему вы научитесь

<!-- @os:windows -->
- Как работают GPU-ядра: сетки (grids), блоки (blocks), потоки (threads) и модель индексации, связывающая их с данными
- Как стек AMD ROCm/HIP позволяет писать код в стиле CUDA, который выполняется на GPU AMD без изменений
- Как скомпилировать ядро во время выполнения с помощью `torch.cuda._compile_kernel`
- Как собрать нативное расширение-ядро на C++ с помощью `CUDAExtension` + pybind11, импортируемое из Python
<!-- @os:end -->
<!-- @os:linux -->
- Как работают GPU-ядра: сетки (grids), блоки (blocks), потоки (threads) и модель индексации, связывающая их с данными
- Как стек AMD ROCm/HIP позволяет писать код в стиле CUDA, который выполняется на GPU AMD без изменений
- Как скомпилировать ядро во время выполнения с помощью `torch.cuda._compile_kernel`
- Как собрать нативное расширение-ядро на C++ с помощью `CUDAExtension` + pybind11, импортируемое из Python
- Как измерять время выполнения ядра и отслеживать загрузку GPU в реальном времени с помощью `amd-smi`
<!-- @os:end -->

---

В этом playbook рассматриваются два подхода к разработке ядер:

<!-- @os:windows -->
| Подход | Точка входа |
|---|---|
| **JIT-компиляция** | `torch.cuda._compile_kernel` — ядро пишется как строка Python, без этапа сборки |
| **Расширение на C++** | `CUDAExtension` + pybind11: компиляция файла `.cu` в нативный `.pyd` и его импорт |
<!-- @os:end -->
<!-- @os:linux -->
| Подход | Точка входа |
|---|---|
| **JIT-компиляция** | `torch.cuda._compile_kernel` — ядро пишется как строка Python, без этапа сборки |
| **Расширение на C++** | `CUDAExtension` + pybind11: компиляция файла `.cu` в нативный `.so` и его импорт |
<!-- @os:end -->

Оба подхода работают на GPU AMD. Это возможно благодаря тому, что сборка PyTorch для ROCm отображает весь набор API CUDA на HIP. Это означает, что `torch.cuda`, `CUDAExtension` и синтаксис ядер CUDA прозрачно работают на оборудовании AMD.

---

## Предыстория

### Что такое GPU-ядро?

GPU-ядро (kernel) — это функция, которая выполняется параллельно на тысячах потоков GPU одновременно. В отличие от функции CPU, которая выполняется один раз при каждом вызове, ядро запускается в виде **сетки (grid)** из **блоков (blocks)**, каждый из которых содержит множество **потоков (threads)**, и все они выполняют один и тот же код над разными данными.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### Модель индексации потоков

При запуске ядра вы указываете два измерения:

| Переменная | Значение |
|---|---|
| `gridDim` | Количество блоков в сетке |
| `blockDim` | Количество потоков в блоке |

Каждый поток имеет доступ к трём встроенным переменным только для чтения:

| Переменная | Значение |
|---|---|
| `blockIdx.x` | Блок, к которому принадлежит данный поток |
| `blockDim.x` | Количество потоков в одном блоке |
| `threadIdx.x` | Индекс потока внутри своего блока |

### Глобальный идентификатор потока

Эти переменные объединяются для вычисления глобально уникального индекса потока:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

Общее количество потоков = `gridDim.x * blockDim.x`. Каждый поток обрабатывает один элемент независимо. Это основа **параллелизма данных (data parallelism)**. Одна и та же операция выполняется сразу над множеством элементов, без зависимостей между потоками.

---

### Модель выполнения GPU: волновые фронты (wavefronts)

GPU AMD выполняют потоки группами по **32**, называемыми **волновыми фронтами (wavefronts)**. Все потоки в волновом фронте выполняют одну и ту же инструкцию одновременно. Это влияет на выбор оптимального размера блока (256 потоков = 8 волновых фронтов = хорошая эффективность планирования).

### Программирование GPU AMD: HIP + ROCm

**ROCm** — это открытый стек вычислений на GPU от AMD (драйверы, компиляторы, библиотеки, среда выполнения). **HIP** располагается поверх него и спроектирован так, чтобы быть синтаксически идентичным CUDA. Сборка PyTorch для ROCm прозрачно отображает `torch.cuda.*` на HIP, поэтому один и тот же код работает на GPU AMD.

---

### PyTorch + AMD/HIP

PyTorch поставляется в сборке для ROCm, где набор API CUDA (`torch.cuda.*`) прозрачно реализован поверх HIP. Это означает, что:

- `torch.cuda.is_available()` работает на GPU AMD с ROCm
- `tensor.to("cuda")` выделяет память на GPU AMD
- `torch.version.hip` отображает версию HIP

PyTorch также предоставляет `torch.cuda._compile_kernel()` — высокоуровневый способ быстро JIT-компилировать строку с исходным кодом ядра и получить вызываемый объект без отдельного этапа сборки.

---

<!-- @device:halo_box -->
## Проверка обновлений программного обеспечения

<!-- @require:software-update -->
<!-- @device:end -->

## Установка необходимого программного обеспечения
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Предварительные требования - Windows
- Установите последнюю версию: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### Создание виртуального окружения

<!-- @os:linux -->
<!-- @device:halo_box -->
В Linux откройте терминал в выбранном вами каталоге и выполните команды для создания venv с уже установленными ROCm+PyTorch.
<!-- @test:id=create-venv timeout=300 -->
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
**Предоставьте вашему пользователю доступ к устройствам GPU** (для вступления в силу выйдите из системы и войдите снова):

```bash
sudo usermod -aG render,video $LOGNAME
```

В Linux откройте терминал в выбранном вами каталоге и выполните команды для создания venv.
<!-- @test:id=create-venv timeout=300 -->
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
В Windows откройте терминал в выбранном вами каталоге и выполните команды для создания venv.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **Совет**: пользователям Windows может потребоваться изменить политику выполнения PowerShell (Execution Policy) (например,
> установить значение RemoteSigned или Unrestricted) перед запуском некоторых команд PowerShell.

<!-- @os:end -->


### Установка базовых зависимостей
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
> **Примечание:** для этого playbook необходимо установить ROCm и PyTorch в виртуальное окружение даже на Ryzen AI Halo, поскольку компиляция пользовательских ядер требует полного набора заголовков разработки (development headers).

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
Установите набор инструментов сборки Linux C/C++. Это системная зависимость, необходимая для примеров с расширениями на C++, так как `CUDAExtension` собирает нативные модули `.so` из файлов `.cu`.

Выполните это один раз на машине с Linux, вне созданного виртуального окружения Python:

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
Убедитесь, что установлена [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) или [более новая версия](https://visualstudio.microsoft.com/vs/community/) с рабочей нагрузкой **Desktop development with C++**.

> **Примечание**: Настройка среды Visual Studio C++ требуется только для подхода **C++ Extension**. Для подхода JIT Compilation она не нужна.

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

**(A) Запустите `vcvars64.bat` и зафиксируйте установленную им среду**

Это делает доступными `cl.exe`, `INCLUDE`, `LIB`, `LIBPATH` и пути к Windows SDK.

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) Импортируйте переменные среды Visual Studio в текущую сессию PowerShell**

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
Убедитесь, что GPU AMD виден с помощью:
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
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Файлы JIT и расширения C++ для ядра умножения матриц |


## Пример 1: Сложение векторов

#### Подход A: JIT-компиляция

JIT (Just-In-Time, компиляция на лету) означает, что ядро записывается как необработанная строка C++ внутри Python и компилируется во время выполнения, без необходимости в дополнительных шагах сборки.

Чтобы использовать [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py), убедитесь, что он загружен, и выполните:
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
> **Совет**: скрипт также запускает фоновый поток, который опрашивает `amd-smi` каждые 100 мс, чтобы регистрировать пиковую и среднюю загрузку GPU во время выполнения ядра.
<!-- @os:end -->

> **Примечание**: **Почему размер блока равен 256?** <br>
> - Ядро использует **256 потоков на блок**, поскольку это хорошо согласуется с **моделью выполнения wavefront на GPU AMD**.
> - Напомним, что оборудование AMD выполняет потоки группами по 32 потока, что дает 8 wavefront на блок. (8 wavefront x 32 потока = 1 блок)


**Что делает рабочая нагрузка:**

Ядро искусственно добавляет дополнительную работу, чтобы продемонстрировать загрузку GPU:

- **100 000 000 элементов** в тензоре
- **Внутренний цикл выполняется 1000 раз** на элемент за один запуск ядра  
- **200 запусков ядра** всего

**Математика:**  
- Каждый элемент: увеличивается на 1 × 1000 итераций × 200 запусков = 200 000  
- Итоговый результат: 1.0 (начальное значение) + 200 000 (сложения) = 200001.0

**Зачем нужен внутренний цикл?**  
- Без цикла `for (int i = 0; i < 1000; i++)` 200 запусков завершились бы мгновенно, и инструменты мониторинга не смогли бы зафиксировать значимую загрузку GPU. Искусственная работа делает каждый запуск ядра достаточно продолжительным, чтобы инструменты мониторинга могли измерить производительность.

<!-- @os:linux -->
**Ожидаемый вывод:**[Показатели производительности будут отличаться]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Примечание**: в Windows `amd-smi` не поддерживается. Для отслеживания загрузки GPU можно использовать Диспетчер задач, где во время выполнения программы должен наблюдаться кратковременный всплеск загрузки.

**Ожидаемый вывод:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**Отличная работа! Вы только что запустили своё первое ядро GPU.**

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
#### Подход Б: расширение C++

Второй подход более ручной: ядро и Python-привязка записываются в один файл `.cu`, компилируются нативно с помощью системы сборки PyTorch и импортируются в Python.

<!-- @os:windows -->
> **Примечание**: подход с расширением C++ требует наличия среды сборки Visual Studio C++, поскольку PyTorch компилирует исходный файл `.cu` в нативный модуль расширения `.pyd`. Сборка этого нативного расширения зависит от набора инструментов Microsoft C++ (компилятор, компоновщик и средства сборки), предоставляемого Visual Studio. Перед сборкой расширения выполните команды активации Visual Studio из раздела настройки.
<!-- @os:end -->

Загрузите следующие файлы, если вы ещё этого не сделали:
<!-- @os:windows -->
| Файл | Роль |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Ядро + функция запуска + привязка pybind11, всё в одном файле |
| [setup.py](assets/Vector_Addition/setup.py) | Скрипт сборки, использует `CUDAExtension` для компиляции `.cu` в `.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Python-скрипт, запускающий собранные артефакты |
<!-- @os:end -->

<!-- @os:linux -->
| Файл | Роль |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Ядро + функция запуска + привязка pybind11, всё в одном файле |
| [setup.py](assets/Vector_Addition/setup.py) | Скрипт сборки, использует `CUDAExtension` для компиляции `.cu` в `.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Python-скрипт, запускающий собранные артефакты |
<!-- @os:end -->

#### **Шаг 1: ядро, функция запуска и привязка** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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

>**Совет**: зачем использовать `hipDeviceSynchronize()`? <br>
> - Запуск ядра GPU выполняется асинхронно. Когда CPU выполняет `add_one<<<grid_size, block_size>>>(data, n);`, он немедленно переходит к выполнению следующей инструкции, не дожидаясь GPU. `hipDeviceSynchronize()` заставляет CPU дождаться завершения работы ядра на GPU.

#### **Шаг 2: сборка**
```bash
pip install --no-build-isolation -v .
```
>**Примечание**: эта команда ищет `setup.py` в текущем каталоге для сборки созданного нами файла .cu.


`CUDAExtension` — это вспомогательный инструмент сборки CUDA из `torch.utils.cpp_extension`. При использовании ROCm PyTorch **перенаправляет `CUDAExtension` на использование `hipcc`** вместо `nvcc`. ROCm перехватывает процесс сборки и направляет его через компилятор HIP, портируя код CUDA на устройства AMD.

В результате создаются следующие файлы:
<!-- @os:windows -->
- `build/`: каталог с файлами `.pyd`
- `add_one_kernel.hip`: исходный код HIP, сгенерированный в результате хипификации файла `.cu`; именно его на самом деле скомпилировал `hipcc`
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: каталог с файлами `.so`
- `add_one_kernel.hip`: исходный код HIP, сгенерированный в результате хипификации файла `.cu`; именно его на самом деле скомпилировал `hipcc`
<!-- @os:end -->

#### **Шаг 3: использование из Python** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
Выполните этот скрипт, чтобы увидеть ядро в действии:
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**Ожидаемый результат:**
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

## Пошаговое руководство 2: умножение матриц

Умножение матриц вычисляет **C = A × B**, где:
- **A** имеет размер M×N (строки × столбцы)
- **B** имеет размер N×K  
- **C** имеет размер M×K (результат)

Каждый элемент результата определяется как:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

Каждый элемент C вычисляется независимо, что делает эту задачу идеальной для параллелизма на GPU.

#### Как это отображается на потоки GPU

В отличие от сложения векторов (1D), умножение матриц даёт **2D-результат**, поэтому используется **2D-сетка потоков**:

| | Сложение векторов | Умножение матриц |
|---|---|---|
| **Форма результата** | одномерный массив | 2D-матрица (M×K) |
| **Отображение потоков** | 1 поток → 1 элемент | 1 поток → 1 элемент результата |
| **Схема запуска** | 1D-сетка: `(grid_x, 1, 1)` | 2D-сетка: `(grid_x, grid_y, 1)` |
| **Размер блока** | `(256, 1, 1)` | `(16, 16, 1)` = 256 потоков |

Каждый поток вычисляет один элемент результирующей матрицы C. Поток в позиции `(row, col)` вычисляет `C[row][col]`, перемножая соответствующую строку A и соответствующий столбец B.

**Компоновка памяти**: память GPU плоская (1D), но матрицы хранятся построчно. Чтобы обратиться к `A[row][col]`, ядро использует `A[row * N + col]`.


#### Подход А: JIT-компиляция:

Как и в пошаговом руководстве 1, ядро записывается в виде необработанной строки C++ внутри Python и компилируется во время выполнения с помощью встроенного JIT-компилятора PyTorch.


Чтобы использовать [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py), убедитесь, что он загружен, и выполните:
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

Скрипт проверяет результат по сравнению с `torch.mm` с небольшим допуском. Операции с плавающей запятой на GPU могут давать небольшие числовые расхождения по сравнению с реализациями на CPU из-за порядка параллельной редукции.

<!-- @os:linux -->
**Ожидаемый результат:** [значения производительности могут отличаться]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Примечание**: в Windows `amd-smi` не поддерживается. Для отслеживания загрузки GPU можно использовать диспетчер задач, где при запуске программы должен быть виден кратковременный всплеск загрузки.

**Ожидаемый результат:**
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
#### Подход B: расширение на C++

Второй подход более ручной: код ядра и Python-привязка записываются в один файл `.cu`, компилируются нативно с использованием системы сборки PyTorch, а затем импортируются в Python.

<!-- @os:windows -->
> **Примечание**: подход с расширением на C++ требует наличия среды сборки Visual Studio C++, так как PyTorch компилирует исходный файл `.cu` в нативный модуль расширения `.pyd`. Сборка такого нативного расширения зависит от набора инструментов Microsoft C++ (компилятора, компоновщика и инструментов сборки), предоставляемого Visual Studio. Перед сборкой расширения выполните команды активации Visual Studio из раздела настройки.
<!-- @os:end -->

Загрузите следующие файлы, если вы ещё этого не сделали:
<!-- @os:windows -->
| Файл | Роль |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Ядро + функция запуска + привязка pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Скрипт сборки, использует `CUDAExtension` для компиляции `.cu` в `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python-скрипт, запускающий собранные артефакты |
<!-- @os:end -->
<!-- @os:linux -->
| Файл | Роль |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Ядро + функция запуска + привязка pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Скрипт сборки, использует `CUDAExtension` для компиляции `.cu` в `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python-скрипт, запускающий собранные артефакты |
<!-- @os:end -->

#### **Шаг 1: Ядро, функция запуска и привязка** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
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

По сравнению с `add_one_launcher` из практического занятия 1, функция запуска здесь:
- Принимает два входных тензора вместо одного
- Определяет все три размерности (M, N, K) на основе форм тензоров, без передачи размеров вручную из Python
- Выделяет и возвращает выходной тензор C, а не изменяет его на месте
- Использует `dim3` как для сетки, так и для блока, чтобы выразить 2D-форму запуска

#### **Шаг 2: Сборка**
```bash
pip install --no-build-isolation -v .
```
>**Примечание**: эта команда ищет `setup.py` в текущем каталоге для сборки созданного нами файла .cu.


В результате будут созданы следующие файлы:
<!-- @os:windows -->
- `build/`: каталог с файлами `.pyd`
- `matmul_kernel.hip`: HIP-исходный код, сгенерированный при hipify-преобразовании файла `.cu`; именно его на самом деле скомпилировал `hipcc`
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: каталог с файлами `.so`
- `matmul_kernel.hip`: HIP-исходный код, сгенерированный при hipify-преобразовании файла `.cu`; именно его на самом деле скомпилировал `hipcc`
<!-- @os:end -->

#### **Шаг 3: Использование из Python** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
Выполните этот скрипт, чтобы увидеть работу ядра:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**Ожидаемый результат:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**Отлично! Вы только что реализовали умножение матриц на GPU.** Это важная веха, поскольку умножение матриц лежит в основе современных операций машинного обучения, таких как:
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

## Дальнейшие шаги

Вы научились писать, компилировать и запускать GPU-ядра, используя как JIT-компиляцию, так и расширения на C++ для базовых параллельных операций.

**Оптимизации производительности:**
- **Тайлинг с использованием разделяемой памяти** — кэширование блоков данных для уменьшения обращений к глобальной памяти
- **Коалесцирование памяти** — оптимизация шаблонов доступа к памяти для повышения пропускной способности

**Алгоритмы из реального мира:**
- **2D-свёртка** — небольшой фильтр (ядро) перемещается по изображению, вычисляя каждый выходной пиксель как взвешенную сумму соседних пикселей. Это вводит понятие трафаретных (stencil) вычислений и тайлинга с использованием разделяемой памяти, где потоки повторно используют перекрывающиеся области изображения для уменьшения обращений к глобальной памяти.
- **Функция Softmax**: Softmax преобразует вектор чисел в вероятности, сумма которых равна 1; часто используется на выходе нейронных сетей. Эффективная реализация на GPU вводит понятия параллельных редукций и методов численной устойчивости при обработке больших векторов.

**Аспекты промышленной эксплуатации:**
- **Обработка ошибок** — проверка границ и управление устройствами
- **Интеграция с PyTorch** — пользовательские операторы с поддержкой автоградиента