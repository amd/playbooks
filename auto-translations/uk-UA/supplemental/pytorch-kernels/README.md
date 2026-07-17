<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Огляд

Напишіть GPU ядро з нуля, скомпілюйте його, запустіть на AMD GPU і спостерігайте за стрибком завантаженості. Цей посібник показує, як насправді працюють GPU обчислення: напишіть код ядра та виконайте його паралельно на тисячах потоків.

> **Примітка**: Це досить складний посібник, який може потребувати додаткового налагодження та модифікацій.

## Що ви дізнаєтесь

<!-- @os:windows -->
- Як працюють GPU ядра: сітки, блоки, потоки та модель індексування, яка відображає їх на дані
- Як стек AMD ROCm/HIP дозволяє писати CUDA-подібний код, що працює на AMD GPU без змін
- Як компілювати ядро під час виконання за допомогою `torch.cuda._compile_kernel`
- Як створити нативне розширення C++ ядра за допомогою `CUDAExtension` + pybind11, яке можна імпортувати з Python
<!-- @os:end -->
<!-- @os:linux -->
- Як працюють GPU ядра: сітки, блоки, потоки та модель індексування, яка відображає їх на дані
- Як стек AMD ROCm/HIP дозволяє писати CUDA-подібний код, що працює на AMD GPU без змін
- Як компілювати ядро під час виконання за допомогою `torch.cuda._compile_kernel`
- Як створити нативне розширення C++ ядра за допомогою `CUDAExtension` + pybind11, яке можна імпортувати з Python
- Як вимірювати час виконання ядра та відстежувати завантаженість GPU в реальному часі за допомогою `amd-smi`
<!-- @os:end -->

---

Цей посібник охоплює два підходи до розробки ядер:

<!-- @os:windows -->
| Підхід | Точка входу |
|---|---|
| **JIT-компіляція** | `torch.cuda._compile_kernel` — написати ядро як рядок Python без кроку збірки |
| **Розширення C++** | `CUDAExtension` + pybind11: скомпілювати файл `.cu` у нативний `.pyd` та імпортувати його |
<!-- @os:end -->
<!-- @os:linux -->
| Підхід | Точка входу |
|---|---|
| **JIT-компіляція** | `torch.cuda._compile_kernel` — написати ядро як рядок Python без кроку збірки |
| **Розширення C++** | `CUDAExtension` + pybind11: скомпілювати файл `.cu` у нативний `.so` та імпортувати його |
<!-- @os:end -->

Обидва підходи працюють на AMD GPU. Це можливо тому, що збірка PyTorch для ROCm відображає весь API-поверхні CUDA на HIP. Це означає, що `torch.cuda`, `CUDAExtension` та синтаксис CUDA ядер прозоро працюють на апаратному забезпеченні AMD.

---

## Передумови

### Що таке GPU ядро?

GPU ядро — це функція, яка виконується паралельно на тисячах GPU потоків одночасно. На відміну від функції CPU, яка виконується один раз за виклик, ядро запускається з **сіткою** **блоків**, кожен з яких містить багато **потоків**, що виконують однаковий код на різних даних.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### Модель індексування потоків

При запуску ядра ви вказуєте два виміри:

| Змінна | Значення |
|---|---|
| `gridDim` | Кількість блоків у сітці |
| `blockDim` | Кількість потоків у блоці |

Кожен потік має доступ до трьох вбудованих змінних лише для читання:

| Змінна | Значення |
|---|---|
| `blockIdx.x` | До якого блоку належить цей потік |
| `blockDim.x` | Кількість потоків в одному блоці |
| `threadIdx.x` | Індекс потоку всередині його блоку |

### Глобальний ідентифікатор потоку

Ці змінні поєднуються для обчислення глобально унікального індексу потоку:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

Загальна кількість потоків = `gridDim.x * blockDim.x`. Кожен потік незалежно обробляє один елемент. Це основа **паралелізму даних**. Одна й та сама операція виконується на багатьох елементах одночасно без залежностей між потоками.

---

### Модель виконання GPU: Wavefronts

AMD GPU виконують потоки групами по **32**, які називаються **wavefronts**. Усі потоки у wavefront виконують одну й ту саму інструкцію одночасно. Це впливає на вибір оптимального розміру блоку (256 потоків = 8 wavefronts = хороша ефективність планування).

### Програмування AMD GPU: HIP + ROCm

**ROCm** — це відкритий стек GPU обчислень AMD (драйвери, компілятори, бібліотеки, середовище виконання). **HIP** розташований поверх нього і розроблений так, щоб бути синтаксично ідентичним CUDA. Збірка PyTorch для ROCm прозоро відображає `torch.cuda.*` на HIP, тому той самий код працює на AMD GPU.

---

### PyTorch + AMD/HIP

PyTorch постачається зі збіркою для ROCm, де API-поверхня CUDA (`torch.cuda.*`) прозоро підтримується HIP. Це означає:

- `torch.cuda.is_available()` працює на AMD GPU з ROCm
- `tensor.to("cuda")` виділяє пам'ять на AMD GPU
- `torch.version.hip` надає версію HIP

PyTorch також надає `torch.cuda._compile_kernel()` — зручний скорочений спосіб JIT-компіляції рядка з необробленим ядром та отримання виклику без необхідності окремого кроку збірки.

---

<!-- @device:halo_box -->
## Перевірка оновлень програмного забезпечення

<!-- @require:software-update -->
<!-- @device:end -->

## Встановлення необхідного програмного забезпечення
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Передумови — Windows
- Встановіть останню версію: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### Створення віртуального середовища

<!-- @os:linux -->
<!-- @device:halo_box -->
У Linux відкрийте термінал у вибраній директорії та виконайте команди для створення venv з уже встановленими ROCm+PyTorch.
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
**Надайте вашому користувачу доступ до пристроїв GPU** (вийдіть із системи та увійдіть знову, щоб зміни набули чинності):

```bash
sudo usermod -aG render,video $LOGNAME
```

У Linux відкрийте термінал у вибраній директорії та виконайте команди для створення venv.
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
У Windows відкрийте термінал у вибраній директорії та виконайте команди для створення venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **Порада**: Користувачам Windows може знадобитися змінити політику виконання PowerShell (наприклад,
> встановити її на RemoteSigned або Unrestricted) перед виконанням деяких команд PowerShell.

<!-- @os:end -->
### Встановлення основних залежностей
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
> **Примітка:** Для цього посібника ROCm і PyTorch потрібно встановити у віртуальне середовище навіть на Ryzen AI Halo, оскільки компіляція власних ядер вимагає повних заголовків розробки.

Встановіть ROCm:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

Встановіть PyTorch:
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

### Встановлення додаткових залежностей

<!-- @os:linux -->
Встановіть набір інструментів збірки Linux C/C++. Це залежність системного рівня, яка необхідна для покрокових інструкцій із розширення C++, оскільки `CUDAExtension` збирає нативні модулі `.so` з файлів `.cu`.

Виконайте це один раз на машині Linux, поза створеним віртуальним середовищем Python:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

Після активації віртуального середовища `kernel-env` встановіть залежності збірки Python:
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
Переконайтеся, що встановлено [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) або [новішу версію](https://visualstudio.microsoft.com/vs/community/) з робочим навантаженням **Розробка робочого столу на C++**.

> **Примітка**: Це налаштування середовища Visual Studio C++ потрібне лише для підходу з **розширенням C++**. Воно не потрібне для підходу з JIT-компіляцією.

Відкрийте термінал PowerShell і виконайте наступні команди перед збіркою розширення C++.

**Крок 1: Знайдіть встановлене середовище Visual Studio C++**

**(A) Знайдіть `vswhere.exe`, який встановлюється разом із Visual Studio Installer**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) Знайдіть `vcvars64.bat` з Visual Studio 2022 або новішої версії з інструментами збірки C++**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(C) Виведіть використовуване середовище Visual Studio C++**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**Крок 2: Активуйте середовище збірки Visual Studio C++**

**(A) Запустіть `vcvars64.bat` і захопіть середовище, яке він встановлює**

Це робить доступними `cl.exe`, `INCLUDE`, `LIB`, `LIBPATH` та шляхи Windows SDK.

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) Імпортуйте змінні середовища Visual Studio у цей сеанс PowerShell**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**Крок 3: Перевірте доступність компілятора Microsoft C++**

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

#### Встановлення змінних середовища
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
Перевірте, що GPU AMD видимий, за допомогою:
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

## Завантаження необхідних файлів

Створіть наступну структуру каталогів, створивши **2 нові папки** та завантаживши відповідні файли:

| Каталог | Файли для завантаження | Опис |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| Файли JIT та розширення C++ для ядра векторного додавання |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Файли JIT та розширення C++ для ядра множення матриць |


## Покрокові інструкції

### Покрокова інструкція 1: Векторне додавання

#### Підхід A: JIT-компіляція

JIT (Just-In-Time, компіляція «на льоту») означає, що ядро написане як необроблений рядок C++ всередині Python і компілюється під час виконання, без необхідності додаткових кроків збірки.

Щоб використати [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py), переконайтеся, що він завантажений, і запустіть:
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**Ключові фрагменти коду**
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
> **Порада**: Скрипт також запускає фоновий потік, який опитує `amd-smi` кожні 100 мс для реєстрації пікового та середнього використання GPU під час виконання ядра.
<!-- @os:end -->

> **Примітка**: **Чому розмір блоку дорівнює 256?** <br>
> - Ядро використовує **256 потоків на блок**, оскільки це добре узгоджується з **моделлю виконання хвильового фронту GPU AMD**.
> - Нагадаємо, що апаратне забезпечення AMD виконує потоки групами по 32 потоки, що дає 8 хвильових фронтів на блок. (8 хвильових фронтів × 32 потоки = 1 блок)


**Що робить робоче навантаження:**

Ядро штучно додає зайву роботу для демонстрації використання GPU:

- **100 000 000 елементів** у тензорі
- **Внутрішній цикл виконується 1 000 разів** на елемент на кожен запуск ядра  
- **200 запусків ядра** загалом

**Математика:**  
- Кожен елемент: збільшується на 1 × 1 000 ітерацій × 200 запусків = 200 000  
- Кінцевий результат: 1,0 (початкове значення) + 200 000 (додавань) = 200 001,0

**Навіщо потрібен внутрішній цикл?**  
- Без циклу `for (int i = 0; i < 1000; i++)` 200 запусків завершилися б миттєво, і інструменти моніторингу не зафіксували б значущого використання GPU. Штучна робота робить кожен запуск ядра достатньо тривалим для вимірювання продуктивності інструментами моніторингу.

<!-- @os:linux -->
**Очікуваний результат:** [Показники продуктивності можуть відрізнятися]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Примітка**: У Windows `amd-smi` не підтримується. Для відстеження використання GPU можна скористатися Диспетчером завдань, де під час запуску програми має спостерігатися короткочасний стрибок використання.

**Очікуваний результат:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**Чудова робота! Ви щойно запустили своє перше ядро GPU.**

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
#### Підхід B: Розширення C++

Другий підхід є більш ручним: напишіть ядро та прив'язку Python до одного файлу `.cu`, скомпілюйте його нативно за допомогою системи збірки PyTorch та імпортуйте в Python.

<!-- @os:windows -->
> **Примітка**: Підхід з розширенням C++ вимагає середовища збірки Visual Studio C++, оскільки PyTorch компілює файл `.cu` у нативний модуль розширення `.pyd`. Збірка цього нативного розширення залежить від інструментарію Microsoft C++ (компілятор, компонувальник та інструменти збірки), що надається Visual Studio. Виконайте команди активації Visual Studio з розділу налаштування перед збіркою розширення.
<!-- @os:end -->

Завантажте наступні файли, якщо ви ще цього не зробили:
<!-- @os:windows -->
| Файл | Роль |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Ядро + запускач + прив'язка pybind11, все в одному файлі |
| [setup.py](assets/Vector_Addition/setup.py) | Скрипт збірки, використовує `CUDAExtension` для компіляції `.cu` у `.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Скрипт Python, що запускає зібрані артефакти |
<!-- @os:end -->

<!-- @os:linux -->
| Файл | Роль |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Ядро + запускач + прив'язка pybind11, все в одному файлі |
| [setup.py](assets/Vector_Addition/setup.py) | Скрипт збірки, використовує `CUDAExtension` для компіляції `.cu` у `.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Скрипт Python, що запускає зібрані артефакти |
<!-- @os:end -->

#### **Крок 1: Ядро, запускач та прив'язка** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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

>**Порада**: Навіщо використовувати `hipDeviceSynchronize()`? <br>
> - Запуски ядер GPU є асинхронними. Коли CPU виконує `add_one<<<grid_size, block_size>>>(data, n);`, він негайно переходить до наступної інструкції, не чекаючи завершення роботи GPU. `hipDeviceSynchronize()` змушує CPU чекати, поки ядро GPU завершить виконання.

#### **Крок 2: Збірка**
```bash
pip install --no-build-isolation -v .
```
>**Примітка**: Ця команда шукає `setup.py` у поточному каталозі для збірки файлу .cu, який ми створили.


`CUDAExtension` — це допоміжний інструмент збірки CUDA з `torch.utils.cpp_extension`. З ROCm PyTorch **перенаправляє `CUDAExtension` на використання `hipcc`** замість `nvcc`. ROCm перехоплює шлях збірки та направляє його через компілятор HIP, портуючи код CUDA на AMD.

Це створює наступні файли:
<!-- @os:windows -->
- `build/`: каталог з файлами `.pyd`
- `add_one_kernel.hip`: джерело HIP, згенероване шляхом hipify файлу `.cu`; саме це компілює `hipcc`
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: каталог з файлами `.so`
- `add_one_kernel.hip`: джерело HIP, згенероване шляхом hipify файлу `.cu`; саме це компілює `hipcc`
<!-- @os:end -->

#### **Крок 3: Використання з Python** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
Виконайте цей скрипт, щоб побачити ядро в дії:
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**Очікуваний результат:**
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

### Покрокове керівництво 2: Множення матриць

Множення матриць обчислює **C = A × B**, де:
- **A** має розмір M×N (рядки × стовпці)
- **B** має розмір N×K  
- **C** має розмір M×K (результат)

Кожен вихідний елемент визначається як:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

Кожен елемент C обчислюється незалежно, що робить цю задачу ідеальною для паралелізму GPU.

#### Як це відображається на потоки GPU

На відміну від векторного додавання (1D), множення матриць дає **2D вихід**, тому ми використовуємо **2D сітку потоків**:

| | Векторне додавання | Множення матриць |
|---|---|---|
| **Форма виходу** | 1D масив | 2D матриця (M×K) |
| **Відображення потоків** | 1 потік → 1 елемент | 1 потік → 1 вихідний елемент |
| **Шаблон запуску** | 1D сітка: `(grid_x, 1, 1)` | 2D сітка: `(grid_x, grid_y, 1)` |
| **Розмір блоку** | `(256, 1, 1)` | `(16, 16, 1)` = 256 потоків |

Кожен потік обчислює один елемент вихідної матриці C. Потік у позиції `(row, col)` обчислює `C[row][col]`, множачи відповідний рядок A на відповідний стовпець B.

**Розміщення в пам'яті**: Пам'ять GPU є плоскою (1D), але матриці зберігаються рядок за рядком. Для доступу до `A[row][col]` ядро використовує `A[row * N + col]`.


#### Підхід A: JIT-компіляція:

Як і в покроковому керівництві 1, ядро записується як рядок C++ у Python та компілюється під час виконання за допомогою вбудованого JIT PyTorch.


Щоб використати [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py), переконайтеся, що він завантажений, та запустіть:
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**Ключові фрагменти коду**
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

Скрипт перевіряє результат порівняно з `torch.mm` з невеликим допуском. Арифметика з плаваючою комою на GPU може давати невеликі числові відмінності порівняно з реалізаціями на CPU через порядок паралельного зведення.

<!-- @os:linux -->
**Очікуваний результат:** [Показники продуктивності можуть відрізнятися]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Примітка**: У Windows `amd-smi` не підтримується. Для відстеження завантаженості GPU можна використовувати Диспетчер завдань, де під час запуску програми має спостерігатися короткочасний стрибок завантаженості.

**Очікуваний результат:**
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
#### Підхід Б: Розширення C++

Другий підхід є більш ручним: написати ядро та прив'язку Python до одного файлу `.cu`, скомпілювати його нативно за допомогою системи збірки PyTorch та імпортувати в Python.

<!-- @os:windows -->
> **Примітка**: Підхід з розширенням C++ вимагає середовища збірки Visual Studio C++, оскільки PyTorch компілює вихідний файл `.cu` у нативний модуль розширення `.pyd`. Збірка цього нативного розширення залежить від інструментального ланцюжка Microsoft C++ (компілятор, компонувальник та інструменти збірки), що надається Visual Studio. Перед збіркою розширення виконайте команди активації Visual Studio з розділу налаштування.
<!-- @os:end -->

Завантажте наступні файли, якщо ви ще цього не зробили:
<!-- @os:windows -->
| Файл | Роль |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Ядро + запускач + прив'язка pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Скрипт збірки, використовує `CUDAExtension` для компіляції `.cu` у `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python-скрипт, що запускає зібрані артефакти |
<!-- @os:end -->
<!-- @os:linux -->
| Файл | Роль |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Ядро + запускач + прив'язка pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Скрипт збірки, використовує `CUDAExtension` для компіляції `.cu` у `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python-скрипт, що запускає зібрані артефакти |
<!-- @os:end -->

#### **Крок 1: Ядро, запускач та прив'язка** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
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

Порівняно з `add_one_launcher` у Покроковому прикладі 1, запускач тут:
- Приймає два вхідних тензори замість одного
- Отримує всі три виміри (M, N, K) з форм тензорів, без ручної передачі розміру з Python
- Виділяє та повертає вихідний тензор C, а не змінює дані на місці
- Використовує `dim3` як для сітки, так і для блоку, щоб виразити двовимірну форму запуску

#### **Крок 2: Збірка**
```bash
pip install --no-build-isolation -v .
```
>**Примітка**: Ця команда шукає `setup.py` у поточному каталозі для збірки створеного нами файлу .cu.


Це створює наступні файли:
<!-- @os:windows -->
- `build/`: каталог з файлами `.pyd`
- `matmul_kernel.hip`: вихідний код HIP, згенерований шляхом hipify-перетворення файлу `.cu`; саме його компілює `hipcc`
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: каталог з файлами `.so`
- `matmul_kernel.hip`: вихідний код HIP, згенерований шляхом hipify-перетворення файлу `.cu`; саме його компілює `hipcc`
<!-- @os:end -->

#### **Крок 3: Використання з Python** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
Виконайте цей скрипт, щоб побачити ядро в дії:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**Очікуваний результат:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**Чудово! Ви щойно реалізували множення матриць на GPU.** Це важливий етап, оскільки множення матриць є основою сучасних операцій машинного навчання, таких як:
- Шари нейронних мереж
- Механізми уваги
- Вбудовування
- Трансформери

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

## Наступні кроки

Ви навчилися писати, компілювати та запускати ядра GPU, використовуючи як JIT-компіляцію, так і розширення C++ для базових паралельних операцій.

**Оптимізації продуктивності:**
- **Тайлінг із спільною пам'яттю** — кешування блоків даних для зменшення звернень до глобальної пам'яті
- **Злиття звернень до пам'яті** — оптимізація шаблонів доступу до пам'яті для підвищення пропускної здатності

**Реальні алгоритми:**
- **2D згортка** — невеликий фільтр (ядро) ковзає по зображенню, обчислюючи кожен вихідний піксель як зважену суму сусідніх пікселів. Це вводить трафаретні обчислення та тайлінг із спільною пам'яттю, де потоки повторно використовують перекриваючі регіони зображення для зменшення звернень до глобальної пам'яті.
- **Функція Softmax**: Softmax перетворює вектор чисел на ймовірності, що в сумі дають 1, і широко використовується у виходах нейронних мереж. Ефективна реалізація на GPU вводить паралельні редукції та методи чисельної стабільності при обробці великих векторів.

**Виробничі міркування:**
- **Обробка помилок** — перевірка меж та керування пристроями
- **Інтеграція з PyTorch** — користувацькі оператори з підтримкою autograd