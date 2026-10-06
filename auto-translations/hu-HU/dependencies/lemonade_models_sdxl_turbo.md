<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Az SDXL-Turbo letöltése a Lemonade-hez

A Lemonade szerver az SDXL-Turbo modellt (`SDXL-Turbo`) szolgálja ki. A modell előzetes letöltéséhez:

```bash
lemonade pull SDXL-Turbo
```

A `lemonade run SDXL-Turbo` parancs is letölti a modellt az első használatkor, ha az még nincs jelen, majd betölti következtetéshez.

A modell a Lemonade szerver letöltött modelljeinek listájában jelenik meg, miután a letöltés befejeződött; az alábbi ellenőrzések megerősítik, hogy jelen van a gépen.

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