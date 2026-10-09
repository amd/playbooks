<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Sťahovanie SDXL-Turbo pre Lemonade

Lemonade server poskytuje model SDXL-Turbo (`SDXL-Turbo`). Ak ho chcete stiahnuť vopred:

```bash
lemonade pull SDXL-Turbo
```

`lemonade run SDXL-Turbo` tiež stiahne model pri prvom použití, ak ešte nie je prítomný, a následne ho načíta na inferenciu.

Model sa zobrazí v zozname stiahnutých modelov na serveri Lemonade po dokončení sťahovania; nasledujúce kontroly overia, že je prítomný na danom počítači.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-sdxl-turbo-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:SDXL-Turbo
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-sdxl-turbo-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q SDXL-Turbo
```
<!-- @test:end -->
<!-- @os:end -->