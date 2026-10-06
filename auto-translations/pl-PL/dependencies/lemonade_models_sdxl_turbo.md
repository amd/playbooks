<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Pobieranie modelu SDXL-Turbo dla Lemonade

Serwer Lemonade udostępnia model SDXL-Turbo (`SDXL-Turbo`). Aby pobrać go z wyprzedzeniem:

```bash
lemonade pull SDXL-Turbo
```

Polecenie `lemonade run SDXL-Turbo` również pobiera model przy pierwszym użyciu, jeśli nie jest on jeszcze obecny, a następnie wczytuje go do wnioskowania.

Model pojawia się na liście pobranych modeli serwera Lemonade po zakończeniu pobierania; poniższe sprawdzenia potwierdzają jego obecność na komputerze.

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