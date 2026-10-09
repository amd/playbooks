<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Prenos SDXL-Turbo za Lemonade

Strežnik Lemonade streže model SDXL-Turbo (`SDXL-Turbo`). Za predhodni prenos:

```bash
lemonade pull SDXL-Turbo
```

Ukaz `lemonade run SDXL-Turbo` ob prvi uporabi model prav tako prenese, če še ni prisoten, nato pa ga naloži za sklepanje.

Model se pojavi na seznamu prenesenih modelov strežnika Lemonade, ko je prenos zaključen; spodnja preverjanja potrdijo, da je prisoten v napravi.

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