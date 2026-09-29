<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

#### PyTorch

생성한 가상 환경에 **AMD ROCm™ 소프트웨어 지원과 함께 PyTorch를 설치**합니다:

<!-- @device:halo,halo_box -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://stable.repo.amd.com/rocm/whl-next/ "torch[device-gfx1151]==2.13.0+rocm10.0.0" "torchvision[device-gfx1151]==0.28.0+rocm10.0.0" "torchaudio==2.11.0.2+rocm10.0.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://stable.repo.amd.com/rocm/whl-next/ "torch[device-gfx1150]==2.13.0+rocm10.0.0" "torchvision[device-gfx1150]==0.28.0+rocm10.0.0" "torchaudio==2.11.0.2+rocm10.0.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:krk -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://stable.repo.amd.com/rocm/whl-next/ "torch[device-gfx1152]==2.13.0+rocm10.0.0" "torchvision[device-gfx1152]==0.28.0+rocm10.0.0" "torchaudio==2.11.0.2+rocm10.0.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx7900xt -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://stable.repo.amd.com/rocm/whl-next/ "torch[device-gfx1100]==2.13.0+rocm10.0.0" "torchvision[device-gfx1100]==0.28.0+rocm10.0.0" "torchaudio==2.11.0.2+rocm10.0.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx9070xt,r9700 -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://stable.repo.amd.com/rocm/whl-next/ "torch[device-gfx1201]==2.13.0+rocm10.0.0" "torchvision[device-gfx1201]==0.28.0+rocm10.0.0" "torchaudio==2.11.0.2+rocm10.0.0"
```
<!-- @test:end -->
<!-- @device:end -->

다른 장치의 경우, 전체 안내는 [ROCm 10.0.0 Documentation](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/frameworks/pytorch/install.html)을 참조하세요.