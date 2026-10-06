<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Gemma-4 E2B:n lataaminen Lemonadelle

Lemonade-palvelin tarjoaa Gemma-4 E2B -mallin (`Gemma-4-E2B-it-GGUF`). Voit ladata sen etukäteen:

```bash
lemonade pull Gemma-4-E2B-it-GGUF
```

`lemonade run Gemma-4-E2B-it-GGUF` lataa myös mallin ensimmäisellä käyttökerralla, jos sitä ei vielä ole koneella, ja lataa sen sitten muistiin päättelyä varten.

Malli näkyy Lemonade-palvelimen ladattujen mallien luettelossa, kun lataus on valmis; alla olevat tarkistukset vahvistavat, että se on koneella.

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