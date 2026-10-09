<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### GPT-OSS 20B downloaden voor Lemonade

De Lemonade-server serveert het GPT-OSS 20B MXFP4 GGUF-model (`gpt-oss-20b-mxfp4-GGUF`). Om het van tevoren te downloaden:

```bash
lemonade pull gpt-oss-20b-mxfp4-GGUF
```

`lemonade run gpt-oss-20b-mxfp4-GGUF` downloadt het model ook bij het eerste gebruik als het nog niet aanwezig is, en laadt het vervolgens voor inferentie.

Het model verschijnt in de lijst met gedownloade modellen van de Lemonade-server zodra het ophalen is voltooid; de onderstaande controles bevestigen dat het aanwezig is op de machine.

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