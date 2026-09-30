<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機器翻譯。**本頁面是由英文自動翻譯而成，尚未經過人工審閱。內容可能包含錯誤，且某些指示、命令、下載項目、產品供應情況或其他內容可能因語言或地區而異。如本文件與英文版本之間存在任何不一致或差異，應以該 playbook 之英文原始版本為準。
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## 概述

從頭開始撰寫 GPU 核心（kernel）、編譯它、在 AMD GPU 上啟動它，並觀察使用率飆升。此操作手冊展示了 GPU 運算實際運作的方式：撰寫核心程式碼，並在數千個執行緒（thread）間並行執行它。

> **注意**：這是一份相當複雜的操作手冊，可能需要一些額外的除錯與修改。

## 您將學到的內容

<!-- @os:windows -->
- GPU 核心如何運作：網格（grid）、區塊（block）、執行緒（thread），以及將它們對應到資料的索引模型
- AMD ROCm/HIP 堆疊如何讓您撰寫 CUDA 風格的程式碼，並在 AMD GPU 上不經修改就能執行
- 如何使用 `torch.cuda._compile_kernel` 在執行期編譯核心
- 如何使用 `CUDAExtension` + pybind11 建置原生 C++ 核心擴充功能，並可從 Python 匯入
<!-- @os:end -->
<!-- @os:linux -->
- GPU 核心如何運作：網格（grid）、區塊（block）、執行緒（thread），以及將它們對應到資料的索引模型
- AMD ROCm/HIP 堆疊如何讓您撰寫 CUDA 風格的程式碼，並在 AMD GPU 上不經修改就能執行
- 如何使用 `torch.cuda._compile_kernel` 在執行期編譯核心
- 如何使用 `CUDAExtension` + pybind11 建置原生 C++ 核心擴充功能，並可從 Python 匯入
- 如何量測核心執行時間，並使用 `amd-smi` 監控即時 GPU 使用率
<!-- @os:end -->

---

本操作手冊涵蓋兩種核心開發方式：

<!-- @os:windows -->
| 方式 | 進入點 |
|---|---|
| **JIT 編譯** | `torch.cuda._compile_kernel`，將核心撰寫為 Python 字串，無需建置步驟 |
| **C++ 擴充功能** | `CUDAExtension` + pybind11：將 `.cu` 檔編譯為原生 `.pyd` 並匯入 |
<!-- @os:end -->
<!-- @os:linux -->
| 方式 | 進入點 |
|---|---|
| **JIT 編譯** | `torch.cuda._compile_kernel`，將核心撰寫為 Python 字串，無需建置步驟 |
| **C++ 擴充功能** | `CUDAExtension` + pybind11：將 `.cu` 檔編譯為原生 `.so` 並匯入 |
<!-- @os:end -->

這兩種方式都能在 AMD GPU 上執行。這是因為 PyTorch 的 ROCm 版本將整個 CUDA API 對應到 HIP。這意味著 `torch.cuda`、`CUDAExtension` 以及 CUDA 核心語法都能透明地在 AMD 硬體上運作。

---

## 背景知識

### 什麼是 GPU 核心（Kernel）？

GPU 核心是一種能同時在數千個 GPU 執行緒間並行執行的函式。與只執行一次的 CPU 函式不同，核心是以一個由多個**區塊（block）**組成的**網格（grid）**方式啟動，每個區塊包含許多**執行緒（thread）**，全部對不同的資料執行相同的程式碼。

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### 執行緒索引模型

啟動核心時，您需要指定兩個維度：

| 變數 | 意義 |
|---|---|
| `gridDim` | 網格中的區塊數量 |
| `blockDim` | 每個區塊中的執行緒數量 |

每個執行緒都可以存取三個內建的唯讀變數：

| 變數 | 意義 |
|---|---|
| `blockIdx.x` | 此執行緒所屬的區塊 |
| `blockDim.x` | 一個區塊中的執行緒數量 |
| `threadIdx.x` | 執行緒在其區塊中的索引 |

### 全域執行緒 ID

這些變數會結合起來，計算出一個全域唯一的執行緒索引：

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

總執行緒數 = `gridDim.x * blockDim.x`。每個執行緒獨立處理一個元素。這是**資料並行性（data parallelism）**的基礎。同一運算會同時在許多元素上執行，且執行緒之間沒有相依性。

---

### GPU 執行模型：Wavefront

AMD GPU 以 **32** 個執行緒為一組來執行，稱為 **wavefront**。一個 wavefront 中的所有執行緒會同時執行相同的指令。這會影響最佳區塊大小的選擇（256 個執行緒 = 8 個 wavefront = 良好的排程效率）。

### AMD GPU 程式設計：HIP + ROCm

**ROCm** 是 AMD 的開源 GPU 運算堆疊（驅動程式、編譯器、函式庫、執行環境）。**HIP** 建構於其上，其設計目標是在語法上與 CUDA 完全相同。PyTorch 的 ROCm 版本會將 `torch.cuda.*` 透明地對應到 HIP，因此相同的程式碼可在 AMD GPU 上運作。

---

### PyTorch + AMD/HIP

PyTorch 提供一個 ROCm 版本，其中 CUDA API（`torch.cuda.*`）由 HIP 透明地支援。這意味著：

- `torch.cuda.is_available()` 在具備 ROCm 的 AMD GPU 上可運作
- `tensor.to("cuda")` 會在 AMD GPU 上配置記憶體
- `torch.version.hip` 會顯示 HIP 版本

PyTorch 也提供了 `torch.cuda._compile_kernel()`，這是一個高階的捷徑函式，可即時（JIT）編譯原始核心字串，並取回一個可呼叫的物件，而無需獨立的建置步驟。

---

<!-- @device:halo_box -->
## 檢查軟體更新

<!-- @require:software-update -->
<!-- @device:end -->

## 安裝軟體必要條件
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### 必要條件 - Windows
- 安裝最新版本：[AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### 建立虛擬環境

<!-- @os:linux -->
<!-- @device:halo_box -->
在 Linux 上，於您選擇的目錄中開啟終端機，並依照下列指令建立一個已預先安裝 ROCm+Pytorch 的 venv。
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
**授予您的使用者存取 GPU 裝置的權限**（需登出並重新登入才會生效）：

```bash
sudo usermod -aG render,video $LOGNAME
```

在 Linux 上，於您選擇的目錄中開啟終端機，並依照下列指令建立一個 venv。
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
在 Windows 上，於您選擇的目錄中開啟終端機，並依照下列指令建立一個 venv。
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **提示**：Windows 使用者在執行部分 PowerShell 指令前，可能需要修改其 PowerShell 執行原則（例如，將其設定為 RemoteSigned 或 Unrestricted）。

<!-- @os:end -->


### 安裝基本相依套件
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
> **注意：** 對於此操作手冊，即使在 Ryzen AI Halo 上，也需要將 ROCm 和 PyTorch 安裝到虛擬環境中，因為自訂核心的編譯需要完整的開發標頭檔（development headers）。

安裝 ROCm：
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

安裝 PyTorch：
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
### 安裝其他相依項目

<!-- @os:linux -->
安裝 Linux C/C++ 建置工具鏈。這是系統層級的相依項目,C++ 擴充功能演練需要它,因為 `CUDAExtension` 會從 `.cu` 檔案建置原生 `.so` 模組。

請在 Linux 機器上執行一次此操作,並在建立的 Python 虛擬環境之外執行:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

啟用 `kernel-env` 虛擬環境後,安裝 Python 建置相依項目:
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
請確認已安裝 [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) 或[更新版本](https://visualstudio.microsoft.com/vs/community/),並包含 **Desktop development with C++** 工作負載。

> **注意**:此 Visual Studio C++ 環境設定僅在使用 **C++ Extension** 方法時才需要。JIT Compilation 方法不需要此設定。

開啟 PowerShell 終端機,並在建置 C++ 擴充功能之前執行以下命令。

**步驟 1:尋找已安裝的 Visual Studio C++ 環境**

**(A) 找出 `vswhere.exe`,此檔案會隨 Visual Studio Installer 一併安裝**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) 從具有 C++ 建置工具的 Visual Studio 2022 或更新版本中找出 `vcvars64.bat`**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(C) 印出目前使用的 Visual Studio C++ 環境**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**步驟 2:啟用 Visual Studio C++ 建置環境**

**(A) 執行 `vcvars64.bat` 並擷取其設定的環境變數**

這會讓 `cl.exe`、`INCLUDE`、`LIB`、`LIBPATH` 以及 Windows SDK 路徑都可供使用。

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) 將 Visual Studio 環境變數匯入此 PowerShell 工作階段**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**步驟 3:確認 Microsoft C++ 編譯器已可使用**

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

#### 設定環境變數
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
使用以下命令確認 AMD GPU 是否可見:
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

## 下載所需檔案

建立以下目錄結構,方法是新增 **2 個新資料夾**,並下載對應的檔案:

| 目錄 | 要下載的檔案 | 說明 |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| 用於向量加法核心的 JIT 與 C++ 擴充功能檔案 |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | 用於矩陣乘法核心的 JIT 與 C++ 擴充功能檔案 |


## 演練 1:向量加法

#### 方法 A:JIT 編譯

JIT(即時)編譯表示核心是以原始 C++ 字串的形式寫在 Python 中,並在執行階段編譯,不需要額外的建置步驟。

若要使用 [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py),請確保已下載該檔案並執行:
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**主要程式碼片段**
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
> **提示**:此指令碼還會產生一個背景執行緒,每 100 毫秒輪詢一次 `amd-smi`,以記錄核心執行期間的尖峰及平均 GPU 使用率。
<!-- @os:end -->

> **注意**:**為什麼區塊大小為 256?** <br>
> - 此核心使用**每個區塊 256 個執行緒**,因為這與 **AMD GPU 的波前(wavefront)執行模型**十分吻合。
> - 請記得 AMD 硬體會以 32 個執行緒為一組執行,因此每個區塊會產生 8 個波前。(8 個波前 x 32 個執行緒 = 1 個區塊)


**此工作負載的執行內容:**

此核心會人為地新增額外的工作,以展示 GPU 使用率:

- 張量中有 **100,000,000 個元素**
- 每次核心啟動時,每個元素的**內層迴圈會執行 1,000 次**
- 總共 **200 次核心啟動**

**數學運算:**  
- 每個元素:每次遞增 1 x 1,000 次疊代 x 200 次啟動 = 200,000  
- 最終結果:1.0(起始值)+ 200,000(累加值)= 200,001.0

**為什麼要使用內層迴圈?**  
- 若沒有 `for (int i = 0; i < 1000; i++)` 迴圈,200 次啟動會瞬間完成,監控工具就無法擷取有意義的 GPU 使用率資料。這個人為增加的工作量能讓每次核心執行時間長到足以讓監控工具測量效能。

<!-- @os:linux -->
**預期輸出:**[效能數字會有所不同]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **注意**:在 Windows 上,不支援 `amd-smi`。若要追蹤 GPU 使用率,您可以使用工作管理員,執行程式時應該會看到短暫的使用率高峰。

**預期輸出:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**做得好!您剛剛執行了第一個 GPU 核心。**

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
#### 方法 B：C++ 擴充

第二種方法較為手動：將核心與 Python 綁定寫入單一 `.cu` 檔案，使用 PyTorch 的建置系統原生編譯，並將其匯入 Python。

<!-- @os:windows -->
> **注意**：C++ 擴充方法需要 Visual Studio C++ 建置環境，因為 PyTorch 會將 `.cu` 原始檔編譯為原生的 `.pyd` 擴充模組。建置該原生擴充模組需要依賴 Visual Studio 提供的 Microsoft C++ 工具鏈（編譯器、連結器和建置工具）。請先執行設定章節中的 Visual Studio 啟用命令，再建置擴充模組。
<!-- @os:end -->

如果尚未下載以下檔案，請先下載：
<!-- @os:windows -->
| 檔案 | 作用 |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | 核心 + 啟動器 + pybind11 綁定，全部集中在同一檔案中 |
| [setup.py](assets/Vector_Addition/setup.py) | 建置腳本，使用 `CUDAExtension` 將 `.cu` 編譯成 `.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | 執行已建置產物的 Python 腳本 |
<!-- @os:end -->

<!-- @os:linux -->
| 檔案 | 作用 |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | 核心 + 啟動器 + pybind11 綁定，全部集中在同一檔案中 |
| [setup.py](assets/Vector_Addition/setup.py) | 建置腳本，使用 `CUDAExtension` 將 `.cu` 編譯成 `.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | 執行已建置產物的 Python 腳本 |
<!-- @os:end -->

#### **步驟 1：核心、啟動器與綁定**（[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)）：
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

>**提示**：為什麼要使用 `hipDeviceSynchronize()`？ <br>
> - GPU 核心啟動是非同步的。當 CPU 執行 `add_one<<<grid_size, block_size>>>(data, n);` 時，它會立即執行下一條指令，而不會等待 GPU。`hipDeviceSynchronize()` 會強制 CPU 等待，直到 GPU 核心執行完成為止。

#### **步驟 2：建置**
```bash
pip install --no-build-isolation -v .
```
>**注意**：此命令會在目前目錄中尋找 `setup.py`，以建置我們建立的 .cu 檔案。


`CUDAExtension` 是來自 `torch.utils.cpp_extension` 的 CUDA 建置輔助工具。在 ROCm 中，PyTorch **會將 `CUDAExtension` 重新對應到使用 `hipcc`**，而非 `nvcc`。ROCm 會攔截建置流程，並將其導向 HIP 編譯器，將 CUDA 程式碼移植到 AMD。

這會產生以下檔案：
<!-- @os:windows -->
- `build/`：包含 `.pyd` 檔案的目錄
- `add_one_kernel.hip`：透過將 `.cu` 檔案進行 hipify 所產生的 HIP 原始碼；這才是 `hipcc` 實際編譯的內容
<!-- @os:end -->
<!-- @os:linux -->
- `build/`：包含 `.so` 檔案的目錄
- `add_one_kernel.hip`：透過將 `.cu` 檔案進行 hipify 所產生的 HIP 原始碼；這才是 `hipcc` 實際編譯的內容
<!-- @os:end -->

#### **步驟 3：從 Python 使用**（[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)）：
執行此腳本以查看核心的實際運作：
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**預期輸出：**
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

## 逐步演練 2：矩陣乘法

矩陣乘法計算 **C = A × B**，其中：
- **A** 為 M×N（列 × 欄）
- **B** 為 N×K  
- **C** 為 M×K（結果）

每個輸出元素定義為：
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

C 的每個元素都是獨立計算的，因此非常適合 GPU 並行處理。

#### 如何對應到 GPU 執行緒

與向量加法（1D）不同，矩陣乘法產生 **2D 輸出**，因此我們使用 **2D 執行緒網格**：

| | 向量加法 | 矩陣乘法 |
|---|---|---|
| **輸出形狀** | 1D 陣列 | 2D 矩陣（M×K） |
| **執行緒對應** | 1 個執行緒 → 1 個元素 | 1 個執行緒 → 1 個輸出元素 |
| **啟動模式** | 1D 網格：`(grid_x, 1, 1)` | 2D 網格：`(grid_x, grid_y, 1)` |
| **區塊大小** | `(256, 1, 1)` | `(16, 16, 1)` = 256 個執行緒 |

每個執行緒計算輸出矩陣 C 中的一個元素。位於 `(row, col)` 位置的執行緒，藉由將 A 對應的列與 B 對應的欄相乘，計算出 `C[row][col]`。

**記憶體配置**：GPU 記憶體是扁平的（1D），但矩陣是逐列儲存的。若要存取 `A[row][col]`，核心會使用 `A[row * N + col]`。


#### 方法 A：JIT 編譯：

與逐步演練 1 相同，核心會以原始 C++ 字串的形式寫在 Python 內，並透過 PyTorch 內建的 JIT 在執行時期編譯。


若要使用 [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)，請確認已下載並執行：
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**關鍵程式碼片段**
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

此腳本會以較小的容許誤差，將結果與 `torch.mm` 進行驗證。由於平行歸約順序的不同，GPU 上的浮點運算可能會產生與 CPU 實作稍有差異的數值結果。

<!-- @os:linux -->
**預期輸出：**[效能數字會有所不同]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **注意**：在 Windows 上，`amd-smi` 不受支援。若要追蹤 GPU 使用率，您可以使用工作管理員，執行程式時應該會看到短暫的使用率高峰。

**預期輸出：**
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
#### 方法 B：C++ 擴充功能

第二種方法比較手動：將核心（kernel）與 Python 綁定寫入單一 `.cu` 檔案，使用 PyTorch 的建置系統原生編譯，然後匯入到 Python 中。

<!-- @os:windows -->
> **注意**：C++ 擴充功能方法需要 Visual Studio C++ 建置環境，因為 PyTorch 會將 `.cu` 原始檔編譯成原生的 `.pyd` 擴充模組。建置該原生擴充功能仰賴 Visual Studio 提供的 Microsoft C++ 工具鏈（編譯器、連結器與建置工具）。請在建置擴充功能之前，先執行設定章節中的 Visual Studio 啟用指令。
<!-- @os:end -->

如果您尚未下載以下檔案，請先下載：
<!-- @os:windows -->
| 檔案 | 角色 |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | 核心 + 啟動器 + pybind11 綁定 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | 建置腳本，使用 `CUDAExtension` 將 `.cu` 編譯成 `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | 執行已建置成品的 Python 腳本 |
<!-- @os:end -->
<!-- @os:linux -->
| 檔案 | 角色 |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | 核心 + 啟動器 + pybind11 綁定 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | 建置腳本，使用 `CUDAExtension` 將 `.cu` 編譯成 `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | 執行已建置成品的 Python 腳本 |
<!-- @os:end -->

#### **步驟 1：核心、啟動器與綁定**（[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)）：
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

與 Walkthrough 1 中的 `add_one_launcher` 相比，這裡的啟動器：
- 接受兩個輸入張量，而非一個
- 從張量形狀推導出全部三個維度（M、N、K），無需從 Python 手動傳遞尺寸
- 配置並回傳輸出張量 C，而非就地修改
- 對網格（grid）與區塊（block）都使用 `dim3`，以表達二維的啟動形狀

#### **步驟 2：建置**
```bash
pip install --no-build-isolation -v .
```
>**注意**：此指令會在目前目錄中尋找 `setup.py`，以建置我們建立的 .cu 檔案。


這會產生以下檔案：
<!-- @os:windows -->
- `build/`：包含 `.pyd` 檔案的目錄
- `matmul_kernel.hip`：由 hipify 化 `.cu` 檔案所產生的 HIP 原始碼；這是 `hipcc` 實際編譯的內容
<!-- @os:end -->
<!-- @os:linux -->
- `build/`：包含 `.so` 檔案的目錄
- `matmul_kernel.hip`：由 hipify 化 `.cu` 檔案所產生的 HIP 原始碼；這是 `hipcc` 實際編譯的內容
<!-- @os:end -->

#### **步驟 3：從 Python 使用**（[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)）：
執行此腳本，觀察核心的實際運作：
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**預期輸出：**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**太棒了！您剛剛在 GPU 上實作了矩陣乘法。** 這是一個重要的里程碑，因為矩陣乘法是現代機器學習運算的核心，例如：
- 神經網路層
- 注意力機制
- 嵌入（Embeddings）
- Transformer

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

## 後續步驟

您已經學會使用即時編譯（JIT compilation）與 C++ 擴充功能來撰寫、編譯並啟動 GPU 核心，以執行基本的平行運算。

**效能最佳化：**
- **共享記憶體分塊（Shared memory tiling）** - 快取資料區塊以減少全域記憶體存取
- **記憶體聯合存取（Memory coalescing）** - 最佳化記憶體存取模式以提升頻寬

**實際演算法：**
- **2D 卷積（Convolution）** - 一個小型濾波器（核心）在影像上滑動，透過相鄰像素的加權總和計算每個輸出像素。這引入了模板運算（stencil computations）與共享記憶體分塊，讓執行緒可重複使用重疊的影像區域，以減少全域記憶體存取。
- **Softmax 函式**：Softmax 會將一組數字轉換成總和為 1 的機率，常用於神經網路的輸出層。在 GPU 上高效實作 Softmax，會在處理大型向量的同時，引入平行歸約（parallel reductions）與數值穩定性技巧。

**生產環境考量：**
- **錯誤處理** - 邊界檢查與裝置管理
- **PyTorch 整合** - 支援自動微分（autograd）的自訂運算子