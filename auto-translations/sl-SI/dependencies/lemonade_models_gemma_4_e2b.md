<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Prenos modela Gemma-4 E2B za Lemonade

Strežnik Lemonade postreže model Gemma-4 E2B (`Gemma-4-E2B-it-GGUF`). Za predhodni prenos:

```bash
lemonade pull Gemma-4-E2B-it-GGUF
```

`lemonade run Gemma-4-E2B-it-GGUF` ob prvi uporabi prav tako prenese model, če ta še ni prisoten, nato pa ga naloži za sklepanje.

Model se na seznamu prenesenih modelov strežnika Lemonade prikaže po zaključenem prenosu; spodnja preverjanja potrdijo, da je prisoten na napravi.

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