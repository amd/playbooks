<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ROCm

**Add the current user to the render and video groups.** A restart will occur to apply the settings.
```bash
sudo usermod -a -G render,video $LOGNAME
sudo reboot
```
#### Install ROCm in the created virtual environment
Ensure the virtual environment is active before proceeding.
<!-- @device:halo,halo_box -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --upgrade pip
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"

```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:krk -->
<!-- @test:id=install-pytorch timeout=300 setup=activate-venv -->
```bash
python -m pip install --upgrade pip
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1152/ "rocm[libraries,devel]"

```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx -->
<!-- @test:id=install-pytorch timeout=300 setup=activate-venv -->
```bash
python -m pip install --upgrade pip
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1150/ "rocm[libraries,devel]"

```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt -->
```bash
python -m pip install --upgrade pip
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx120x-all/ "rocm[libraries,devel]"
```
<!-- @device:end -->