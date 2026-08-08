<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機器翻譯。**本頁面是由英文自動翻譯而成，尚未經過人工審閱。內容可能包含錯誤，且某些指示、命令、下載項目、產品供應情況或其他內容可能因語言或地區而異。如本文件與英文版本之間存在任何不一致或差異，應以該 playbook 之英文原始版本為準。
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## 概觀

從零開始撰寫一個 GPU kernel、編譯它、在 AMD GPU 上啟動它，並觀察使用率的飆升。此手冊展示 GPU 運算實際上是如何運作的：撰寫 kernel 程式碼，並在數千個執行緒間並行執行。

> **注意**：這是一份相當複雜的手冊，可能需要額外的除錯與修改。

## 你將學到什麼

<!-- @os:windows -->
- GPU kernel 的運作方式：grid、block、thread，以及將它們對應到資料的索引模型
- AMD ROCm/HIP 堆疊如何讓你撰寫 CUDA 風格的程式碼，並無需修改即可在 AMD GPU 上執行
- 如何使用 `torch.cuda._compile_kernel` 在執行時期編譯 kernel
- 如何使用 `CUDAExtension` + pybind11 建置原生 C++ kernel 擴充套件，並可從 Python 中匯入
<!-- @os:end -->
<!-- @os:linux -->
- GPU kernel 的運作方式：grid、block、thread，以及將它們對應到資料的索引模型
- AMD ROCm/HIP 堆疊如何讓你撰寫 CUDA 風格的程式碼，並無需修改即可在 AMD GPU 上執行
- 如何使用 `torch.cuda._compile_kernel` 在執行時期編譯 kernel
- 如何使用 `CUDAExtension` + pybind11 建置原生 C++ kernel 擴充套件，並可從 Python 中匯入
- 如何測量 kernel 執行時間，並使用 `amd-smi` 監控即時 GPU 使用率
<!-- @os:end -->

---

此手冊涵蓋兩種 kernel 開發方法：

<!-- @os:windows -->
| 方法 | 進入點 |
|---|---|
| **JIT 編譯** | `torch.cuda._compile_kernel`，以 Python 字串撰寫 kernel，無需建置步驟 |
| **C++ 擴充套件** | `CUDAExtension` + pybind11：將 `.cu` 檔案編譯為原生 `.pyd` 並匯入 |
<!-- @os:end -->
<!-- @os:linux -->
| 方法 | 進入點 |
|---|---|
| **JIT 編譯** | `torch.cuda._compile_kernel`，以 Python 字串撰寫 kernel，無需建置步驟 |
| **C++ 擴充套件** | `CUDAExtension` + pybind11：將 `.cu` 檔案編譯為原生 `.so` 並匯入 |
<!-- @os:end -->

這兩種方法都能在 AMD GPU 上執行。這是因為 PyTorch 的 ROCm 建置版本將整個 CUDA API 介面對應到 HIP。這代表 `torch.cuda`、`CUDAExtension` 以及 CUDA kernel 語法都能透明地在 AMD 硬體上運作。

---

## 背景知識

### 什麼是 GPU Kernel？

GPU kernel 是一個能在數千個 GPU 執行緒間同時並行執行的函式。與只執行一次的 CPU 函式不同，kernel 是以一個由多個 **block** 組成的 **grid** 來啟動的，每個 block 包含許多 **thread**，全部對不同的資料執行相同的程式碼。

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### 執行緒索引模型

啟動 kernel 時，你需要指定兩個維度：

| 變數 | 意義 |
|---|---|
| `gridDim` | grid 中的 block 數量 |
| `blockDim` | 每個 block 中的執行緒數量 |

每個執行緒都能存取三個內建的唯讀變數：

| 變數 | 意義 |
|---|---|
| `blockIdx.x` | 此執行緒所屬的 block |
| `blockDim.x` | 一個 block 中的執行緒數量 |
| `threadIdx.x` | 此執行緒在其 block 內的索引 |

### 全域執行緒 ID

這些變數會結合起來計算一個全域唯一的執行緒索引：

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

總執行緒數 = `gridDim.x * blockDim.x`。每個執行緒獨立處理一個元素。這正是**資料並行（data parallelism）**的基礎。相同的運算會同時作用於許多元素，且執行緒之間沒有相依性。

---

### GPU 執行模型：Wavefront

AMD GPU 會以 **32** 個執行緒為一組進行執行，稱為 **wavefront**。一個 wavefront 中的所有執行緒會同時執行相同的指令。這會影響最佳 block 大小的選擇（256 個執行緒 = 8 個 wavefront = 良好的排程效率）。

### AMD GPU 程式設計：HIP + ROCm

**ROCm** 是 AMD 的開源 GPU 運算堆疊（驅動程式、編譯器、函式庫、執行環境）。**HIP** 建構於其上，其設計目標是在語法上與 CUDA 完全相同。PyTorch 的 ROCm 建置版本會將 `torch.cuda.*` 透明地對應到 HIP，因此相同的程式碼可在 AMD GPU 上運作。

---

### PyTorch + AMD/HIP

PyTorch 提供一個 ROCm 建置版本，其中 CUDA API 介面（`torch.cuda.*`）由 HIP 透明地支援。這代表：

- `torch.cuda.is_available()` 可在搭載 ROCm 的 AMD GPU 上運作
- `tensor.to("cuda")` 會在 AMD GPU 上配置記憶體
- `torch.version.hip` 會顯示 HIP 版本

PyTorch 也提供了 `torch.cuda._compile_kernel()`，這是一個高階的捷徑，可用來 JIT 編譯一個原始 kernel 字串並取得一個可呼叫的物件，而無需另外的建置步驟。

---

<!-- @device:halo_box -->
## 檢查軟體更新

<!-- @require:software-update -->
<!-- @device:end -->

## 安裝軟體先決條件
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### 先決條件 - Windows
- 安裝最新版本：[AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### 建立虛擬環境

<!-- @os:linux -->
<!-- @device:halo_box -->
在 Linux 上，於你選擇的目錄中開啟終端機，並依照下列指令建立一個已預先安裝 ROCm+PyTorch 的虛擬環境。
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
**授予你的使用者存取 GPU 裝置的權限**（需要登出並重新登入才會生效）：

```bash
sudo usermod -aG render,video $LOGNAME
```

在 Linux 上，於你選擇的目錄中開啟終端機，並依照下列指令建立一個虛擬環境。
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
在 Windows 上，於你選擇的目錄中開啟終端機，並依照下列指令建立一個虛擬環境。
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **提示**：Windows 使用者在執行部分 PowerShell 指令前，可能需要修改其 PowerShell 執行原則（例如，設定為 RemoteSigned 或 Unrestricted）。

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
> **注意：**在此教學文件中，即使是在 Ryzen AI Halo 上，也需要將 ROCm 和 PyTorch 安裝到虛擬環境中，因為自訂核心編譯需要完整的開發標頭檔。

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

### 安裝其他相依套件

<!-- @os:linux -->
安裝 Linux C/C++ 建置工具鏈。這是系統層級的相依套件，也是 C++ 擴充功能演練所必需的，因為 `CUDAExtension` 會從 `.cu` 檔案建置原生的 `.so` 模組。

請在 Linux 機器上執行一次此步驟，且不要在建立的 Python 虛擬環境中執行：

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

啟用 `kernel-env` 虛擬環境後，安裝 Python 建置相依套件：
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
請確認已安裝 [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) 或[更新版本](https://visualstudio.microsoft.com/vs/community/)，並選取 **Desktop development with C++** 工作負載。

> **注意**：此 Visual Studio C++ 環境設定僅在使用**C++ 擴充功能**方法時才需要。若採用 JIT 編譯方法，則不需要此設定。

開啟 PowerShell 終端機，並在建置 C++ 擴充功能之前執行下列命令。

**步驟 1：找出已安裝的 Visual Studio C++ 環境**

**(A) 找出隨 Visual Studio 安裝程式一起安裝的 `vswhere.exe`**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) 從 Visual Studio 2022 或更新版本中找出含有 C++ 建置工具的 `vcvars64.bat`**

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

**步驟 2：啟用 Visual Studio C++ 建置環境**

**(A) 執行 `vcvars64.bat` 並擷取其設定的環境**

這會讓 `cl.exe`、`INCLUDE`、`LIB`、`LIBPATH` 以及 Windows SDK 路徑可供使用。

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

**步驟 3：確認 Microsoft C++ 編譯器可正常使用**

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
確認可看到 AMD GPU：
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

## 下載必要檔案

建立以下目錄結構，方式為建立 **2 個新資料夾**，並下載對應的檔案：

| 目錄 | 需下載的檔案 | 說明 |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| 用於向量加法核心的 JIT 及 C++ 擴充功能檔案 |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | 用於矩陣乘法核心的 JIT 及 C++ 擴充功能檔案 |


## 演練

### 演練 1：向量加法

#### 方法 A：JIT 編譯

JIT（Just-In-Time，即時）編譯代表核心程式碼是以原始 C++ 字串的形式撰寫在 Python 中，並在執行階段進行編譯，不需要額外的建置步驟。

若要使用 [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)，請先確認已下載該檔案，然後執行：
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**關鍵程式碼片段**
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
> **提示**：此指令碼也會啟動一個背景執行緒，每 100 毫秒輪詢一次 `amd-smi`，以在核心執行期間記錄 GPU 使用率的峰值與平均值。
<!-- @os:end -->

> **注意**：**為什麼區塊大小是 256？** <br>
> - 此核心使用**每個區塊 256 個執行緒**，因為這與 **AMD GPU 的波前（wavefront）執行模型**相當契合。
> - 請回想 AMD 硬體以每 32 個執行緒為一組來執行，因此每個區塊會產生 8 個波前。（8 個波前 x 32 個執行緒 = 1 個區塊）


**此工作負載的執行內容：**

此核心刻意加入額外的運算工作，以展示 GPU 使用率：

- 張量中有 **100,000,000 個元素**
- 每個元素在每次核心啟動時，**內部迴圈執行 1,000 次**  
- 總共啟動核心 **200 次**

**數學計算：**  
- 每個元素：增加 1 × 1,000 次迭代 × 200 次啟動 = 200,000  
- 最終結果：1.0（初始值）+ 200,000（累加值）= 200,001.0

**為什麼需要內部迴圈？**  
- 若沒有 `for (int i = 0; i < 1000; i++)` 迴圈，200 次啟動會立即完成，監控工具將無法擷取到有意義的 GPU 使用率資料。這段人為加入的工作可讓每次核心執行的時間夠長，以便監控工具能夠測量效能。

<!-- @os:linux -->
**預期輸出：**[效能數值會有所不同]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **注意**：在 Windows 上，不支援 `amd-smi`。若要追蹤 GPU 使用率，可以使用工作管理員，執行程式時應會看到短暫的使用率高峰。

**預期輸出：**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**做得好！你剛剛執行了你的第一個 GPU 核心。**

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
#### 方法 B：C++ Extension

第二種方法較為手動：將核心與 Python 綁定寫入單一 `.cu` 檔案，使用 PyTorch 的建置系統原生編譯，然後匯入 Python。

<!-- @os:windows -->
> **注意**：C++ Extension 方法需要 Visual Studio C++ 建置環境，因為 PyTorch 會將 `.cu` 原始檔編譯成原生的 `.pyd` 擴充模組。建置該原生擴充模組需要依賴 Visual Studio 提供的 Microsoft C++ 工具鏈（編譯器、連結器與建置工具）。請在建置擴充模組之前，先執行設定章節中的 Visual Studio 啟用指令。
<!-- @os:end -->

如果尚未下載，請下載以下檔案：
<!-- @os:windows -->
| 檔案 | 角色 |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | 核心 + 啟動器 + pybind11 綁定，全部集中於一個檔案 |
| [setup.py](assets/Vector_Addition/setup.py) | 建置腳本，使用 `CUDAExtension` 將 `.cu` 編譯成 `.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | 用於執行建置成品的 Python 腳本 |
<!-- @os:end -->

<!-- @os:linux -->
| 檔案 | 角色 |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | 核心 + 啟動器 + pybind11 綁定，全部集中於一個檔案 |
| [setup.py](assets/Vector_Addition/setup.py) | 建置腳本，使用 `CUDAExtension` 將 `.cu` 編譯成 `.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | 用於執行建置成品的 Python 腳本 |
<!-- @os:end -->

#### **步驟 1：核心、啟動器與綁定** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu))：
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
> - GPU 核心啟動是非同步的。當 CPU 執行 `add_one<<<grid_size, block_size>>>(data, n);` 時，會立即執行下一個指令，而不等待 GPU 完成。`hipDeviceSynchronize()` 會強制 CPU 等待，直到 GPU 核心執行完成。

#### **步驟 2：建置**
```bash
pip install --no-build-isolation -v .
```
>**注意**：此指令會在目前目錄中尋找 `setup.py`，以建置我們建立的 .cu 檔案。


`CUDAExtension` 是來自 `torch.utils.cpp_extension` 的 CUDA 建置輔助工具。在 ROCm 中，PyTorch 會**將 `CUDAExtension` 重新導向為使用 `hipcc`**，而非 `nvcc`。ROCm 會攔截建置流程，並將其導向 HIP 編譯器，把 CUDA 程式碼移植到 AMD 平台上。

這會產生以下檔案：
<!-- @os:windows -->
- `build/`：包含 `.pyd` 檔案的目錄
- `add_one_kernel.hip`：透過 hipify `.cu` 檔案所產生的 HIP 原始碼；這才是 `hipcc` 實際編譯的內容
<!-- @os:end -->

<!-- @os:linux -->
- `build/`：包含 `.so` 檔案的目錄
- `add_one_kernel.hip`：透過 hipify `.cu` 檔案所產生的 HIP 原始碼；這才是 `hipcc` 實際編譯的內容
<!-- @os:end -->

#### **步驟 3：從 Python 使用** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py))：
執行此腳本以查看核心運作：
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

### 演練 2：矩陣乘法

矩陣乘法計算 **C = A × B**，其中：
- **A** 是 M×N（列 × 欄）
- **B** 是 N×K  
- **C** 是 M×K（結果）

每個輸出元素定義如下：
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

C 的每個元素都是獨立計算的，這使其非常適合 GPU 平行處理。

#### 如何映射至 GPU 執行緒

與向量加法（1D）不同，矩陣乘法會產生**二維輸出**，因此我們使用**二維執行緒網格**：

| | 向量加法 | 矩陣乘法 |
|---|---|---|
| **輸出形狀** | 一維陣列 | 二維矩陣（M×K） |
| **執行緒映射** | 1 個執行緒 → 1 個元素 | 1 個執行緒 → 1 個輸出元素 |
| **啟動模式** | 一維網格：`(grid_x, 1, 1)` | 二維網格：`(grid_x, grid_y, 1)` |
| **區塊大小** | `(256, 1, 1)` | `(16, 16, 1)` = 256 個執行緒 |

每個執行緒計算輸出矩陣 C 的一個元素。位於 `(row, col)` 的執行緒，透過將 A 的對應列與 B 的對應欄相乘來計算 `C[row][col]`。

**記憶體配置**：GPU 記憶體是平坦的（一維），但矩陣是逐列儲存的。要存取 `A[row][col]`，核心會使用 `A[row * N + col]`。


#### 方法 A：JIT 編譯：

與演練 1 相同，核心以原始 C++ 字串的形式寫在 Python 中，並透過 PyTorch 內建的 JIT 在執行時期編譯。


若要使用 [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)，請確保已下載並執行：
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

此腳本會以小容差值，將結果與 `torch.mm` 進行比對驗證。由於平行歸約順序的差異，GPU 上的浮點數運算可能與 CPU 實作相比產生微小的數值差異。

<!-- @os:linux -->
**預期輸出：**[效能數值可能有所不同]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **注意**：在 Windows 上，不支援 `amd-smi`。若要追蹤 GPU 使用率，可以使用工作管理員，執行程式時應會看到短暫的使用率高峰。

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

第二種方法較為手動：將核心與 Python 綁定寫入單一 `.cu` 檔案，使用 PyTorch 的建置系統原生編譯，然後匯入 Python。

<!-- @os:windows -->
> **注意**：C++ 擴充功能方法需要 Visual Studio C++ 建置環境，因為 PyTorch 會將 `.cu` 原始檔編譯為原生 `.pyd` 擴充模組。建置該原生擴充功能需要依賴 Visual Studio 提供的 Microsoft C++ 工具鏈（編譯器、連結器和建置工具）。請在建置擴充功能前，先執行設定章節中的 Visual Studio 啟用命令。
<!-- @os:end -->

如果尚未下載以下檔案，請先下載：
<!-- @os:windows -->
| 檔案 | 角色 |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | 核心 + 啟動器 + pybind11 綁定 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | 建置腳本，使用 `CUDAExtension` 將 `.cu` 編譯為 `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | 用於執行建置成品的 Python 腳本 |
<!-- @os:end -->
<!-- @os:linux -->
| 檔案 | 角色 |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | 核心 + 啟動器 + pybind11 綁定 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | 建置腳本，使用 `CUDAExtension` 將 `.cu` 編譯為 `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | 用於執行建置成品的 Python 腳本 |
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

與逐步教學 1 中的 `add_one_launcher`相比，這裡的啟動器：
- 接受兩個輸入張量，而非一個
- 從張量形狀推導出所有三個維度（M、N、K），無需從 Python 手動傳入大小
- 分配並回傳輸出張量 C，而非就地修改
- 對網格與區塊皆使用 `dim3`，以表達 2D 啟動形狀

#### **步驟 2：建置**
```bash
pip install --no-build-isolation -v .
```
>**注意**：此命令會在目前目錄中尋找 `setup.py`，以建置我們建立的 .cu 檔案。


這會產生以下檔案：
<!-- @os:windows -->
- `build/`：包含 `.pyd` 檔案的目錄
- `matmul_kernel.hip`：由 hipify 化 `.cu` 檔案所產生的 HIP 原始碼；這才是 `hipcc` 實際編譯的內容
<!-- @os:end -->
<!-- @os:linux -->
- `build/`：包含 `.so` 檔案的目錄
- `matmul_kernel.hip`：由 hipify 化 `.cu` 檔案所產生的 HIP 原始碼；這才是 `hipcc` 實際編譯的內容
<!-- @os:end -->

#### **步驟 3：從 Python 使用**（[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)）：
執行此腳本以觀看核心的實際運作：
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**預期輸出：**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**太棒了！你剛剛在 GPU 上實作了矩陣乘法。** 這是一個重要的里程碑，因為矩陣乘法是現代機器學習運算的核心基礎，例如：
- 神經網路層
- 注意力機制
- 嵌入（Embeddings）
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

## 後續步驟

你已經學會使用即時（JIT）編譯與 C++ 擴充功能兩種方式，來撰寫、編譯並啟動基本平行運算的 GPU 核心。

**效能最佳化：**
- **共享記憶體平鋪（Shared memory tiling）** - 快取資料區塊以減少全域記憶體存取
- **記憶體合併（Memory coalescing）** - 最佳化記憶體存取模式以提升頻寬

**實際應用演算法：**
- **2D 卷積** - 一個小型過濾器（核心）在影像上滑動，透過相鄰像素的加權總和計算每個輸出像素。這引入了模板運算（stencil computations）與共享記憶體平鋪，讓執行緒能重複使用重疊的影像區域，以減少全域記憶體存取。
- **Softmax 函數**：Softmax 將一組數字轉換為總和為 1 的機率，常用於神經網路輸出。要在 GPU 上高效實作它，需要引入平行歸約（parallel reductions）與數值穩定性技巧，同時處理大型向量。

**生產環境考量：**
- **錯誤處理** - 邊界檢查與裝置管理
- **PyTorch 整合** - 支援自動微分（autograd）的自訂運算子