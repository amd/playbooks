<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU -ajuri

Päivitä uusimpaan AMD GPU -ajuriin käyttämällä [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html) -sovellusta.

1. Avaa `AMD Software: Adrenalin Edition` Käynnistä-valikosta tai järjestelmäpalkista.
2. Siirry kohtaan **Driver and Software** ja napsauta **Manage Updates**.
3. Jos päivitys on saatavilla, seuraa ohjeita ladataksesi ja asentaaksesi sen.

<!-- @test:id=amd-gpu-visible-windows timeout=60 hidden=True -->
```powershell
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
### AMD GPU -ajuri

Asenna AMD GPU -ajuri (amdgpu) käyttämällä Radeon Software for Linux (RSL) -menetelmää. Katso jakelullesi sopivat ohjeet kohdasta [Ytimen ajurin asentaminen](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).

<!-- @device:end -->
<!-- @os:end -->