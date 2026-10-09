<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Preuzimanje GPT-OSS 20B za Lemonade

Lemonade server servira GPT-OSS 20B MXFP4 GGUF model (`gpt-oss-20b-mxfp4-GGUF`). Da biste ga preuzeli unapred:

```bash
lemonade pull gpt-oss-20b-mxfp4-GGUF
```

`lemonade run gpt-oss-20b-mxfp4-GGUF` takođe preuzima model prilikom prve upotrebe ako već nije prisutan, a zatim ga učitava za zaključivanje.

Model se pojavljuje na listi preuzetih modela Lemonade servera čim se preuzimanje završi; provere ispod potvrđuju da je prisutan na mašini.

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