<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Stažení Gemma-4 E2B pro Lemonade

Server Lemonade obsluhuje model Gemma-4 E2B (`Gemma-4-E2B-it-GGUF`). Chcete-li jej stáhnout předem:

```bash
lemonade pull Gemma-4-E2B-it-GGUF
```

Příkaz `lemonade run Gemma-4-E2B-it-GGUF` model při prvním použití rovněž stáhne, pokud ještě není k dispozici, a poté jej načte pro inferenci.

Jakmile stahování dokončí, model se zobrazí v seznamu stažených modelů serveru Lemonade; níže uvedené kontroly ověří, že je na počítači skutečně přítomen.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-gemma-4-e2b-it-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Gemma-4-E2B-it-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-gemma-4-e2b-it-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Gemma-4-E2B-it-GGUF
```
<!-- @test:end -->
<!-- @os:end -->