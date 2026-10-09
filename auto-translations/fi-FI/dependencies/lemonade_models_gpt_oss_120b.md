<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### GPT-OSS 120B -mallin lataaminen Lemonadelle

Lemonade-palvelin tarjoilee GPT-OSS 120B MXFP4 GGUF -mallia (`gpt-oss-120b-mxfp-GGUF`). Voit ladata sen etukäteen seuraavasti:

```bash
lemonade pull gpt-oss-120b-mxfp-GGUF
```

`lemonade run gpt-oss-120b-mxfp-GGUF` lataa mallin myös ensimmäisellä käyttökerralla, jos sitä ei vielä ole, ja lataa sen sitten käyttöön päättelyä varten.

Malli näkyy Lemonade-palvelimen ladattujen mallien luettelossa, kun lataus on valmis. Alla olevilla tarkistuksilla voit varmistaa, että se on koneella.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-gpt-oss-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:gpt-oss-120b-mxfp-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-gpt-oss-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q gpt-oss-120b-mxfp-GGUF
```
<!-- @test:end -->
<!-- @os:end -->