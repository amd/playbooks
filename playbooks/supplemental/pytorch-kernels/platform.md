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

### Install ROCm Python packages via pip

```bash
# Create a venv - Recommended approach
python3 -m venv ~/rocm-env

# Activate it
source ~/rocm-env/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# For gfx1151:
pip install --index-url https://rocm.nightlies.amd.com/v2/gfx1151/ "rocm[libraries,devel]"

# Initialize the devel libraries. Some tools (HIPRTC, libroctx64, etc.) are lazily expanded, so run:
rocm-sdk init

# Set environment variables
export ROCM_HOME="$VIRTUAL_ENV/lib/python3.12/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH="$ROCM_HOME/lib:$LD_LIBRARY_PATH"
export PATH="$ROCM_HOME/bin:$PATH"

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
ls $ROCM_HOME/lib/libhiprtc.so*
ls $ROCM_HOME/lib/libroctx64.so*
```
You should see files like libhiprtc.so and libroctx64.so. If this returns nothing, the ROCm SDK was not initialized correctly.
```bash
hipcc --version
rocminfo
amd-smi
```

### Install PyTorch

```bash
pip install --pre --index-url https://rocm.nightlies.amd.com/v2/gfx1151/ torch==2.10.0 torchaudio torchvision
```

#### Verify:
```python
import torch

print("HIP available:", torch.cuda.is_available())
print("Device name:", torch.cuda.get_device_name(0))
print("Device count:", torch.cuda.device_count())
```

---
