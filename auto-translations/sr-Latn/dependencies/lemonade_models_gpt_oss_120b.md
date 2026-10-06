<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Preuzimanje GPT-OSS 120B za Lemonade

Lemonade server servira GPT-OSS 120B MXFP4 GGUF model (`gpt-oss-120b-mxfp-GGUF`). Da biste ga preuzeli unapred:

```bash
lemonade pull gpt-oss-120b-mxfp-GGUF
```

`lemonade run gpt-oss-120b-mxfp-GGUF` takođe preuzima model prilikom prve upotrebe ako već nije prisutan, a zatim ga učitava radi zaključivanja.

Model se pojavljuje na listi preuzetih modela Lemonade servera nakon što se preuzimanje završi; provere ispod potvrđuju da je prisutan na mašini.

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