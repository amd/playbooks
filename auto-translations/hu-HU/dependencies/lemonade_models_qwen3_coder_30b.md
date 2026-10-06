<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### A Qwen3-Coder 30B A3B letöltése a Lemonade számára

A Lemonade szerver a Qwen3-Coder 30B A3B modellt (`Qwen3-Coder-30B-A3B-Instruct-GGUF`) szolgálja ki. Az előzetes letöltéshez:

```bash
lemonade pull Qwen3-Coder-30B-A3B-Instruct-GGUF
```

A `lemonade run Qwen3-Coder-30B-A3B-Instruct-GGUF` parancs az első használatkor is letölti a modellt, ha az még nincs jelen, majd betölti a következtetéshez.

A modell a letöltés befejezése után megjelenik a Lemonade szerver letöltött modellek listájában; az alábbi ellenőrzések megerősítik, hogy jelen van a gépen.

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