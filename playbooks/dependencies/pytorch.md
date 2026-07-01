<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

#### PyTorch

**Install PyTorch with AMD ROCm™ software support** in the created virtual environment:
<!-- @device:halo -->
> **Windows Python version note:** The current `gfx1151` ROCm PyTorch wheel
> set includes Windows wheels through Python 3.13. If you are on Windows with
> Python 3.14, create this virtual environment with Python 3.13 or earlier
> before installing PyTorch.

<!-- @test:id=check-gfx1151-python-version timeout=30 hidden=True setup=activate-venv -->
```python
import platform
import sys

if platform.system() == "Windows" and sys.version_info >= (3, 14):
    raise SystemExit(
        "ROCm PyTorch wheels for gfx1151 are not available for Windows "
        "Python 3.14 yet. Recreate the virtual environment with Python "
        "3.13 or earlier, then rerun the PyTorch install step."
    )
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "torch==2.11.0+rocm7.13.0" "torchvision==0.26.0+rocm7.13.0" "torchaudio==2.11.0+rocm7.13.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1150/ "torch==2.11.0+rocm7.13.0" "torchvision==0.26.0+rocm7.13.0" "torchaudio==2.11.0+rocm7.13.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:krk -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1152/ "torch==2.11.0+rocm7.13.0" "torchvision==0.26.0+rocm7.13.0" "torchaudio==2.11.0+rocm7.13.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx7900xt -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx110X-all/ "torch==2.11.0+rocm7.13.0" "torchvision==0.26.0+rocm7.13.0" "torchaudio==2.11.0+rocm7.13.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx9070xt,r9700 -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx120X-all/ "torch==2.11.0+rocm7.13.0" "torchvision==0.26.0+rocm7.13.0" "torchaudio==2.11.0+rocm7.13.0"
```
<!-- @test:end -->
<!-- @device:end -->

For other devices, please refer to [this link](https://rocm.docs.amd.com/en/7.13.0-preview/frameworks/pytorch/install.html) for full instructions.
