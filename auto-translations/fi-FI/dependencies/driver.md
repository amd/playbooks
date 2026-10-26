<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
### AMD GPU -ajuri

Päivitä AMD GPU -ajuri uusimpaan versioon käyttämällä [`AMD Software: Adrenalin Edition™`](https://www.amd.com/en/products/software/adrenalin.html) -sovellusta.

1. Avaa `AMD Software: Adrenalin Edition` Käynnistä-valikosta tai ilmaisinalueelta.
2. Siirry kohtaan **Driver and Software** ja napsauta **Manage Updates**.
3. Jos päivitys on saatavilla, seuraa ohjeita sen lataamiseksi ja asentamiseksi.

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

Asenna AMD GPU -ajuri (amdgpu) käyttämällä Radeon Software for Linux (RSL) -menetelmää. Katso jakelullesi sopivat ohjeet ROCm-asennuksesta: [Asenna ytimen ajuri](https://rocm.docs.amd.com/en/latest/install/rocm.html?fam=radeon&w=graphics&os=ubuntu&ubuntu-ver=26.04&i=amdgpu-install). 

Itse ajurin löydät osoitteesta [Linux® Drivers for AMD Radeon™](https://www.amd.com/en/support/download/linux-drivers.html)

<!-- @device:end -->
<!-- @os:end -->