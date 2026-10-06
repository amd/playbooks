<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Pobieranie modelu GPT-OSS 120B dla Lemonade

Serwer Lemonade udostępnia model GPT-OSS 120B MXFP4 GGUF (`gpt-oss-120b-mxfp-GGUF`). Aby pobrać go z wyprzedzeniem:

```bash
lemonade pull gpt-oss-120b-mxfp-GGUF
```

Polecenie `lemonade run gpt-oss-120b-mxfp-GGUF` również pobiera model przy pierwszym użyciu, jeśli nie jest on jeszcze dostępny, a następnie wczytuje go do wnioskowania.

Model pojawia się na liście pobranych modeli serwera Lemonade po zakończeniu pobierania; poniższe sprawdzenia potwierdzają jego obecność na maszynie.

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