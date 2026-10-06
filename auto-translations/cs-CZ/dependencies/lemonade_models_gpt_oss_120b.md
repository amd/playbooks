<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Stažení GPT-OSS 120B pro Lemonade

Server Lemonade obsluhuje model GPT-OSS 120B MXFP4 GGUF (`gpt-oss-120b-mxfp-GGUF`). Chcete-li jej stáhnout předem:

```bash
lemonade pull gpt-oss-120b-mxfp-GGUF
```

Příkaz `lemonade run gpt-oss-120b-mxfp-GGUF` také stáhne model při prvním použití, pokud ještě není k dispozici, a poté jej načte pro inferenci.

Model se objeví v seznamu stažených modelů serveru Lemonade po dokončení stahování; níže uvedené kontroly potvrzují, že je na počítači přítomen.

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