<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

#### PyTorch

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
**Before starting, grant your user access to GPU devices** (log out/in for this to take effect):

```bash
sudo usermod -a -G render,video $LOGNAME
```
<!-- @device:end -->
<!-- @os:end -->

**Install PyTorch with AMD ROCm™ software support** in the created virtual environment:
<!-- @device:halo,halo_box -->
<!-- @test:id=install-pytorch timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ torch torchvision torchaudio
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:krk -->
<!-- @test:id=install-pytorch timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1152/ torch torchvision torchaudio
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx -->
<!-- @test:id=install-pytorch timeout=300 setup=activate-venv -->
```bash
python -m pip install  --index-url https://repo.amd.com/rocm/whl/gfx1150/ torch torchvision torchaudio
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt -->
See [this link](https://rocm.docs.amd.com/projects/radeon-ryzen/en/latest/docs/install/installryz/native_linux/install-ryzen.html) for details.
<!-- @device:end -->
