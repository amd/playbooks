<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### A GPT-OSS 120B letöltése a Lemonade számára

A Lemonade szerver a GPT-OSS 120B MXFP4 GGUF modellt (`gpt-oss-120b-mxfp-GGUF`) szolgálja ki. Az előzetes letöltéséhez:

```bash
lemonade pull gpt-oss-120b-mxfp-GGUF
```

A `lemonade run gpt-oss-120b-mxfp-GGUF` parancs első használatkor szintén letölti a modellt, ha az még nincs jelen, majd betölti következtetéshez.

A modell a letöltés befejezése után megjelenik a Lemonade szerver letöltött modelljeinek listájában; az alábbi ellenőrzések megerősítik, hogy jelen van a gépen.

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