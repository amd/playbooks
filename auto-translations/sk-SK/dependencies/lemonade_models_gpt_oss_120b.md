<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Stiahnutie GPT-OSS 120B pre Lemonade

Lemonade server poskytuje model GPT-OSS 120B MXFP4 GGUF (`gpt-oss-120b-mxfp-GGUF`). Ak ho chcete stiahnuť vopred:

```bash
lemonade pull gpt-oss-120b-mxfp-GGUF
```

`lemonade run gpt-oss-120b-mxfp-GGUF` taktiež stiahne model pri prvom použití, ak ešte nie je prítomný, a následne ho načíta na inferenciu.

Model sa zobrazí v zozname stiahnutých modelov na Lemonade serveri hneď po dokončení sťahovania; nasledujúce kontroly potvrdia, že je prítomný v zariadení.

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