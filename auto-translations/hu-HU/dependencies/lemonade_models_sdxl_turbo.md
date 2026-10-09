<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### SDXL-Turbo letöltése a Lemonade-hez

A Lemonade szerver az SDXL-Turbo modellt (`SDXL-Turbo`) szolgálja ki. Előzetes letöltéshez:

```bash
lemonade pull SDXL-Turbo
```

A `lemonade run SDXL-Turbo` parancs első használatkor szintén letölti a modellt, ha az még nincs meg, majd betölti az inferenciához.

A modell megjelenik a Lemonade szerver letöltött modelleket tartalmazó listájában, amint a letöltés befejeződik; az alábbi ellenőrzések igazolják, hogy jelen van a gépen.

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