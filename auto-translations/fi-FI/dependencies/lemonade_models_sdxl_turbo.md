<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### SDXL-Turbon lataaminen Lemonadelle

Lemonade-palvelin tarjoaa SDXL-Turbo-mallia (`SDXL-Turbo`). Lataa se etukäteen seuraavasti:

```bash
lemonade pull SDXL-Turbo
```

`lemonade run SDXL-Turbo` lataa mallin myös ensimmäisellä käyttökerralla, jos sitä ei vielä ole, ja lataa sen sitten muistiin päättelyä varten.

Malli näkyy Lemonade-palvelimen ladattujen mallien luettelossa, kun lataus on valmis; alla olevat tarkistukset vahvistavat, että se on koneella.

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