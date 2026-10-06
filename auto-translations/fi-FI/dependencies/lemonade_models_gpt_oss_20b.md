<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### GPT-OSS 20B -mallin lataaminen Lemonadea varten

Lemonade-palvelin tarjoilee GPT-OSS 20B MXFP4 GGUF -mallia (`gpt-oss-20b-mxfp4-GGUF`). Voit ladata sen etukäteen seuraavasti:

```bash
lemonade pull gpt-oss-20b-mxfp4-GGUF
```

`lemonade run gpt-oss-20b-mxfp4-GGUF` lataa mallin myös ensimmäisellä käyttökerralla, jos sitä ei ole vielä ladattu, ja lataa sen sitten muistiin päättelyä varten.

Malli näkyy Lemonade-palvelimen ladattujen mallien luettelossa, kun lataus on valmis; alla olevat tarkistukset vahvistavat, että se on läsnä koneella.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-gpt-oss-20b-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:gpt-oss-20b-mxfp4-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-gpt-oss-20b-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q gpt-oss-20b-mxfp4-GGUF
```
<!-- @test:end -->
<!-- @os:end -->