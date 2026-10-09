<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Gemma-4 E2B:n lataaminen Lemonadea varten

Lemonade-palvelin tarjoilee Gemma-4 E2B -mallia (`Gemma-4-E2B-it-GGUF`). Voit ladata sen etukäteen seuraavasti:

```bash
lemonade pull Gemma-4-E2B-it-GGUF
```

Myös `lemonade run Gemma-4-E2B-it-GGUF` lataa mallin ensimmäisellä käyttökerralla, jos sitä ei vielä ole, ja lataa sen sitten muistiin päättelyä varten.

Malli ilmestyy Lemonade-palvelimen ladattujen mallien luetteloon, kun lataus on valmis; alla olevat tarkistukset vahvistavat, että se on läsnä koneella.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-gemma-4-e2b-it-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Gemma-4-E2B-it-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-gemma-4-e2b-it-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Gemma-4-E2B-it-GGUF
```
<!-- @test:end -->
<!-- @os:end -->