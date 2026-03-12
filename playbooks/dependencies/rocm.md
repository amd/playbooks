# ROCm on Linux: Install, Permissions, and Verification

### 1. Install ROCm on Linux
```bash
sudo apt update
wget https://repo.radeon.com/amdgpu-install/7.2/ubuntu/noble/amdgpu-install_7.2.70200-1_all.deb
sudo apt install ./amdgpu-install_7.2.70200-1_all.deb
sudo amdgpu-install -y --usecase=rocm --no-dkms
```

### 2. Set the correct user permissions
```bash
sudo usermod -aG render,video $USER
```

### 3. Reboot the system
```bash
sudo reboot
```
This is important for the runtime stack and permissions to settle.

### 4. Verify that ROCm is installed correctly and usable

<!-- @test:id=verify-linux-rocm-installation timeout=180 -->
```bash
# Check ROCm path (paths should exist)
ls -l /opt/rocm
ls -l /opt/rocm/lib/libroctx64.so*

# Check ROCm device files (Device files owned by the render group should be visible)
ls -l /dev/kfd
ls -l /dev/dri/renderD* 

# Check user groups ($USER should be listed in both render and video)
id
groups

# Check ROCm with rocminfo ('Permission denied' error should NOT be seen)
rocminfo | sed -n '1,120p'
```
<!-- @test:end -->

---
