<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### SDXL-Turbo-mallin lataaminen Lemonadelle

Lemonade-palvelin tarjoilee SDXL-Turbo-mallia (`SDXL-Turbo`). Lataaksesi sen etukäteen:

```bash
lemonade pull SDXL-Turbo
```

Myös `lemonade run SDXL-Turbo` lataa mallin ensimmäisellä käyttökerralla, jos sitä ei vielä ole koneella, ja lataa sen sitten käyttöön päättelyä varten.

Malli ilmestyy Lemonade-palvelimen ladattujen mallien luetteloon, kun lataus on valmis; alla olevat tarkistukset vahvistavat, että se on läsnä koneella.

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