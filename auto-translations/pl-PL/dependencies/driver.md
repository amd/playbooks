<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### Sterownik AMD GPU

Zaktualizuj do najnowszego sterownika AMD GPU, korzystając z [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Otwórz `AMD Software: Adrenalin Edition` z menu Start lub zasobnika systemowego.
2. Przejdź do **Driver and Software**, kliknij **Manage Updates**.
3. Jeśli dostępna jest aktualizacja, postępuj zgodnie z instrukcjami, aby ją pobrać i zainstalować.

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### Sterownik AMD GPU

Zainstaluj sterownik AMD GPU (amdgpu), korzystając z procesu Radeon Software for Linux (RSL). Instrukcje dla Twojej dystrybucji znajdziesz w instalacji ROCm pod adresem: [Install the kernel driver](https://rocm.docs.amd.com/en/latest/install/rocm.html?fam=radeon&w=graphics&os=ubuntu&ubuntu-ver=26.04&i=amdgpu-install).

Sam sterownik znajdziesz na stronie [Linux® Drivers for AMD Radeon™](https://www.amd.com/en/support/download/linux-drivers.html)

<!-- @device:end -->
<!-- @os:end -->