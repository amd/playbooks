<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **机器翻译。**本页面由英文自动翻译，未经人工审核。其中可能包含错误，某些说明、命令、下载内容、产品可用性或其他内容可能因语言或地区而异。如内容存在任何不一致或差异，应以英文原版 playbook 为准。
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## 概述

从零开始编写一个 GPU kernel，编译它，在 AMD GPU 上启动它，并观察利用率飙升。本手册展示 GPU 计算的实际工作原理：编写 kernel 代码，并在数千个线程中并行执行它。

> **注意**：这是一个相当复杂的手册，可能需要一些额外的调试和修改。

## 你将学到什么

<!-- @os:windows -->
- GPU kernel 是如何工作的：网格（grid）、块（block）、线程（thread），以及将它们映射到数据的索引模型
- AMD ROCm/HIP 技术栈如何让你编写的 CUDA 风格代码无需修改即可在 AMD GPU 上运行
- 如何使用 `torch.cuda._compile_kernel` 在运行时编译 kernel
- 如何使用 `CUDAExtension` + pybind11 构建一个原生 C++ kernel 扩展，并从 Python 中导入它
<!-- @os:end -->
<!-- @os:linux -->
- GPU kernel 是如何工作的：网格（grid）、块（block）、线程（thread），以及将它们映射到数据的索引模型
- AMD ROCm/HIP 技术栈如何让你编写的 CUDA 风格代码无需修改即可在 AMD GPU 上运行
- 如何使用 `torch.cuda._compile_kernel` 在运行时编译 kernel
- 如何使用 `CUDAExtension` + pybind11 构建一个原生 C++ kernel 扩展，并从 Python 中导入它
- 如何测量 kernel 执行时间，并使用 `amd-smi` 实时监控 GPU 利用率
<!-- @os:end -->

---

本手册涵盖两种 kernel 开发方法：

<!-- @os:windows -->
| 方法 | 入口点 |
|---|---|
| **JIT 编译** | `torch.cuda._compile_kernel`，将 kernel 编写为 Python 字符串，无需构建步骤 |
| **C++ 扩展** | `CUDAExtension` + pybind11：将 `.cu` 文件编译为原生 `.pyd` 并导入它 |
<!-- @os:end -->
<!-- @os:linux -->
| 方法 | 入口点 |
|---|---|
| **JIT 编译** | `torch.cuda._compile_kernel`，将 kernel 编写为 Python 字符串，无需构建步骤 |
| **C++ 扩展** | `CUDAExtension` + pybind11：将 `.cu` 文件编译为原生 `.so` 并导入它 |
<!-- @os:end -->

这两种方法都可以在 AMD GPU 上运行。这是因为 PyTorch 的 ROCm 构建版本将整个 CUDA API 表面映射到了 HIP。这意味着 `torch.cuda`、`CUDAExtension` 以及 CUDA kernel 语法都可以在 AMD 硬件上透明地工作。

---

## 背景知识

### 什么是 GPU Kernel？

GPU kernel 是一个可以同时在数千个 GPU 线程中并行运行的函数。与每次调用只执行一次的 CPU 函数不同，kernel 是通过一个由多个 **块（block）** 组成的 **网格（grid）** 来启动的，每个块包含许多 **线程（thread）**，它们都在不同的数据上执行相同的代码。

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### 线程索引模型

启动 kernel 时，你需要指定两个维度：

| 变量 | 含义 |
|---|---|
| `gridDim` | 网格中的块数量 |
| `blockDim` | 每个块中的线程数量 |

每个线程都可以访问三个内置的只读变量：

| 变量 | 含义 |
|---|---|
| `blockIdx.x` | 该线程属于哪个块 |
| `blockDim.x` | 一个块中的线程数量 |
| `threadIdx.x` | 线程在其所属块内的索引 |

### 全局线程 ID

这些变量组合起来可以计算出一个全局唯一的线程索引：

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

总线程数 = `gridDim.x * blockDim.x`。每个线程独立处理一个元素。这是**数据并行**的基础。相同的操作会同时在许多元素上运行，线程之间没有依赖关系。

---

### GPU 执行模型：波前（Wavefronts）

AMD GPU 以称为 **波前（wavefront）** 的 **32** 个线程为一组来执行线程。波前中的所有线程会同时执行相同的指令。这会影响最佳块大小的选择（256 个线程 = 8 个波前 = 良好的调度效率）。

### AMD GPU 编程：HIP + ROCm

**ROCm** 是 AMD 的开源 GPU 计算技术栈（驱动程序、编译器、库、运行时）。**HIP** 构建在其之上，其设计目标是在语法上与 CUDA 保持一致。PyTorch 的 ROCm 构建版本会将 `torch.cuda.*` 透明地映射到 HIP，因此相同的代码可以在 AMD GPU 上运行。

---

### PyTorch + AMD/HIP

PyTorch 提供了一个 ROCm 构建版本，其中 CUDA API 表面（`torch.cuda.*`）由 HIP 透明地支撑。这意味着：

- `torch.cuda.is_available()` 在装有 ROCm 的 AMD GPU 上可以正常工作
- `tensor.to("cuda")` 会在 AMD GPU 上分配内存
- `torch.version.hip` 会暴露 HIP 版本

PyTorch 还提供了 `torch.cuda._compile_kernel()`，这是一个高级快捷方式，可以即时编译原始的 kernel 字符串并返回一个可调用对象，而无需单独的构建步骤。

---

<!-- @device:halo_box -->
## 检查软件更新

<!-- @require:software-update -->
<!-- @device:end -->

## 安装软件依赖项
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### 前提条件 - Windows
- 安装最新版本：[AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### 创建虚拟环境

<!-- @os:linux -->
<!-- @device:halo_box -->
在 Linux 上，在你选择的目录中打开一个终端，按照以下命令创建一个已经安装好 ROCm+Pytorch 的 venv。
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
**授予你的用户访问 GPU 设备的权限**（需要注销并重新登录才能生效）：

```bash
sudo usermod -aG render,video $LOGNAME
```

在 Linux 上，在你选择的目录中打开一个终端，按照以下命令创建一个 venv。
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
在 Windows 上，在你选择的目录中打开一个终端，按照以下命令创建一个 venv。
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **提示**：Windows 用户在运行某些 PowerShell 命令之前，可能需要修改其 PowerShell 执行策略（例如，
> 将其设置为 RemoteSigned 或 Unrestricted）。

<!-- @os:end -->
### 安装基本依赖项
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
> **注意：** 对于本手册,即使在 Ryzen AI Halo 上,也需要在虚拟环境中安装 ROCm 和 PyTorch,因为自定义内核编译需要完整的开发头文件。

安装 ROCm:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

安装 PyTorch:
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

### 安装其他依赖项

<!-- @os:linux -->
安装 Linux C/C++ 构建工具链。这是系统级依赖项,是 C++ 扩展演练所必需的,因为 `CUDAExtension` 需要从 `.cu` 文件构建原生 `.so` 模块。

请在 Linux 机器上运行一次此操作,在创建的 Python 虚拟环境之外:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

激活 `kernel-env` 虚拟环境后,安装 Python 构建依赖项:
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
请确保已安装 [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) 或[更新版本](https://visualstudio.microsoft.com/vs/community/),并包含**使用 C++ 的桌面开发**工作负载。

> **注意**：此 Visual Studio C++ 环境设置仅在 **C++ 扩展**方法中需要。JIT 编译方法不需要此设置。

打开 PowerShell 终端,并在构建 C++ 扩展之前运行以下命令。

**步骤 1：查找已安装的 Visual Studio C++ 环境**

**(A) 定位随 Visual Studio Installer 一起安装的 `vswhere.exe`**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) 从 Visual Studio 2022 或更新版本中查找带有 C++ 构建工具的 `vcvars64.bat`**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(C) 打印正在使用的 Visual Studio C++ 环境**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**步骤 2：激活 Visual Studio C++ 构建环境**

**(A) 运行 `vcvars64.bat` 并捕获其设置的环境**

这将使 `cl.exe`、`INCLUDE`、`LIB`、`LIBPATH` 和 Windows SDK 路径可用。

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) 将 Visual Studio 环境变量导入此 PowerShell 会话**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**步骤 3：验证 Microsoft C++ 编译器是否可用**

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

#### 设置环境变量
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
使用以下命令验证 AMD GPU 是否可见:
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

## 下载所需文件

创建以下目录结构,方法是新建 **2 个文件夹**并下载相应的文件:

| 目录 | 需下载的文件 | 说明 |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| 用于向量加法内核的 JIT 和 C++ 扩展文件 |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | 用于矩阵乘法内核的 JIT 和 C++ 扩展文件 |


## 演练

### 演练 1：向量加法

#### 方法 A：JIT 编译

JIT（即时）编译意味着内核以原始 C++ 字符串的形式写在 Python 中,并在运行时编译,无需额外的构建步骤。

要使用 [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py),请确保已下载该文件并运行:
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**关键代码片段**
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
> **提示**：该脚本还会启动一个后台线程,每 100ms 轮询一次 `amd-smi`,以记录内核运行期间的峰值和平均 GPU 利用率。
<!-- @os:end -->

> **注意**：**为什么区块大小是 256？** <br>
> - 内核使用**每个区块 256 个线程**,因为这与 **AMD GPU 的波前执行模型**很好地契合。
> - 请记住,AMD 硬件以 32 个线程为一组执行线程,因此每个区块产生 8 个波前。（8 个波前 x 32 个线程 = 1 个区块）


**该工作负载的作用：**

该内核人为地添加额外工作以展示 GPU 利用率：

- 张量中包含 **100,000,000 个元素**
- 每次内核启动时,每个元素的**内循环运行 1,000 次**
- 总共 **200 次内核启动**

**数学计算：**  
- 每个元素：递增 1 × 1,000 次迭代 × 200 次启动 = 200,000  
- 最终结果：1.0（初始值）+ 200,000（累加值）= 200,001.0

**为什么需要内循环？**  
- 如果没有 `for (int i = 0; i < 1000; i++)` 循环,200 次启动会立即完成,监控工具将无法捕获有意义的 GPU 利用率数据。人为添加的工作量使每次内核运行的时间足够长,便于监控工具测量性能。

<!-- @os:linux -->
**预期输出：**[性能数据会有所不同]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **注意**：在 Windows 上,不支持 `amd-smi`。要跟踪 GPU 利用率,可以使用任务管理器,运行程序时你应该会看到短暂的利用率峰值。

**预期输出：**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**做得好！你刚刚运行了第一个 GPU 内核。**

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
#### 方法 B：C++ 扩展

第二种方法更加手动：将内核和 Python 绑定写入单个 `.cu` 文件，使用 PyTorch 的构建系统进行本机编译，然后将其导入 Python。

<!-- @os:windows -->
> **注意**：C++ 扩展方法需要 Visual Studio C++ 构建环境，因为 PyTorch 会将 `.cu` 源文件编译为本机 `.pyd` 扩展模块。构建该本机扩展依赖于 Visual Studio 提供的 Microsoft C++ 工具链（编译器、链接器和构建工具）。在构建扩展之前，请先运行设置章节中的 Visual Studio 激活命令。
<!-- @os:end -->

如果尚未下载以下文件，请先下载：
<!-- @os:windows -->
| 文件 | 作用 |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | 内核 + 启动器 + pybind11 绑定，全部在一个文件中 |
| [setup.py](assets/Vector_Addition/setup.py) | 构建脚本，使用 `CUDAExtension` 将 `.cu` 编译为 `.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | 运行构建好的产物的 Python 脚本 |
<!-- @os:end -->

<!-- @os:linux -->
| 文件 | 作用 |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | 内核 + 启动器 + pybind11 绑定，全部在一个文件中 |
| [setup.py](assets/Vector_Addition/setup.py) | 构建脚本，使用 `CUDAExtension` 将 `.cu` 编译为 `.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | 运行构建好的产物的 Python 脚本 |
<!-- @os:end -->

#### **步骤 1：内核、启动器和绑定**（[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)）：
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

>**提示**：为什么要使用 `hipDeviceSynchronize()`？<br>
> - GPU 内核启动是异步的。当 CPU 运行 `add_one<<<grid_size, block_size>>>(data, n);` 时，它会立即执行下一条指令，而不会等待 GPU。`hipDeviceSynchronize()` 会强制 CPU 等待，直到 GPU 内核执行完成。

#### **步骤 2：构建**
```bash
pip install --no-build-isolation -v .
```
>**注意**：此命令会在当前目录中查找 `setup.py`，以构建我们创建的 .cu 文件。


`CUDAExtension` 是来自 `torch.utils.cpp_extension` 的 CUDA 构建辅助工具。在 ROCm 环境下，PyTorch 会**将 `CUDAExtension` 重新映射为使用 `hipcc`**，而不是 `nvcc`。ROCm 会拦截构建路径，并将其通过 HIP 编译器进行路由，从而将 CUDA 代码移植到 AMD。

这将生成以下文件：
<!-- @os:windows -->
- `build/`：包含 `.pyd` 文件的目录
- `add_one_kernel.hip`：对 `.cu` 文件进行 hipify 转换后生成的 HIP 源代码；这才是 `hipcc` 实际编译的内容
<!-- @os:end -->
<!-- @os:linux -->
- `build/`：包含 `.so` 文件的目录
- `add_one_kernel.hip`：对 `.cu` 文件进行 hipify 转换后生成的 HIP 源代码；这才是 `hipcc` 实际编译的内容
<!-- @os:end -->

#### **步骤 3：从 Python 中使用**（[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)）：
执行此脚本以查看内核的运行效果：
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**预期输出：**
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

### 演示 2：矩阵乘法

矩阵乘法计算 **C = A × B**，其中：
- **A** 是 M×N（行 × 列）
- **B** 是 N×K  
- **C** 是 M×K（结果）

每个输出元素定义为：
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

C 的每个元素都是独立计算的，这使其非常适合 GPU 并行处理。

#### 如何映射到 GPU 线程

与（一维的）向量加法不同，矩阵乘法产生的是**二维输出**，因此我们使用**二维线程网格**：

| | 向量加法 | 矩阵乘法 |
|---|---|---|
| **输出形状** | 一维数组 | 二维矩阵（M×K） |
| **线程映射** | 1 个线程 → 1 个元素 | 1 个线程 → 1 个输出元素 |
| **启动模式** | 一维网格：`(grid_x, 1, 1)` | 二维网格：`(grid_x, grid_y, 1)` |
| **块大小** | `(256, 1, 1)` | `(16, 16, 1)` = 256 个线程 |

每个线程计算输出矩阵 C 中的一个元素。位于 `(row, col)` 位置的线程通过将 A 的相应行与 B 的相应列相乘，来计算 `C[row][col]`。

**内存布局**：GPU 内存是扁平的（一维），但矩阵是按行存储的。要访问 `A[row][col]`，内核使用 `A[row * N + col]`。


#### 方法 A：JIT 编译：

与演示 1 类似，内核在 Python 中以原始 C++ 字符串的形式编写，并通过 PyTorch 内置的 JIT 在运行时进行编译。


要使用 [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)，请确保已下载该文件，然后运行：
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**关键代码片段**
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

该脚本会以较小的容差将结果与 `torch.mm` 进行验证。由于并行归约顺序的不同，GPU 上的浮点运算相比 CPU 实现可能会产生细微的数值差异。

<!-- @os:linux -->
**预期输出：**[性能数据会有所不同]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **注意**：在 Windows 上，不支持 `amd-smi`。要跟踪 GPU 利用率，可以使用任务管理器，运行程序时应能看到短暂的利用率峰值。

**预期输出：**
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
#### 方法 B：C++ 扩展

第二种方法更为手动：将内核和 Python 绑定写入单个 `.cu` 文件，使用 PyTorch 的构建系统进行本地编译，然后将其导入 Python。

<!-- @os:windows -->
> **注意**：C++ 扩展方法需要 Visual Studio C++ 构建环境，因为 PyTorch 会将 `.cu` 源文件编译成本地的 `.pyd` 扩展模块。构建该本地扩展依赖于 Visual Studio 提供的 Microsoft C++ 工具链（编译器、链接器和构建工具）。在构建扩展之前，请先运行设置部分中的 Visual Studio 激活命令。
<!-- @os:end -->

如果尚未下载以下文件，请先下载：
<!-- @os:windows -->
| 文件 | 作用 |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | 内核 + 启动器 + pybind11 绑定 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | 构建脚本，使用 `CUDAExtension` 将 `.cu` 编译成 `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | 运行已构建产物的 Python 脚本 |
<!-- @os:end -->
<!-- @os:linux -->
| 文件 | 作用 |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | 内核 + 启动器 + pybind11 绑定 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | 构建脚本，使用 `CUDAExtension` 将 `.cu` 编译成 `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | 运行已构建产物的 Python 脚本 |
<!-- @os:end -->

#### **步骤 1：内核、启动器和绑定** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu))：
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

与演练 1 中的 `add_one_launcher` 相比，这里的启动器：
- 接受两个输入张量，而不是一个
- 从张量形状中推导出所有三个维度（M、N、K），无需从 Python 手动传递大小
- 分配并返回输出张量 C，而不是原地修改
- 对网格和线程块都使用 `dim3` 来表达二维启动形状

#### **步骤 2：构建**
```bash
pip install --no-build-isolation -v .
```
>**注意**：此命令会在当前目录中查找 `setup.py`，以构建我们创建的 .cu 文件。


这将生成以下文件：
<!-- @os:windows -->
- `build/`：包含 `.pyd` 文件的目录
- `matmul_kernel.hip`：对 `.cu` 文件进行 hipify 后生成的 HIP 源文件；这是 `hipcc` 实际编译的内容
<!-- @os:end -->
<!-- @os:linux -->
- `build/`：包含 `.so` 文件的目录
- `matmul_kernel.hip`：对 `.cu` 文件进行 hipify 后生成的 HIP 源文件；这是 `hipcc` 实际编译的内容
<!-- @os:end -->

#### **步骤 3：在 Python 中使用** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py))：
执行此脚本以查看内核的运行效果：
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**预期输出：**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**太棒了！你刚刚实现了 GPU 上的矩阵乘法。** 这是一个重要的里程碑，因为矩阵乘法是现代机器学习操作的支柱，例如：
- 神经网络层
- 注意力机制
- 嵌入
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

## 后续步骤

您已经学会了如何使用 JIT 编译和 C++ 扩展来编写、编译和启动 GPU 内核，以执行基本的并行操作。

**性能优化：**
- **共享内存分块** - 缓存数据块以减少全局内存访问
- **内存合并** - 优化内存访问模式以提升带宽

**实际算法：**
- **2D 卷积** - 一个小的滤波器（内核）在图像上滑动，通过相邻像素的加权和计算每个输出像素。这引入了模板计算和共享内存分块技术，线程可以重用重叠的图像区域以减少全局内存访问。
- **Softmax 函数**：Softmax 将一个数字向量转换为总和为 1 的概率，常用于神经网络输出。要在 GPU 上高效实现它，需要引入并行归约和数值稳定性技术，同时处理大型向量。

**生产环境注意事项：**
- **错误处理** - 边界检查和设备管理
- **PyTorch 集成** - 支持自动求导的自定义算子