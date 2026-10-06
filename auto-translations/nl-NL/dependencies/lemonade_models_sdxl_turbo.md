<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### SDXL-Turbo downloaden voor Lemonade

De Lemonade-server host het SDXL-Turbo-model (`SDXL-Turbo`). Om het model vooraf te downloaden:

```bash
lemonade pull SDXL-Turbo
```

`lemonade run SDXL-Turbo` downloadt het model ook bij het eerste gebruik als het nog niet aanwezig is, en laadt het vervolgens voor inferentie.

Het model verschijnt in de lijst met gedownloade modellen van de Lemonade-server zodra het ophalen is voltooid; de onderstaande controles bevestigen dat het aanwezig is op de machine.

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