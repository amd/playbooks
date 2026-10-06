<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Preuzimanje Qwen3.6 35B A3B za Lemonade

Lemonade server opslužuje model Qwen3.6 35B A3B (`Qwen3.6-35B-A3B-GGUF`). Da biste ga preuzeli unapred:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

`lemonade run Qwen3.6-35B-A3B-GGUF` takođe preuzima model prilikom prve upotrebe ako već nije prisutan, a zatim ga učitava za zaključivanje (inference).

Model se pojavljuje na listi preuzetih modela Lemonade servera čim se preuzimanje završi; provere ispod potvrđuju da je prisutan na mašini.

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