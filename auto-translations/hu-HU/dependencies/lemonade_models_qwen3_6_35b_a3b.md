<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Qwen3.6 35B A3B letöltése Lemonade-hez

A Lemonade szerver a Qwen3.6 35B A3B modellt (`Qwen3.6-35B-A3B-GGUF`) szolgálja ki. Az előzetes letöltéshez:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

A `lemonade run Qwen3.6-35B-A3B-GGUF` parancs az első használatkor szintén letölti a modellt, ha az még nincs jelen, majd betölti a következtetéshez.

A modell a letöltés befejezése után megjelenik a Lemonade szerver letöltött modelljeinek listájában; az alábbi ellenőrzések megerősítik, hogy a gépen megtalálható.

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