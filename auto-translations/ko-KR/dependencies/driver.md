<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU 드라이버

[`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html)을 사용하여 최신 AMD GPU 드라이버로 업데이트하세요.

1. 시작 메뉴 또는 시스템 트레이에서 `AMD Software: Adrenalin Edition`을 엽니다.
2. **Driver and Software**로 이동하여 **Manage Updates**를 클릭합니다.
3. 업데이트가 있으면 안내에 따라 다운로드하고 설치합니다.

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### AMD GPU 드라이버

Radeon Software for Linux(RSL) 방식을 사용하여 AMD GPU 드라이버(amdgpu)를 설치하세요. 배포판별 지침은 [커널 드라이버 설치](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html)를 참조하세요.

<!-- @device:end -->
<!-- @os:end -->