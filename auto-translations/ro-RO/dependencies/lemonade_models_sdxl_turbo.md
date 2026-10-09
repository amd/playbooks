<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Descărcarea SDXL-Turbo pentru Lemonade

Serverul Lemonade servește modelul SDXL-Turbo (`SDXL-Turbo`). Pentru a-l descărca în prealabil:

```bash
lemonade pull SDXL-Turbo
```

`lemonade run SDXL-Turbo` descarcă de asemenea modelul la prima utilizare, dacă nu este deja prezent, apoi îl încarcă pentru inferență.

Modelul apare în lista de modele descărcate a serverului Lemonade odată ce descărcarea este finalizată; verificările de mai jos confirmă că acesta este prezent pe mașină.

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