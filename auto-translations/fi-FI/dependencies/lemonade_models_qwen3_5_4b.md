<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Qwen3.5 4B -mallin lataaminen Lemonadelle

Lemonade-palvelin tarjoilee Qwen3.5 4B -mallia (`Qwen3.5-4B-GGUF`). Voit ladata sen etukäteen seuraavasti:

```bash
lemonade pull Qwen3.5-4B-GGUF
```

Myös komento `lemonade run Qwen3.5-4B-GGUF` lataa mallin ensimmäisellä käyttökerralla, jos sitä ei vielä ole saatavilla, ja lataa sen sen jälkeen muistiin päättelyä varten.

Malli näkyy Lemonade-palvelimen ladattujen mallien listassa, kun lataus on valmis; alla olevat tarkistukset vahvistavat, että se on läsnä koneella.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-5-4b-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3.5-4B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-qwen3-5-4b-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Qwen3.5-4B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->