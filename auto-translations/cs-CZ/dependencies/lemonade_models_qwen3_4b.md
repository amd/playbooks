<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Stažení modelu Qwen3.5 4B pro Lemonade

Server Lemonade obsluhuje model Qwen3.5 4B (`Qwen3.5-4B-GGUF`). Chcete-li jej stáhnout předem:

```bash
lemonade pull Qwen3.5-4B-GGUF
```

`lemonade run Qwen3.5-4B-GGUF` model také při prvním použití stáhne, pokud ještě není k dispozici, a poté jej načte pro inferenci.

Model se objeví v seznamu stažených modelů serveru Lemonade, jakmile je stahování dokončeno; níže uvedené kontroly potvrdí, že je na počítači přítomen.

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