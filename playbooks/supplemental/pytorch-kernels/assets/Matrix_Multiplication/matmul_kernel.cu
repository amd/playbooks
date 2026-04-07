#include <torch/extension.h>
#include <hip/hip_runtime.h>

#define BLOCK 16

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

// A: (M, N), B: (N, K) -> returns C: (M, K)
torch::Tensor matmul_launcher(torch::Tensor A, torch::Tensor B) {
    int M = A.size(0);
    int N = A.size(1);
    int K = B.size(1);

    auto C = torch::zeros({M, K}, A.options());

    float* a_ptr = A.data_ptr<float>();
    float* b_ptr = B.data_ptr<float>();
    float* c_ptr = C.data_ptr<float>();

    dim3 block(BLOCK, BLOCK);
    dim3 grid((K + BLOCK - 1) / BLOCK, (M + BLOCK - 1) / BLOCK);

    matmul<<<grid, block>>>(a_ptr, b_ptr, c_ptr, M, N, K);
    hipDeviceSynchronize();

    return C;
}

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) {
    m.def("matmul", &matmul_launcher, "Naive matmul kernel (HIP): A(M,N) @ B(N,K) -> C(M,K)");
}
