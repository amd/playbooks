# Platform Configuration

This document describes the expected platform configurations for running this playbook.

## Required Frameworks
### Linux

If you're running this on a Halo Box, you don't have to worry about the dependencies, as ROCm and Torch come pre‑installed. You can validate them by running:

```bash
hipcc --version
rocminfo
python3 -c "import torch; print(torch.version.hip)"
python3 -c "import torch; print(torch.cuda.is_available())"
```

However, if you want to remove the existing stack and reinstall the dependencies, or if you're running this playbook on a different hardware setup, you may follow these steps:

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

Verify it's gone: running `rocminfo` should either return “command not found” or produce an empty output.

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
