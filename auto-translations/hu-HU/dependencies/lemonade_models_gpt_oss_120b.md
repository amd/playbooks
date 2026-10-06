<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### GPT-OSS 120B letöltése a Lemonade-hez

A Lemonade szerver a GPT-OSS 120B MXFP4 GGUF modellt (`gpt-oss-120b-mxfp-GGUF`) szolgálja ki. Előzetes letöltéséhez:

```bash
lemonade pull gpt-oss-120b-mxfp-GGUF
```

A `lemonade run gpt-oss-120b-mxfp-GGUF` parancs is letölti a modellt első használatkor, ha még nincs jelen, majd betölti következtetéshez.

A modell megjelenik a Lemonade szerver letöltött modellek listájában, amint a letöltés befejeződik; az alábbi ellenőrzések megerősítik, hogy jelen van a gépen.

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