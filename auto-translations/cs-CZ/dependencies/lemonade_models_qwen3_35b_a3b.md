<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Stažení modelu Qwen3.6 35B A3B pro Lemonade

Server Lemonade poskytuje model Qwen3.6 35B A3B (`Qwen3.6-35B-A3B-GGUF`). Chcete-li jej stáhnout předem:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Příkaz `lemonade run Qwen3.6-35B-A3B-GGUF` také stáhne model při prvním použití, pokud ještě není k dispozici, a poté jej načte pro inferenci.

Model se objeví v seznamu stažených modelů serveru Lemonade, jakmile stahování dokončí; níže uvedené kontroly potvrzují, že je na daném počítači přítomen.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-6-35b-a3b-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3.6-35B-A3B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-qwen3-6-35b-a3b-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Qwen3.6-35B-A3B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->