<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Qwen3.6 35B A3B -mallin lataaminen Lemonadelle

Lemonade-palvelin tarjoilee Qwen3.6 35B A3B -mallia (`Qwen3.6-35B-A3B-GGUF`). Voit ladata sen etukäteen seuraavasti:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Komento `lemonade run Qwen3.6-35B-A3B-GGUF` lataa mallin myös ensimmäisellä käyttökerralla, jos sitä ei vielä ole koneella, ja lataa sen sitten muistiin päättelyä varten.

Malli näkyy Lemonade-palvelimen ladattujen mallien listalla, kun lataus on valmis; alla olevat tarkistukset varmistavat, että malli on koneella.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-6-35b-a3b-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3.6-35B-A3B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-qwen3-6-35b-a3b-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Qwen3.6-35B-A3B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->