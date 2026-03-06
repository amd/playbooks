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

Write a GPU kernel from scratch, compile it, and launch it on an AMD GPU — then watch utilization spike. This playbook shows how GPU computation actually works: you write the kernel code, and it executes in parallel across thousands of threads.

## What You'll Learn

- How GPU kernels work: grids, blocks, threads, and the indexing model that maps them to data
- How AMD's ROCm/HIP stack lets you write CUDA-style code that runs on AMD GPUs without modification
- How to compile a kernel at runtime using `torch.cuda._compile_kernel`
- How to build a native C++ kernel extension with `CUDAExtension` + pybind11, importable from Python
- How to measure kernel execution time and monitor live GPU utilization with `rocm-smi`

---

This playbook covers two flows for kernel development:

| | Flow | Entry point |
|---|---|---|
| **1** | High-level JIT compilation | `torch.cuda._compile_kernel`, write a kernel as a Python string, no build step |
| **2** | Low-level C++ extension | `CUDAExtension` + pybind11, compile a `.cu` file into a native `.so` and import it |

Both flows run on AMD GPUs. This is possible because PyTorch's ROCm build **maps the entire CUDA API surface to HIP**, `torch.cuda`, `CUDAExtension`, and CUDA kernel syntax all work on AMD hardware transparently. You write CUDA-style code; ROCm handles the translation.

---

## What is a GPU Kernel?

A GPU kernel is a function that runs **in parallel across thousands of GPU threads simultaneously**. Unlike a CPU function that executes once per call, a kernel is launched with a **grid** of **blocks**, each containing many **threads**, all executing the same code on different data.

```
Grid
└── Block [0]  Block [1]  Block [2]  ...
     └── Thread[0..255]  (each processes one data element)
```

### Core Concepts:

### `__global__` — the kernel qualifier

In HIP/CUDA, `__global__` marks a function as a GPU kernel:

- It **runs on the GPU** (device)
- It is **launched from the CPU** (host)
- It **executes in parallel** across many GPU threads simultaneously

```c
__global__ void add_one(float* data, int n) { ... }
```

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

## AMD GPU Programming: HIP

AMD GPUs use **HIP** (Heterogeneous-Compute Interface for Portability), part of the **ROCm** (Radeon Open Compute) platform.

HIP is designed to be syntactically close to CUDA. Most CUDA code can be translated to HIP mechanically using the `hipify` tool (which is what generated the `.hip` files in this repo).

| CUDA | HIP equivalent |
|---|---|
| `cudaMalloc` | `hipMalloc` |
| `cudaDeviceSynchronize` | `hipDeviceSynchronize` |
| `kernel<<<grid, block>>>` | `hipLaunchKernelGGL(kernel, ...)` |
| `nvcc` | `hipcc` |

**ROCm** is the full AMD open-source GPU compute stack: drivers, compilers, libraries, and runtime. HIP sits on top of ROCm.

---

## PyTorch + AMD/HIP

PyTorch ships a ROCm build where the CUDA API surface (`torch.cuda.*`) is transparently backed by HIP. This means:

- `torch.cuda.is_available()` works on AMD GPUs with ROCm
- `tensor.to("cuda")` allocates on the AMD GPU
- `torch.version.hip` exposes the HIP version

PyTorch also exposes `torch.cuda._compile_kernel()`, a high-level shortcut to JIT-compile a raw kernel string and get back a callable, without needing a separate build step.

---

## Installing Dependencies

### 1. Uninstall Old Stack

```bash
pip uninstall torch torchvision torchaudio

# Remove old ROCm
sudo apt purge 'rocm*' 'hip*' 'hsa*' -y
sudo rm -rf /opt/rocm*
sudo rm -rf /etc/apt/sources.list.d/rocm*
sudo apt autoremove -y
sudo apt update
```

Verify it's gone: `rocminfo` shouldn't return anything.

### 2. Install ROCm 7.1.1

Check your Ubuntu version first:
- **24.04** → `noble`
- **22.04** → `jammy`

```bash
# Download the installer (noble shown; swap for jammy if needed)
wget https://repo.radeon.com/amdgpu-install/7.1.1/ubuntu/noble/amdgpu-install_7.1.1.70101-1_all.deb

# Install the package
sudo DEBIAN_FRONTEND=noninteractive apt install -y ./amdgpu-install_7.1.1.70101-1_all.deb

# Install ROCm + HIP
sudo amdgpu-install --usecase=rocm,hip -y
```

Verify:
```bash
hipcc --version
rocminfo
```

### 3. Install PyTorch for ROCm 7.1

```bash
pip install torch torchvision torchaudio \
  --index-url https://download.pytorch.org/whl/rocm7.1
```

Verify:
```bash
python3 -c "import torch; print(torch.version.hip)"
python3 -c "import torch; print(torch.cuda.is_available())"
```

---

## Examples

### Example 1: Simple Vector Addition

#### Flow 1: High-Level: `add_one_kernel.py`

Kernel is written as a raw C++ string inside Python and compiled at runtime via PyTorch's built-in JIT.

**Files:** [add_one_kernel.py](assets/Vector%20Addition/add_one_kernel.py)

**How it works:**

```python
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

# 3. Launch: specify grid/block dimensions and pass tensor args directly
add_one_kernel(
    grid=(grid_size, 1, 1),
    block=(block_size, 1, 1),
    args=[x, n],
)
```

The script also spawns a background thread that polls `rocm-smi` every 100ms to log peak and average GPU utilization during the kernel run.

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
python add_one_kernel.py
```

**Expected output:**[The performance numbers might vary]
```
Elapsed time: 2.347s
Peak GPU Utilization: 94%
Average GPU Utilization: 67.06%
```

---

#### Flow 2: Low-Level: HIP C++ Extension

The full manual path: write the kernel and Python binding in a single `.cu` file, compile it as a native extension using PyTorch's build system, then import and call it from Python.

**Files:**

| File | Role |
|---|---|
| [add_one_kernel.cu](assets/Vector%20Addition/add_one_kernel.cu) | Kernel + launcher + pybind11 binding, everything in one file |
| [setup.py](assets/Vector%20Addition/setup.py) | Build script, uses `CUDAExtension` to compile the `.cu` into a `.so` |

**How it works:**

**Step 1: The kernel, launcher, and binding** ([add_one_kernel.cu](assets/Vector%20Addition/add_one_kernel.cu)):
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

**Step 2: Build** ([setup.py](assets/Vector%20Addition/setup.py)):
```bash
python setup.py build_ext --inplace
```
`CUDAExtension` is a CUDA build helper from `torch.utils.cpp_extension`. On AMD with ROCm, PyTorch **remaps `CUDAExtension` to use `hipcc`** instead of `nvcc`, so the same `setup.py` that would build a CUDA extension on NVIDIA compiles to AMD GPU code without any changes. This is the key mechanism that makes CUDA extension code portable to AMD: PyTorch's ROCm build intercepts the build path and routes it through the HIP compiler. Produces two files in the same directory:
- `add_one_ext.cpython-*.so` — the importable Python extension
- `add_one_kernel.hip` — the HIP source generated by hipifying the `.cu` file; this is what `hipcc` actually compiled

**Step 3: Use from Python:**
```python
import add_one_ext
import torch

x = torch.ones(10, device="cuda")
add_one_ext.add_one(x)
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

### Example 2: Matrix Multiplication

Given matrices **A** (M×N) and **B** (N×P), compute **C = A * B** (M×P). Each element `C[i][j]` is the dot product of row `i` of A with column `j` of B, completely independent of every other output element, making this a natural fit for GPU parallelism.

#### The Math

Each output element is defined as:

$$C[row, col] = \sum_{k=0}^{N-1} A[row, k] \cdot B[k, col]$$

Each output element is assigned to exactly one thread, and threads don't depend on each other's results, thread `(0,0)` and thread `(1,5)` run simultaneously with no coordination. However, within a single thread the dot product is **sequential**: the `k` loop iterates N times, accumulating one multiply-add per step.

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

The same principle applies to B (column width P):

$$B[k, col] = B[k \times P + col]$$

Substituting into the matmul formula gives the exact inner loop in the kernel:

$$C[row, col] = \sum_{k=0}^{N-1} A[row \times N + k] \cdot B[k \times P + col]$$

#### 2D thread indexing

Vector addition maps one thread to one element of a 1D array. Matrix multiplication maps one thread to one element of a 2D output matrix, so the natural launch shape is a **2D grid of 2D blocks**.

| | Vector Addition | Matrix Multiplication |
|---|---|---|
| Output shape | 1D vector, length N | 2D matrix, M×P |
| Thread grid | 1D: `(grid_x, 1, 1)` | 2D: `(grid_x, grid_y, 1)` |
| Thread block | 1D: `(256, 1, 1)` = 256 threads | 2D: `(16, 16, 1)` = 256 threads |
| Thread index | `idx = blockIdx.x * blockDim.x + threadIdx.x` | `row = blockIdx.y * blockDim.y + threadIdx.y` & `col = blockIdx.x * blockDim.x + threadIdx.x` |
| Work per thread | `data[idx] += 1` | `C[row][col] = Σ A[row][k] * B[k][col]` |

The block is still 256 threads total (16×16), matching the convention from Example 1, but arranged in a square to align naturally with the 2D output.

```
Grid (2D)
└── Block [bx, by]  ...
     └── Thread [tx, ty]  →  computes C[by*16+ty][bx*16+tx]
```

The grid covers the full output:
```
grid_x = ceil(P / 16)   # enough blocks to span all P columns
grid_y = ceil(M / 16)   # enough blocks to span all M rows
```

---

#### Flow 1: High-Level: `matmul_kernel.py`

Kernel is written as a raw C++ string inside Python and compiled at runtime via PyTorch's built-in JIT. Identical workflow to Example 1, only the kernel body and launch dimensions change.

**Files:** [matmul_kernel.py](assets/Matrix%20Multiplication/matmul_kernel.py)

**How it works:**

```python
# 1. Kernel source, 2D indexing to map threads onto the M×P output matrix
KERNEL_SOURCE = """
extern "C"
__global__ void matmul(float* A, float* B, float* C, int M, int N, int P) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;

    if (row < M && col < P) {
        float sum = 0.0f;
        for (int k = 0; k < N; k++) {
            sum += A[row * N + k] * B[k * P + col];
        }
        C[row * P + col] = sum;
    }
}
"""

# 2. Compile the kernel string
matmul_kernel = torch.cuda._compile_kernel(KERNEL_SOURCE, "matmul")

# 3. Launch with a 2D grid, grid_x covers columns (P), grid_y covers rows (M)
BLOCK = 16
matmul_kernel(
    grid=(grid_x, grid_y, 1),
    block=(BLOCK, BLOCK, 1),
    args=[A, B, C, M, N, P],
)
```

The row-major memory layout of the tensors maps directly to how the kernel indexes the flat pointers:
- `A[row * N + k]` — row `row`, column `k`
- `B[k * P + col]`  — row `k`, column `col`

The script spawns the same background monitoring thread from Example 1 (`rocm-smi` polled every 100ms) and verifies the result against `torch.mm`.

**Run:**
```bash
python matmul_kernel.py
```

**Expected output:**[The performance numbers might vary]
```
Elapsed time: 0.255s
Max error vs torch.mm: 0.000160
Peak GPU Utilization:    100%
Average GPU Utilization: 55.00%
```

---

#### Flow 2: Low-Level: HIP C++ Extension

The full manual path: write the kernel and Python binding in a `.cu` file, compile it as a native extension, then import and call it from Python. Mirrors the structure of `add_one_kernel.cu` exactly, only the kernel signature and launcher logic differ.

**Files:**

| File | Role |
|---|---|
| [matmul_kernel.cu](assets/Matrix%20Multiplication/matmul_kernel.cu) | Kernel + launcher + pybind11 binding |
| [setup.py](assets/Matrix%20Multiplication/setup.py) | Build script, uses `CUDAExtension` to compile the `.cu` into a `.so` |

**How it works:**

**Step 1: The kernel, launcher, and binding** ([matmul_kernel.cu](assets/Matrix%20Multiplication/matmul_kernel.cu)):
```cpp
#define BLOCK 16

// GPU kernel, one thread per output element of C
__global__ void matmul(float* A, float* B, float* C, int M, int N, int P) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;

    if (row < M && col < P) {
        float sum = 0.0f;
        for (int k = 0; k < N; k++) {
            sum += A[row * N + k] * B[k * P + col];
        }
        C[row * P + col] = sum;
    }
}

// Launcher, extracts dims from torch::Tensor, allocates C, sets 2D grid/block
torch::Tensor matmul_launcher(torch::Tensor A, torch::Tensor B) {
    int M = A.size(0), N = A.size(1), P = B.size(1);
    auto C = torch::zeros({M, P}, A.options());

    dim3 block(BLOCK, BLOCK);
    dim3 grid((P + BLOCK - 1) / BLOCK, (M + BLOCK - 1) / BLOCK);

    matmul<<<grid, block>>>(A.data_ptr<float>(), B.data_ptr<float>(),
                            C.data_ptr<float>(), M, N, P);
    hipDeviceSynchronize();
    return C;
}

// Python binding, exposes matmul_launcher as matmul_ext.matmul
PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) {
    m.def("matmul", &matmul_launcher, "Naive matmul kernel (HIP): A(M,N) @ B(N,P) -> C(M,P)");
}
```

Compared to `add_one_launcher` in Example 1, the launcher here:
- Takes **two** input tensors instead of one
- Derives all three dimensions (M, N, P) from tensor shapes, no manual size passing from Python
- Allocates and **returns** the output tensor C, rather than mutating in-place
- Uses `dim3` for both grid and block to express the 2D launch shape

**Step 2: Build** ([setup.py](assets/Matrix%20Multiplication/setup.py)):
```bash
cd "Matrix Multiplication"
python setup.py build_ext --inplace
```
Produces two files in the same directory:
- `matmul_ext.cpython-*.so` — the importable Python extension
- `matmul_kernel.hip` — the HIP source generated by hipifying the `.cu` file; this is what `hipcc` actually compiled

The same `CUDAExtension` → `hipcc` remapping as Example 1 applies here unchanged.

**Step 3: Use from Python:**
```python
import matmul_ext
import torch

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

---

## Next Steps

Once you understand the naive matmul kernel, you can explore more advanced GPU strategies:
- Each product A[row][k] * B[k][col] is independent. Instead of one thread computing the full dot product, multiple threads can compute partial sums and then reduce them together.

- Instead of computing one output element, a thread can compute a tile of outputs (e.g., 4×4). This allows reuse of loaded A and B values across multiple accumulations, improving arithmetic intensity.

You may take one step further and implement these real-world GPU workloads:
- **2D Convolution (Image Filtering)**: A small filter (kernel) slides across an image, computing each output pixel from a weighted sum of neighboring pixels. This introduces **stencil computations and shared memory tiling**, where threads reuse overlapping image regions to reduce global memory access.

- **Softmax Function**: Softmax converts a vector of numbers into probabilities that sum to 1, commonly used in neural network outputs. Implementing it efficiently on GPU introduces **parallel reductions and numerical stability techniques** while processing large vectors.
