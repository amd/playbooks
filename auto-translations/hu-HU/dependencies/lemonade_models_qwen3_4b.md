<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### A Qwen3.5 4B letöltése a Lemonade-hoz

A Lemonade szerver a Qwen3.5 4B modellt (`Qwen3.5-4B-GGUF`) szolgálja ki. Az előzetes letöltéshez:

```bash
lemonade pull Qwen3.5-4B-GGUF
```

A `lemonade run Qwen3.5-4B-GGUF` parancs is letölti a modellt az első használatkor, ha az még nincs jelen, majd betölti a következtetéshez.

A modell a letöltés befejezése után megjelenik a Lemonade szerver letöltött modelleket tartalmazó listájában; az alábbi ellenőrzések megerősítik, hogy jelen van a gépen.

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