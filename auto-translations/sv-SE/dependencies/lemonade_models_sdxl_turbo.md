<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Ladda ner SDXL-Turbo för Lemonade

Lemonade-servern tillhandahåller SDXL-Turbo-modellen (`SDXL-Turbo`). För att ladda ner den i förväg:

```bash
lemonade pull SDXL-Turbo
```

`lemonade run SDXL-Turbo` laddar också ner modellen vid första användningen om den inte redan finns, och läser sedan in den för inferens.

Modellen visas i Lemonade-serverns lista över nerladdade modeller när hämtningen är klar; kontrollerna nedan bekräftar att den finns på maskinen.

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