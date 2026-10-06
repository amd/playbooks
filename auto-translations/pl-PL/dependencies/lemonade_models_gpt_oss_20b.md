<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Pobieranie modelu GPT-OSS 20B dla Lemonade

Serwer Lemonade udostępnia model GPT-OSS 20B MXFP4 GGUF (`gpt-oss-20b-mxfp4-GGUF`). Aby pobrać go z wyprzedzeniem:

```bash
lemonade pull gpt-oss-20b-mxfp4-GGUF
```

Polecenie `lemonade run gpt-oss-20b-mxfp4-GGUF` pobiera model przy pierwszym użyciu, jeśli nie jest on jeszcze dostępny, a następnie ładuje go do wnioskowania.

Model pojawia się na liście pobranych modeli serwera Lemonade po zakończeniu pobierania; poniższe kontrole potwierdzają jego obecność na komputerze.

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