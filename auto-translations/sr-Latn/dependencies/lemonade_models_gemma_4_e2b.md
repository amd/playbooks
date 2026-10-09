<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Preuzimanje Gemma-4 E2B modela za Lemonade

Lemonade server servira Gemma-4 E2B model (`Gemma-4-E2B-it-GGUF`). Da biste ga unapred preuzeli:

```bash
lemonade pull Gemma-4-E2B-it-GGUF
```

`lemonade run Gemma-4-E2B-it-GGUF` takođe preuzima model prilikom prve upotrebe ako već nije prisutan, a zatim ga učitava za zaključivanje (inferenciju).

Model se pojavljuje na listi preuzetih modela na Lemonade serveru čim se preuzimanje završi; provere ispod potvrđuju da je prisutan na mašini.

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