import torch
import subprocess
import threading
import time
import re

# A is M x N, B is N x K, C is M x K
M, N, K = 1024, 512, 768

KERNEL_SOURCE = """
extern "C"
__global__ void matmul(float* A, float* B, float* C, int M, int N, int K) {
    // Each thread computes one element of C
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

print("HIP version:", torch.version.hip)
print("Device:", torch.cuda.get_device_name(0))
print(f"Matrix dims: A({M}x{N}) @ B({N}x{K}) -> C({M}x{K})")

matmul_kernel = torch.cuda._compile_kernel(KERNEL_SOURCE, "matmul")

# Row-major contiguous tensors on GPU
A = torch.randn(M, N, dtype=torch.float32, device="cuda")
B = torch.randn(N, K, dtype=torch.float32, device="cuda")
C = torch.zeros(M, K, dtype=torch.float32, device="cuda")

BLOCK = 16
grid_x = (K + BLOCK - 1) // BLOCK   # blocks to cover columns
grid_y = (M + BLOCK - 1) // BLOCK   # blocks to cover rows

gpu_usage_log = []
monitoring = True


def monitor_gpu():
    global monitoring
    while monitoring:
        try:
            result = subprocess.check_output(
                ["rocm-smi", "--showuse"],
                encoding="utf-8"
            )
            match = re.search(r"GPU use \(%\)\s*:\s*(\d+)", result)
            if match:
                usage = int(match.group(1))
                gpu_usage_log.append(usage)
        except Exception:
            pass
        time.sleep(0.1)


monitor_thread = threading.Thread(target=monitor_gpu)
monitor_thread.start()

print("Running matmul kernel...")

start_event = torch.cuda.Event(enable_timing=True)
end_event = torch.cuda.Event(enable_timing=True)

torch.cuda.synchronize()
start_event.record()

for _ in range(50):
    matmul_kernel(
        grid=(grid_x, grid_y, 1),
        block=(BLOCK, BLOCK, 1),
        args=[A, B, C, M, N, K],
    )

end_event.record()
torch.cuda.synchronize()

monitoring = False
monitor_thread.join()

elapsed_ms = start_event.elapsed_time(end_event)
print(f"Elapsed time: {elapsed_ms / 1000:.3f}s")

# Verify the output against torch.mm
C_ref = torch.mm(A, B)
max_err = (C - C_ref).abs().max().item()
print(f"Max error vs torch.mm: {max_err:.6f}")

if gpu_usage_log:
    print(f"Peak GPU Utilization:    {max(gpu_usage_log)}%")
    print(f"Average GPU Utilization: {sum(gpu_usage_log)/len(gpu_usage_log):.2f}%")
else:
    print("No GPU usage captured.")
