<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### A Gemma-4 E2B modell letöltése a Lemonade számára

A Lemonade szerver kiszolgálja a Gemma-4 E2B modellt (`Gemma-4-E2B-it-GGUF`). Az előzetes letöltéshez:

```bash
lemonade pull Gemma-4-E2B-it-GGUF
```

A `lemonade run Gemma-4-E2B-it-GGUF` parancs az első használatkor is letölti a modellt, ha az még nincs jelen, majd betölti következtetéshez.

A modell a letöltés befejezése után megjelenik a Lemonade szerver letöltött modelljeinek listájában; az alábbi ellenőrzések igazolják, hogy jelen van a gépen.

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