<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Stažení Qwen3-Coder 30B A3B pro Lemonade

Server Lemonade obsluhuje model Qwen3-Coder 30B A3B (`Qwen3-Coder-30B-A3B-Instruct-GGUF`). Chcete-li jej stáhnout předem:

```bash
lemonade pull Qwen3-Coder-30B-A3B-Instruct-GGUF
```

Příkaz `lemonade run Qwen3-Coder-30B-A3B-Instruct-GGUF` také stáhne model při prvním použití, pokud ještě není k dispozici, a poté jej načte pro inferenci.

Model se objeví v seznamu stažených modelů serveru Lemonade po dokončení stažení; níže uvedené kontroly potvrzují, že je na počítači přítomen.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-coder-30b-a3b-instruct-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-Coder-30B-A3B-Instruct-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-qwen3-coder-30b-a3b-instruct-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Qwen3-Coder-30B-A3B-Instruct-GGUF
```
<!-- @test:end -->
<!-- @os:end -->