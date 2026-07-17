<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU Driver

Zaktualizuj do najnowszego sterownika AMD GPU za pomocą [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html).

1. Otwórz `AMD Software: Adrenalin Edition` z menu Start lub zasobnika systemowego.
2. Przejdź do **Driver and Software**, kliknij **Manage Updates**.
3. Jeśli aktualizacja jest dostępna, postępuj zgodnie z instrukcjami, aby ją pobrać i zainstalować.

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### AMD GPU Driver

Zainstaluj sterownik AMD GPU (amdgpu) przy użyciu przepływu Radeon Software for Linux (RSL). Instrukcje dla swojej dystrybucji znajdziesz w sekcji [Instalacja sterownika jądra](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->