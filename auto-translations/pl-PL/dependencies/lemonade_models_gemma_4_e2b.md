<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Pobieranie modelu Gemma-4 E2B dla Lemonade

Serwer Lemonade udostępnia model Gemma-4 E2B (`Gemma-4-E2B-it-GGUF`). Aby pobrać go z wyprzedzeniem:

```bash
lemonade pull Gemma-4-E2B-it-GGUF
```

Polecenie `lemonade run Gemma-4-E2B-it-GGUF` również pobiera model przy pierwszym użyciu, jeśli nie jest on jeszcze dostępny, a następnie ładuje go do wnioskowania.

Model pojawia się na liście pobranych modeli serwera Lemonade po zakończeniu pobierania; poniższe kontrole potwierdzają jego obecność na maszynie.

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