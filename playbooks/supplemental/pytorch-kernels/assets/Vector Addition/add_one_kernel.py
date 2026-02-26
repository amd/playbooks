import torch
import subprocess
import threading
import time
import re

KERNEL_SOURCE = """
extern "C"
__global__ void add_one(float* data, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        for (int i = 0; i < 1000; i++)  // make workload heavy
            data[idx] += 1.0f;
    }
}
"""

print("HIP version:", torch.version.hip)
print("Device:", torch.cuda.get_device_name(0))

add_one_kernel = torch.cuda._compile_kernel(KERNEL_SOURCE, "add_one")

x = torch.ones(100_000_000, dtype=torch.float32, device="cuda")
n = x.numel()

block_size = 256
grid_size = (n + block_size - 1) // block_size

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

        time.sleep(0.1)  # sample every 100ms


monitor_thread = threading.Thread(target=monitor_gpu)
monitor_thread.start()

print("Running kernel...")

start = time.perf_counter()

for _ in range(200):
    add_one_kernel(
        grid=(grid_size, 1, 1),
        block=(block_size, 1, 1),
        args=[x, n],
    )

torch.cuda.synchronize()

end = time.perf_counter()

monitoring = False
monitor_thread.join()

print(f"Elapsed time: {end - start:.3f}s")

if gpu_usage_log:
    print(f"Peak GPU Utilization: {max(gpu_usage_log)}%")
    print(f"Average GPU Utilization: {sum(gpu_usage_log)/len(gpu_usage_log):.2f}%")
else:
    print("No GPU usage captured.")