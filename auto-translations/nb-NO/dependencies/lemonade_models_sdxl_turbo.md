<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Laster ned SDXL-Turbo for Lemonade

Lemonade-serveren serverer SDXL-Turbo-modellen (`SDXL-Turbo`). For å laste den ned på forhånd:

```bash
lemonade pull SDXL-Turbo
```

`lemonade run SDXL-Turbo` laster også ned modellen ved første bruk hvis den ikke allerede finnes, og laster den deretter inn for inferens.

Modellen vises i Lemonade-serverens liste over nedlastede modeller så snart nedlastingen er fullført; sjekkene nedenfor bekrefter at den er til stede på maskinen.

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