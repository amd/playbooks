<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Pobieranie modelu Qwen3.6 35B A3B dla Lemonade

Serwer Lemonade udostępnia model Qwen3.6 35B A3B (`Qwen3.6-35B-A3B-GGUF`). Aby pobrać go z wyprzedzeniem:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

`lemonade run Qwen3.6-35B-A3B-GGUF` również pobiera model przy pierwszym użyciu, jeśli nie jest on jeszcze dostępny, a następnie wczytuje go do wnioskowania.

Model pojawia się na liście pobranych modeli serwera Lemonade po zakończeniu pobierania; poniższe kontrole potwierdzają jego obecność na maszynie.

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