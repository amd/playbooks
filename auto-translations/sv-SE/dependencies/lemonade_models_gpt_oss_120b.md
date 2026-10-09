<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Hämta GPT-OSS 120B för Lemonade

Lemonade-servern serverar modellen GPT-OSS 120B MXFP4 GGUF (`gpt-oss-120b-mxfp-GGUF`). Så här hämtar du den i förväg:

```bash
lemonade pull gpt-oss-120b-mxfp-GGUF
```

`lemonade run gpt-oss-120b-mxfp-GGUF` hämtar också modellen vid första användningen om den inte redan finns, och läser sedan in den för inferens.

Modellen visas i Lemonade-serverns lista över hämtade modeller när hämtningen är klar; kontrollerna nedan bekräftar att den finns på maskinen.

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