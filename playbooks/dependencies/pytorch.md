### PyTorch
1. **Install PyTorch with ROCm support:**
<!-- @test:id=install-pytorch platform=all timeout=300 depends_on=create-venv setup=activate-venv -->
```bash
pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ torch torchvision torchaudio
```
<!-- @test:end -->