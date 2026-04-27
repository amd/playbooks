<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ROCm

**Add the current user to the render and video groups.** 
```bash
sudo usermod -a -G render,video $LOGNAME
```
**Restart your system to apply the settings.**
```bash
sudo reboot
```
**Install ROCm in the created virtual environment.**
> **Note**: Ensure the virtual environment is active before proceeding.
<!-- @device:halo,halo_box -->
```bash
python -m pip install --upgrade pip
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"

```
<!-- @device:end -->

<!-- @device:krk -->

```bash
python -m pip install --upgrade pip
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1152/ "rocm[libraries,devel]"

```
<!-- @device:end -->

<!-- @device:stx -->

```bash
python -m pip install --upgrade pip
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1150/ "rocm[libraries,devel]"

```
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt -->
```bash
python -m pip install --upgrade pip
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx120x-all/ "rocm[libraries,devel]"
```
<!-- @device:end -->

For further installation help, please see this [link](https://rocm.docs.amd.com/en/7.12.0-preview/install/rocm.html?fam=ryzen&gpu=max-pro-395&os=ubuntu&os-version=24.04&i=pip).