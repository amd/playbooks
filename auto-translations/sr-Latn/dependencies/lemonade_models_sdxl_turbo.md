<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Preuzimanje SDXL-Turbo za Lemonade

Lemonade server opslužuje model SDXL-Turbo (`SDXL-Turbo`). Da biste ga preuzeli unapred:

```bash
lemonade pull SDXL-Turbo
```

`lemonade run SDXL-Turbo` takođe preuzima model prilikom prvog korišćenja ukoliko već nije prisutan, a zatim ga učitava radi zaključivanja (inference).

Model se pojavljuje na listi preuzetih modela na Lemonade serveru čim se preuzimanje završi; provere ispod potvrđuju da je prisutan na mašini.

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