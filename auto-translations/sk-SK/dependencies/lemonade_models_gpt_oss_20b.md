<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Stiahnutie modelu GPT-OSS 20B pre Lemonade

Server Lemonade poskytuje model GPT-OSS 20B MXFP4 GGUF (`gpt-oss-20b-mxfp4-GGUF`). Ak ho chcete stiahnuť vopred:

```bash
lemonade pull gpt-oss-20b-mxfp4-GGUF
```

Príkaz `lemonade run gpt-oss-20b-mxfp4-GGUF` tiež pri prvom použití stiahne model, ak ešte nie je prítomný, a následne ho načíta na inferenciu.

Model sa v zozname stiahnutých modelov na serveri Lemonade zobrazí po dokončení sťahovania; nasledujúce kontroly potvrdzujú, že je na počítači prítomný.

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