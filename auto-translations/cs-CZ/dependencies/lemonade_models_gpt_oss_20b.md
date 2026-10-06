<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Stažení GPT-OSS 20B pro Lemonade

Server Lemonade obsluhuje model GPT-OSS 20B MXFP4 GGUF (`gpt-oss-20b-mxfp4-GGUF`). Pro jeho stažení předem:

```bash
lemonade pull gpt-oss-20b-mxfp4-GGUF
```

Příkaz `lemonade run gpt-oss-20b-mxfp4-GGUF` také stáhne model při prvním použití, pokud ještě není k dispozici, a poté jej načte pro inferenci.

Model se v seznamu stažených modelů serveru Lemonade objeví po dokončení stahování; níže uvedené kontroly potvrzují jeho přítomnost na daném počítači.

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