<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Stažení GPT-OSS 120B pro Lemonade

Server Lemonade obsluhuje model GPT-OSS 120B MXFP4 GGUF (`gpt-oss-120b-mxfp-GGUF`). Chcete-li jej stáhnout předem:

```bash
lemonade pull gpt-oss-120b-mxfp-GGUF
```

Příkaz `lemonade run gpt-oss-120b-mxfp-GGUF` model při prvním použití také stáhne, pokud ještě není k dispozici, a poté jej načte pro inferenci.

Model se v seznamu stažených modelů serveru Lemonade objeví po dokončení stahování; níže uvedené kontroly potvrdí, že je na stroji přítomen.

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