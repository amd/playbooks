<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Compile your own GPU kernels for Pytorch+ROCm

## Overview

Write a GPU kernel from scratch, compile it, and launch it on an AMD GPU, then watch utilization spike. This playbook shows how GPU computation actually works: you write the kernel code, and it executes in parallel across thousands of threads.

## What You'll Learn

<!-- @os:windows -->
- How GPU kernels work: grids, blocks, threads, and the indexing model that maps them to data
- How AMD's ROCm/HIP stack lets you write CUDA-style code that runs on AMD GPUs without modification
- How to compile a kernel at runtime using `torch.cuda._compile_kernel`
- How to build a native C++ kernel extension with `CUDAExtension` + pybind11, importable from Python
<!-- @os:end -->
<!-- @os:linux -->
- How GPU kernels work: grids, blocks, threads, and the indexing model that maps them to data
- How AMD's ROCm/HIP stack lets you write CUDA-style code that runs on AMD GPUs without modification
- How to compile a kernel at runtime using `torch.cuda._compile_kernel`
- How to build a native C++ kernel extension with `CUDAExtension` + pybind11, importable from Python
- How to measure kernel execution time and monitor live GPU utilization with `rocm-smi`
<!-- @os:end -->

---

This playbook covers two approaches for kernel development:

<!-- @os:windows -->
| Approach | Entry point |
|---|---|
| **JIT Compilation** | `torch.cuda._compile_kernel`, write a kernel as a Python string, no build step |
| **C++ Extension** | `CUDAExtension` + pybind11, compile a `.cu` file into a native `.pyd` and import it |
<!-- @os:end -->
<!-- @os:linux -->
| Approach | Entry point |
|---|---|
| **JIT Compilation** | `torch.cuda._compile_kernel`, write a kernel as a Python string, no build step |
| **C++ Extension** | `CUDAExtension` + pybind11, compile a `.cu` file into a native `.so` and import it |
<!-- @os:end -->

Both approaches run on AMD GPUs. This is possible because PyTorch's ROCm build maps the entire CUDA API surface to HIP, `torch.cuda`, `CUDAExtension`, and CUDA kernel syntax all work on AMD hardware transparently. You write CUDA-style code; ROCm handles the translation.

---

## Background

### What is a GPU Kernel?

A GPU kernel is a function that runs in parallel across thousands of GPU threads simultaneously. Unlike a CPU function that executes once per call, a kernel is launched with a **grid** of **blocks**, each containing many **threads**, all executing the same code on different data.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### GPU Execution Model: Wavefronts

GPU threads are scheduled in groups rather than completely independently; threads in a group execute the same instructions simultaneously. On AMD GPUs, these groups are called **wavefronts**.

A wavefront is the smallest group of threads that the GPU scheduler executes simultaneously. All threads in a wavefront execute the same instruction at the same time. A wavefront on Radeon GPUs consists of 32 threads.

This will become relevant later when discussing block size choices.

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

Total threads = `gridDim.x * blockDim.x`. Each thread processes one element independently, this is **data parallelism**. The same operation runs on many elements at once with no inter-thread dependency.

---

### AMD GPU Programming: HIP

AMD GPUs use **HIP** (Heterogeneous-Compute Interface for Portability), part of the **ROCm** (Radeon Open Compute) platform. **ROCm** is the full AMD open-source GPU compute stack: drivers, compilers, libraries, and runtime. HIP sits on top of ROCm.

HIP is designed to be syntactically close to CUDA. Most CUDA code can be translated to HIP mechanically using the `hipify` tool (which is what generated the `.hip` files in this repo).

---

### PyTorch + AMD/HIP

PyTorch ships a ROCm build where the CUDA API surface (`torch.cuda.*`) is transparently backed by HIP. This means:

- `torch.cuda.is_available()` works on AMD GPUs with ROCm
- `tensor.to("cuda")` allocates on the AMD GPU
- `torch.version.hip` exposes the HIP version

PyTorch also exposes `torch.cuda._compile_kernel()`, a high-level shortcut to JIT-compile a raw kernel string and get back a callable, without needing a separate build step.

---

## Setup
<!-- @os:windows -->
### Prerequisites - Windows
- Install latest: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @os:end -->

### Create a Virtual Environment
<!-- @os:linux -->
```bash
sudo apt install -y python3-venv
python3 -m venv ~/rocm-env
source ~/rocm-env/bin/activate
```
<!-- @setup:id=activate-venv command="source rocm-env/bin/activate" -->
<!-- @os:end -->

<!-- @os:windows -->
```bash
python -m venv rocm-env
rocm-env\Scripts\activate
```
<!-- @setup:id=activate-venv command="rocm-env\Scripts\activate" -->
<!-- @os:end -->

---

### Installing Dependencies
<!-- @os:linux -->
```bash
source ~/rocm-env/bin/activate

pip install --upgrade pip setuptools wheel
pip install --index-url https://rocm.nightlies.amd.com/v2/gfx1151/ "rocm[libraries,devel]"
# sudo reboot

source ~/rocm-env/bin/activate

pip install --pre --index-url https://rocm.nightlies.amd.com/v2/gfx1151/ torch==2.10.0 torchaudio torchvision
```
<!-- @os:end -->

<!-- @os:windows -->
```bash
rocm-env\Scripts\activate

pip install --upgrade pip setuptools wheel
pip install --index-url https://rocm.nightlies.amd.com/v2/gfx1151/ "rocm[libraries,devel]"
# Reboot

# Open a Powershell terminal and activate Visual Studio environment
cmd /c '"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1 && set' | ForEach-Object { if ($_ -match '^([^=]+)=(.*)$') { [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process') } }

rocm-env\Scripts\activate

pip install --pre --index-url https://rocm.nightlies.amd.com/v2/gfx1151/ torch==2.10.0 torchaudio torchvision
```
<!-- @os:end -->

#### Set Environment Variables
<!-- @os:linux -->
```bash
rocm-sdk init # Initialize the devel libraries

export ROCM_HOME = "$VIRTUAL_ENV/lib/python3.12/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH = "$ROCM_HOME/lib:$LD_LIBRARY_PATH"
export PATH = "$ROCM_HOME/bin:$PATH"
```
<!-- @os:end -->

<!-- @os:windows -->
```bash
rocm-sdk init # Initialize the devel libraries

$ROCM_ROOT = (rocm-sdk path --root).Trim()
$ROCM_BIN = (rocm-sdk path --bin).Trim()

$env:PATH = "$ROCM_ROOT\lib\llvm\bin;$ROCM_BIN;$env:PATH"

# Set compiler and build settings
$env:CC = "clang-cl"
$env:CXX = "clang-cl"
$env:DISTUTILS_USE_SDK = "1"
```
<!-- @os:end -->

---

## Walkthroughs

### Walkthrough 1: Vector Addition

#### Approach A:  JIT Compilation: [`add_one_kernel.py`](assets/Vector_Addition/add_one_kernel.py)

Kernel is written as a raw C++ string inside Python and compiled at runtime via PyTorch's built-in JIT.

#### Why Block Size = 256?
The kernel uses **256 threads per block**. This value is commonly used because it aligns well with the **wavefront execution model of AMD GPUs**.

AMD Radeon GPUs execute threads in groups of 32 threads, called a wavefront. 
```
256 threads per block = 8 wavefronts per block
                      = 8 × 32 threads
```
This allows the GPU scheduler to keep multiple wavefronts active within a single block, which improves scheduling efficiency and helps keep compute units busy.

**How it works:**
```python
import torch

# 1. Kernel source as a string
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

# 2. Compile the kernel string, PyTorch calls hipcc under the hood on ROCm
add_one_kernel = torch.cuda._compile_kernel(KERNEL_SOURCE, "add_one")

x = torch.ones(100_000_000, dtype=torch.float32, device="cuda")
n = x.numel()
block_size = 256
grid_size = (n + block_size - 1) // block_size

# 3. Launch: specify grid/block dimensions and pass tensor args directly
for _ in range(200):
    add_one_kernel(
        grid=(grid_size, 1, 1),
        block=(block_size, 1, 1),
        args=[x, n],
    )

# 4. Test the output
print("First 5 elements:", x[:5].cpu()) #tensor([200001., 200001., 200001., 200001., 200001.])
```
<!-- @os:linux -->
The script also spawns a background thread that polls `rocm-smi` every 100ms to log peak and average GPU utilization during the kernel run.
<!-- @os:end -->
**What the workload actually does:**

```
100,000,000 elements in the tensor
  × 1,000 inner loop iterations per kernel launch  →  +1,000 per element per launch
  × 200 outer loop launches                        →  +200,000 per element total

Starting value: 1.0
Final value:    200,001.0  (per element)
```

The inner `for (int i = 0; i < 1000; i++)` loop is artificial, its only purpose is to make each kernel launch run long enough for `rocm-smi` to capture meaningful utilization. Without it, 200 launches over 100M elements would complete near-instantly and the sampling thread would likely read very low GPU utilization.

**Run:**
```bash
python "Vector_Addition/add_one_kernel.py"
```

**Expected output:**[The performance numbers might vary]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:windows -->
On Windows, `rocm-smi` is not supported. To track GPU utilization, you can use Task Manager, where you should see a brief spike to 100% utilization when you run the program.
<!-- @os:end -->
**Nice work! You just ran your first GPU kernel.**

---

#### Approach B:  C++ Extension

The full manual path: write the kernel and Python binding in a single `.cu` file, compile it as a native extension using PyTorch's build system, then import and call it from Python.

**Files:**

<!-- @os:windows -->
| File | Role |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + launcher + pybind11 binding, everything in one file |
| [setup.py](assets/Vector_Addition/setup.py) | Build script, uses `CUDAExtension` to compile the `.cu` into a `.pyd` |
<!-- @os:end -->
<!-- @os:linux -->
| File | Role |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + launcher + pybind11 binding, everything in one file |
| [setup.py](assets/Vector_Addition/setup.py) | Build script, uses `CUDAExtension` to compile the `.cu` into a `.so` |
<!-- @os:end -->

**How it works:**

**Step 1: The kernel, launcher, and binding** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
```cpp
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

#### Why `hipDeviceSynchronize()`?

GPU kernel launches are asynchronous. When the CPU launches a kernel like this:
```
add_one<<<grid_size, block_size>>>(data, n);
```
the CPU immediately continues executing the next instruction without waiting for the GPU to finish. `hipDeviceSynchronize()` forces the CPU to block until the GPU kernel completes.

**Step 2: Build**

```bash
pip install --no-build-isolation -v .
```

`CUDAExtension` is a CUDA build helper from `torch.utils.cpp_extension`. On AMD with ROCm, PyTorch **remaps `CUDAExtension` to use `hipcc`** instead of `nvcc`, so the same `setup.py` that would build a CUDA extension on NVIDIA compiles to AMD GPU code without any changes. This is the key mechanism that makes CUDA extension code portable to AMD: PyTorch's ROCm build intercepts the build path and routes it through the HIP compiler. Produces these in the same directory:
<!-- @os:windows -->
- `build/`:  directory with the `.pyd` files
- `add_one_kernel.hip`:  the HIP source generated by hipifying the `.cu` file; this is what `hipcc` actually compiled
<!-- @os:end -->
<!-- @os:linux -->
- `build/`:  directory with the `.so` files
- `add_one_kernel.hip`:  the HIP source generated by hipifying the `.cu` file; this is what `hipcc` actually compiled
<!-- @os:end -->

**Step 3: Use from Python**
```python
import os, sys
import torch
os.chdir("Vector_Addition")
sys.path.insert(0, os.getcwd())
import add_one_ext

x = torch.ones(10, device="cuda")
add_one_ext.add_one(x)
print(x[:5].cpu())
```

**Expected output:**
```python
>>> x = torch.ones(10, device="cuda")
>>> x
tensor([1., 1., 1., 1., 1., 1., 1., 1., 1., 1.], device='cuda:0')
>>> add_one_ext.add_one(x)
>>> x
tensor([2., 2., 2., 2., 2., 2., 2., 2., 2., 2.], device='cuda:0')
```

---

### Walkthrough 2: Matrix Multiplication

Given matrices **A** (M×N) and **B** (N×K), compute **C = A * B** (M×K). Each element `C[i][j]` is the dot product of row `i` of A with column `j` of B, completely independent of every other output element, making this a natural fit for GPU parallelism.

#### The Math

Each output element is defined as:

$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

Each output element is assigned to exactly one thread, and threads don't depend on each other's results, thread `(0,0)` and thread `(1,5)` run simultaneously with no coordination. However, within a single thread the dot product is **sequential**: the `n` loop iterates N times, accumulating one multiply-add per step.

#### Row-Major Memory Layout

GPU memory is **flat (1D)**. A 2D matrix stored in row-major order lays out each row contiguously, one after another.

For a 2×3 matrix A:

```
A = [ a00  a01  a02
      a10  a11  a12 ]

Stored in memory:
  Index:  0    1    2    3    4    5
  Value: a00  a01  a02  a10  a11  a12
```

To reach `A[row][col]`, skip `row` full rows (each `N` elements wide), then advance `col` steps:

$$A[row, col] = A[row \times N + col]$$

The same principle applies to B (column width K):

$$B[n, col] = B[n \times K + col]$$

Substituting into the matmul formula gives the exact inner loop in the kernel:

$$C[row, col] = \sum_{n=0}^{N-1} A[row \times N + n] \cdot B[n \times K + col]$$

#### 2D thread indexing

Vector addition maps one thread to one element of a 1D array. Matrix multiplication maps one thread to one element of a 2D output matrix, so the natural launch shape is a **2D grid of 2D blocks**.

| | Vector Addition | Matrix Multiplication |
|---|---|---|
| Output shape | 1D vector, length N | 2D matrix, M×K |
| Thread grid | 1D: `(grid_x, 1, 1)` | 2D: `(grid_x, grid_y, 1)` |
| Thread block | 1D: `(256, 1, 1)` = 256 threads | 2D: `(16, 16, 1)` = 256 threads |
| Thread index | `idx = blockIdx.x * blockDim.x + threadIdx.x` | `row = blockIdx.y * blockDim.y + threadIdx.y` & `col = blockIdx.x * blockDim.x + threadIdx.x` |
| Work per thread | `data[idx] += 1` | `C[row][col] = Σ A[row][k] * B[k][col]` |

The block is still 256 threads total (16×16), matching the convention from Walkthrough 1, but arranged in a square to align naturally with the 2D output.

```
Grid (2D)
└── Block [bx, by]  ...
     └── Thread [tx, ty]  →  computes C[by*16+ty][bx*16+tx]
```

The grid covers the full output:
```
grid_x = ceil(K / 16)   # enough blocks to span all K columns
grid_y = ceil(M / 16)   # enough blocks to span all M rows
```

#### Approach A:  JIT Compilation: [`matmul_kernel.py`](assets/Matrix_Multiplication/matmul_kernel.py)

Kernel is written as a raw C++ string inside Python and compiled at runtime via PyTorch's built-in JIT. Identical workflow to Walkthrough 1, only the kernel body and launch dimensions change.

**How it works:**
```python
import torch

# 1. Kernel source, 2D indexing to map threads onto the M×K output matrix
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
# Inputs: A is M x N, B is N x K, C is M x K
M, N, K = 1024, 512, 768

A = torch.randn(M, N, dtype=torch.float32, device="cuda")
B = torch.randn(N, K, dtype=torch.float32, device="cuda")
C = torch.zeros(M, K, dtype=torch.float32, device="cuda")

BLOCK = 16
grid_x = (K + BLOCK - 1) // BLOCK
grid_y = (M + BLOCK - 1) // BLOCK

# 2. Compile the kernel string
matmul_kernel = torch.cuda._compile_kernel(KERNEL_SOURCE, "matmul")

# 3. Launch with a 2D grid, grid_x covers columns (K), grid_y covers rows (M)
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

The row-major memory layout of the tensors maps directly to how the kernel indexes the flat pointers:
- `A[row * N + n]`:  row `row`, column `n`
- `B[n * K + col]`:  row `n`, column `col`

The script spawns the same background monitoring thread from Walkthrough 1 (`rocm-smi` polled every 100ms) and verifies the result against `torch.mm`. Floating-point arithmetic on GPUs may produce small numerical differences compared to CPU implementations due to parallel reduction order. This is why we verify the result using a tolerance (`max error`) instead of exact equality.

**Run:**
```bash
python "Matrix_Multiplication/matmul_kernel.py"
```

**Expected output:**[The performance numbers might vary]
```
Elapsed time: 0.255s
Max error vs torch.mm: 0.000160
Peak GPU Utilization:    100%
Average GPU Utilization: 55.00%
```

---

#### Approach B:  C++ Extension

The full manual path: write the kernel and Python binding in a `.cu` file, compile it as a native extension, then import and call it from Python. Mirrors the structure of `add_one_kernel.cu` exactly, only the kernel signature and launcher logic differ.

**Files:**
<!-- @os:windows -->
| File | Role |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + launcher + pybind11 binding |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Build script, uses `CUDAExtension` to compile the `.cu` into a `.pyd` |
<!-- @os:end -->
<!-- @os:linux -->
| File | Role |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + launcher + pybind11 binding |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Build script, uses `CUDAExtension` to compile the `.cu` into a `.so` |
<!-- @os:end -->

**How it works:**

**Step 1: The kernel, launcher, and binding** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
```cpp
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

**Step 2: Build**

```bash
pip install --no-build-isolation -v .
```

Produces these in the same directory:
<!-- @os:windows -->
- `build/`:  directory with the `.pyd` files
- `matmul_kernel.hip`:  the HIP source generated by hipifying the `.cu` file; this is what `hipcc` actually compiled
<!-- @os:end -->
<!-- @os:linux -->
- `build/`:  directory with the `.so` files
- `matmul_kernel.hip`:  the HIP source generated by hipifying the `.cu` file; this is what `hipcc` actually compiled
<!-- @os:end -->

The same `CUDAExtension` → `hipcc` remapping as walkthrough 1 applies here unchanged.

**Step 3: Use from Python**
```python
import os, sys
import torch
os.chdir("Matrix_Multiplication")
sys.path.insert(0, os.getcwd())
import matmul_ext

A = torch.tensor([[1., 2.],
                  [3., 4.]], device="cuda")

B = torch.tensor([[5., 6.],
                  [7., 8.]], device="cuda")

C = matmul_ext.matmul(A, B)
```

**Expected output:**
```python
>>> C
tensor([[19., 22.],
        [43., 50.]], device='cuda:0')
>>> (C - torch.mm(A, B)).abs().max()
tensor(0., device='cuda:0')
```
**Awesome! You just implemented matrix multiplication on the GPU.** This is a major milestone because matrix multiplication is the backbone of modern machine learning operations like:
- Neural network layers
- Attention mechanisms
- Embeddings
- Transformers

---

## Next Steps

Once you understand the naive matmul kernel, you can explore more advanced GPU strategies. You may take one step further and implement these improvements:
- Instead of reading every value of A and B from global memory repeatedly, blocks of threads load tiles into shared memory and reuse them across many multiply-add operations.
  
- Each product `A[row][k] * B[k][col]` is independent. Instead of one thread computing the full dot product, multiple threads can compute partial sums and then reduce them together.

- Rather than computing a single element per thread, a thread can compute a small tile (e.g., 4×4) of the output. This increases data reuse from shared memory and improves arithmetic intensity.

You may also implement real-world GPU workloads:
- **2D Convolution (Image Filtering)**: A small filter (kernel) slides across an image, computing each output pixel from a weighted sum of neighboring pixels. This introduces stencil computations and shared memory tiling, where threads reuse overlapping image regions to reduce global memory access.

- **Softmax Function**: Softmax converts a vector of numbers into probabilities that sum to 1, commonly used in neural network outputs. Implementing it efficiently on GPU introduces parallel reductions and numerical stability techniques while processing large vectors.
