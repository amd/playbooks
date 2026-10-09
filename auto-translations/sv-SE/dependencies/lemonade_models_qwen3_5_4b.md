<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Ladda ner Qwen3.5 4B för Lemonade

Lemonade-servern serverar modellen Qwen3.5 4B (`Qwen3.5-4B-GGUF`). För att ladda ner den i förväg:

```bash
lemonade pull Qwen3.5-4B-GGUF
```

`lemonade run Qwen3.5-4B-GGUF` laddar även ner modellen vid första användningen om den inte redan finns, och läser sedan in den för inferens.

Modellen visas i Lemonade-serverns lista över nedladdade modeller när hämtningen är klar; kontrollerna nedan bekräftar att den finns på maskinen.

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