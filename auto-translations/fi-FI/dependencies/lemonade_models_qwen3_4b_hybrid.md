<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Qwen3 4B Hybrid -mallin lataaminen Lemonadelle

Lemonade-palvelin tarjoaa Qwen3 4B Hybrid -mallia (`Qwen3-4B-Hybrid`), joka toimii Ryzen AI -suorittimien NPU:lla ja GPU:lla. Voit ladata sen etukäteen seuraavasti:

```powershell
lemonade pull Qwen3-4B-Hybrid
```

Malli ilmestyy Lemonade-palvelimen ladattujen mallien luetteloon, kun lataus on valmis; alla oleva tarkistus varmistaa, että se on läsnä koneella.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-4b-hybrid-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-4B-Hybrid
```
<!-- @test:end -->
<!-- @os:end -->