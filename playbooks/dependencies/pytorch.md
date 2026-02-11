### PyTorch
> **Note**: The PyTorch-ROCm build provides native iGPU acceleration for both Windows and Linux.

1. **Create a Python 3.12 or 3.13 environment and activate it:**  
   (Use your preferred tool: `venv`, `conda`, etc.)

2. **Install PyTorch with ROCm support:**

   ```bash
   pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ torch torchvision torchaudio
   ```