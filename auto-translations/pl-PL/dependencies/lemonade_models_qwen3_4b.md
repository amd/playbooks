<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Pobieranie modelu Qwen3.5 4B dla Lemonade

Serwer Lemonade udostępnia model Qwen3.5 4B (`Qwen3.5-4B-GGUF`). Aby pobrać go z wyprzedzeniem:

```bash
lemonade pull Qwen3.5-4B-GGUF
```

Polecenie `lemonade run Qwen3.5-4B-GGUF` przy pierwszym użyciu również pobiera model, jeśli nie jest on jeszcze dostępny, a następnie wczytuje go do pamięci na potrzeby wnioskowania.

Model pojawia się na liście pobranych modeli serwera Lemonade po zakończeniu pobierania; poniższe kontrole potwierdzają jego obecność na komputerze.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-5-4b-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3.5-4B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-qwen3-5-4b-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Qwen3.5-4B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->