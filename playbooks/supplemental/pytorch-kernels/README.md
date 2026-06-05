<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Compile your own GPU kernels for PyTorch + AMD ROCm™ Software

## Overview

Write a GPU kernel from scratch, compile it, launch it on an AMD GPU, and watch utilization spike. This playbook shows how GPU computation actually works: write the kernel code, and execute it in parallel across thousands of threads.

> **Note**: This is a fairly complex playbook, which may require some extra debugging and modifications.

## What You'll Learn

<!-- @os:windows -->
- How GPU kernels work: grids, blocks, threads, and the indexing model that maps them to data
- How the AMD ROCm/HIP stack lets you write CUDA-style code that runs on AMD GPUs without modification
- How to compile a kernel at runtime using `torch.cuda._compile_kernel`
- How to build a native C++ kernel extension with `CUDAExtension` + pybind11, importable from Python
<!-- @os:end -->
<!-- @os:linux -->
- How GPU kernels work: grids, blocks, threads, and the indexing model that maps them to data
- How the AMD ROCm/HIP stack lets you write CUDA-style code that runs on AMD GPUs without modification
- How to compile a kernel at runtime using `torch.cuda._compile_kernel`
- How to build a native C++ kernel extension with `CUDAExtension` + pybind11, importable from Python
- How to measure kernel execution time and monitor live GPU utilization with `amd-smi`
<!-- @os:end -->

---

This playbook covers two approaches for kernel development:

<!-- @os:windows -->
| Approach | Entry point |
|---|---|
| **JIT Compilation** | `torch.cuda._compile_kernel`, write a kernel as a Python string, with no build step |
| **C++ Extension** | `CUDAExtension` + pybind11: compile a `.cu` file into a native `.pyd` and import it |
<!-- @os:end -->
<!-- @os:linux -->
| Approach | Entry point |
|---|---|
| **JIT Compilation** | `torch.cuda._compile_kernel`, write a kernel as a Python string, with no build step |
| **C++ Extension** | `CUDAExtension` + pybind11: compile a `.cu` file into a native `.so` and import it |
<!-- @os:end -->

Both approaches run on AMD GPUs. This is possible because PyTorch's ROCm build maps the entire CUDA API surface to HIP. This means `torch.cuda`, `CUDAExtension`, and CUDA kernel syntax all work on AMD hardware transparently.

---

## Background

### What is a GPU Kernel?

A GPU kernel is a function that runs in parallel across thousands of GPU threads simultaneously. Unlike a CPU function that executes once per call, a kernel is launched with a **grid** of **blocks**, each containing many **threads**, all executing the same code on different data.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### Thread Indexing Model

When launching a kernel you specify two dimensions:

| Variable | Meaning |
|---|---|
| `gridDim` | Number of blocks in the grid |
| `blockDim` | Number of threads per block |

Each thread has access to three built-in read-only variables:

| Variable | Meaning |
|---|---|
| `blockIdx.x` | Which block this thread belongs to |
| `blockDim.x` | Number of threads in one block |
| `threadIdx.x` | Thread index within its block |

### Global Thread ID

These variables are combined to compute a globally unique thread index:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

Total threads = `gridDim.x * blockDim.x`. Each thread processes one element independently. This is the foundation of **data parallelism**. The same operation runs on many elements at once, with no inter-thread dependency.

---

### GPU Execution Model: Wavefronts

AMD GPUs execute threads in groups of **32** called **wavefronts**. All threads in a wavefront run the same instruction simultaneously. This affects optimal block size choices (256 threads = 8 wavefronts = good scheduling efficiency).

### AMD GPU Programming: HIP + ROCm

**ROCm** is AMD's open-source GPU compute stack (drivers, compilers, libraries, runtime). **HIP** sits on top, designed to be syntactically identical to CUDA. PyTorch's ROCm build transparently maps `torch.cuda.*` to HIP, so the same code works on AMD GPUs.

---

## Installing Software Prerequisites

### Create a Virtual Environment

<!-- @device:halo_box -->
<!-- @os:windows -->
On Windows, open a terminal in the directory of your choice and follow the commands to create a venv with ROCm+Pytorch already installed.
```bash
python -m venv kernel-env --system-site-packages
kernel-env\Scripts\activate
```

> **Tip**: Windows users may need to modify their PowerShell Execution Policy (e.g.
> setting it to RemoteSigned or Unrestricted) before running some Powershell commands.

<!-- @os:end -->

<!-- @os:linux -->
On Linux, open a terminal in the directory of your choice and follow the commands to create a venv with ROCm+Pytorch already installed.
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv kernel-env --system-site-packages
source kernel-env/bin/activate
```
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @os:windows -->
On Windows, open a terminal in the directory of your choice and follow the commands to create a venv.
```powershell
python -m venv kernel-env
kernel-env\Scripts\activate
```

> **Tip**: Windows users may need to modify their PowerShell Execution Policy (e.g.
> setting it to RemoteSigned or Unrestricted) before running some Powershell commands.

<!-- @os:end -->

<!-- @os:linux -->
On Linux, open a terminal in the directory of your choice and follow the commands to create a venv.
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv kernel-env
source kernel-env/bin/activate
```
<!-- @os:end -->
<!-- @device:end -->



### Installing Basic Dependencies
<!-- @os:linux -->
<!-- @require:rocm,pytorch -->
<!-- @os:end -->
<!-- @os:windows -->
<!-- @require:driver,rocm,pytorch -->
<!-- @os:end -->

---

### Installing Additional Dependencies

```bash
pip install --upgrade setuptools wheel
```
<!-- @os:windows -->
Please ensure [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) is installed.

Open a Powershell terminal and activate Visual Studio environment C++ dependencies.
```powershell
cmd /c '"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1 && set' | ForEach-Object { if ($_ -match '^([^=]+)=(.*)$') { [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process') } }
```
<!-- @os:end -->

#### Set Environment Variables
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @os:linux -->
```bash
rocm-sdk init # Initialize the devel libraries

# Get the active Python version (e.g. "3.13") so the path works with any Python release
PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
export ROCM_HOME="$VIRTUAL_ENV/lib/python${PY_MM}/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH="$ROCM_HOME/lib:$LD_LIBRARY_PATH"
export PATH="$ROCM_HOME/bin:$PATH"
```

```bash
# Set compiler and build settings
export CC=clang
export CXX=clang
export DISTUTILS_USE_SDK=1
```
<!-- @os:end -->

<!-- @os:windows -->
#### Windows
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
$env:HIP_PLATFORM = "amd"

# Set compiler and build settings
$env:CC = "clang-cl"
$env:CXX = "clang-cl"
$env:DISTUTILS_USE_SDK = "1"
```
<!-- @os:end -->
<!-- @device:end -->
<!-- @os:linux -->
Verify that the AMD GPU is visible with:
```bash
amd-smi
```
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=env-setup-rocm-pytorch-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

python3 -m venv rocm-env

VENV="$PWD/rocm-env"
if [ ! -f "$VENV/bin/activate" ]; then
  echo "Missing venv at $VENV. Run the setup steps first."
  exit 1
fi

source "$VENV/bin/activate"

pip install --upgrade pip setuptools wheel
pip install --index-url https://rocm.nightlies.amd.com/v2/gfx1151/ "rocm[libraries,devel]"
pip install --pre --index-url https://rocm.nightlies.amd.com/v2/gfx1151/ torch==2.10.0 torchaudio torchvision

rocm-sdk init

PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
export ROCM_HOME="$VIRTUAL_ENV/lib/python${PY_MM}/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH="$ROCM_HOME/lib:${LD_LIBRARY_PATH:-}"
export PATH="$ROCM_HOME/bin:$PATH"

test -f "$ROCM_HOME/lib/libhiprtc.so" || ls "$ROCM_HOME/lib"/libhiprtc.so*
test -f "$ROCM_HOME/lib/libroctx64.so" || ls "$ROCM_HOME/lib"/libroctx64.so*

hipcc --version >/dev/null
rocminfo >/dev/null

python - <<'PY'
import sys
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

<!-- @os:linux -->
<!-- @test:id=amd-smi-linux timeout=1200 hidden=True -->
```bash
source "./rocm-env/bin/activate"
amd-smi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=env-setup-rocm-pytorch-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

python -m venv rocm-env
rocm-env\Scripts\activate

$Venv = Join-Path (Get-Location) "rocm-env"
$Python = Join-Path $Venv "Scripts\python.exe"

if (-not (Test-Path $Python)) {throw "Missing venv at $Venv. Run the setup steps first."}

pip install --upgrade pip setuptools wheel
pip install --index-url https://rocm.nightlies.amd.com/v2/gfx1151/ "rocm[libraries,devel]"
pip install --pre --index-url https://rocm.nightlies.amd.com/v2/gfx1151/ torch==2.10.0 torchaudio torchvision

$RocmSdk = Join-Path $Venv "Scripts\rocm-sdk.exe"
if (-not (Test-Path $RocmSdk)) {throw "Missing rocm-sdk.exe at $RocmSdk. Run the setup steps first."}
& $RocmSdk init

$ROCM_ROOT = (& $RocmSdk path --root).Trim()
$ROCM_BIN  = (& $RocmSdk path --bin).Trim()

$ExpectedHiprtc = Join-Path $ROCM_BIN "hiprtc0701.dll"
$ActualHiprtc = Join-Path $ROCM_BIN "hiprtc07013.dll"
if ((-not (Test-Path $ExpectedHiprtc)) -and (Test-Path $ActualHiprtc)) {
  Copy-Item $ActualHiprtc $ExpectedHiprtc -Force
  Write-Host "Created HIPRTC compatibility copy: $ExpectedHiprtc"
}

$RocmPathEntries = @(
  $ROCM_BIN,
  "$ROCM_ROOT\bin",
  "$ROCM_ROOT\lib",
  "$ROCM_ROOT\lib\llvm\bin"
) | Where-Object { $_ -and (Test-Path $_) }
$env:PATH = (($RocmPathEntries + @($env:PATH)) -join ";")

$env:ROCM_HOME = $ROCM_ROOT
$env:HIP_PATH = $ROCM_ROOT
$env:HIP_PLATFORM = "amd"
$env:CC = "clang-cl"
$env:CXX = "clang-cl"
$env:DISTUTILS_USE_SDK = "1"

Write-Host "ROCM_ROOT=$ROCM_ROOT"
Write-Host "ROCM_BIN=$ROCM_BIN"

Get-ChildItem -Path $ROCM_ROOT -Recurse -Filter "hiprtc*.dll" | Select-Object -First 10 FullName | Out-Host

hipcc --version | Out-Host
hipinfo | Out-Host

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

$code | & $Python -
```
<!-- @test:end --> 
<!-- @os:end -->

---

## Download Required Files

Create the following directory structure by making the **2 new folders** and downloading the corresponding files:

| Directory | Files to Download | Description |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| JIT and C++ extension files for vector addition kernel |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | JIT and C++ extension files for matrix multiplication kernel |


## Walkthroughs

### Walkthrough 1: Vector Addition

#### Approach A:  JIT Compilation

JIT (Just-In-Time) compilation means the kernel is written as a raw C++ string inside Python and compiled at runtime, without needing extra build steps.

To use [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py), make sure it's downloaded and run:
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**Key Code Snippets**
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
> **Tip**: The script also spawns a background thread that polls `amd-smi` every 100ms to log peak and average GPU utilization during the kernel run.
<!-- @os:end -->

> **Note**: **Why is Block Size 256?** <br>
> - The kernel uses **256 threads per block** because it aligns well with the **wavefront execution model of AMD GPUs**.
> - Recall that AMD hardware executes threads in groups of 32 threads, resulting in 8 wavefronts per block. (8 wavefronts x 32 threads = 1 block)


**What the workload does:**

The kernel artificially adds extra work to demonstrate GPU utilization:

- **100,000,000 elements** in the tensor
- **Inner loop runs 1,000 times** per element per kernel launch  
- **200 kernel launches** total

**Math:**  
- Each element: gets incremented by 1 × 1,000 iterations × 200 launches = 200,000  
- Final result: 1.0 (starting value) + 200,000 (additions) = 200,001.0

**Why the inner loop?**  
- Without the `for (int i = 0; i < 1000; i++)` loop, 200 launches would finish instantly and the monitoring tools wouldn't capture meaningful GPU utilization. The artificial work makes each kernel run long enough for monitoring tools to measure performance.

<!-- @os:linux -->
**Expected output:**[The performance numbers will vary]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
>**Note**: On Windows, `amd-smi` is not supported. To track GPU utilization, you can use Task Manager, where you should see a brief spike of utilization when you run the program.
**Expected output:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**Nice work! You just ran your first GPU kernel.**

<!-- @os:linux -->
<!-- @test:id=vector-addition-jit-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

source "./rocm-env/bin/activate"
rocm-sdk init

PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
export ROCM_HOME="$VIRTUAL_ENV/lib/python${PY_MM}/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH="$ROCM_HOME/lib:${LD_LIBRARY_PATH:-}"
export PATH="$ROCM_HOME/bin:$PATH"

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
<!-- @test:id=vector-addition-jit-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

rocm-env\Scripts\activate
$Venv = Join-Path (Get-Location) "rocm-env"
$Python = Join-Path $Venv "Scripts\python.exe"
$RocmSdk = Join-Path $Venv "Scripts\rocm-sdk.exe"

& $RocmSdk init
$ROCM_ROOT = (& $RocmSdk path --root).Trim()
$ROCM_BIN  = (& $RocmSdk path --bin).Trim()

$ExpectedHiprtc = Join-Path $ROCM_BIN "hiprtc0701.dll"
$ActualHiprtc = Join-Path $ROCM_BIN "hiprtc07013.dll"
if ((-not (Test-Path $ExpectedHiprtc)) -and (Test-Path $ActualHiprtc)) {
  Copy-Item $ActualHiprtc $ExpectedHiprtc -Force
  Write-Host "Created HIPRTC compatibility copy: $ExpectedHiprtc"
}

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

$code | & $Python -
```
<!-- @test:end -->
<!-- @os:end -->

---

#### Approach B:  C++ Extension

The second approach is more manual: write the kernel and Python binding to a single `.cu` file, compile it natively using PyTorch's build system, and import it into Python.

Download the following files if you haven't already:
<!-- @os:windows -->
| File | Role |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + launcher + pybind11 binding, everything in one file |
| [setup.py](assets/Vector_Addition/setup.py) | Build script, uses `CUDAExtension` to compile the `.cu` into a `.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Python script that runs the built artifacts |
<!-- @os:end -->

<!-- @os:linux -->
| File | Role |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + launcher + pybind11 binding, everything in one file |
| [setup.py](assets/Vector_Addition/setup.py) | Build script, uses `CUDAExtension` to compile the `.cu` into a `.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Python script that runs the built artifacts |
<!-- @os:end -->

#### **Step 1: The kernel, launcher, and binding** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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

>**Tip**: Why use `hipDeviceSynchronize()`? <br>
> - GPU kernel launches are asynchronous. When the CPU runs `add_one<<<grid_size, block_size>>>(data, n);` it would immediately execute the next instruction without waiting for the GPU. `hipDeviceSynchronize()` forces the CPU to wait until the GPU kernel completes.

#### **Step 2: Build**
```bash
pip install --no-build-isolation -v .
```
>**Note**: This command looks for `setup.py` in the current directory to build the .cu file we have created.


`CUDAExtension` is a CUDA build helper from `torch.utils.cpp_extension`. With ROCm, PyTorch **remaps `CUDAExtension` to use `hipcc`** instead of `nvcc`. ROCm intercepts the build path and routes it through the HIP compiler, porting CUDA code to AMD.

This produces the following files:
<!-- @os:windows -->
- `build/`:  directory with the `.pyd` files
- `add_one_kernel.hip`:  the HIP source generated by hipifying the `.cu` file; this is what `hipcc` actually compiled
<!-- @os:end -->
<!-- @os:linux -->
- `build/`:  directory with the `.so` files
- `add_one_kernel.hip`:  the HIP source generated by hipifying the `.cu` file; this is what `hipcc` actually compiled
<!-- @os:end -->

#### **Step 3: Use from Python** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
Execute this script to see the kernel in action:
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**Expected output:**
```
Before: tensor([1., 1., 1., 1., 1., 1., 1., 1., 1., 1.], device='cuda:0')
After: tensor([2., 2., 2., 2., 2., 2., 2., 2., 2., 2.], device='cuda:0')
```

<!-- @os:linux -->
<!-- @test:id=vector-extension-linux timeout=600 hidden=True -->
```bash
set -euo pipefail

source "./rocm-env/bin/activate"
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
<!-- @test:id=vector-extension-windows timeout=600 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

rocm-env\Scripts\activate
$Venv = Join-Path (Get-Location) "rocm-env"
$Python = Join-Path $Venv "Scripts\python.exe"
$RocmSdk = Join-Path $Venv "Scripts\rocm-sdk.exe"

$VcvarsCandidates = @(
  "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat",
  "C:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat",
  "C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvars64.bat",
  "C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvars64.bat"
)

$Vcvars = $VcvarsCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $Vcvars) {
  throw "Could not find vcvars64.bat. Install Visual Studio 2022 C++ Build Tools."
}

cmd /c "`"$Vcvars`" >nul 2>&1 && set" | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}

& $RocmSdk init
$ROCM_ROOT = (& $RocmSdk path --root).Trim()
$ROCM_BIN  = (& $RocmSdk path --bin).Trim()

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
  & $Python -m pip install --no-build-isolation -v .

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

  $code | & $Python -
}
finally {
  Pop-Location
}
```
<!-- @test:end --> 
<!-- @os:end -->

---

### Walkthrough 2: Matrix Multiplication

Matrix multiplication computes **C = A × B** where:
- **A** is M×N (rows × columns)
- **B** is N×K  
- **C** is M×K (the result)

Each output element is defined as:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

Each element of C is calculated independently, making this perfect for GPU parallelism.

#### How It Maps to GPU Threads

Unlike vector addition (1D), matrix multiplication produces a **2D output**, so we use a **2D grid of threads**:

| | Vector Addition | Matrix Multiplication |
|---|---|---|
| **Output shape** | 1D array | 2D matrix (M×K) |
| **Thread mapping** | 1 thread → 1 element | 1 thread → 1 output element |
| **Launch pattern** | 1D grid: `(grid_x, 1, 1)` | 2D grid: `(grid_x, grid_y, 1)` |
| **Block size** | `(256, 1, 1)` | `(16, 16, 1)` = 256 threads |

Each thread computes one element of the output matrix C. Thread at position `(row, col)` computes `C[row][col]` by multiplying the corresponding row of A with the corresponding column of B.

**Memory Layout**: GPU memory is flat (1D), but matrices are stored row-by-row. To access `A[row][col]`, the kernel uses `A[row * N + col]`.


#### Approach A:  JIT Compilation:

Like Walkthrough 1, the kernel is written as a raw C++ string inside Python and compiled at runtime via PyTorch's built-in JIT.


To use [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py), make sure it's downloaded and run:
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**Key Code Snippets**
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

The script verifies the result against `torch.mm` with a small tolerance. Floating-point arithmetic on GPUs may produce small numerical differences compared to CPU implementations due to parallel reduction order.

<!-- @os:linux -->
**Expected output:**[The performance numbers will vary]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
>**Note**: On Windows, `amd-smi` is not supported. To track GPU utilization, you can use Task Manager, where you should see a brief spike of utilization when you run the program.
**Expected output:**
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
No GPU Usage captured.
```
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=matmul-jit-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

source "./rocm-env/bin/activate"
rocm-sdk init

PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
export ROCM_HOME="$VIRTUAL_ENV/lib/python${PY_MM}/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH="$ROCM_HOME/lib:${LD_LIBRARY_PATH:-}"
export PATH="$ROCM_HOME/bin:$PATH"

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
<!-- @test:id=matmul-jit-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

rocm-env\Scripts\activate
$Venv = Join-Path (Get-Location) "rocm-env"
$Python = Join-Path $Venv "Scripts\python.exe"
$RocmSdk = Join-Path $Venv "Scripts\rocm-sdk.exe"

& $RocmSdk init
$ROCM_ROOT = (& $RocmSdk path --root).Trim()
$ROCM_BIN  = (& $RocmSdk path --bin).Trim()

$ExpectedHiprtc = Join-Path $ROCM_BIN "hiprtc0701.dll"
$ActualHiprtc = Join-Path $ROCM_BIN "hiprtc07013.dll"
if ((-not (Test-Path $ExpectedHiprtc)) -and (Test-Path $ActualHiprtc)) {
  Copy-Item $ActualHiprtc $ExpectedHiprtc -Force
  Write-Host "Created HIPRTC compatibility copy: $ExpectedHiprtc"
}

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

$code | & $Python -
```
<!-- @test:end --> 
<!-- @os:end -->

---

#### Approach B:  C++ Extension

The second approach is more manual: write the kernel and Python binding to a single `.cu` file, compile it natively using PyTorch's build system, and import it into Python.

Download the following files if you haven't already:
<!-- @os:windows -->
| File | Role |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + launcher + pybind11 binding |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Build script, uses `CUDAExtension` to compile the `.cu` into a `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python script that runs the built artifacts |
<!-- @os:end -->
<!-- @os:linux -->
| File | Role |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + launcher + pybind11 binding |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Build script, uses `CUDAExtension` to compile the `.cu` into a `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python script that runs the built artifacts |
<!-- @os:end -->

#### **Step 1: The kernel, launcher, and binding** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
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

Compared to `add_one_launcher` in Walkthrough 1, the launcher here:
- Takes two input tensors instead of one
- Derives all three dimensions (M, N, K) from tensor shapes, no manual size passing from Python
- Allocates and returns the output tensor C, rather than mutating in-place
- Uses `dim3` for both grid and block to express the 2D launch shape

#### **Step 2: Build**
```bash
pip install --no-build-isolation -v .
```
>**Note**: This command looks for `setup.py` in the current directory to build the .cu file we have created.


This produces the following files:
<!-- @os:windows -->
- `build/`:  directory with the `.pyd` files
- `matmul_kernel.hip`:  the HIP source generated by hipifying the `.cu` file; this is what `hipcc` actually compiled
<!-- @os:end -->
<!-- @os:linux -->
- `build/`:  directory with the `.so` files
- `matmul_kernel.hip`:  the HIP source generated by hipifying the `.cu` file; this is what `hipcc` actually compiled
<!-- @os:end -->

#### **Step 3: Use from Python** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
Execute this script to see the kernel in action:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**Expected output:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**Awesome! You just implemented matrix multiplication on the GPU.** This is a major milestone because matrix multiplication is the backbone of modern machine learning operations like:
- Neural network layers
- Attention mechanisms
- Embeddings
- Transformers

<!-- @os:linux -->
<!-- @test:id=matmul-extension-linux timeout=600 hidden=True -->
```bash
set -euo pipefail

source "./rocm-env/bin/activate"
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
<!-- @test:id=matmul-extension-windows timeout=600 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

rocm-env\Scripts\activate
$Venv = Join-Path (Get-Location) "rocm-env"
$Python = Join-Path $Venv "Scripts\python.exe"
$RocmSdk = Join-Path $Venv "Scripts\rocm-sdk.exe"

$VcvarsCandidates = @(
  "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat",
  "C:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat",
  "C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvars64.bat",
  "C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvars64.bat"
)

$Vcvars = $VcvarsCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $Vcvars) {
  throw "Could not find vcvars64.bat. Install Visual Studio 2022 C++ Build Tools."
}

cmd /c "`"$Vcvars`" >nul 2>&1 && set" | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}

& $RocmSdk init
$ROCM_ROOT = (& $RocmSdk path --root).Trim()
$ROCM_BIN  = (& $RocmSdk path --bin).Trim()

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
  & $Python -m pip install --no-build-isolation -v .

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

  $code | & $Python -
}
finally {
  Pop-Location
}
```
<!-- @test:end --> 
<!-- @os:end -->

---

## Next Steps

You've learned to write, compile, and launch GPU kernels using both JIT compilation and C++ extensions for basic parallel operations.

**Performance optimizations:**
- **Shared memory tiling** - Cache data blocks to reduce global memory access
- **Memory coalescing** - Optimize memory access patterns for bandwidth

**Real-world algorithms:**
- **2D Convolution** - A small filter (kernel) slides across an image, computing each output pixel from a weighted sum of neighboring pixels. This introduces stencil computations and shared memory tiling, where threads reuse overlapping image regions to reduce global memory access.
- **Softmax Function**: Softmax converts a vector of numbers into probabilities that sum to 1, commonly used in neural network outputs. Implementing it efficiently on GPU introduces parallel reductions and numerical stability techniques while processing large vectors.

**Production considerations:**
- **Error handling** - Bounds checking and device management
- **PyTorch integration** - Custom operators with autograd support