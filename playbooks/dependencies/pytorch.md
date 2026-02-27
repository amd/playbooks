### PyTorch
<!-- @os:linux -->
<!-- @test:id=install-rocm timeout=600 hidden=True -->
```bash
sudo apt update && sudo apt install -y linux-oem-24.04c
sudo apt update
wget https://repo.radeon.com/amdgpu-install/7.2/ubuntu/noble/amdgpu-install_7.2.70200-1_all.deb
sudo apt install ./amdgpu-install_7.2.70200-1_all.deb
amdgpu-install -y --usecase=rocm --no-dkms

```
<!-- @test:end -->
<!-- @os:end -->
1. **Install PyTorch with ROCm support:**
<!-- @device:halo -->
<!-- @test:id=install-pytorch timeout=300 setup=activate-venv -->
```bash
pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ torch torchvision torchaudio
```
<!-- @test:end -->
<!-- @device:end -->
<!-- @device:krackan -->
<!-- @test:id=install-pytorch timeout=300 setup=activate-venv -->
```bash
pip install --index-url https://repo.amd.com/rocm/whl/gfx1150/ torch torchvision torchaudio
```
<!-- @test:end -->
<!-- @device:end -->
<!-- @device:stx,rx7900xt,rx9070xt -->
See [this link](https://rocm.docs.amd.com/projects/radeon-ryzen/en/latest/docs/install/installryz/native_linux/install-ryzen.html) for details.
<!-- @device:end -->