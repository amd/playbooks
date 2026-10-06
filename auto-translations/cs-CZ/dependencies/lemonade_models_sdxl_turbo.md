<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Stažení SDXL-Turbo pro Lemonade

Server Lemonade poskytuje model SDXL-Turbo (`SDXL-Turbo`). Pro jeho stažení předem:

```bash
lemonade pull SDXL-Turbo
```

Příkaz `lemonade run SDXL-Turbo` model také stáhne při prvním použití, pokud ještě není přítomen, a poté jej načte pro inferenci.

Model se v seznamu stažených modelů serveru Lemonade objeví po dokončení stahování; níže uvedené kontroly ověří, že je na počítači přítomen.

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