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

### Uninstall Old Stack

```bash
pip uninstall torch torchvision torchaudio

# Remove ROCm
sudo rm -rf /opt/rocm
sudo apt purge -y 'amdgpu*' 'rocm*' 'hip*'
sudo apt autoremove -y

sudo rm -rf /etc/ld.so.conf.d/rocm.conf
sudo rm -rf /etc/profile.d/rocm.sh
```

#### Verify cleanup:
```bash
which hipcc       # should return nothing
rocminfo          # should fail if ROCm is fully removed
amd-smi           # should fail or report no ROCm
ls -l /opt/rocm   # should not exist
```

### Install ROCm 7.2

```bash
sudo apt update
wget https://repo.radeon.com/amdgpu-install/7.2/ubuntu/noble/amdgpu-install_7.2.70200-1_all.deb
sudo apt install ./amdgpu-install_7.2.70200-1_all.deb
sudo amdgpu-install -y --usecase=rocm --no-dkms
```

#### Set user permissions
```bash
sudo usermod -aG render,video $USER
```

#### Reboot
```bash
sudo reboot
```

#### Verify:
```bash
hipcc --version
rocminfo
```

### Install PyTorch

```bash
pip install torch torchvision torchaudio \
  --index-url https://download.pytorch.org/whl/rocm7.2
```

#### Verify:
```bash
python3 -c "import torch; print(torch.version.hip)"
python3 -c "import torch; print(torch.cuda.is_available())"
```

---
