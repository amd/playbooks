<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### A GPT-OSS 20B letöltése a Lemonade számára

A Lemonade szerver a GPT-OSS 20B MXFP4 GGUF modellt (`gpt-oss-20b-mxfp4-GGUF`) szolgálja ki. Az előzetes letöltéshez:

```bash
lemonade pull gpt-oss-20b-mxfp4-GGUF
```

A `lemonade run gpt-oss-20b-mxfp4-GGUF` parancs az első használatkor is letölti a modellt, ha az még nincs jelen, majd betölti következtetéshez.

A modell a letöltés befejezése után megjelenik a Lemonade szerver letöltött modelleket tartalmazó listájában; az alábbi ellenőrzések megerősítik, hogy jelen van a gépen.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-gpt-oss-20b-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:gpt-oss-20b-mxfp4-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-gpt-oss-20b-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q gpt-oss-20b-mxfp4-GGUF
```
<!-- @test:end -->
<!-- @os:end -->