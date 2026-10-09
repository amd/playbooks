<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Nedladdning av Gemma-4 E2B för Lemonade

Lemonade-servern serverar Gemma-4 E2B-modellen (`Gemma-4-E2B-it-GGUF`). För att ladda ner den i förväg:

```bash
lemonade pull Gemma-4-E2B-it-GGUF
```

`lemonade run Gemma-4-E2B-it-GGUF` laddar även ner modellen vid första användningen om den inte redan finns, och laddar den sedan för inferens.

Modellen visas i Lemonade-serverns lista över nedladdade modeller när hämtningen är klar; kontrollerna nedan bekräftar att den finns på maskinen.

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