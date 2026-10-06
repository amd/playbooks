<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Sťahovanie GPT-OSS 120B pre Lemonade

Server Lemonade poskytuje model GPT-OSS 120B MXFP4 GGUF (`gpt-oss-120b-mxfp-GGUF`). Ak ho chcete stiahnuť vopred:

```bash
lemonade pull gpt-oss-120b-mxfp-GGUF
```

Príkaz `lemonade run gpt-oss-120b-mxfp-GGUF` model pri prvom použití stiahne, ak ešte nie je prítomný, a následne ho načíta na inferenciu.

Model sa v zozname stiahnutých modelov servera Lemonade zobrazí po dokončení sťahovania; nižšie uvedené kontroly potvrdia, že sa nachádza na danom počítači.

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