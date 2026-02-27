### PyTorch
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
<!-- @device:krk -->
<!-- @test:id=install-pytorch timeout=300 setup=activate-venv -->
```bash
pip install --index-url https://repo.amd.com/rocm/whl/gfx1150/ torch torchvision torchaudio
```
<!-- @test:end -->
<!-- @device:end -->
<!-- @device:stx,rx7900xt,rx9070xt -->
See [this link](https://rocm.docs.amd.com/projects/radeon-ryzen/en/latest/docs/install/installryz/native_linux/install-ryzen.html) for details.
<!-- @device:end -->