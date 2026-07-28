<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

#### ROCm

**현재 사용자를 render 및 video 그룹에 추가합니다.** 
```bash
sudo usermod -a -G render,video $LOGNAME
```

**설정을 적용하려면 시스템을 재시작하세요.**
```bash
sudo reboot
```

**생성한 가상 환경에 ROCm을 설치합니다.**
> **참고**: 계속하기 전에 가상 환경이 활성화되어 있는지 확인하세요.

<!-- @device:halo_box,halo -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "rocm[libraries,devel,device-gfx1151]==7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "rocm[libraries,devel,device-gfx1150]==7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:krk -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "rocm[libraries,devel,device-gfx1152]==7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx7900xt -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "rocm[libraries,devel,device-gfx1100]==7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx9070xt,r9700 -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "rocm[libraries,devel,device-gfx1201]==7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

설치에 대한 자세한 도움말은 [ROCm 7.14 문서](https://rocm.docs.amd.com/en/latest/install/rocm.html)를 참조하세요.