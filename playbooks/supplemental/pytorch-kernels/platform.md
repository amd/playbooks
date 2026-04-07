# Platform Configuration

This document describes the expected platform configurations for running this playbook.

## Required Frameworks
## Linux

If you're running on a Halo Box, ROCm and PyTorch are preinstalled. You can validate them by running:

```bash
hipcc --version
rocminfo
amd-smi
python3 -c "import torch; print(torch.version.hip)"
python3 -c "import torch; print(torch.cuda.is_available())"
```

However, if you want to remove the existing stack and reinstall the dependencies, or if you're running this playbook on a different hardware setup, you may follow these steps:

### Uninstall Old Stack

```bash
pip uninstall torch torchvision torchaudio

# Remove ROCm
pip uninstall -y rocm rocm-sdk-core rocm-sdk-devel rocm-sdk-libraries-gfx1151 triton triton-rocm

rm -f ~/.local/bin/hipcc
rm -f ~/.local/bin/amd-smi

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
```

### Install ROCm Python packages via pip

```bash
# Create a venv - Recommended approach
python3 -m venv ~/rocm-env
source ~/rocm-env/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# ROCm for gfx1151:
pip install --index-url https://rocm.nightlies.amd.com/v2/gfx1151/ "rocm[libraries,devel]"
```

#### Set user permissions and reboot
```bash
sudo usermod -aG render,video $USER
sudo reboot
```

#### Export environment variables
```bash
source ~/rocm-env/bin/activate
# Initialize the devel libraries. Some tools (HIPRTC, libroctx64, etc.) are lazily expanded
rocm-sdk init

# Set environment variables
export ROCM_HOME="$VIRTUAL_ENV/lib/python3.12/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH="$ROCM_HOME/lib:$LD_LIBRARY_PATH"
export PATH="$ROCM_HOME/bin:$PATH"
```

#### Verify ROCm:
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
source ~/rocm-env/bin/activate
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

## Windows

If you're running on a Halo Box, ROCm and PyTorch are preinstalled. You can validate them by running:

```bash
hipcc --version
hipinfo

print("HIP available:", torch.cuda.is_available())
```

### Prerequisites
- Install latest: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)

### Install ROCm Python packages via pip
```bash
# Create a venv - Recommended approach
python -m venv rocm-env
rocm-env\Scripts\activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# ROCm for gfx1151:
pip install --index-url https://rocm.nightlies.amd.com/v2/gfx1151/ "rocm[libraries,devel]"

#Reboot

# Open a Powershell terminal and activate Visual Studio environment
cmd /c '"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1 && set' | ForEach-Object { if ($_ -match '^([^=]+)=(.*)$') { [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process') } }

rocm-env\Scripts\activate

# Initialize the devel libraries. Some tools (HIPRTC, libroctx64, etc.) are lazily expanded
rocm-sdk init

# Set environment variables
$ROCM_ROOT = (rocm-sdk path --root).Trim()
$ROCM_BIN = (rocm-sdk path --bin).Trim()

$env:PATH = "$ROCM_ROOT\lib\llvm\bin;$ROCM_BIN;$env:PATH"

# Set compiler and build settings
$env:CC = "clang-cl"
$env:CXX = "clang-cl"
$env:DISTUTILS_USE_SDK = "1"
```

#### Verify:
```bash
hipcc --version
hipInfo
```

### Install PyTorch

```bash
rocm-env\Scripts\activate
pip install --pre --index-url https://rocm.nightlies.amd.com/v2/gfx1151/ torch torchaudio torchvision
```

#### Verify:
```python
import torch

print("HIP available:", torch.cuda.is_available())
print("Device name:", torch.cuda.get_device_name(0))
print("Device count:", torch.cuda.device_count())
```
