<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Hämtar Qwen3.6 35B A3B för Lemonade

Lemonade-servern tillhandahåller modellen Qwen3.6 35B A3B (`Qwen3.6-35B-A3B-GGUF`). Så här hämtar du den i förväg:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

`lemonade run Qwen3.6-35B-A3B-GGUF` hämtar också modellen vid första användningen om den inte redan finns, och laddar den sedan för inferens.

Modellen visas i Lemonade-serverns lista över hämtade modeller när hämtningen är klar. Kontrollerna nedan bekräftar att den finns på datorn.

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